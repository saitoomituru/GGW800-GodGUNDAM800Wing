# GGW800のSphere-DOS入口

導入SurfaceはAtlantisの **Surface 2: .vendor submodule埋め込み**。固定Atlantis revisionは `4380940f91c49cdc14b9fcc45783528647ed17d7`。
明示Manifestは `assets/ZeroRoomLab-manifest`（`446470b27f6a7bf6d0cb498f87ac5658639ba7ad`）。[workspace](GGW800.code-workspace)はこの3repositoryだけを参照する。

```bash
make bootstrap
make sphere ARGS="interfaces --json"
make sphere ARGS="sphere-dos boot --json"
make sphere ARGS="sphere-dos status --json"
make audit
make verify
```

`bootstrap`は2つの直接submoduleをgitlinkのrevisionへ展開し、Atlantis既存bootstrapでvenvを作る。自動pullや `--remote` 更新、nested IBD/FQueryの再帰取得は行わない。

`sphere`はAtlantisのcwdから既存 `atlantis_cli` を呼ぶ。bootはAtlantis内の `.atlantis/` へsession receiptを生成する。GGW800の作業机はrootの `GGW800.code-workspace` を開く。Atlantis既定workspaceの欠損componentをGGW800の必須依存にしない。

`audit`は既存MAGI resolverの三Positionとcompositeを明示profile付きで実行する。これはsourceの存在・参照解決の検証であり、AIによる監査本文・機器検証・人格の自動起動ではない。参照sourceを読んだ監査者が判断・unknown・receiptを残す。

Python 3.11以上とGit、makeを使う。Windowsでmakeがない場合はWSLまたはdevcontainer、または[手動手順](docs/development.ja.md)を使う。
