#!/usr/bin/env bash
# setup_pyrobo_macos.sh — instala PyRoboAdvisor en macOS usando createVenv
set -euo pipefail

# 1) Homebrew
if ! command -v brew >/dev/null 2>&1; then
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi
# Cargar entorno de brew
if [ -x /opt/homebrew/bin/brew ]; then eval "$(/opt/homebrew/bin/brew shellenv)"; fi
if [ -x /usr/local/bin/brew ]; then eval "$(/usr/local/bin/brew shellenv)"; fi

# 2) Python 3.11 + git
brew update
brew install python@3.11 git

# 3) Código
cd "$HOME"
if [ -d pyroboadvisor/.git ]; then
  git -C pyroboadvisor pull --ff-only || git -C pyroboadvisor pull --rebase
else
  git clone https://github.com/daradija/pyroboadvisor.git
fi
cd "$HOME/pyroboadvisor"

# 4) Entorno virtual con createVenv (script ZSH)
if [ -x ./createVenv ]; then
  # Le mandamos un Enter para que no se quede esperando en el read final
  printf '\n' | zsh ./createVenv
else
  # Fallback si algún día no existe createVenv
  proj="${PWD##*/}"
  venv_dir="$HOME/venvs/$proj"
  python3.11 -m venv "$venv_dir"
fi

# 5) Requisitos del driver usando el mismo venv que createVenv
proj="${PWD##*/}"
venv_dir="$HOME/venvs/$proj"
venv_python="$venv_dir/bin/python"

cd driver
"$venv_python" -m pip install -U pip
"$venv_python" -m pip install -r requirements.txt
cd ..

echo
echo "✔ Instalación completa."s
echo "✔ Entorno creado en: $venv_dir"
echo
echo "Para ejecutar la simulación, en una terminal nueva:"
echo "source "$HOME/venvs/pyroboadvisor/bin/activate" && cd "$HOME/pyroboadvisor" && python ./sample_b.py"