# GGW800開発足場の導入receipt

記録時刻: 2026-11-05T02:28:08.120Z  
実行者: ChatGPT / GitHub connector。対象: saitoomituru/GGW800-GodGUNDAM800Wing。新repositoryは開始時empty。利用者はsubmodule導入・Manifest asset化・既存Issue範囲の文書整備・CAD/SPICE公開方針を明示依頼。

## 固定source

- SphereOS Atlantis: `4380940f91c49cdc14b9fcc45783528647ed17d7`
- Manifest: `446470b27f6a7bf6d0cb498f87ac5658639ba7ad`、AGENTS blob `1a7dde10fb3ac6e46c54d1b4c3b19e781718c42e`
- MAGI bundle: canonical_coordinate 0.200.1、legacy path 0.2.1、previous_bundle 0.2.0、Skill workflows IMPLEMENTED_ALPHA。
- 前回Manifest PR #73はmerge済み。原記録を固定revisionから受領し設計文書へ再配置。
- GGW800の初期commit: `5b1a576c115d22b7ce7f1007d6897f92db62afb2`。今回の実装・文書・gitlinkはこの上へ追加。

## source・導入方法

AtlantisのAGENTS、README、SPHERE-DOS、導入文書、CONTRIBUTING、二重記述憲章、lineage・license方針、CLI parser、bootstrap、resolver、MAGI bundle・source-mapと三Position Skillを参照。Surface 2を採用し、Manifestはassetsの固定submoduleへ配置する。
新workspaceはGGW800.code-workspaceの3folderのみ。上流編集や別workspace・secretの探索は行わない。

## Maxwell

Declared Position: 生存しつつ設計・実験へ戻る条件を残す。3畳縮小を最終目標にせず、CAD・SPICE・統合実験を資源到着に応じて進める。
Position-talk Risk: 助手が足場の完成を資源問題解消へすり替える危険。材料・電力・加工・計測・人手の要求を保持。

## Uriel

Declared Position: Gitへの設置、CLI実行、CAD/SPICEの設計、発電実測を分ける。
[FACT] GitHub上の公開source・commitとempty状態を取得。
[FIX] gitlinkとlock・workspaceを照合するcheck、既存CLI・resolverを呼ぶmake／CIを配置。
[UNKNOWN] 本作業用のlocal実行hostは利用不能。clone、CLI・devcontainer起動、CAD/SPICE、機器試験はこのreceipt作成時未実行。GitHub Actionsのrunを別証拠として確認する。

## Raphael

Declared Position: 開発ツール、Manifest asset、製品設計、現地生存運用の棚を保持。
[FIX] 製品の設計・CAD・回路・実験はGGW800、生活縮小と上位資源窓口はManifest #71/#72へ接続。神格・着想を保持し、温度・W/Whの実測と混同しない。
[INTERPRETATION] submodule設置は装置runtimeへのSphere統合でも、永続人格の稼働でもない。CERN hardware、Apache tool、CC文書、上流licenseを分ける。

## 再利用と検証

reuse: Atlantisのvenv bootstrap、atlantis_cli、MAGI source resolver。
adapt: Makefileとdevcontainer。
create: GGW800固有のpin/lock/3folder検査。Atlantis workspace registryとは入力と対象集合が異なるため、既存registryを改変しない。

checks: 公開後のtree/gitlink・ファイル読み戻し、GitHub Actionsのbootstrap／boot／status／source解決。CAD・回路・実測の結果は作らない。
[SEMANTIC-STOP] 未測定寸法・電圧・素子定数・性能を補完しない。historical-oae-unavailable。過去の観測を遡及生成しない。

## 実行確認の追記

確認時刻: 2026-11-05T02:29:34.179Z  
対象commit: `b05bd68d083ffbd02431e304df7563eac38f6f4f`  
[GitHub Actions run 41955427068](https://github.com/saitoomituru/GGW800-GodGUNDAM800Wing/actions/runs/41955427068) / job 127009084821、conclusion: **success**。

- 公開repositoryのcheckoutと直接submodule2件の取得が成功。
- Python 3.12上で既存bootstrapによるvenv再構築が成功。
- GGW800 gitlink / lock / workspace検査がPASS。
- atlantis_cli interfaces、Sphere-DOS boot、statusが成功。
- MAGIのmaxwell・uriel・raphael・composite、profile zeroroomlabのsource解決が成功し、各required_missing_locallyは0。
- root文書の相対link検査に欠損なし。JSON設定のparseを確認。

この結果はNative Engineering SurfaceのCI上の再構築確認であり、devcontainer GUI起動・CAD/SPICE実モデル・熱電発電実機・現地越冬の合格ではない。本追記は文書のみで、検証済みcodeとgitlinkを変更しない。
