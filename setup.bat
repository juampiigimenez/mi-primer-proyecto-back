@echo off
echo ========================================
echo  Finanzas Backend - Setup
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no encontrado. Instalar Python 3.9+
    pause
    exit /b 1
)

echo [1/4] Creando entorno virtual...
python -m venv venv
if errorlevel 1 (
    echo ERROR: No se pudo crear el entorno virtual
    pause
    exit /b 1
)

echo [2/4] Activando entorno virtual...
call venv\Scripts\activate.bat

echo [3/4] Instalando dependencias...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Falló la instalación de dependencias
    pause
    exit /b 1
)

echo [4/4] Verificando instalación...
python -c "import fastapi, pandas, openpyxl; print('✅ Dependencias OK')"

echo.
echo ========================================
echo  Setup Completado!
echo ========================================
echo.
echo Para iniciar el servidor:
echo   venv\Scripts\activate
echo   uvicorn app.main:app --reload
echo.
echo O ejecuta: start.bat
echo.
pause
