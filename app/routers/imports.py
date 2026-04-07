"""
Import router - Upload and manage transaction imports
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional, List, Dict, Any
from pathlib import Path
import tempfile
import shutil

from app.models.enums import SourceType
from app.services.importer_simple import MercadoPagoImporterSimple
from app.repositories import get_db

router = APIRouter()


@router.post("/upload")
async def upload_file_import(
    file: UploadFile = File(...),
    source_type: Optional[SourceType] = Form(None),
):
    """
    Upload and import transactions from CSV/Excel file de Mercado Pago

    Args:
        file: CSV or Excel file
        source_type: Optional source type (defaults to mercadopago based on extension)

    Returns:
        JSON con summary y lista de transacciones
    """
    # Validate file extension
    allowed_extensions = ['.csv', '.xlsx', '.xls']
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Formato de archivo no soportado: {file_ext}. Use: {', '.join(allowed_extensions)}"
        )

    # Auto-detect source_type if not provided
    if not source_type:
        if file_ext == '.csv':
            source_type = SourceType.MERCADOPAGO_CSV
        else:  # .xlsx or .xls
            source_type = SourceType.MERCADOPAGO_EXCEL

    # Create temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
        # Copy uploaded file to temp
        shutil.copyfileobj(file.file, temp_file)
        temp_path = Path(temp_file.name)

    try:
        # Import file con importador simplificado
        importer = MercadoPagoImporterSimple()
        result = importer.import_file(
            file_path=temp_path,
            source_type=source_type,
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al importar archivo: {str(e)}"
        )
    finally:
        # Clean up temp file
        if temp_path.exists():
            temp_path.unlink()


@router.get("/batches/{batch_id}/transactions")
async def get_batch_transactions(batch_id: str) -> Dict[str, Any]:
    """
    Obtiene las transacciones de un batch importado

    Args:
        batch_id: ID del batch

    Returns:
        JSON con lista de transacciones del batch
    """
    db = get_db()

    # Verificar que el batch existe
    if 'import_batches' not in db.data:
        raise HTTPException(
            status_code=404,
            detail="No hay batches importados"
        )

    batches = db.data['import_batches']
    if batch_id not in batches:
        raise HTTPException(
            status_code=404,
            detail=f"Batch {batch_id} no encontrado"
        )

    batch = batches[batch_id]

    return {
        "success": True,
        "batch_id": batch_id,
        "transactions": batch.get('transactions', [])
    }


@router.post("/batches/{batch_id}/confirm")
async def confirm_batch_transactions(batch_id: str) -> Dict[str, Any]:
    """
    Confirma un batch importado y pasa las transacciones al dashboard

    Los ingresos se registran como ingresos en el dashboard.
    Los egresos se registran como gastos en el dashboard.

    Args:
        batch_id: ID del batch a confirmar

    Returns:
        JSON con resumen de confirmación
    """
    import storage

    db = get_db()

    # Verificar que el batch existe
    if 'import_batches' not in db.data:
        raise HTTPException(
            status_code=404,
            detail="No hay batches importados"
        )

    batches = db.data['import_batches']
    if batch_id not in batches:
        raise HTTPException(
            status_code=404,
            detail=f"Batch {batch_id} no encontrado"
        )

    batch = batches[batch_id]
    transactions = batch.get('transactions', [])

    # Contadores
    ingresos_confirmados = 0
    gastos_confirmados = 0
    total_ingresos = 0.0
    total_gastos = 0.0

    # Procesar cada transacción del batch
    for tx in transactions:
        tx_type = tx.get('transaction_type')
        amount = tx.get('amount', 0)
        description = tx.get('description', 'Sin descripción')

        if tx_type == 'ingreso':
            # Registrar como ingreso en el dashboard
            storage.agregar_transaccion(
                tipo='ingreso',
                monto=amount,
                descripcion=description
            )
            ingresos_confirmados += 1
            total_ingresos += amount

        elif tx_type == 'gasto':
            # Registrar como gasto en el dashboard
            storage.agregar_transaccion(
                tipo='gasto',
                monto=amount,
                descripcion=description
            )
            gastos_confirmados += 1
            total_gastos += amount

    # Marcar el batch como confirmado
    batch['confirmed'] = True
    batch['confirmed_at'] = datetime.now().isoformat()
    db.save()

    return {
        "success": True,
        "batch_id": batch_id,
        "summary": {
            "ingresos_confirmados": ingresos_confirmados,
            "gastos_confirmados": gastos_confirmados,
            "total_ingresos_ars": total_ingresos,
            "total_gastos_ars": total_gastos,
            "total_transacciones": ingresos_confirmados + gastos_confirmados
        }
    }
