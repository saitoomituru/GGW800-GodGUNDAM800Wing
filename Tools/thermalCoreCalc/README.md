# thermalCoreCalc

状態: 定数モデルの実装。実機未校正。  
model_id: `tec-constant-properties-open-circuit/1`  
license: Apache-2.0（計算software）。hardware設計SourceのCERN-OHL-P-2.0とは別責務。

TEC1-12706が4枚見つかった時点の、熱的並列・理想接触・0℃無限冷熱源・開放端の計算を固定する。推定の出典は[HBデータシート](https://hebeiltd.com.cn/peltier.datasheet/TEC1-12706.pdf)、式の参照は[Ferrotecの熱電モデル](https://thermal.ferrotec.com/technology/thermoelectric-reference-guide/thermalRef11/)。

## 関数と式

`fit_cooling_spec(spec)`: QmaxはΔT=0、ΔTmaxはQc=0で、両方とも同じImaxでの値とする定数モデル。Rを固定して次をfitする。ThはKelvinへ変換する。

```text
Qc = α*Tc*I - I²*R/2 - K*ΔT
α  = (Qmax + Imax²*R/2) / (Th_K*Imax)
K  = Qmax/ΔTmax - α*Imax
Rθ = 1/K
```

`heat_input_at_temperature(...)`: 開放端I=0、N枚を熱的並列にする。熱入力Q、合成熱抵抗、総面積、熱流束を返す。

```text
K_total = N*K
Rθ_total = 1/(N*K)
Q = N*K*(Th-Tc)
A_total_cm² = N*width_mm*height_mm/100
heat_flux_W_cm² = Q/A_total_cm²
```

`calculate_scenario(scenario)`: 全入力・前提を検査し、各校正仕様と温度について計算する。入力を変更しないpure function。結果のmin/maxは2つの仕様点から得る値の幅で、統計的信頼区間ではない。

## 入力

基準入力は[scenario JSON](scenarios/tec1-12706-four-snow0.json)。変更する変数は、枚数、1枚の幅・高さ、冷面温度、高温側の評価温度・宣言上限、冷却仕様の校正点。単位はJSON keyに明記している。

- N=4、40×40mm、cold=0℃、評価点80/100/120/138℃、宣言上限138℃。
- 仮定: 熱的並列、開放端、冷熱源は等温・無限、接触熱抵抗0、均一熱流、迂回熱流0。
- calibrationはHBのTh=25℃と50℃の2点。手持ち素子の製造元・実測熱抵抗を確定したという意味ではない。
- 寸法は面積・熱流束の算出に使う。面積を変えてもKは自動相似拡大しない。別素子・形状には対応する校正情報が必要。
- 負荷接続、有限の雪、接触熱抵抗、熱直列、過渡、温度依存等を扱う入力は今の版で黙って近似せず拒否する。
- 未知field、重複JSON key、NaN/Infinity、負の面積、0枚、絶対零度以下、上限超えも拒否する。

0℃は融解中の雪という基準case。CLIで別cold値を指定すれば同じ等温境界の計算はできるが、雪の相変化・有限量を実装した意味にはならない。

## API / CLI

```python
import json
from pathlib import Path
from Tools.thermalCoreCalc import calculate_scenario

scenario = json.loads(Path(
    "Tools/thermalCoreCalc/scenarios/tec1-12706-four-snow0.json"
).read_text())
result = calculate_scenario(scenario)
```

```console
python3 -B -m Tools.thermalCoreCalc --input Tools/thermalCoreCalc/scenarios/tec1-12706-four-snow0.json
make thermal-calc
make test-thermal
```

CLIへ `--output path.json` を渡すと結果receiptを保存する。親directoryは呼出側が準備する。成功exit=0、入力・計算・出力エラーexit=2。失敗時に過去の出力fileを新しい結果として使わず、exit statusと入力hashを確認する。

receiptは全入力、出典、model_id、計算結果、Python版、実行時刻、取得できたGit revision、module source・input・resultのSHA-256、Actions run IDを持つ。pure resultとresult hashは同じ入力・codeで再利用でき、実行時刻はCLI envelopeに分離する。Git revisionだけで未commit差分を隠さず、source hashも照合する。

## GitHub Actions計算server

workflow: [thermal-core-calc.yml](../../.github/workflows/thermal-core-calc.yml)。

Actions画面の「thermalCoreCalc 計算」からRun workflow。scenario_jsonを空欄にすると基準入力、JSON全文を渡すと指定条件で計算する。code変更時はpush／PRでも回帰計算する。

GitHub CLIから:

```console
gh workflow run thermal-core-calc.yml --ref main
gh workflow run thermal-core-calc.yml --ref main -F scenario_json=@my-scenario.json
gh run list --workflow thermal-core-calc.yml
gh run download <RUN_ID> --dir calculation-receipt
```

任意のrefで計算するときは `--ref` を明示し、receiptのGit revisionと照合する。[GitHub公式CLI仕様](https://cli.github.com/manual/gh_workflow_run)に従う。workflowはJSONを環境変数経由で入力fileへ渡し、shell codeへ展開しない。生成される入力と結果のartifact保持期間は30日なので、採用した結果はrun URLと共に実験票へ保存する。

## PLIの呼出契約

「4枚、雪0℃、理想接触、開放端で計算して」のような要求では、Agentは基準scenarioを読み、変更点だけを明示して同じCLIまたはworkflowを実行する。結果を返すときはmodel_id、入力、commit／source hash、run URLまたは実行receiptを添える。実行できなければ未実行として手順を返し、計算成功を捏造しない。

これはrepository上のPLI routing規約であり、独立した常駐API・daemon・MAGIの自動裁定を実装したものではない。MAGIは目的・出典・仮定・物理との適合を監査し、数値計算はこのmoduleへ渡す。

## 実験で更新する

実測の校正データには素子ID・温度・熱流・電気条件・計測器・不確かさ・sourceを記録する。今回のbaselineとfit条件は消さず、新しいscenarioや新modelへ並行保存する。

fieldの意味・式・未対応条件を変えるときはmodel_idを更新し、旧結果を再解釈しない。反例・測定との差をtestへ追加して拘束を磨く。測定前に「安全熱入力」を返すmodelへ名称だけ変えない。

基準結果: 1枚Rθ≈2.20〜2.28K/W、4枚Rθ≈0.551〜0.571K/W、総面積64cm²。cold=0℃、hot=138℃では約241.691〜250.535W。138℃は材料境界への到達計算であり、連続使用推奨値・安全認定ではない。温度依存は固定して外挿している。
