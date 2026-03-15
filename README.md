# API de Finanzas Personales

API REST simple construida con FastAPI para registrar ingresos y gastos, y consultar el balance total. Los datos se almacenan en un archivo JSON local.

## Características

- Registrar ingresos y gastos
- Consultar todas las transacciones
- Obtener balance total (ingresos - gastos)
- Almacenamiento en archivo JSON local
- Documentación interactiva automática

## Instalación

1. Crear un entorno virtual (recomendado):
```bash
python -m venv venv
venv\Scripts\activate  # En Windows
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Uso

### Iniciar el servidor

```bash
uvicorn main:app --reload
```

El servidor estará disponible en: `http://localhost:8000`

### Documentación interactiva

Una vez iniciado el servidor, accede a:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints

### 1. Crear una transacción
**POST** `/transacciones`

Crea un nuevo ingreso o gasto.

**Body:**
```json
{
  "tipo": "ingreso",
  "monto": 1500.50,
  "descripcion": "Salario mensual"
}
```

**Respuesta:**
```json
{
  "id": 1,
  "tipo": "ingreso",
  "monto": 1500.50,
  "descripcion": "Salario mensual",
  "fecha": "2026-03-15T10:30:00.123456"
}
```

### 2. Obtener todas las transacciones
**GET** `/transacciones`

Devuelve la lista completa de transacciones.

**Respuesta:**
```json
[
  {
    "id": 1,
    "tipo": "ingreso",
    "monto": 1500.50,
    "descripcion": "Salario mensual",
    "fecha": "2026-03-15T10:30:00.123456"
  },
  {
    "id": 2,
    "tipo": "gasto",
    "monto": 350.00,
    "descripcion": "Compras del supermercado",
    "fecha": "2026-03-15T11:15:00.789012"
  }
]
```

### 3. Obtener balance
**GET** `/balance`

Calcula y devuelve el balance total.

**Respuesta:**
```json
{
  "ingresos": 1500.50,
  "gastos": 350.00,
  "balance": 1150.50
}
```

## Ejemplos de uso con curl

### Registrar un ingreso
```bash
curl -X POST "http://localhost:8000/transacciones" \
  -H "Content-Type: application/json" \
  -d "{\"tipo\":\"ingreso\",\"monto\":1500.50,\"descripcion\":\"Salario mensual\"}"
```

### Registrar un gasto
```bash
curl -X POST "http://localhost:8000/transacciones" \
  -H "Content-Type: application/json" \
  -d "{\"tipo\":\"gasto\",\"monto\":350.00,\"descripcion\":\"Compras del supermercado\"}"
```

### Consultar transacciones
```bash
curl http://localhost:8000/transacciones
```

### Consultar balance
```bash
curl http://localhost:8000/balance
```

## Estructura del proyecto

```
finanzas-back/
├── main.py              # Aplicación FastAPI con los endpoints
├── storage.py           # Módulo de gestión del almacenamiento JSON
├── requirements.txt     # Dependencias del proyecto
├── README.md           # Este archivo
└── transacciones.json  # Archivo de datos (se crea automáticamente)
```

## Almacenamiento de datos

Los datos se guardan automáticamente en el archivo `transacciones.json` en el directorio del proyecto. Este archivo se crea automáticamente al registrar la primera transacción.

## Tecnologías utilizadas

- **FastAPI**: Framework web moderno y rápido
- **Uvicorn**: Servidor ASGI de alto rendimiento
- **Pydantic**: Validación de datos y serialización
