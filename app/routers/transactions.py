"""
Transaction CRUD router
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List
import storage

router = APIRouter()


# Pydantic models
class TransaccionCreate(BaseModel):
    monto: float = Field(..., gt=0)
    tipo: str  # Will validate manually
    descripcion: str = Field(..., min_length=1)


class Transaccion(TransaccionCreate):
    id: int
    fecha: str


# Validation helper
def _validate_tipo(tipo: str):
    """Validate transaction type"""
    if tipo not in ["ingreso", "gasto"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El tipo debe ser 'ingreso' o 'gasto'"
        )


@router.get("", response_model=List[Transaccion])
async def get_all_transactions():
    """Get all transactions from legacy storage"""
    transactions = storage.leer_transacciones()
    return transactions


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_transaction(transaccion: TransaccionCreate):
    """Create a new transaction"""
    _validate_tipo(transaccion.tipo)

    nueva_transaccion = storage.agregar_transaccion(
        tipo=transaccion.tipo,
        monto=transaccion.monto,
        descripcion=transaccion.descripcion
    )

    return nueva_transaccion


@router.get("/{transaction_id}", response_model=Transaccion)
async def get_transaction(transaction_id: int):
    """Get a specific transaction by ID"""
    transactions = storage.leer_transacciones()

    for transaction in transactions:
        if transaction["id"] == transaction_id:
            return transaction

    raise HTTPException(
        status_code=404,
        detail=f"Transacción {transaction_id} no encontrada"
    )


@router.put("/{transaction_id}")
async def update_transaction(
    transaction_id: int,
    transaccion: TransaccionCreate
):
    """Update an existing transaction"""
    _validate_tipo(transaccion.tipo)

    transactions = storage.leer_transacciones()

    for i, tx in enumerate(transactions):
        if tx["id"] == transaction_id:
            transactions[i]["monto"] = transaccion.monto
            transactions[i]["tipo"] = transaccion.tipo
            transactions[i]["descripcion"] = transaccion.descripcion

            storage.guardar_transacciones(transactions)
            return transactions[i]

    raise HTTPException(
        status_code=404,
        detail=f"Transacción {transaction_id} no encontrada"
    )


@router.delete("/{transaction_id}")
async def delete_transaction(transaction_id: int):
    """Delete a transaction"""
    transactions = storage.leer_transacciones()

    for i, transaction in enumerate(transactions):
        if transaction["id"] == transaction_id:
            transactions.pop(i)
            storage.guardar_transacciones(transactions)
            return {"success": True, "message": f"Transacción {transaction_id} eliminada"}

    raise HTTPException(
        status_code=404,
        detail=f"Transacción {transaction_id} no encontrada"
    )
