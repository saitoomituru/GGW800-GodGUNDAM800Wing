# SPDX-License-Identifier: Apache-2.0
"""TECの冷却仕様から定数モデルを推定し、開放端熱伝導を計算する。"""
from __future__ import annotations

from copy import deepcopy
import math
from typing import Any, Mapping

MODEL_ID = "tec-constant-properties-open-circuit/1"
ASSUMPTIONS = {
    "thermal_arrangement": "parallel",
    "electrical_condition": "open_circuit",
    "cold_reservoir": "isothermal_infinite",
    "contact_thermal_resistance_k_per_w": 0,
    "heat_distribution": "uniform",
    "bypass_heat_flow_w": 0,
}
SPEC_KEYS = {
    "id", "hot_side_c", "qmax_w", "delta_tmax_k",
    "imax_a", "resistance_ohm", "source_url",
}


def _fields(value: Any, expected: set[str], name: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{name}: objectが必要")
    actual = set(value)
    if actual != expected:
        raise ValueError(
            f"{name}: missing={sorted(expected-actual)}, unknown={sorted(actual-expected)}"
        )
    return value


def _number(value: Any, name: str, *, positive: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name}: 有限の数値が必要")
    try:
        number = float(value)
    except OverflowError as error:
        raise ValueError(f"{name}: 有限の数値が必要") from error
    if not math.isfinite(number) or (positive and number <= 0):
        raise ValueError(f"{name}: 有限{'かつ正' if positive else ''}の数値が必要")
    return number


def _temperature(value: Any, name: str) -> float:
    value = _number(value, name)
    if value <= -273.15:
        raise ValueError(f"{name}: 絶対零度より高い温度が必要")
    return value


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name}: 空でない文字列が必要")
    return value


def fit_cooling_spec(spec: Mapping[str, Any]) -> dict[str, Any]:
    """Qmax/ΔTmaxを同じImaxでの値として、αとKをfitする。Tは内部でK。"""
    spec = _fields(spec, SPEC_KEYS, "calibration")
    name = _text(spec["id"], "calibration.id")
    source = _text(spec["source_url"], "source_url")
    th_c = _temperature(spec["hot_side_c"], "calibration.hot_side_c")
    th_k = th_c + 273.15
    q = _number(spec["qmax_w"], "qmax_w", positive=True)
    dt = _number(spec["delta_tmax_k"], "delta_tmax_k", positive=True)
    current = _number(spec["imax_a"], "imax_a", positive=True)
    resistance = _number(spec["resistance_ohm"], "resistance_ohm", positive=True)
    if dt >= th_k:
        raise ValueError("calibration: ΔTmaxから得る冷面が絶対零度以下")
    alpha = (q + 0.5 * current**2 * resistance) / (th_k * current)
    conductance = q / dt - alpha * current
    _number(alpha, "derived.alpha", positive=True)
    _number(conductance, "derived.conductance", positive=True)
    return {
        "id": name,
        "calibration_hot_side_c": th_c,
        "seebeck_v_per_k": alpha,
        "conductance_w_per_k": conductance,
        "thermal_resistance_k_per_w": 1.0 / conductance,
        "electrical_resistance_ohm": resistance,
        "property_basis": "estimated_from_cooling_spec_not_measured",
        "source_url": source,
        "source_spec": dict(spec),
    }


def heat_input_at_temperature(
    *,
    module_count: int,
    conductance_w_per_k: float,
    area_per_module_mm2: float,
    cold_side_c: float,
    hot_side_c: float,
) -> dict[str, float]:
    """熱的並列・開放端・理想接触に限定したQ=N*K*ΔT。"""
    if isinstance(module_count, bool) or not isinstance(module_count, int) or module_count < 1:
        raise ValueError("module_count: 正の整数が必要")
    conductance = _number(conductance_w_per_k, "conductance_w_per_k", positive=True)
    area = _number(area_per_module_mm2, "area_per_module_mm2", positive=True)
    cold = _temperature(cold_side_c, "cold_side_c")
    hot = _temperature(hot_side_c, "hot_side_c")
    if hot < cold:
        raise ValueError("hot_side_cはcold_side_c以上が必要")
    total_k = module_count * conductance
    q = total_k * (hot - cold)
    total_area_mm2 = module_count * area
    result = {
        "hot_side_c": hot, "cold_side_c": cold, "delta_t_k": hot - cold,
        "total_conductance_w_per_k": total_k,
        "total_thermal_resistance_k_per_w": 1.0 / total_k,
        "total_area_mm2": total_area_mm2,
        "total_area_cm2": total_area_mm2 / 100.0,
        "heat_input_w": q,
        "heat_input_per_module_w": q / module_count,
        "heat_flux_w_per_cm2": q / (total_area_mm2 / 100.0),
    }
    for key, value in result.items():
        _number(value, "result." + key)
    return result


