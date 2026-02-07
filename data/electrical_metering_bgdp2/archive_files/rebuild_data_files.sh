#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"

BASE_DIR="$(cd "$HERE/.." && pwd)"

OUT_DIR="$BASE_DIR/data_files"
ARCH="$HERE/data_files.tar.zst"

echo "Checking required files"
ls -1 data_files.tar.zst.part-* >/dev/null
test -f SHA256SUMS

echo "Verifying parts (sha256)"
sha256sum -c SHA256SUMS

echo "Reassembling archive"
cat data_files.tar.zst.part-* > "$ARCH"

echo "Preparing output directory: $OUT_DIR"
mkdir -p "$OUT_DIR"

case "$OUT_DIR" in
  "$BASE_DIR"/*) ;;
  *) echo "Refusing to write outside base dir: $BASE_DIR" >&2; exit 1 ;;
esac

echo "Extracting dataset into: $OUT_DIR"
TMP_LIST="$(mktemp)"
zstd -d -c "$ARCH" | tar -tf - > "$TMP_LIST"

if head -n 1 "$TMP_LIST" | grep -q '^data_files/'; then
  echo "Detected top-level 'data_files/' in archive; extracting into base dir: $BASE_DIR"
  zstd -d -c "$ARCH" | tar -C "$BASE_DIR" -xf -
else
  zstd -d -c "$ARCH" | tar -C "$OUT_DIR" -xf -
fi

rm -f "$TMP_LIST"

echo "Cleaning up temporary archive"
rm -f "$ARCH"

echo "Done!"
echo "Dataset is available at: $OUT_DIR"
echo "Archive parts were kept in: $HERE"
