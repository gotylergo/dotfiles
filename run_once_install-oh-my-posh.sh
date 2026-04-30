#!/usr/bin/env bash
# chezmoi run_once_ script — runs exactly once per content hash.
# Installs oh-my-posh into ~/.local/bin if it isn't already on PATH.
set -euo pipefail

if command -v oh-my-posh >/dev/null 2>&1; then
	exit 0
fi

mkdir -p "$HOME/.local/bin"
curl -s https://ohmyposh.dev/install.sh | bash -s -- -d "$HOME/.local/bin"
