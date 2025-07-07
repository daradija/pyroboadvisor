# 🚀 PyRoboAdvisor + IB Gateway en GitHub Codespaces

<div align="center">

![PyRoboAdvisor](https://img.shields.io/badge/PyRoboAdvisor-Trading%20Bot-blue?style=for-the-badge&logo=python)
![Interactive Brokers](https://img.shields.io/badge/Interactive%20Brokers-API%20Ready-green?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDJMMTMuMDkgOC4yNkwyMCA5TDEzLjA5IDE1Ljc0TDEyIDIyTDEwLjkxIDE1Ljc0TDQgOUwxMC45MSA4LjI2TDEyIDJaIiBmaWxsPSJ3aGl0ZSIvPgo8L3N2Zz4K)
![Codespaces Ready](https://img.shields.io/badge/Codespaces-Ready%20to%20Deploy-orange?style=for-the-badge&logo=github)
![Paper Trading](https://img.shields.io/badge/Paper%20Trading-Safe%20Testing-yellow?style=for-the-badge&logo=shield-check)

**🎯 Trading algorítmico automatizado en la nube con un solo clic**

*Ejecuta estrategias de PyRoboAdvisor con Interactive Brokers directamente desde tu navegador*

[🚀 **Crear Codespace**](#-quick-start---crear-tu-entorno-en-3-pasos) • [📚 **Documentación**](#-comandos-disponibles) • [🔧 **Troubleshooting**](#-troubleshooting)

</div>

---

## 🌟 **¿Qué es esto?**

**La primera implementación completa** de PyRoboAdvisor + IB Gateway funcionando en **GitHub Codespaces**. 

🎉 **Sin instalaciones locales** • 🔒 **Entorno seguro** • ⚡ **Setup automático** • 🌐 **Acceso desde navegador**

### ✨ **Características Principales**

| 🎯 **Funcionalidad** | 📋 **Descripción** | 🔗 **Acceso** |
|---------------------|-------------------|---------------|
| 🤖 **PyRoboAdvisor** | Estrategias algorítmicas S&P 500 | API integrada |
| 📊 **IB Gateway** | Conexión Interactive Brokers | Puerto 4002 |
| 🖥️ **VNC Desktop** | Acceso gráfico remoto | http://localhost:6080 |
| 📈 **Paper Trading** | Trading seguro sin riesgo | Modo simulación |
| 🛠️ **Auto-Setup** | Instalación completamente automática | Un solo clic |

---

## 🚀 **Quick Start - Crear tu Entorno en 3 Pasos**

### **Paso 1: Crear Codespace** 🎯

1. **Haz clic en el botón verde `Code`** en este repositorio
2. **Selecciona la pestaña `Codespaces`**
3. **Clic en `Create codespace on codespaces2`**

```
GitHub.com → Tu Repo → Code → Codespaces → Create codespace
```

### **Paso 2: Esperar la Configuración Automática** ⏳

El sistema instalará automáticamente:

```bash
🚀 Configuración COMPLETA de IB Trading en Codespaces
=====================================================
[INFO]  Actualizando sistema y dependencias...
[INFO]  Creando estructura de directorios...
[INFO]  Instalando librerías Python básicas...
[INFO]  Instalando requirements específicos del proyecto...
[INFO]  Configurando VNC...
[INFO]  Descargando e instalando IB Gateway...
[INFO]  Creando scripts de automatización...
[OK] ✅ CONFIGURACIÓN COMPLETA TERMINADA!
```

**⏱️ Tiempo total: 3-5 minutos la primera vez**

### **Paso 3: IMPORTANTE - Reiniciar para Activar Aliases** 🔄

> [!IMPORTANT]
> **Cuando veas el mensaje "CONFIGURACIÓN COMPLETA TERMINADA":**
> 
> 1. 🔴 **Cierra completamente el Codespace** (botón X o cerrar pestaña)
> 2. 🔵 **Vuelve al repositorio en GitHub**
> 3. 🟢 **Reconecta al Codespace** desde Code → Codespaces → `Reconnect`

**¿Por qué es necesario?** Los aliases y comandos personalizados solo se cargan en nuevas sesiones de terminal.

---

## 🎮 **Comandos Disponibles**

Una vez reconectado, tendrás estos **super comandos** disponibles:

### 🚀 **Comandos Principales**
```bash
start-trading      # 🎯 Inicia TODO el sistema (Display + IB Gateway)
start-display      # 🖥️ Solo display virtual y VNC
start-ib          # 📊 Solo IB Gateway
```

### 🔍 **Diagnóstico y Monitoreo**
```bash
ib-logs           # 📋 Ver logs de IB Gateway en tiempo real
show-ports        # 🌐 Mostrar puertos activos del sistema
check-system      # 🔧 Verificación completa del estado
```

### 📁 **Navegación Rápida**
```bash
proyecto          # 📂 Ir al directorio del proyecto
driver            # 🔌 Ir al directorio del driver IB
market            # 📈 Ir a módulos de mercado
trading-dir       # 🏠 Ir al directorio trading
```

---

## 🎯 **Workflow Completo de Trading**

### **1. Iniciar el Sistema** 🚀
```bash
start-trading
```

**Resultado esperado:**
```bash
🚀 Iniciando sistema completo de trading...
[INFO] Configurando display virtual...
[OK] Xvfb ya está corriendo y funcionando
[OK] VNC server ya está corriendo
[OK] Display virtual configurado!
[OK] IB Gateway iniciado - PID: 1234
✅ Sistema listo!
```

### **2. Acceder a IB Gateway** 🖥️

1. **Abre en nueva pestaña:** http://localhost:6080
2. **Haz clic en "Connect"** en la interfaz VNC
3. **Verás el escritorio virtual** con IB Gateway

### **3. Login en IB Gateway** 🔐

En la ventana de IB Gateway:

| Campo | Valor |
|-------|-------|
| **API Type** | `IB API` ✅ |
| **Trading Mode** | `Paper Trading` ✅ |
| **Username** | Tu usuario IB |
| **Password** | Tu contraseña IB |

**Haz clic en "Log In"**

### **4. Configurar API** ⚙️

**Después del login exitoso:**

1. **Menu** → **Configure** → **Settings** → **API**
2. **Configurar:**
   - ✅ **Enable ActiveX and Socket Clients**
   - ❌ **Read-Only API** (desmarcar)
   - 🔢 **Socket port:** `4002`
   - 🏠 **Trusted IPs:** `127.0.0.1`
3. **Apply** → **OK**

### **5. Ejecutar PyRoboAdvisor** 🤖

```bash
# Ir al proyecto
proyecto

# Configurar credenciales en sample.py (si es necesario)
code sample.py

# Ejecutar trading bot
python3 sample.py
```

---

## 🌐 **Puertos y Accesos**

| 🎯 **Servicio** | 📡 **Puerto** | 🔗 **URL/Dirección** | 📋 **Descripción** |
|----------------|--------------|-------------------|------------------|
| 🖥️ **noVNC Desktop** | 6080 | http://localhost:6080 | Escritorio virtual en navegador |
| 📺 **VNC Server** | 5901 | localhost:5901 | Servidor VNC nativo |
| 📊 **IB API Paper** | 4002 | localhost:4002 | API Interactive Brokers Paper Trading |
| 🔄 **IB API Live** | 4001 | localhost:4001 | API Interactive Brokers Live Trading |
| 🎛️ **Dashboard** | 8080 | http://localhost:8080 | Dashboard de trading (futuro) |

---

## 📁 **Estructura del Proyecto**

```
ib-trading-codespaces/
├── 📁 .devcontainer/           # Configuración Codespaces
│   ├── devcontainer.json       # Configuración del entorno
│   ├── setup.sh               # Setup básico
│   └── complete-setup.sh      # Setup completo automatizado
├── 📁 driver/                 # Driver Interactive Brokers
│   ├── driverIB.py           # Conexión con IB Gateway
│   └── requirements.txt       # Dependencias del driver
├── 📁 market/                 # Módulos de mercado
│   ├── source.py             # Fuentes de datos
│   ├── simulator.py          # Simulador de trading
│   └── evaluacion.py         # Evaluación de estrategias
├── 📄 sample.py              # Script principal de trading
├── 📄 strategyClient.py      # Cliente PyRoboAdvisor
├── 📄 requirements.txt       # Dependencias del proyecto
└── 📄 README.md             # Esta documentación
```

---

## 🔧 **Troubleshooting**

### ❌ **Problemas Comunes**

#### **1. "ConnectionRefusedError en puerto 4002"**
```bash
# Verificar que IB Gateway esté corriendo
check-system

# Si no está corriendo, iniciarlo
start-ib

# Verificar login en VNC
# http://localhost:6080
```

#### **2. "No se puede conectar a VNC"**
```bash
# Reiniciar display virtual
start-display

# Verificar puertos
show-ports
```

#### **3. "Error al importar librerías"**
```bash
# Verificar instalaciones
python3 -c "import yfinance, ib_insync; print('✅ OK')"

# Reinstalar si es necesario
pip3 install --user -r requirements.txt
cd driver && pip3 install --user -r requirements.txt
```

#### **4. "PyRoboAdvisor: Ya se ha llamado a set_portfolio hoy"**
```bash
# Es un límite de la API de PyRoboAdvisor
# Opciones:
# 1. Esperar al día siguiente
# 2. Usar otra licencia
# 3. Comentar la línea en sample.py
```

### 🔍 **Comandos de Diagnóstico**

```bash
# Estado completo del sistema
check-system

# Logs detallados de IB Gateway
ib-logs

# Verificar conexión API
python3 -c "
from ib_insync import IB
ib = IB()
try:
    ib.connect('127.0.0.1', 4002, clientId=1)
    print('✅ API conectada')
    print('Cuentas:', ib.managedAccounts())
    ib.disconnect()
except Exception as e:
    print('❌ Error:', e)
"
```

---

## 📊 **Ejemplo de Resultado**

**Simulación histórica exitosa:**
```bash
TAE: 35.13% DDPP: 96.46%/60.21%
2024-07-05 Value: $441653 $93284 AMD/476 DXCM/633 ENPH/168
```

**Conexión IB Gateway exitosa:**
```bash
✅ Conectado a IB Gateway!
💰 Cash disponible: 1000324.16 EUR
📊 Portfolio: 0 posiciones activas

Comprar:
82 acciones de SMCI a 46.73
[BUY-LMT] 82 SMCI @ 46.73

Vender:
23 acciones de AMZN a 213.71
[SELL-LMT] 23 AMZN @ 213.71
```

---

## 🚨 **Advertencias Importantes**

> [!WARNING]
> **Paper Trading Únicamente**
> 
> Esta configuración está optimizada para **Paper Trading**. Para trading real:
> 1. Cambia puerto a `4001` en el código
> 2. Configura límites de riesgo adicionales
> 3. Prueba extensivamente en paper trading primero

> [!NOTE]
> **Límites de PyRoboAdvisor**
> 
> - Una llamada a `set_portfolio` por día con licencia gratuita
> - Para uso intensivo, considera obtener licencia comercial

---

## 🤝 **Contribuciones**

¡Las contribuciones son bienvenidas! 

### **Áreas de Mejora:**
- 🎨 Dashboard web para monitoreo
- 🔧 Soporte para más brokers
- 📊 Métricas avanzadas de trading
- 🚨 Sistema de alertas
- 📱 Interfaz móvil

### **Proceso:**
1. Fork el repositorio
2. Crea una rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit: `git commit -m 'Añadir nueva funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Abre un Pull Request

---

## 📄 **Licencia**

Este proyecto está bajo la licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

## 🙏 **Agradecimientos**

- **David Ragel Díaz-Jara** por PyRoboAdvisor y su visión del trading algorítmico
- **Interactive Brokers** por su robusta API
- **GitHub** por Codespaces y la democratización del desarrollo en la nube
- **Comunidad open source** que hace posible estos proyectos

---

## 📞 **Soporte**

- 📧 **Issues:** [Abrir issue en GitHub](../../issues)
- 💬 **Discord:** [Únete a la comunidad PyRoboAdvisor](#)
- 📚 **Documentación:** [PyRoboAdvisor.org](https://pyroboadvisor.org)

---

<div align="center">

**🚀 ¡Hecho con ❤️ para la comunidad de trading algorítmico! 🚀**

⭐ **¿Te gusta el proyecto? ¡Dale una estrella!** ⭐

[![GitHub stars](https://img.shields.io/github/stars/tu-usuario/ib-trading-codespaces?style=social)](../../stargazers)
[![GitHub forks](https://img.shields.io/github/forks/tu-usuario/ib-trading-codespaces?style=social)](../../network/members)

</div>
