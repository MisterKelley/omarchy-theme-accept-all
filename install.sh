#!/usr/bin/env bash
# Symlink this repo into Omarchy's user themes dir.
set -euo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="$HOME/.config/omarchy/themes/accept-all"
mkdir -p "$HOME/.config/omarchy/themes"
if [[ -e $DEST && ! -L $DEST ]]; then
  echo "!! $DEST exists and is not a symlink — move it aside first." >&2
  exit 1
fi
ln -nsf "$SRC" "$DEST"
echo "Linked $DEST -> $SRC"
echo "Apply with: omarchy theme set accept-all"
