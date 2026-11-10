#!/bin/bash
# One-time setup. Safe to run again. It changes three things, all on your own machine:
#   1. links bin/factory into ~/.local/bin so you can type `factory` anywhere
#   2. adds ~/.local/bin to PATH in ~/.zshrc if it is not there yet
#   3. turns on the Factory's git pre-commit hook (runs the tests before any commit to the Factory)
# Then it runs `factory doctor`.
set -eu
FACTORY="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$HOME/.local/bin"
ln -sf "$FACTORY/bin/factory" "$HOME/.local/bin/factory"
echo "linked: ~/.local/bin/factory -> $FACTORY/bin/factory"
RC="$HOME/.zshrc"; [ -n "${BASH_VERSION:-}" ] && [ "$(basename "${SHELL:-}")" = "bash" ] && RC="$HOME/.bashrc"
case ":$PATH:" in *":$HOME/.local/bin:"*) ;; *)
  if ! grep -qs 'HOME/.local/bin' "$RC"; then
    printf '\n# Factory launcher\nexport PATH="$HOME/.local/bin:$PATH"\n' >> "$RC"; echo "added ~/.local/bin to PATH in $RC (open a new terminal, or: source $RC)"
  fi;;
esac
git -C "$FACTORY" config core.hooksPath hooks && echo "pre-commit hook: on"
"$FACTORY/bin/factory" doctor
