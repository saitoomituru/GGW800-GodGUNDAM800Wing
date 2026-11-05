# 開発とrevision更新

## 再構築

`make bootstrap`はGitの直接submodule2件とAtlantisのvenvだけを準備する。`make verify`で固定revisionとworkspace、既存CLIのinterfaces・Sphere-DOS boot/status、三Positionとcompositeのsource解決を確認する。部品のruntime・発電装置・CAD/SPICEの実動作まで合格するcheckではない。

手動で準備する場合:

```console
git submodule update --init -- .vendor/SphereOS-Atlantis assets/ZeroRoomLab-manifest
python3 .vendor/SphereOS-Atlantis/scripts/bootstrap_venv.py --json
```

その後、Atlantis directoryで `.venv/bin/python -B -m atlantis_cli interfaces --json` 等を実行する。Windowsでは `.venv\Scripts\python.exe` へ読み替える。GUI作業机は `GGW800.code-workspace`。devcontainerは上流で使用するPython 3.12 imageを採用し、作成後にbootstrapする。

## 操作と副作用

| 操作 | 作用 |
| --- | --- |
| bootstrap | 明示network取得、submodule展開、venv作成 |
| sphere interfaces | interface一覧のread |
| sphere-dos boot | Atlantis内の.atlantisにlocal session receiptを生成 |
| audit | source-mapとprofileのsource存在を解決。モデルや外部APIは呼ばない |
| verify | lock・gitlink・workspace、CLIとsource解決のsmoke確認 |

GGW800の装置runtimeへAtlantisを組み込まない。既定の `workspace init` は別componentをcloneするので、この導入では呼ばない。

## 更新

1. 更新先の正確なcommit、AGENTS・導入契約・licenseと影響を読む。
2. 変更前の利用可能branchとunknownを保持する。
3. 対象submoduleだけを新revisionへ明示更新し、gitlinkと `dependencies.lock.json` を同じ変更で揃える。
4. `make verify` と変更に応じたCAD/SPICE・実機検証を行う。
5. commit・環境・結果・未試験をreceiptへ残す。自動 `--remote` 更新や上流改変はしない。

## tool再利用の判断

Atlantisの `scripts/bootstrap_venv.py`、`atlantis_cli`、`magi/0.2.1/resolve_sources.py` を再利用。Makefileは呼出adapterだけを追加する。

`scripts/check_scaffold.py` はGGW800固有のgitlink・lock・3folder workspaceを検査する。Atlantisの `workspace/components.json` はAtlantis自身の別component集合を扱うので、そのschemaを書き換えてGGW800へ流用しない。CLIやresolverの別実装は作らない。

ローカルhostが本作業時に利用不能だったため、CLI実行はGitHub Actionsへ引き渡す。CIの結果はworkflow runを証拠とし、ファイル登録だけで起動確認済みにはしない。

## 計算Tools / PLI・CLI・Actions

[Tools索引](../Tools/README.md)からthermalCoreCalcのAPI・CLI・計算workflowを利用する。`make test-thermal`は単位・回帰・前提拒否を検証し、`make verify`にも含める。`make thermal-calc`は基準scenarioの計算だけを行いsubmodule展開を必要としない。

code正本・scenario・model_id・hash・run URLに出力を接続する。MAGIのsource解決成功を物理の実証へ変換せず、実験結果で拘束を更新する。
