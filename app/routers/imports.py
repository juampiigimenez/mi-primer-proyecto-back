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
