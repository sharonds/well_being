#!/usr/bin/env bash
set -euo pipefail

# Placeholder script to install Garmin Connect IQ SDK.
# You must accept Garmin's license manually and supply the download URL.
# Usage: ./scripts/setup_connectiq_sdk.sh <download_url> <sdk_version>

URL=${1:-}
VER=${2:-7.2.0}
DEST="$HOME/connectiq-sdk"

if [[ -z "$URL" ]]; then
  echo "ERROR: Provide SDK download URL (manual due to license)." >&2
  exit 1
fi

mkdir -p "$DEST"
cd "$DEST"

if [[ -d "$DEST/bin" ]]; then
  echo "SDK already present at $DEST" >&2
  exit 0
fi

echo "Downloading SDK $VER from $URL ..." >&2
curl -L "$URL" -o sdk.zip
unzip -q sdk.zip
rm sdk.zip

echo "SDK installed at $DEST"
