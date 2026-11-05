# thermalCoreCalc実装receipt

記録時刻: 2026-11-05T02:49:37.383Z  
基点: `ae3f61a8a3d185edb998b472ef77b0e4d0f486c4`  
利用者指定: 熱計算をTools/thermalCoreCalcへ関数化、変数を入力として再利用、GitHub Actions計算、PLI/CLIから同じcodeとreceiptへ接続、実験で拘束を更新する。

## sourceと再利用preflight

GGW800のAGENTS、workspace、設計・開発文書、lockとlicenseを参照。固定Atlantis `4380940f91c49cdc14b9fcc45783528647ed17d7` の公開treeにはthermal/heat/calcの既存toolがない。venv/CLI/MAGI resolverは継続利用し、熱計算の責務が異なるため、新規moduleをGGW800へ置いた。上流のAGENTS・bundle/source-mapは固定revisionを参照し、submodule pinは変更しない。

## Maxwell

Declared Position: 同じ計算を何度もLLMへ生成させず、実験・校正・反証に資源を使う。
Position-talk Risk: 初回の理想モデルを普遍的な正解へ昇格する危険。
[FIX] baselineとmodel IDを保持し、校正scenarioや新modelを増やせる。負荷・有限雪・接触抵抗等の枝は未対応として残す。

## Uriel

Declared Position: 出典、入力、式、単位、計算結果と実測を追跡する。
[FACT] 冷却仕様fitと開放端Q=N*K*ΔTをPythonへ固定。HB-Th25/Th50の推定は同じImaxでQmax/ΔTmaxを読む仮定。
[FIX] 未知field、単位不正、非有限数、重複JSON key、未対応前提を拒否。CLIは入力・model・source/code hash・result hash・Git revision・run IDを保存。
[UNKNOWN] 手持ち4枚の製造元・実測K・温度依存は未校正。138℃到達計算を安全認定値にしない。

## Raphael

Declared Position: PLIは入力と説明、CLI/APIは数値計算、Actionsは同じcodeの実行、MAGIは意味・前提・出典を監査する。
[FIX] Tools索引と呼出規約、make target、workflow_dispatchのJSON入口、artifactを追加。入力JSONをshellへ直接展開しない。
[SEMANTIC-STOP] 実行不能・非ゼロexitを成功結果にしない。source resolverの成功を実測や物理モデルの普遍妥当性へ変換しない。

## 検証

ローカルPythonで8 test method（23の入力拒否case、CLIの不正JSON3件を含む）を実行して成功。冷却境界の再構成、独立した200Wの伝導例、4枚/面積/温度の単位、非対応前提、非有限入力、決定的result hashを確認。

基準結果: 138℃境界で `241.6911032028471〜250.53526175049166 W`。面積64cm²。これは開放端・定数モデルの推定値で、実測ではない。

GitHub Actionsの結果は公開後のrunを別記録として参照する。専用daemon、汎用document server、物理装置の自動制御はこの変更の対象外。
