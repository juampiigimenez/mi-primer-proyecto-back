#!/bin/bash
echo "========================================"
echo " Finanzas Backend - Iniciando Servidor"
echo "========================================"
echo

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "ERROR: Entorno virtual no encontrado."
    echo "Ejecuta primero: ./setup.sh"
    exit 1
fi

echo "Activando entorno virtual..."
source venv/bin/activate

echo "Iniciando servidor FastAPI..."
echo
echo "Servidor disponible en: http://localhost:8000"
echo "Swagger UI: http://localhost:8000/docs"
echo
echo "Presiona Ctrl+C para detener el servidor"
echo

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
