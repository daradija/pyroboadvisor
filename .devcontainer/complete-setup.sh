#!/bin/bash
set -e

echo "🚀 Configuración COMPLETA de IB Trading en Codespaces"
echo "====================================================="

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]  $1${NC}"; }
log_success() { echo -e "${GREEN}[OK] $1${NC}"; }
log_warning() { echo -e "${YELLOW}[WARN]  $1${NC}"; }

# 1. INSTALACIÓN COMPLETA DEL SISTEMA
log_info "Actualizando sistema y dependencias..."
sudo apt-get update
sudo apt-get install -y \
    wget curl unzip \
    xvfb x11vnc xfonts-base \
    libxi-dev libxmu-dev \
    socat netcat-openbsd \
    python3-pip jq htop tree

# 2. CREAR ESTRUCTURA COMPLETA
log_info "Creando estructura de directorios..."
mkdir -p ~/trading/{ib-setup,scripts,logs,data,config,strategies,utils,notebooks}
mkdir -p ~/.vnc

# 3. INSTALAR LIBRERÍAS PYTHON BÁSICAS
log_info "Instalando librerías Python básicas..."
pip3 install --user \
    ib-insync pandas numpy matplotlib \
    flask requests python-dotenv psutil \
    yfinance jupyter notebook \
    scipy scikit-learn plotly dash

# 4. INSTALAR REQUIREMENTS DEL PROYECTO
log_info "Instalando requirements específicos del proyecto..."

# Determinar directorio del workspace
WORKSPACE_DIR="/workspaces/pyroboadvisor"
if [ ! -d "$WORKSPACE_DIR" ]; then
    WORKSPACE_DIR="/workspace"
fi
if [ ! -d "$WORKSPACE_DIR" ]; then
    WORKSPACE_DIR="$(pwd)"
fi

# Instalar requirements de la raíz del proyecto
if [ -f "$WORKSPACE_DIR/requirements.txt" ]; then
    log_info "Instalando requirements del proyecto principal..."
    pip3 install --user -r "$WORKSPACE_DIR/requirements.txt"
    log_success "Requirements del proyecto instalados"
else
    log_warning "No se encontró requirements.txt en la raíz: $WORKSPACE_DIR"
fi

# Instalar requirements del driver
if [ -f "$WORKSPACE_DIR/driver/requirements.txt" ]; then
    log_info "Instalando requirements del driver..."
    pip3 install --user -r "$WORKSPACE_DIR/driver/requirements.txt"
    log_success "Requirements del driver instalados"
else
    log_warning "No se encontró requirements.txt en driver/"
fi

# Verificar instalaciones críticas
log_info "Verificando instalaciones críticas..."
python3 -c "
try:
    import yfinance
    print('✅ yfinance instalado')
except ImportError:
    print('❌ yfinance NO instalado')

try:
    import ib_insync
    print('✅ ib_insync instalado')
except ImportError:
    print('❌ ib_insync NO instalado')

try:
    import pandas, numpy, matplotlib
    print('✅ pandas, numpy, matplotlib instalados')
except ImportError:
    print('❌ Algunas librerías básicas NO instaladas')
"

# 5. CONFIGURAR VNC
log_info "Configurando VNC..."
echo "ibtrading" | vncpasswd -f > ~/.vnc/passwd
chmod 600 ~/.vnc/passwd

# 6. DESCARGAR E INSTALAR IB GATEWAY AUTOMÁTICAMENTE
log_info "Descargando e instalando IB Gateway..."
cd ~/trading/ib-setup
if [ ! -f "ibgateway-installer.sh" ]; then
    wget -q https://download2.interactivebrokers.com/installers/ibgateway/stable-standalone/ibgateway-stable-standalone-linux-x64.sh \
        -O ibgateway-installer.sh
    chmod +x ibgateway-installer.sh
fi

if [ ! -d "$HOME/Jts" ]; then
    echo -e "\n\ny\n$HOME/Jts\nn\n" | ./ibgateway-installer.sh -c
    log_success "IB Gateway instalado"
fi

# 7. CREAR TODOS LOS SCRIPTS AUTOMÁTICAMENTE
log_info "Creando scripts de automatización..."

# Script para iniciar display
cat > ~/trading/scripts/start-display.sh << 'EOF'
#!/bin/bash
export DISPLAY=:1
if ! pgrep -x "Xvfb" > /dev/null; then
    Xvfb :1 -screen 0 1440x900x24 -ac -nolisten tcp -dpi 96 &
    sleep 2
fi
if ! pgrep -x "x11vnc" > /dev/null; then
    x11vnc -display :1 -bg -forever -nopw -quiet -listen localhost -xkb
fi
echo "[OK] Display virtual listo - VNC: http://localhost:6080"
EOF

# Script para iniciar IB Gateway
cat > ~/trading/scripts/start-ib-gateway.sh << 'EOF'
#!/bin/bash
export DISPLAY=:1
IB_PATH=$(find ~/Jts -name "ibgateway" -type f | head -1)
mkdir -p ~/trading/logs
cd $(dirname "$IB_PATH")
nohup ./ibgateway > ~/trading/logs/ibgateway.log 2>&1 &
echo "[OK] IB Gateway iniciado - PID: $!"
echo "VNC: http://localhost:6080"
echo "API: localhost:4002 (Paper Trading)"
EOF

