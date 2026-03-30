"""
Import router - Upload and manage transaction imports
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional, List
from pathlib import Path
import tempfile
import shutil

from app.models.enums import SourceType
from app.services.importer import ImportService

router = APIRouter()


@router.post("/upload")
async def upload_file_import(
    file: UploadFile = File(...),
    source_type: Optional[SourceType] = Form(None),
    account_id: Optional[str] = Form(None),
    credit_card_id: Optional[str] = Form(None),
):
    """
    Upload and import transactions from CSV/Excel file

    Args:
        file: CSV or Excel file
        source_type: Optional source type (defaults to mercadopago based on extension)
        account_id: Optional default account ID for transactions
        credit_card_id: Optional default credit card ID for transactions

    Returns:
        Import batch with results
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
        # Import file
        import_service = ImportService()
        batch = import_service.import_file(
            file_path=temp_path,
            source_type=source_type,
            account_id=account_id,
            credit_card_id=credit_card_id,
        )

        # Build summary response
        return {
            "success": True,
            "message": "Importación completada exitosamente",
            "summary": {
                "total_rows": batch.get('total_rows', 0),
                "processed": batch.get('processed_rows', 0),
                "duplicates": batch.get('duplicated_rows', 0),
                "errors": batch.get('failed_rows', 0),
                "review_required": batch.get('metadata', {}).get('review_required', 0)
            },
            "batch_id": batch.get('id'),
            "batch": batch
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al importar archivo: {str(e)}"
        )
    finally:
        # Clean up temp file
        if temp_path.exists():
            temp_path.unlink()


@router.get("/batches")
def get_all_batches():
    """Get all import batches"""
    import_service = ImportService()
    batches = import_service.get_all_batches()
    return {"batches": batches}


@router.get("/batches/{batch_id}")
def get_batch_details(batch_id: str):
    """Get import batch details"""
    import_service = ImportService()
    batch = import_service.get_batch_status(batch_id)

    if not batch:
        raise HTTPException(status_code=404, detail="Batch no encontrado")

    return {"batch": batch}


@router.get("/batches/{batch_id}/transactions")
def get_batch_transactions(batch_id: str):
    """Get all transactions from an import batch"""
    import_service = ImportService()

    # Check batch exists
    batch = import_service.get_batch_status(batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch no encontrado")

    transactions = import_service.get_batch_transactions(batch_id)

    return {
        "batch_id": batch_id,
        "total": len(transactions),
        "transactions": transactions
    }


@router.get("/batches/{batch_id}/raw")
def get_batch_raw_rows(batch_id: str):
    """Get all raw import rows from a batch (for debugging)"""
    import_service = ImportService()

    # Check batch exists
    batch = import_service.get_batch_status(batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch no encontrado")

    raw_rows = import_service.get_batch_raw_rows(batch_id)

    return {
        "batch_id": batch_id,
        "total": len(raw_rows),
        "raw_rows": raw_rows
    }
