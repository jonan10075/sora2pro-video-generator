@echo off
setlocal

REM =======================
REM  Ir a la raíz del proyecto
REM =======================
cd /d "%~dp0.."

REM =======================
REM  Crear y activar el entorno virtual
REM =======================
if not exist venv (
  echo [INFO] Creando entorno virtual...
  python -m venv venv
)

call venv\Scripts\activate.bat

REM =======================
REM  Instalar dependencias
REM =======================
if exist backend\requirements.txt (
  python -m pip install --upgrade pip
  pip install -r backend\requirements.txt
) else (
  echo [ERROR] No se encuentra backend\requirements.txt
  pause
  exit /b 1
)

REM =======================
REM  API key de APIMart
REM  >>> CAMBIA ESTO POR TU CLAVE <<<
REM =======================
set "APIMART_API_KEY=YOUR_APIMART_API_KEY"

if "%APIMART_API_KEY%"=="" (
  echo [ERROR] La variable APIMART_API_KEY no está definida.
  echo Edita start_server.bat y escribe tu clave de APIMart.
  pause
  exit /b 1
)

REM =======================
REM  Lanzar el servidor Flask
REM =======================
echo [INFO] Iniciando servidor...
python backend\app.py

echo.
echo Si ves errores arriba, revisa la configuracion.
pause
endlocal

