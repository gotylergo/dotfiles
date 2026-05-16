#!/usr/bin/env bash
# chezmoi run_once_ script — clones antidote if it's not found in expected paths.
set -euo pipefail

ANTIDOTE_DIR="$HOME/.antidote"

if [[ -d "$ANTIDOTE_DIR" ]]; then
    exit 0
fi

# Also check other common paths from dot_zshrc.tmpl
if [[ -f "/home/linuxbrew/.linuxbrew/opt/antidote/share/antidote/antidote.zsh" ]] || \
   [[ -f "$HOME/.local/share/antidote/antidote.zsh" ]]; then
    exit 0
fi

echo "Installing antidote..."
git clone --depth=1 https://github.com/mattmc3/antidote.git "$ANTIDOTE_DIR"
