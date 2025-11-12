<# ===========================================================
 setup_pyrobo.ps1
 Instala PyRoboAdvisor (desde Paso 4 en Windows 10).
 Si falta Python 3.11+ o es inferior, instala automáticamente Python 3.11.9.
 Si falta Git, intenta instalarlo (winget/choco/scoop o GitHub releases).

 Como ejecutar:
   powershell -ExecutionPolicy Bypass -File .\setup_pyrobo.ps1 [opciones]

 Opciones (todas opcionales):
   -RepoUrl           URL del repo Git (por defecto: https://github.com/daradija/pyroboadvisor.git)
   -ProjectName       Nombre de carpeta del repo (por defecto: pyroboadvisor)
   -BasePath          Carpeta base donde clonar (por defecto: $env:USERPROFILE\)
   -PythonMinVersion  Versión mínima de Python (por defecto: 3.11.0)
   -UpdateOnly        Solo actualizar repo y deps si ya existe (no recrea venv)
   -NoVSCode          No configurar VS Code ni instalar la extensión de Python
   -OpenVSCode        Abrir el proyecto en VS Code al finalizar
   -RestartVSCode     Si -OpenVSCode: reiniciar VS Code (fuera de VS Code host)
   -Quiet             Salida reducida

 Requisitos previos:
   - (Opcional) VS Code instalado

 Nota:
   No cambia la ExecutionPolicy global; ejecuta con -ExecutionPolicy Bypass.
=========================================================== #>

param(
  [string]$RepoUrl = "https://github.com/daradija/pyroboadvisor.git",
  [string]$ProjectName = "pyroboadvisor",
  [string]$BasePath = "$env:USERPROFILE\",
  [string]$PythonMinVersion = "3.11.0",
  [switch]$UpdateOnly,
  [switch]$NoVSCode,
  [switch]$OpenVSCode,
  [switch]$RestartVSCode,
  [switch]$Quiet
)

# Configuración de errores y salida
$ErrorActionPreference = 'Stop'
function Step($msg){ if(-not $Quiet){ Write-Host "`n==> $msg" -ForegroundColor Cyan } }
function Warn($msg){ if(-not $Quiet){ Write-Host $msg -ForegroundColor Yellow } }
function Ok($msg){  if(-not $Quiet){ Write-Host $msg -ForegroundColor Green } }

# Helpers
function Test-Command { param([string]$Name) (Get-Command $Name -ErrorAction SilentlyContinue) -ne $null }
function Compare-SemVer { param([string]$A,[string]$B) ([version]$A).CompareTo([version]$B) }
function Get-IsAdmin {
  try{
    $wi=[Security.Principal.WindowsIdentity]::GetCurrent()
    $wp=New-Object Security.Principal.WindowsPrincipal($wi)
    return $wp.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
  }catch{ return $false }
}
function Get-CodeCmd {
  if (Test-Command code) { return "code" }
  $cands=@(
    "$env:LOCALAPPDATA\Programs\Microsoft VS Code\Code.exe",
    "$env:ProgramFiles\Microsoft VS Code\Code.exe",
    "$env:ProgramFiles(x86)\Microsoft VS Code\Code.exe"
  )
  foreach($p in $cands){ if(Test-Path $p){ return $p } }
  return $null
}
function In-VSCodeHost { return ($env:TERM_PROGRAM -eq "vscode" -or $env:VSCODE_PID -or $env:VSCODE_CWD) }
function Restart-VSCode {
  param([string]$CodeCmd,[string]$Folder)
  if(-not $CodeCmd){ Warn "AVISO: VS Code no detectado."; return }
  if (In-VSCodeHost) {
    Step "Terminal integrada de VS Code detectada: reutilizando la ventana actual."
    try { & $CodeCmd -r "$Folder" | Out-Null } catch { Warn ("AVISO: Fallo al cambiar a {0}: {1}" -f $Folder, $_) }
    return
  }
  Step "Cerrando VS Code abierto (si lo hay)..."
  try {
    $procs=Get-Process -Name Code -ErrorAction SilentlyContinue
    if($procs){
      foreach($p in $procs){ try{ $p.CloseMainWindow() | Out-Null }catch{} }
      Start-Sleep 1.5
      $procs=Get-Process -Name Code -ErrorAction SilentlyContinue
      if($procs){ $procs | Stop-Process -Force }
    }
  } catch { Warn ("AVISO: No se pudo cerrar VS Code: {0}" -f $_) }
  Step ("Abriendo VS Code en {0} ..." -f $Folder)
  try { Start-Process -FilePath $CodeCmd -ArgumentList @("-n","$Folder") | Out-Null } catch { Warn ("AVISO: Fallo al abrir VS Code: {0}" -f $_) }
}

# ---------- Instalación automática de Python 3.11.9 ----------
function Get-PythonInstallerInfo {
  $base = "https://www.python.org/ftp/python/3.11.9"
  $arch = if ($env:PROCESSOR_ARCHITECTURE -match 'ARM64' -or $env:PROCESSOR_ARCHITEW6432 -match 'ARM64') { 'arm64' }
          elseif ([Environment]::Is64BitOperatingSystem) { 'amd64' } else { 'x86' }
  $file = switch ($arch) {
    'amd64' { 'python-3.11.9-amd64.exe' }
    'arm64' { 'python-3.11.9-arm64.exe' }
    default { 'python-3.11.9.exe' }
  }
  return @{ Url = "$base/$file"; FileName = $file }
}
function Install-Python3119 {
  Step "Instalando Python 3.11.9 (descarga silenciosa desde python.org)..."
  $info = Get-PythonInstallerInfo
  $tmp  = Join-Path $env:TEMP $info.FileName
  try {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest -Uri $info.Url -OutFile $tmp -UseBasicParsing
  } catch { throw ("No se pudo descargar {0}: {1}" -f $info.Url, $_) }

  $args=@('/quiet','Include_pip=1','PrependPath=1','Include_test=0')
  if (Get-IsAdmin) { $args += 'InstallAllUsers=1' }  # si no, instalación por-usuario

  try { Start-Process -FilePath $tmp -ArgumentList $args -Wait -PassThru | Out-Null }
  catch { throw ("Fallo al instalar Python 3.11.9: {0}" -f $_) }

  $cands=@("$env:ProgramFiles\Python311\python.exe","$env:LOCALAPPDATA\Programs\Python\Python311\python.exe")
  foreach($c in $cands){ if(Test-Path $c){ return $c } }
  try { $probe = & py -3.11 -c "import sys;print(sys.executable)" 2>$null; if ($probe) { return $probe.Trim() } } catch {}
  return $null
}

# ---------- Instalación automática de Git ----------
function Ensure-Git {
  # 1) si ya está, salir
  if (Get-Command git -ErrorAction SilentlyContinue) { return }

  # 2) intentar con winget/choco/scoop
  if (Get-Command winget -ErrorAction SilentlyContinue) {
    Step "Instalando Git con winget..."
    $args = @('install','--id','Git.Git','-e','--source','winget','--accept-package-agreements','--accept-source-agreements','--silent')
    try { Start-Process winget -ArgumentList $args -Wait | Out-Null } catch { Warn ("AVISO: winget falló: {0}" -f $_) }
  }
  if (-not (Get-Command git -ErrorAction SilentlyContinue) -and (Get-Command choco -ErrorAction SilentlyContinue)) {
    Step "Instalando Git con Chocolatey..."
    try { Start-Process choco -ArgumentList @('install','git','-y','--no-progress') -Wait | Out-Null } catch { Warn ("AVISO: choco falló: {0}" -f $_) }
  }
  if (-not (Get-Command git -ErrorAction SilentlyContinue) -and (Get-Command scoop -ErrorAction SilentlyContinue)) {
    Step "Instalando Git con Scoop..."
    try { Start-Process powershell -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-Command','scoop install git') -Wait | Out-Null } catch { Warn ("AVISO: scoop falló: {0}" -f $_) }
  }

  # 3) último recurso: descargar del último release en GitHub (API)
  if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Step "Instalando Git desde GitHub (última release)..."
    try {
      [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
      $rel = Invoke-RestMethod -Uri 'https://api.github.com/repos/git-for-windows/git/releases/latest' -Headers @{ 'User-Agent'='PowerShell' }
      $want64 = [Environment]::Is64BitOperatingSystem
      $asset = if ($want64) {
        $rel.assets | Where-Object { $_.name -match '^Git-.*-64-bit\.exe$' } | Select-Object -First 1
      } else {
        $rel.assets | Where-Object { $_.name -match '^Git-.*-32-bit\.exe$' } | Select-Object -First 1
      }
      if (-not $asset) { throw "No se encontró instalador .exe en la release." }
      $tmp = Join-Path $env:TEMP $asset.name
      Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $tmp -UseBasicParsing
      Start-Process -FilePath $tmp -ArgumentList @('/VERYSILENT','/NORESTART','/SP-') -Wait | Out-Null
    } catch { throw ("No se pudo instalar Git desde GitHub: {0}" -f $_) }
  }

  # 4) asegurar rutas típicas en PATH (para esta sesión)
  $paths = @("C:\Program Files\Git\cmd","C:\Program Files\Git\bin","C:\Program Files (x86)\Git\cmd",(Join-Path $env:LOCALAPPDATA "Programs\Git\cmd"))
  foreach($p in $paths){ if(Test-Path $p -PathType Container -and -not (($env:Path -split ';') -contains $p)){ $env:Path="$env:Path;$p" } }

  # 5) verificación final
  $gitCmd = Get-Command git -ErrorAction SilentlyContinue
  if (-not $gitCmd) { throw "Git no pudo instalarse o no está accesible en PATH." }
  Ok ("OK: git detectado -> {0}" -f $gitCmd.Source)
}

# ===================== PRECHECKS (git / python) =====================
Step "Comprobando herramientas (git y python)..."

# Intentar detectar/instalar Git
# (primero: si está instalado pero fuera de PATH, añadir rutas comunes; luego Ensure-Git)
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  Warn "AVISO: git no está en PATH. Intentando añadir rutas comunes..."
  $gitCandidates = @(
    "C:\Program Files\Git\cmd",
    "C:\Program Files\Git\bin",
    "C:\Program Files (x86)\Git\cmd",
    (Join-Path $env:LOCALAPPDATA "Programs\Git\cmd")
  )
  foreach ($p in $gitCandidates) {
    if (Test-Path $p -PathType Container -and -not (($env:Path -split ';') -contains $p)) { $env:Path = "$env:Path;$p" }
  }
}
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { Ensure-Git }

# Python 3.11+: localizar/instalar si falta o es viejo
$pythonExe = $null
$probes = @(
  { & py -3.11 -c "import sys;print(sys.executable)" 2>$null },
  { & python   -c "import sys;print(sys.executable)" 2>$null }
)
foreach($p in $probes){ try{ $r=& $p; if($LASTEXITCODE -eq 0 -and $r){ $pythonExe=$r.Trim(); break } }catch{} }

$needInstall = $true
if ($pythonExe) {
  $pyVer = & "$pythonExe" -c "import platform;print(platform.python_version())"
  if ( (Compare-SemVer $pyVer $PythonMinVersion) -ge 0 ) { $needInstall = $false }
}
if ($needInstall) {
  $pythonExe = Install-Python3119
  if (-not $pythonExe) { throw "Python 3.11.9 parece no haberse instalado correctamente." }
  $pyVer = & "$pythonExe" -c "import platform;print(platform.python_version())"
}
Ok ("OK: Python {0} detectado" -f $pyVer)

# Detectar VS Code (CLI o exe) si procede
$codeCmd = if (-not $NoVSCode) { Get-CodeCmd } else { $null }

# ===================== DIRECTORIOS =====================
if(-not (Test-Path $BasePath)){ throw "La ruta base no existe: $BasePath" }
$ProjectDir = Join-Path $BasePath $ProjectName
Step ("Usando carpeta de proyecto: {0}" -f $ProjectDir)
New-Item -ItemType Directory -Path $ProjectDir -Force | Out-Null

# ===================== GIT: CLONE / PULL =====================
if(-not (Test-Path (Join-Path $ProjectDir ".git"))){
  Step "Clonando repositorio..."
  Push-Location $BasePath
  git clone $RepoUrl $ProjectName
  Pop-Location
  Ok ("OK: Clonado en {0}" -f $ProjectDir)
}else{
  Step "Repositorio ya existe. Actualizando (git pull)..."
  Push-Location $ProjectDir
  git pull --rebase --autostash
  Pop-Location
  Ok "OK: Actualización completada"
}

# ===================== ENTORNO VIRTUAL (carpeta: venv) =====================
Push-Location $ProjectDir
$venvDir       = Join-Path $ProjectDir "venv"
$venvPy        = Join-Path $venvDir "Scripts\python.exe"
$venvActivate  = Join-Path $venvDir "Scripts\Activate.ps1"

if ($UpdateOnly) {
  Step "UpdateOnly: no se recrea el entorno virtual."
}elseif (-not (Test-Path $venvPy)) {
  Step "Creando entorno virtual (.\venv)..."
  & "$pythonExe" -m venv "venv"
  Ok "OK: Entorno virtual creado"
}else{
  Step "Entorno virtual encontrado (se reutiliza)."
}

if (-not (Test-Path $venvPy)) { throw "No se encontró el intérprete del venv: $venvPy" }

# ===================== DEPENDENCIAS =====================
Step "Actualizando pip en el venv..."
& "$venvPy" -m pip install --upgrade pip

Step "Instalando requirements (raíz)..."
$reqRoot = Join-Path $ProjectDir "requirements.txt"
if (Test-Path $reqRoot) {
  & "$venvPy" -m pip install -r "$reqRoot"
} else {
  Warn "AVISO: No se encontró requirements.txt en raíz (se continúa)"
}

Step "Instalando requirements (driver)..."
$reqDriver = Join-Path $ProjectDir "driver\requirements.txt"
if (Test-Path $reqDriver) {
  & "$venvPy" -m pip install -r "$reqDriver"
} else {
  Warn "AVISO: No se encontró driver\requirements.txt (se continúa)"
}

# ===================== VS CODE (OPCIONAL) =====================
if(-not $NoVSCode){
  Step "Configurando VS Code (si disponible)..."
  $vscodeDir = Join-Path $ProjectDir ".vscode"
  New-Item -ItemType Directory -Path $vscodeDir -Force | Out-Null
  $settingsPath = Join-Path $vscodeDir "settings.json"
  $settings = @{
    "python.defaultInterpreterPath" = $venvPy
    "terminal.integrated.defaultProfile.windows" = "PowerShell"
  } | ConvertTo-Json -Depth 4
  $settings | Out-File -FilePath $settingsPath -Encoding UTF8

  if ($codeCmd) {
    try { & $codeCmd --install-extension ms-python.python --force | Out-Null; Ok "OK: Extensión Python instalada/actualizada" }
    catch { Warn ("AVISO: No se pudo instalar la extensión de Python: {0} (se continúa)" -f $_) }
  } else {
    Warn "AVISO: VS Code no detectado; se omite la instalación de la extensión."
  }
}else{
  Step "Omitiendo configuración de VS Code por -NoVSCode."
}

# ===================== ACTIVAR VENV EN ESTE PROCESO =====================
if (Test-Path $venvActivate) {
  Step "Activando entorno virtual (.\venv\Scripts\Activate.ps1) en este proceso..."
  . "$venvActivate"
  Ok "OK: Entorno virtual activado en este proceso"
} else {
  Warn "AVISO: No se encontró: $venvActivate"
}

# ===================== SMOKE TEST RÁPIDO =====================
Step "Validando Python/pip dentro del venv..."
python -c "import sys;print('Python:',sys.version.split()[0])"
python -c "import pip;print('pip OK')"
try { python -c "import importlib; importlib.import_module('matplotlib'); print('matplotlib OK')" }
catch { Warn "AVISO: matplotlib no disponible (opcional). Se continúa." }

# ===================== RESUMEN =====================
Write-Host "`nInstalación completada." -ForegroundColor Green
Write-Host ("Proyecto: {0}" -f $ProjectDir)
Write-Host ("Venv: {0}" -f $venvPy)
Write-Host "Usar ahora (esta consola ya está activada):  python .\sample_b.py"
Write-Host "Reactivar en otra consola:  cd `"$ProjectDir`"; .\venv\Scripts\Activate.ps1"

# ===================== ABRIR / REINICIAR VS CODE (opcional) =====================
if ($OpenVSCode) {
  $codeCmd = Get-CodeCmd
  if ($codeCmd) {
    if ($RestartVSCode) {
      Restart-VSCode -CodeCmd $codeCmd -Folder $ProjectDir
    } else {
      Step ("Abriendo VS Code en {0} ..." -f $ProjectDir)
      try { & $codeCmd -r "$ProjectDir" | Out-Null } catch { Warn ("AVISO: Fallo al abrir VS Code: {0}" -f $_) }
    }
  } else {
    Warn "AVISO: No se encontró VS Code (code/Code.exe). No se puede abrir automáticamente."
  }
}

Pop-Location
