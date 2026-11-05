# SPDX-License-Identifier: Apache-2.0
ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
AT := $(ROOT)/.vendor/SphereOS-Atlantis
MF := $(ROOT)/assets/ZeroRoomLab-manifest
PY := $(AT)/.venv/bin/python

.PHONY: help bootstrap sphere audit verify

help:
	@printf '%s\n' 'make bootstrap: 固定submoduleとvenvを準備' 'make sphere ARGS="interfaces --json": Atlantis CLI' 'make audit: MAGI sourceを解決' 'make verify: 開発足場のsmoke確認'

bootstrap:
	git -C "$(ROOT)" submodule update --init -- .vendor/SphereOS-Atlantis assets/ZeroRoomLab-manifest
	python3 "$(AT)/scripts/bootstrap_venv.py" --json

sphere:
	cd "$(AT)" && "$(PY)" -B -m atlantis_cli $(ARGS)

audit:
	cd "$(AT)" && "$(PY)" -B magi/0.2.1/resolve_sources.py --slot maxwell --profile zeroroomlab --repo-root "ZeroRoomLab-manifest=$(MF)" --require-local
	cd "$(AT)" && "$(PY)" -B magi/0.2.1/resolve_sources.py --slot uriel --profile zeroroomlab --repo-root "ZeroRoomLab-manifest=$(MF)" --require-local
	cd "$(AT)" && "$(PY)" -B magi/0.2.1/resolve_sources.py --slot raphael --profile zeroroomlab --repo-root "ZeroRoomLab-manifest=$(MF)" --require-local
	cd "$(AT)" && "$(PY)" -B magi/0.2.1/resolve_sources.py --slot composite --profile zeroroomlab --repo-root "ZeroRoomLab-manifest=$(MF)" --require-local

verify:
	python3 "$(ROOT)/scripts/check_scaffold.py"
	git -C "$(ROOT)" submodule status -- .vendor/SphereOS-Atlantis assets/ZeroRoomLab-manifest
	$(MAKE) --no-print-directory sphere ARGS="interfaces --json"
	$(MAKE) --no-print-directory sphere ARGS="sphere-dos boot --json"
	$(MAKE) --no-print-directory sphere ARGS="sphere-dos status --json"
	$(MAKE) --no-print-directory audit
