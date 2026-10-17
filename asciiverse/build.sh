#!/bin/sh
# Builds the console (ncurses) Dungeon Crawl Stone Soup into out/crawl:
# the crawl binary with dat/, docs/ and settings/ beside it, the layout
# both an av install and the system packages use (the packages move the
# binary to /usr/bin and the rest to /usr/share/crawl, where it also looks).
#
# Linux: run inside alpine:3.22 for a fully static binary;
#   docker run --rm -v "$PWD":/src -w /src alpine:3.22 sh asciiverse/build.sh
# macOS: run on the runner with CC_ARCH set to x86_64 or arm64.
#
# Lua, SQLite and zlib are crawl's own copies in crawl-ref/source/contrib
# (git submodules), built as static libraries by its Makefile; ncursesw
# comes from Alpine (static) or macOS. Needs the submodules checked out:
#   git submodule update --init --depth 1 crawl-ref/source/contrib/lua \
#     crawl-ref/source/contrib/sqlite crawl-ref/source/contrib/zlib
set -eu
cd "$(dirname "$0")/.."
root=$PWD
version="${CRAWL_VERSION:-0.34.1}"

for c in lua sqlite zlib; do
  [ -f "crawl-ref/source/contrib/$c/Makefile" ] || [ -f "crawl-ref/source/contrib/$c/src/Makefile" ] || {
    echo "crawl-ref/source/contrib/$c is missing: check out the submodules first" >&2; exit 1; }
done

jobs=$(getconf _NPROCESSORS_ONLN 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 2)
set -- BUILD_LUA=y BUILD_SQLITE=y BUILD_ZLIB=y NO_TRY_LLD=y NO_TRY_GOLD=y
if [ -f /etc/alpine-release ]; then
  apk add --no-cache build-base perl python3 py3-yaml bison flex pkgconf \
    ncurses-dev ncurses-static >/dev/null
  # ncursesw through pkg-config, with what a static link needs
  set -- "$@" "PKGCONFIG=pkg-config --static" EXTERNAL_LDFLAGS=-static
  game=crawl
else
  # upstream's own macOS route: the system ncurses, contribs for the rest
  : "${CC_ARCH:?set CC_ARCH to x86_64 or arm64}"
  target="$CC_ARCH-apple-macos${MACOSX_DEPLOYMENT_TARGET:-11.0}"
  set -- "$@" MAC_TARGET="$target"
  game="crawl-$target"
fi

cd crawl-ref/source
# The version comes from util/release_ver, not git describe: our tags
# (v0.34.1-av.1) are not upstream's, and CI clones are shallow.
echo "$version" > util/release_ver
GIT_DIR=/nonexistent make -j"$jobs" "$@" >/dev/null
strip "$game" 2>/dev/null || strip -x "$game"

rm -rf "$root/out/crawl" && mkdir -p "$root/out/crawl"
# install-data copies dat/, docs/ and settings/ into DESTDIR; with prefix
# and DATADIR empty that is the folder itself, upstream's portable layout
GIT_DIR=/nonexistent make "$@" DESTDIR="$root/out/crawl/" prefix= DATADIR= SAVEDIR= \
  install-data >/dev/null
cp "$game" "$root/out/crawl/crawl"
echo "built out/crawl ($version)"