def calculate_scenario(scenario: Mapping[str, Any]) -> dict[str, Any]:
    """入力前提を検証して計算。I/O、clock、network、device controlは行わない。"""
    scenario = _fields(
        scenario,
        {"model_id", "module", "module_count", "cold_side_c", "hot_side_targets_c",
         "assumptions", "calibrations"},
        "scenario",
    )
    if scenario["model_id"] != MODEL_ID:
        raise ValueError(f"未対応model_id: {scenario['model_id']}")
    assumptions = _fields(scenario["assumptions"], set(ASSUMPTIONS), "assumptions")
    for key, expected in ASSUMPTIONS.items():
        actual = assumptions[key]
        if isinstance(expected, str):
            valid = isinstance(actual, str) and actual == expected
        else:
            valid = not isinstance(actual, bool) and _number(actual, key) == expected
        if not valid:
            raise ValueError(f"未対応の前提: {key}={actual!r}")
    module = _fields(scenario["module"], {"name", "width_mm", "height_mm", "limit_c"}, "module")
    _text(module["name"], "module.name")
    width = _number(module["width_mm"], "width_mm", positive=True)
    height = _number(module["height_mm"], "height_mm", positive=True)
    limit = _temperature(module["limit_c"], "limit_c")
    targets = scenario["hot_side_targets_c"]
    calibrations = scenario["calibrations"]
    if not isinstance(targets, list) or not 1 <= len(targets) <= 100:
        raise ValueError("hot_side_targets_c: 1〜100件の配列が必要")
    if not isinstance(calibrations, list) or not 1 <= len(calibrations) <= 100:
        raise ValueError("calibrations: 1〜100件の配列が必要")
    cold = _temperature(scenario["cold_side_c"], "cold_side_c")
    if limit < cold:
        raise ValueError("module.limit_cはcold_side_c以上が必要")
    fitted = [fit_cooling_spec(item) for item in calibrations]
    if len({x["id"] for x in fitted}) != len(fitted):
        raise ValueError("calibration.idが重複")
    cases = []
    for target in targets:
        hot = _temperature(target, "hot_side_targets_c")
        if hot > limit:
            raise ValueError("hot_side_targets_cがmodule.limit_cを超える")
        variants = []
        for properties in fitted:
            result = heat_input_at_temperature(
                module_count=scenario["module_count"],
                conductance_w_per_k=properties["conductance_w_per_k"],
                area_per_module_mm2=width * height,
                cold_side_c=cold,
                hot_side_c=hot,
            )
            result["calibration_id"] = properties["id"]
            variants.append(result)
        cases.append({
            "hot_side_c": hot,
            "relation_to_declared_limit": "at_boundary" if hot == limit else "below_boundary",
            "variants": variants,
            "heat_input_w_min": min(x["heat_input_w"] for x in variants),
            "heat_input_w_max": max(x["heat_input_w"] for x in variants),
        })
    return {
        "schema_version": "thermalCoreCalc-result/1",
        "model_id": MODEL_ID,
        "result_kind": "ideal_open_circuit_boundary_estimate",
        "input": deepcopy(scenario),
        "properties": fitted,
        "cases": cases,
        "scope": {
            "calibration_spread_is_confidence_interval": False,
            "temperature_dependence": "held_constant_extrapolation",
            "geometry_use": "area_reports_flux_only_K_is_not_rescaled",
            "real_device_validation": "not_tested",
            "safety_certification": "not_provided",
            "excluded": ["loaded_generator", "finite_snow", "contact_resistance",
                         "transient_heat", "uneven_heat", "bypass_heat"],
        },
    }
