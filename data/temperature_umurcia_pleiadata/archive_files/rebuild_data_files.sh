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

echo "Creating output dir: $OUT_DIR"
mkdir -p "$OUT_DIR"

rm -rf "$OUT_DIR/processed_data" "$OUT_DIR/raw_data"

echo "Extracting into: $OUT_DIR"
zstd -d -c "$ARCH" | tar -C "$OUT_DIR" -xf -

echo "Cleaning up temporary archive"
rm -f "$ARCH"

echo "Validating output structure"
test -d "$OUT_DIR/processed_data"
test -d "$OUT_DIR/raw_data"

EXTRA="$(find "$OUT_DIR" -mindepth 1 -maxdepth 1 -type d \
  ! -name processed_data ! -name raw_data | wc -l)"
if [[ "$EXTRA" -ne 0 ]]; then
  echo "ERROR: Unexpected extra directory/directories found in $OUT_DIR" >&2
  find "$OUT_DIR" -mindepth 1 -maxdepth 1 -type d >&2
  exit 1
fi

echo "Done! Rebuilt dataset at: $OUT_DIR"
