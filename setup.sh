#!/bin/bash
echo "========================================"
echo " Finanzas Backend - Setup"
echo "========================================"
echo

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 no encontrado. Instalar Python 3.9+"
    exit 1
fi

echo "[1/4] Creando entorno virtual..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: No se pudo crear el entorno virtual"
    exit 1
fi

echo "[2/4] Activando entorno virtual..."
source venv/bin/activate

echo "[3/4] Instalando dependencias..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Falló la instalación de dependencias"
    exit 1
fi

echo "[4/4] Verificando instalación..."
python -c "import fastapi, pandas, openpyxl; print('✅ Dependencias OK')"

echo
echo "========================================"
echo " Setup Completado!"
echo "========================================"
echo
echo "Para iniciar el servidor:"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --reload"
echo
echo "O ejecuta: ./start.sh"
echo