# Script completo de inicio
cat > ~/trading/scripts/start-all.sh << 'EOF'
#!/bin/bash
echo "🚀 Iniciando sistema completo de trading..."
~/trading/scripts/start-display.sh
sleep 3
~/trading/scripts/start-ib-gateway.sh
echo "✅ Sistema listo!"
echo "1. Accede a: http://localhost:6080"
echo "2. Haz login en IB Gateway (Paper Trading)"
echo "3. Configura API en Settings"
EOF

# Script de verificación del sistema
cat > ~/trading/scripts/check-system.sh << 'EOF'
#!/bin/bash
echo "🔍 Verificación del Sistema de Trading"
echo "======================================"

echo "📋 Procesos activos:"
ps aux | grep -E "(ibgateway|Xvfb|x11vnc)" | grep -v grep

echo -e "\n🌐 Puertos abiertos:"
netstat -tlnp | grep -E "(400[12]|5901|6080)" || echo "No hay puertos de trading activos"

echo -e "\n📚 Librerías Python:"
python3 -c "
libs = ['yfinance', 'ib_insync', 'pandas', 'numpy', 'matplotlib']
for lib in libs:
    try:
        __import__(lib)
        print(f'✅ {lib}')
    except ImportError:
        print(f'❌ {lib}')
"

echo -e "\n📁 Estructura de directorios:"
ls -la ~/trading/ 2>/dev/null || echo "Directorio trading no encontrado"
EOF

# Hacer scripts ejecutables
chmod +x ~/trading/scripts/*.sh

# 8. CREAR CONFIGURACIONES EJEMPLO
cat > ~/trading/config/trading_config.yaml << 'EOF'
ib_gateway:
  api:
    host: "127.0.0.1"
    port: 4002
    client_id: 1
    timeout: 10
  settings:
    read_only: false
    trusted_ips: ["127.0.0.1"]
    
trading:
  mode: "paper"
  capital: 100000
  max_positions: 10
  
pyroboadvisor:
  estrategia: "S&P500"
  apalancamiento: 1.67
  margen_compra: 0.005
  margen_venta: 0.005
EOF

# 9. CREAR README DE COMANDOS ÚTILES
cat > ~/trading/COMANDOS.md << 'EOF'
# 🚀 Comandos Útiles para Trading en Codespaces

## 🎯 Comandos Principales
```bash
start-trading      # Inicia todo el sistema
start-display      # Solo display virtual
start-ib          # Solo IB Gateway
```

## 🔍 Diagnóstico
```bash
ib-logs           # Ver logs de IB Gateway
show-ports        # Mostrar puertos activos
~/trading/scripts/check-system.sh  # Verificación completa
```

## 📁 Navegación
```bash
trading-dir       # Ir a directorio trading
cd /workspaces/pyroboadvisor  # Ir al proyecto
```

## 🌐 Accesos Web
- **VNC Desktop**: http://localhost:6080
- **IB Gateway API**: localhost:4002

## 🔧 Troubleshooting
```bash
# Reiniciar IB Gateway
pkill -f ibgateway
start-ib

# Ver logs detallados
tail -f ~/trading/logs/ibgateway.log

# Verificar conexión API
python3 -c "
from ib_insync import IB
ib = IB()
try:
    ib.connect('127.0.0.1', 4002, clientId=1)
    print('✅ API conectada')
    ib.disconnect()
except:
    print('❌ API no disponible')
"
```
EOF

# 10. CREAR ALIASES ÚTILES
cat >> ~/.bashrc << 'EOF'

# 🚀 IB Trading Aliases
alias start-trading='~/trading/scripts/start-all.sh'
alias start-display='~/trading/scripts/start-display.sh'
alias start-ib='~/trading/scripts/start-ib-gateway.sh'
alias ib-logs='tail -f ~/trading/logs/ibgateway.log'
alias trading-dir='cd ~/trading'
alias show-ports='netstat -tlnp | grep -E "(400[12]|5901|6080)"'
alias check-system='~/trading/scripts/check-system.sh'

# 📁 Navegación rápida
alias proyecto='cd /workspaces/pyroboadvisor'
alias driver='cd /workspaces/pyroboadvisor/driver'
alias market='cd /workspaces/pyroboadvisor/market'

# 🐍 Python shortcuts
alias python='python3'
alias pip='pip3'

EOF

# 11. MENSAJE FINAL
log_success "✅ CONFIGURACIÓN COMPLETA TERMINADA!"
echo ""
echo "🎯 COMANDOS DISPONIBLES:"
echo "  start-trading      - Inicia todo el sistema"
echo "  start-display      - Solo display virtual"
echo "  start-ib          - Solo IB Gateway"
echo "  ib-logs           - Ver logs de IB Gateway"
echo "  show-ports        - Mostrar puertos activos"
echo "  check-system      - Verificación completa"
echo ""
echo "🌐 ACCESOS:"
echo "  VNC Web: http://localhost:6080"
echo "  API: localhost:4002"
echo ""
echo "📚 PRÓXIMOS PASOS:"
echo "1. Ejecuta: start-trading"
echo "2. Ve a: http://localhost:6080"
echo "3. Login en IB Gateway con Paper Trading"
echo "4. Configura API en Settings → API"
echo "5. Ejecuta: python3 sample.py"
echo ""
echo "📖 Documentación: ~/trading/COMANDOS.md"
echo ""
log_info "Reinicia el terminal para activar los aliases: source ~/.bashrc"
