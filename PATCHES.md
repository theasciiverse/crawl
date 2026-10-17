# Changes from upstream

This is the Asciiverse packaging of Dungeon Crawl Stone Soup (DCSS), the
open-source roguelike by Linley Henzell (Linley's Dungeon Crawl, 1997) and
the Stone Soup team since 2006, GPL-2.0-or-later (see LICENSE). Upstream is
[crawl/crawl](https://github.com/crawl/crawl), remote `upstream`; branch
`asciiverse` starts at its tag `0.34.1` (2026-03-15, the latest stable
release on 2026-10-17) and carries our commits on top.

Only the console (ncurses) game is built: no tiles, no webtiles. The source
is `crawl-ref/source`; Lua, SQLite and zlib are crawl's own bundled copies
(the `crawl-ref/source/contrib` submodules), built as static libraries by
its Makefile.

## Code

- Player files in the XDG data folder (`initfile.cc`). With no `CRAWL_DIR`
  set, crawl's own folder is `$XDG_DATA_HOME/crawl`, else
  `~/.local/share/crawl`, on Linux and macOS alike (upstream: `~/.crawl`
  in installed and AppImage builds, the current folder in a portable
  build, `~/Library/Application Support/Dungeon Crawl Stone Soup` on
  macOS). Saves, scores, the logfile, level and text caches
  (`saves/`), morgue files (`morgue/`), `init.txt` and `macro.txt` all go
  there; macros used to go to `~/.crawl`. An existing `~/.crawlrc` or
  `~/.crawl/init.txt` is still read when the data folder has no
  `init.txt`. `CRAWL_DIR`, `-dir` and `-rc` work as before.
- Read-only data beside the binary or in `../share/crawl` (`files.cc`).
  The build has no `DATA_DIR_PATH` (upstream's portable layout), so crawl
  looks for `dat/`, `docs/` and `settings/` next to its binary, as in an
  av install; the added `../share/crawl/` lets `/usr/bin/crawl` from the
  system packages find `/usr/share/crawl`.
- macOS: the binary's own path comes from `_NSGetExecutablePath` and
  `realpath` (`initfile.cc`). The Unix branch looked in `/proc/self/exe`,
  which macOS lacks, and then used `argv[0]`, which is a bare name or a
  symlink when crawl is started from `PATH` (av links `~/.local/bin/crawl`
  into its install folder), so the data beside it was not found.
- musl: no backtraces in crash reports on Linux without glibc (`crash.cc`),
  since musl has no `execinfo.h`.

## Packaging (new files)

- `asciiverse/build.sh`: static Linux build in Alpine (musl, ncursesw
  static), macOS builds per architecture with the system ncurses and
  upstream's `MAC_TARGET`; both leave `out/crawl` with the binary and
  `dat/`, `docs/` and `settings/` (upstream's `install-data`). The version
  string comes from `util/release_ver`, written by the script, because our
  tags are not upstream's and CI clones are shallow.
- `asciiverse/nfpm.yaml`: .deb, .rpm, .apk and Arch packages; the binary
  in `/usr/bin`, data in `/usr/share/crawl`, the man page, no menu entry.
- `asciiverse/record-preview.py` and `asciiverse/crawl.cast`: the catalog
  preview, a Minotaur Fighter on seed 7 exploring and fighting on D:1.
- `.github/workflows/release.yml`: builds all of it on a tag.

## Removed

- `.github/workflows/ci.yml`, upstream's CI: dozens of jobs on every push
  (lint, many Linux, macOS and Windows builds, release uploads), which do
  not belong in this repo. Its console builds were the model for ours:
  the Linux AppImage and macOS `mac-app-console` jobs use the same
  Makefile, with the bundled contribs on macOS.

## Not built

- Tiles and webtiles.
- Windows. Upstream ships a win32 console build: its CI cross-compiles it
  on Ubuntu with MinGW (`make CROSSHOST=i686-w64-mingw32
  package-windows-console`, bundled Lua, SQLite, zlib and PCRE, the
  Windows console through `libw32c.cc` instead of curses). A Windows
  target here would take that job for `x86_64-w64-mingw32`, packed as
  `crawl-x86_64-pc-windows-msvc.zip` or similar, and one more change: the
  XDG patch above is Unix only, so on Windows the player files would stay
  in `saves/` and `morgue/` under the folder crawl is started in, which
  av sets to the install folder that an update replaces; they would need
  to move to `%APPDATA%`.
