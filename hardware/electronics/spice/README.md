# SPICE回路情報

SPDX-License-Identifier: CERN-OHL-P-2.0  
Copyright (C) 2026 ふさもふ / 齋藤みつる / ZeroRoomLab

[公開仕様](../../../docs/publication.ja.md)に従い、netlist、model / subcircuit、実行条件・方言・版を公開する。ngspice互換テキストを第一候補とし、他simulatorの固有機能は明記する。

モデル導入時は、定数ごとに測定／メーカー資料／仮定、単位、温度・電流範囲、sourceとlicenseを記録する。起動・負荷掃引・DC/DCの損失や補機消費を検討し、結果はsimulationとして実測と区別する。

現在、製品のnetlist・採用model・実行済み波形はない。適当な電圧や抵抗を置いたトイ回路を製品設計として公開しない。
