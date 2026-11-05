# SPDX-License-Identifier: Apache-2.0
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from Tools.thermalCoreCalc import calculate_scenario, fit_cooling_spec, heat_input_at_temperature

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = ROOT / "Tools/thermalCoreCalc/scenarios/tec1-12706-four-snow0.json"


def baseline():
    return json.loads(SCENARIO.read_text(encoding="utf-8"))


class ThermalCoreTests(unittest.TestCase):
    def test_independent_conduction_and_area_units(self):
        result = heat_input_at_temperature(
            module_count=4, conductance_w_per_k=0.5, area_per_module_mm2=1600,
            cold_side_c=0, hot_side_c=100,
        )
        self.assertEqual(result["heat_input_w"], 200)
        self.assertEqual(result["total_thermal_resistance_k_per_w"], 0.5)
        self.assertEqual(result["total_area_cm2"], 64)
        self.assertEqual(result["heat_flux_w_per_cm2"], 3.125)

    def test_fit_recovers_both_declared_cooling_conditions(self):
        for spec in baseline()["calibrations"]:
            properties = fit_cooling_spec(spec)
            a, k, i, r = (properties["seebeck_v_per_k"],
                          properties["conductance_w_per_k"],
                          spec["imax_a"], spec["resistance_ohm"])
            th = spec["hot_side_c"] + 273.15
            self.assertAlmostEqual(a * th * i - 0.5 * i * i * r, spec["qmax_w"])
            tc = th - spec["delta_tmax_k"]
            self.assertAlmostEqual(a * tc * i - 0.5 * i * i * r
                                   - k * spec["delta_tmax_k"], 0)

    def test_regression_four_modules_boundary(self):
        scenario = baseline()
        original = deepcopy(scenario)
        result = calculate_scenario(scenario)
        self.assertEqual(scenario, original, "入力を変更しない")
        self.assertEqual(result, calculate_scenario(scenario), "pure resultは決定的")
        boundary = result["cases"][-1]
        self.assertAlmostEqual(boundary["heat_input_w_min"], 241.6911032028471)
        self.assertAlmostEqual(boundary["heat_input_w_max"], 250.53526175049166)
        self.assertEqual(boundary["relation_to_declared_limit"], "at_boundary")
        self.assertFalse(result["scope"]["calibration_spread_is_confidence_interval"])

    def test_count_scales_heat_and_inverse_resistance(self):
        one = baseline()
        one["module_count"] = 1
        four = calculate_scenario(baseline())["cases"][0]["variants"][0]
        single = calculate_scenario(one)["cases"][0]["variants"][0]
        self.assertAlmostEqual(four["heat_input_w"], single["heat_input_w"] * 4)
        self.assertAlmostEqual(four["total_thermal_resistance_k_per_w"],
                               single["total_thermal_resistance_k_per_w"] / 4)

    def test_area_does_not_invent_a_new_conductance(self):
        scenario = baseline()
        original = calculate_scenario(scenario)["cases"][0]["variants"][0]
        scenario["module"]["width_mm"] *= 2
        changed = calculate_scenario(scenario)["cases"][0]["variants"][0]
        self.assertEqual(original["heat_input_w"], changed["heat_input_w"])
        self.assertAlmostEqual(original["heat_flux_w_per_cm2"] / 2,
                               changed["heat_flux_w_per_cm2"])

    def test_zero_delta_and_shifted_cold_reservoir(self):
        args = dict(module_count=4, conductance_w_per_k=0.5, area_per_module_mm2=1600)
        self.assertEqual(heat_input_at_temperature(**args, cold_side_c=0, hot_side_c=0)
                         ["heat_input_w"], 0)
        self.assertEqual(heat_input_at_temperature(**args, cold_side_c=20, hot_side_c=100)
                         ["heat_input_w"], 160)

    def test_reject_invalid_or_unsupported_scenarios(self):
        mutations = [
            lambda x: x.update(module_count=0),
            lambda x: x.update(module_count=True),
            lambda x: x.update(module_count=4.0),
            lambda x: x.update(cold_side_c=-273.15),
            lambda x: x.update(cold_side_c=float("nan")),
            lambda x: x.update(hot_side_targets_c=[139]),
            lambda x: x.update(hot_side_targets_c=[-1]),
            lambda x: x.update(hot_side_targets_c=[]),
            lambda x: x.update(calibrations=[]),
            lambda x: x.update(model_id="unknown"),
            lambda x: x.update(extra=1),
            lambda x: x["module"].update(width_mm=float("inf")),
            lambda x: x["module"].update(width_mm=-1),
            lambda x: x["assumptions"].update(contact_thermal_resistance_k_per_w=0.1),
            lambda x: x["assumptions"].update(contact_thermal_resistance_k_per_w=False),
            lambda x: x["assumptions"].update(electrical_condition="matched_load"),
            lambda x: x["assumptions"].update(cold_reservoir="finite_snow"),
            lambda x: x["assumptions"].update(thermal_arrangement="series"),
            lambda x: x["calibrations"][0].update(imax_a=0),
            lambda x: x["calibrations"][0].update(resistance_ohm=100),
            lambda x: x["calibrations"][0].update(delta_tmax_k=500),
            lambda x: x["calibrations"][0].update(source_url=""),
            lambda x: x["calibrations"][1].update(id=x["calibrations"][0]["id"]),
        ]
        for mutation in mutations:
            scenario = baseline()
            mutation(scenario)
            with self.subTest(mutation=mutations.index(mutation)):
                with self.assertRaises(ValueError):
                    calculate_scenario(scenario)

    def test_cli_receipt_hash_reproducibility_and_error_exit(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "result.json"
            command = [sys.executable, "-B", "-m", "Tools.thermalCoreCalc",
                       "--input", str(SCENARIO), "--output", str(target)]
            subprocess.run(command, cwd=ROOT, check=True)
            first = json.loads(target.read_text())
            subprocess.run(command, cwd=ROOT, check=True)
            second = json.loads(target.read_text())
            self.assertEqual(first["provenance"]["result_sha256"],
                             second["provenance"]["result_sha256"])
            self.assertEqual(len(first["provenance"]["module_source_sha256"]), 64)
            invalid = Path(directory) / "bad.json"
            for body in ('{"x":NaN}', '{"model_id":1,"model_id":2}', '{"x":Infinity}'):
                invalid.write_text(body)
                failed = subprocess.run(
                    [sys.executable, "-B", "-m", "Tools.thermalCoreCalc",
                     "--input", str(invalid)], cwd=ROOT, capture_output=True, text=True,
                )
                self.assertEqual(failed.returncode, 2)
                self.assertEqual(failed.stdout, "")
                self.assertIn("thermalCoreCalc:", failed.stderr)


if __name__ == "__main__":
    unittest.main()
