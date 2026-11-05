#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""GGW800固有のGit pinと開発workspaceを検査する。"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    ".vendor/SphereOS-Atlantis": "https://github.com/saitoomituru/SphereOS-Atlantis.git",
    "assets/ZeroRoomLab-manifest": "https://github.com/saitoomituru/ZeroRoomLab-manifest.git",
}


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def main() -> None:
    lock = json.loads((ROOT / "dependencies.lock.json").read_text(encoding="utf-8"))
    dependencies = lock["dependencies"]
    paths = [item["path"] for item in dependencies]
    assert len(paths) == len(set(paths)) == len(EXPECTED), "依存pathの重複・欠損"
    assert set(paths) == set(EXPECTED), "未宣言の依存path"
    for item in dependencies:
        path, revision = item["path"], item["revision"]
        assert item["url"] == EXPECTED[path], (path, "URL不一致")
        assert len(revision) == 40 and all(c in "0123456789abcdef" for c in revision)
        entry = git("ls-files", "--stage", "--", path)
        metadata, indexed_path = entry.split("\t")
        assert indexed_path == path
        assert metadata.split() == ["160000", revision, "0"], (path, "gitlink不一致")
        assert git("-C", str(ROOT / path), "rev-parse", "HEAD") == revision, (path, "checkout不一致")
        configured = git("config", "-f", ".gitmodules", "submodule." + path + ".url")
        assert configured == EXPECTED[path], (path, ".gitmodules不一致")
    workspace = json.loads((ROOT / "GGW800.code-workspace").read_text(encoding="utf-8"))
    assert [x["path"] for x in workspace["folders"]] == [".", *EXPECTED], "workspace越境"
    for folder in workspace["folders"]:
        assert (ROOT / folder["path"]).is_dir(), folder["path"]
    print("GGW800 gitlink / lock / workspace: PASS")


if __name__ == "__main__":
    main()
