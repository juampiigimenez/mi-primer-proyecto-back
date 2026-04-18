"""
Import router - Upload and manage transaction imports
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime
import tempfile
import shutil
import re
import uuid

from app.models.enums import SourceType
from app.services.importer_simple import MercadoPagoImporterSimple
from app.repositories import get_db

router = APIRouter()


def parse_settlement_filename(filename: str) -> dict:
    """
    Parse settlement filename to extract date and calculate week number.

    Expected format: settlement-x-YYYY-MM-DD.csv

    Args:
        filename: The filename to parse

    Returns:
        dict with keys: date (datetime), week (int), year (int), display_name (str)

    Raises:
        ValueError: If filename format is invalid

    Example:
        >>> parse_settlement_filename("settlement-x-2024-04-18.csv")
        {
            "date": datetime(2024, 4, 18),
            "week": 16,
            "year": 2024,
            "display_name": "Semana 16 - 2024"
        }
    """
    # Regex to extract date: YYYY-MM-DD
    pattern = r'settlement-x-(\d{4})-(\d{2})-(\d{2})'
    match = re.search(pattern, filename)

    if not match:
        raise ValueError(f"Formato de filename inválido: {filename}")

    year_str, month_str, day_str = match.groups()
    year = int(year_str)
    month = int(month_str)
    day = int(day_str)

    # Create datetime object
    date = datetime(year, month, day)

    # Calculate ISO 8601 week number
    iso_calendar = date.isocalendar()
    week_number = iso_calendar[1]  # Returns (year, week, weekday)

    # Create display name
    display_name = f"Semana {week_number} - {year}"

    return {
        "date": date,
        "week": week_number,
        "year": year,
        "display_name": display_name
    }


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
    Confirma un batch importado y pasa las transacciones al dashboard.
    Creates a history record of the confirmed import.

    Los ingresos se registran como ingresos en el dashboard.
    Los egresos se registran como gastos en el dashboard.

    Args:
        batch_id: ID del batch a confirmar

    Returns:
        JSON con resumen de confirmación y history_id
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
    filename = batch.get('filename', 'unknown.csv')
    uploaded_at_str = batch.get('uploaded_at', datetime.now().isoformat())

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

    # Parse filename to get week information
    try:
        parsed = parse_settlement_filename(filename)
        week_number = parsed["week"]
        display_name = parsed["display_name"]
    except ValueError:
        # Fallback for invalid filenames
        week_number = 0
        display_name = f"Importación - {datetime.now().strftime('%d/%m/%Y %H:%M')}"

    # Create import history record
    history_id = f"hist-{str(uuid.uuid4())[:8]}"
    confirmed_at = datetime.now()

    # Initialize import_history collection if it doesn't exist
    if 'import_history' not in db.data:
        db.data['import_history'] = {}

    db.data['import_history'][history_id] = {
        "id": history_id,
        "filename": filename,
        "uploaded_at": uploaded_at_str,
        "confirmed_at": confirmed_at.isoformat(),
        "batch_id": batch_id,
        "status": "confirmed",
        "total_transactions": ingresos_confirmados + gastos_confirmados,
        "total_ingresos": total_ingresos,
        "total_gastos": total_gastos,
        "week_number": week_number,
        "display_name": display_name
    }

    # Marcar el batch como confirmado
    batch['confirmed'] = True
    batch['confirmed_at'] = confirmed_at.isoformat()
    db.save()

    return {
        "success": True,
        "batch_id": batch_id,
        "history_id": history_id,
        "summary": {
            "ingresos_confirmados": ingresos_confirmados,
            "gastos_confirmados": gastos_confirmados,
            "total_ingresos_ars": total_ingresos,
            "total_gastos_ars": total_gastos,
            "total_transacciones": ingresos_confirmados + gastos_confirmados
        }
    }


@router.get("/history")
async def get_import_history() -> Dict[str, Any]:
    """
    Get history of all confirmed import batches.

    Returns:
        JSON with list of import history records, ordered by confirmed_at descending

    Example response:
        {
            "success": true,
            "history": [
                {
                    "id": "hist-abc123",
                    "filename": "settlement-x-2024-04-18.csv",
                    "confirmed_at": "2024-04-18T14:30:00",
                    "display_name": "Semana 16 - 2024",
                    "total_transactions": 24,
                    "total_ingresos": 15000.50,
                    "total_gastos": 8500.75,
                    "status": "confirmed"
                }
            ]
        }
    """
    db = get_db()

    # Get import_history collection (may not exist in old databases)
    history_data = db.data.get('import_history', {})

    # Convert to list of dicts
    history_list = list(history_data.values())

    # Sort by confirmed_at descending (most recent first)
    history_list.sort(
        key=lambda x: x.get('confirmed_at', ''),
        reverse=True
    )

    return {
        "success": True,
        "history": history_list
    }
