#!/usr/bin/env bash
# chezmoi run_once_ script — bootstraps vim-plug and runs PlugInstall once,
# so dot_vimrc works immediately on a fresh machine.
set -euo pipefail

PLUG_PATH="$HOME/.vim/autoload/plug.vim"

if [[ -f "$PLUG_PATH" ]]; then
	exit 0
fi

curl -fLo "$PLUG_PATH" --create-dirs \
	https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim

if command -v vim >/dev/null 2>&1; then
	vim +PlugInstall +qall >/dev/null 2>&1 || true
fi
