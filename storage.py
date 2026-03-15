import json
import os
from typing import List, Dict
from datetime import datetime

FILENAME = "transacciones.json"

def leer_transacciones() -> List[Dict]:
    """Lee todas las transacciones del archivo JSON"""
    if not os.path.exists(FILENAME):
        return []

    try:
        with open(FILENAME, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def guardar_transacciones(transacciones: List[Dict]) -> None:
    """Guarda las transacciones en el archivo JSON"""
    with open(FILENAME, 'w', encoding='utf-8') as f:
        json.dump(transacciones, f, ensure_ascii=False, indent=2)

def agregar_transaccion(tipo: str, monto: float, descripcion: str) -> Dict:
    """Agrega una nueva transacción"""
    transacciones = leer_transacciones()

    nueva_transaccion = {
        "id": len(transacciones) + 1,
        "tipo": tipo,
        "monto": monto,
        "descripcion": descripcion,
        "fecha": datetime.now().isoformat()
    }

    transacciones.append(nueva_transaccion)
    guardar_transacciones(transacciones)

    return nueva_transaccion

def calcular_balance() -> Dict:
    """Calcula el balance total de ingresos y gastos"""
    transacciones = leer_transacciones()

    ingresos = sum(t["monto"] for t in transacciones if t["tipo"] == "ingreso")
    gastos = sum(t["monto"] for t in transacciones if t["tipo"] == "gasto")
    balance = ingresos - gastos

    return {
        "ingresos": ingresos,
        "gastos": gastos,
        "balance": balance
    }
