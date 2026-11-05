# Manifest asset

`ZeroRoomLab-manifest` はGit submodule。固定revisionは `446470b27f6a7bf6d0cb498f87ac5658639ba7ad`。GGW800の明示Manifestとして読む。

入口は `ZeroRoomLab-manifest/AGENTS.md`、`docs/projects/2026-11-05-winter-survival-cogeneration.ja.md`、`docs/operations/issue-contribution-guidelines.ja.md`、`FUNDING.md`。意味・文書規約・来歴・支援方針のassetであり、物理装置のruntime依存ではない。

MAGIは `--profile zeroroomlab` と `--repo-root ZeroRoomLab-manifest=<このsubmoduleの絶対path>` を明示する。Flavor／Role assetは配置だけでauto-mountしない。必要なsourceはresolverの出力を読み、黙って別repositoryを探索しない。
