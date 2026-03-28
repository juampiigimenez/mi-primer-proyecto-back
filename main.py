from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from typing import List
import storage

app = FastAPI(
    title="API de Finanzas Personales",
    description="API REST para registrar ingresos y gastos",
    version="1.0.0"
)

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

@app.get("/")
def root():
    """Endpoint raíz con información de la API"""
    return {
        "mensaje": "API de Finanzas Personales",
        "version": "1.0.0",
        "endpoints": {
            "POST /transacciones": "Crear nueva transacción",
            "GET /transacciones": "Listar todas las transacciones",
            "GET /balance": "Obtener balance total"
        }
    }

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
    uvicorn.run(app, host="0.0.0.0", port=8000)
