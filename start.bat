@echo off
echo ========================================
echo  Finanzas Backend - Iniciando Servidor
echo ========================================
echo.

REM Check if venv exists
if not exist "venv\" (
    echo ERROR: Entorno virtual no encontrado.
    echo Ejecuta primero: setup.bat
    pause
    exit /b 1
)

echo Activando entorno virtual...
call venv\Scripts\activate.bat

echo Iniciando servidor FastAPI...
echo.
echo Servidor disponible en: http://localhost:8000
echo Swagger UI: http://localhost:8000/docs
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
