"""
Main FastAPI application with modular architecture
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict
from typing import List

from config.settings import (
    API_TITLE,
    API_VERSION,
    API_DESCRIPTION,
    CORS_ORIGINS,
    CORS_ALLOW_CREDENTIALS,
    CORS_ALLOW_METHODS,
    CORS_ALLOW_HEADERS,
)

# Import routers
from app.routers import imports

# Import storage module for original endpoints
import storage

app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=CORS_ALLOW_METHODS,
    allow_headers=CORS_ALLOW_HEADERS,
)

# Pydantic models for original endpoints
class TransaccionCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tipo": "ingreso",
                "monto": 1500.50,
                "descripcion": "Salario mensual"
            }
        }
    )

    tipo: str = Field(..., description="Tipo de transacción: 'ingreso' o 'gasto'")
    monto: float = Field(..., gt=0, description="Monto de la transacción (debe ser positivo)")
    descripcion: str = Field(..., min_length=1, description="Descripción de la transacción")

class Transaccion(TransaccionCreate):
    id: int
    fecha: str

class Balance(BaseModel):
    ingresos: float
    gastos: float
    balance: float


# Include routers
app.include_router(imports.router, prefix="/api/v1/imports", tags=["Imports"])
# app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["Transactions"])  # TODO: Next phase
# app.include_router(accounts.router, prefix="/api/v1/accounts", tags=["Accounts"])  # TODO: Next phase
# app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])  # TODO: Next phase


@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "name": API_TITLE,
        "version": API_VERSION,
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "POST /transacciones": "Crear nueva transacción",
            "GET /transacciones": "Listar todas las transacciones",
            "GET /balance": "Obtener balance total (en ARS)",
            "POST /api/v1/imports/upload": "Importar transacciones desde archivo CSV",
            "GET /api/v1/imports/batches/{batch_id}/transactions": "Ver transacciones de un batch importado",
            "POST /api/v1/imports/batches/{batch_id}/confirm": "Confirmar y pasar transacciones al dashboard"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": API_VERSION
    }


# Original endpoints from main.py
@app.post("/transacciones", response_model=Transaccion, status_code=201)
def crear_transaccion(transaccion: TransaccionCreate):
    """Crea una nueva transacción (ingreso o gasto)"""
    if transaccion.tipo not in ["ingreso", "gasto"]:
        raise HTTPException(
            status_code=400,
            detail="El tipo debe ser 'ingreso' o 'gasto'"
        )

    nueva_transaccion = storage.agregar_transaccion(
        tipo=transaccion.tipo,
        monto=transaccion.monto,
        descripcion=transaccion.descripcion
    )

    return nueva_transaccion


@app.get("/transacciones", response_model=List[Transaccion])
def obtener_transacciones():
    """Obtiene todas las transacciones registradas"""
    return storage.leer_transacciones()


@app.get("/balance", response_model=Balance)
def obtener_balance():
    """Obtiene el balance total (ingresos - gastos)"""
    return storage.calcular_balance()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
