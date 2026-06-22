#!/usr/bin/env bash
# Apply exported registry.yaml to the secretary config directory.
# Usage: sh apply_config.sh [path/to/registry.yaml]
#
# If no path given, looks for registry.yaml in ~/Downloads first,
# then falls back to the current directory.

set -euo pipefail

TARGET_DIR="$HOME/.agent_worlds/secretary"
TARGET="$TARGET_DIR/registry.yaml"

# Resolve source file
if [ $# -ge 1 ]; then
  SRC="$1"
elif [ -f "$HOME/Downloads/registry.yaml" ]; then
  SRC="$HOME/Downloads/registry.yaml"
elif [ -f "./registry.yaml" ]; then
  SRC="./registry.yaml"
else
  echo "❌  No registry.yaml found."
  echo "    Export one from the dashboard, then run:"
  echo "    sh apply_config.sh ~/Downloads/registry.yaml"
  exit 1
fi

# Ensure target directory exists
mkdir -p "$TARGET_DIR"

# Backup existing config
if [ -f "$TARGET" ]; then
  BACKUP="${TARGET}.bak"
  cp "$TARGET" "$BACKUP"
  echo "📦  Backed up existing config → $BACKUP"
fi

# Apply
cp "$SRC" "$TARGET"
echo "✅  Config applied → $TARGET"
echo ""
echo "    Run the secretary to pick up the new config:"
echo "    Ask Claude: \"Run the daily digest for today.\""
