# GGW800 — GodGUNDAM800Wing

**イーロン式ボイジャーカムイ発電 / Elon-style Voyager–Kamui Cogeneration**

灯油の熱と山形の雪で、越冬の生活電力を取り出す。X800・八百万（Yaoyorozu）シリーズの実験的コジェネシステム。

電源不要の芯式ストーブを高温源、雪のヒートジャケットを低温源にして、ゼーベック発電からスニーカーグリッドへ補給する。プロダクト名、カムイ、Voyager核電池、宇宙世紀Grok甲冑の放熱翼という着想の来歴を、[設計文書](docs/design.ja.md)に残す。

**どの神に取り付けられるかは動作保証外。Δ取れるならOKハゲ。**

## 設計と公開物

豪雪地帯のローカル設計。ロシア・アラスカ等は現地適応の候補であり、世界普遍性は主張しない。

| 棚 | 公開するもの | 状態 |
| --- | --- | --- |
| [設計](docs/design.ja.md) | 熱・電力系統、現場条件、実験案、資源条件 | 文書化済み、実機出力未測定 |
| [CAD](hardware/cad/README.md) | 編集可能なCAD原本、STEP等、寸法・材質・取付情報 | 公開形式を整備、実図面は未作成 |
| [電子回路](hardware/electronics/README.md) | 回路情報、SPICE netlist、モデル出典・条件 | 公開形式を整備、実回路は未作成 |
| [部材](hardware/bom/README.md) | BOM、入手・加工・代替条件 | 部材台帳の項目を定義、現物未棚卸し |
| [実験](experiments/README.md) | 実測・シミュレーション・失敗条件・ログ | 記録形式を整備、測定未実施 |

公開契約は[CAD / SPICE公開仕様](docs/publication.ja.md)。計算例を設計確定値や実測にしない。スターリング系も並行候補として残す。

## 開発足場

Sphere-DOSは[SphereOS Atlantis](https://github.com/saitoomituru/SphereOS-Atlantis)を `.vendor/SphereOS-Atlantis` へ、Manifestは `assets/ZeroRoomLab-manifest` へGit submoduleとして固定する。実装をコピーせず、既存CLI・venv bootstrap・MAGI resolverを利用する。

```bash
git clone --recurse-submodules https://github.com/saitoomituru/GGW800-GodGUNDAM800Wing.git
cd GGW800-GodGUNDAM800Wing
make bootstrap
make verify
```

`GGW800.code-workspace`を開く。[導入とコマンド](SPHERE-DOS.md) / [開発・更新規約](docs/development.ja.md) / [固定revision](dependencies.lock.json)。

## 再利用する計算Tools

[thermalCoreCalc](Tools/thermalCoreCalc/README.md)に、4枚・理想接触・雪0℃・開放端の熱入力境界計算を固定。Python API、CLI、[GitHub Actions計算](.github/workflows/thermal-core-calc.yml)から同じmoduleを使い、入力・モデル版・出典・結果hashをreceiptに残す。実験で校正・適用範囲・testを更新する。

```console
make thermal-calc
make test-thermal
```

## イシューと資源

[CAD #1](https://github.com/saitoomituru/GGW800-GodGUNDAM800Wing/issues/1)、[回路・SPICE #2](https://github.com/saitoomituru/GGW800-GodGUNDAM800Wing/issues/2)、[統合実験・資源 #3](https://github.com/saitoomituru/GGW800-GodGUNDAM800Wing/issues/3)。[Manifestとの責務分担](docs/issue-map.ja.md)も参照。

生活・保温区画を寝室3畳へ集約する計画、約2.4kWの灯油熱源、約980Whの生活用LiFePO₄、研究設備全面停止という背景は、[Manifestの越冬運用 #71](https://github.com/saitoomituru/ZeroRoomLab-manifest/issues/71)に保持する。

素子、熱交換・断熱部材、充電・輸送、加工機利用、計測、燃料・維持費の協力を求める。追加自弁・研究設備の自動再開を前提にしない。

## ライセンス

ハードウェア設計・CAD・回路・SPICE設計Sourceは **CERN-OHL-P-2.0**。開発補助コードはApache-2.0、一般文書はCC-BY-4.0、上流submodule・第三者モデルは各出典の条件を保持する。[適用範囲と無保証](LICENSE-POLICY.md) / [来歴](NOTICE.md)。
