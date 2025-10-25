#!/usr/bin/env bash
# setup_pyrobo_macos.sh — instalación estilo tutorial macOS
set -euo pipefail

# 1) Homebrew (si falta) — tutorial mac: instala brew con este script
# https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh
if ! command -v brew >/dev/null 2>&1; then
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi
# carga entorno brew (Apple Silicon / Intel)
if [ -x /opt/homebrew/bin/brew ]; then eval "$(/opt/homebrew/bin/brew shellenv)"; fi
if [ -x /usr/local/bin/brew ]; then eval "$(/usr/local/bin/brew shellenv)"; fi

# 2) Python 3.11 — según tutorial mac
brew update
brew install python@3.11

# 3) Código: clonar o actualizar repo — igual flujo que en el tutorial
cd "$HOME"
if [ -d pyroboadvisor/.git ]; then
  git -C pyroboadvisor pull --ff-only || git -C pyroboadvisor pull --rebase
else
  git clone https://github.com/daradija/pyroboadvisor.git
fi
cd "$HOME/pyroboadvisor"

# 4) Entorno virtual — el tutorial manda: `source createVenv`
if [ -f ./createVenv ]; then
  . ./createVenv
else
  # respaldo si createVenv no estuviera
  python3.11 -m venv venv
  . venv/bin/activate
fi
# 5) Requisitos del driver — `cd driver; pip install -r requirements.txt; cd ..`
cd driver
python -m pip install -U pip
python -m pip install -r requirements.txt
cd ..

echo
echo "✔ Instalación completa."
echo "Para ejecutar la simulación (como en el tutorial mac):"
echo "source \"$HOME/pyroboadvisor/venv/bin/activate\" && python ./sample_b"
