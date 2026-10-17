# Dungeon Crawl Stone Soup (Asciiverse packaging)

DCSS, the open-source roguelike (Linley Henzell 1997, Stone Soup team since
2006, GPL-2.0-or-later), console edition, packaged for the Asciiverse
catalog and as system packages. Not our code: keep changes small and list
every one in PATCHES.md.

- Remotes: `upstream` is github.com/crawl/crawl, `origin` is
  github.com/theasciiverse/crawl.
- Branch `asciiverse` = upstream tag `0.34.1` plus our commits.
- Release: tag `v0.34.1-av.<n>` and push it. For a new upstream version,
  rebase onto its tag and change the default `CRAWL_VERSION` in
  `asciiverse/build.sh` (CI takes it from the tag).
- Source is `crawl-ref/source`. Lua, SQLite and zlib are submodules:
  `git submodule update --init --depth 1 crawl-ref/source/contrib/lua
  crawl-ref/source/contrib/sqlite crawl-ref/source/contrib/zlib`.
- Local static build: `docker run --rm -v "$PWD":/src -w /src alpine:3.22
  sh asciiverse/build.sh`, then chown the tree back; output in `out/crawl`.
- Player files: `$XDG_DATA_HOME/crawl` (default `~/.local/share/crawl`);
  data beside the binary, or `/usr/share/crawl` from the packages.
- Preview: `python3 asciiverse/record-preview.py` after a build.
