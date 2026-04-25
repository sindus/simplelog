#!/usr/bin/env bash
# Usage: ./build/update_tap.sh <version>   e.g.  ./build/update_tap.sh 1.1.0
set -euo pipefail

VERSION=${1:?Usage: $0 <version>  e.g. $0 1.1.0}
OWNER="simplelogdev"
REPO="simplelog"
TAP_REPO="homebrew-simplelog"
URL="https://github.com/${OWNER}/${REPO}/archive/refs/tags/v${VERSION}.tar.gz"

echo "→ Computing sha256 for v${VERSION}..."
SHA256=$(curl -sL "$URL" | shasum -a 256 | awk '{print $1}')
echo "  sha256: ${SHA256}"

TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

echo "→ Cloning tap..."
git clone --quiet "https://github.com/${OWNER}/${TAP_REPO}.git" "$TMPDIR"

FORMULA="$TMPDIR/Formula/simplelog.rb"
perl -i -pe "s|url \".*\"|url \"${URL}\"|" "$FORMULA"
perl -i -pe "s|sha256 \".*\"|sha256 \"${SHA256}\"|" "$FORMULA"

git -C "$TMPDIR" add Formula/simplelog.rb
GIT_AUTHOR_NAME="Sikander Ravate" \
GIT_AUTHOR_EMAIL="sikander.ravate@gmail.com" \
GIT_COMMITTER_NAME="Sikander Ravate" \
GIT_COMMITTER_EMAIL="sikander.ravate@gmail.com" \
git -C "$TMPDIR" commit -m "Update simplelog formula to v${VERSION}"
git -C "$TMPDIR" push origin main

echo "✓ Tap updated to v${VERSION}"
