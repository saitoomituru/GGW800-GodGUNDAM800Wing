# Tools — 実験で拘束を磨く計算道具

人間・PLI・CLI・GitHub Actionsが同じ関数を使うtool棚。モデル・入力・出典・結果・実測の対応を残し、数式や数値を毎回生成し直さない。

| Tool | Python API | CLI / Actions | 依存・副作用 | license |
| --- | --- | --- | --- | --- |
| [thermalCoreCalc](thermalCoreCalc/README.md) | fit_cooling_spec / heat_input_at_temperature / calculate_scenario | `python -m Tools.thermalCoreCalc` / thermal-core-calc.yml | Python 3.11+標準library。CLIは入力readと指定出力write、Git revision read。network・機器操作なし | Apache-2.0 |

実験で校正データ・適用条件・反証を積み重ねる。新しいtoolを追加するときは既存ToolsとAtlantisのtoolを確認し、再利用／拡張／adapter／新規作成の理由、入力・出力・権限・版・検証をこの索引へ追加する。

LLMの説明は入力作成・操作案内・結果の解釈を担当し、数値は成功したCLI／Actions receiptへ接続する。MAGIのsource解決成功と物理モデルの妥当性・実機性能を混同しない。
