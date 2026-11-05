# SPDX-License-Identifier: Apache-2.0
"""JSON入力からthermalCoreCalcを実行し、再現receiptを返す。"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from .core import calculate_scenario


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def reject_constant(value: str) -> None:
    raise ValueError(f"非有限JSON数値は使用不可: {value}")


def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"JSON keyが重複: {key}")
        result[key] = value
    return result


def source_hash() -> str:
    digest = hashlib.sha256()
    for path in sorted(Path(__file__).parent.glob("*.py")):
        digest.update(path.name.encode("utf-8") + b"\0" + path.read_bytes() + b"\0")
    return digest.hexdigest()


def git_revision() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(Path(__file__).resolve().parents[2]), "rev-parse", "HEAD"],
            text=True, stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="前提を明記したscenario JSON")
    parser.add_argument("--output", type=Path, help="出力JSON。省略時は標準出力")
    args = parser.parse_args(argv)
    try:
        raw = args.input.read_bytes()
        scenario = json.loads(raw, parse_constant=reject_constant,
                              object_pairs_hook=reject_duplicate_keys)
        result = calculate_scenario(scenario)
        output = {
            "receipt_version": "thermalCoreCalc-receipt/1",
            "provenance": {
                "tool": "Tools.thermalCoreCalc",
                "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                "python_version": sys.version.split()[0],
                "git_revision": git_revision(),
                "module_source_sha256": source_hash(),
                "input_file_sha256": hashlib.sha256(raw).hexdigest(),
                "input_sha256": hashlib.sha256(canonical_bytes(scenario)).hexdigest(),
                "result_sha256": hashlib.sha256(canonical_bytes(result)).hexdigest(),
                "github_run_id": os.environ.get("GITHUB_RUN_ID"),
                "github_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
            },
            "result": result,
        }
        rendered = json.dumps(output, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        if args.output:
            args.output.write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
    except (OSError, ValueError, OverflowError) as error:
        print(f"thermalCoreCalc: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
