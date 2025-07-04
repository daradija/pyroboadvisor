#!/bin/bash
set -e

echo "Configurando entorno de trading con IB Gateway..."
echo "=================================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]  $1${NC}"
}

log_success() {
    echo -e "${GREEN}[OK] $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[WARN]  $1${NC}"
}

# Actualizar sistema
log_info "Actualizando sistema..."
sudo apt-get update

# Instalar dependencias del sistema
log_info "Instalando dependencias del sistema..."
sudo apt-get install -y \
    wget curl unzip \
    xvfb x11vnc xfonts-base \
    libxi-dev libxmu-dev \
    socat netcat-openbsd \
    python3-pip \
    jq \
    htop

# Crear estructura de directorios
log_info "Creando estructura de directorios..."
mkdir -p ~/trading/{ib-setup,scripts,logs,data,config}
mkdir -p ~/.vnc

# Instalar librerías de Python
log_info "Instalando librerías de Python..."
pip3 install --user \
    ib-insync \
    pandas \
    numpy \
    matplotlib \
    flask \
    requests \
    python3-dotenv \
    psutil

# Configurar VNC password
log_info "Configurando VNC..."
echo "ibtrading" | vncpasswd -f > ~/.vnc/passwd
chmod 600 ~/.vnc/passwd

log_success "Configuración base completada!"
echo
echo "Próximos pasos:"
echo "1. Descargar IB Gateway"
echo "2. Configurar display virtual"
echo "3. Probar conexión API"
