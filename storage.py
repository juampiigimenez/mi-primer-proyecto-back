import json
import os
from typing import List, Dict
from datetime import datetime

FILENAME = "transacciones.json"
DATA_FILE = "data/finanzas.json"

def leer_transacciones() -> List[Dict]:
    """Lee todas las transacciones del archivo JSON (now reads from finanzas.json)"""
    data = leer_datos()

    # Extract transactions from the new system
    transactions_dict = data.get('transactions', {})

    # Convert dict to list and transform to expected schema
    transactions_list = []
    for tx_key, tx in transactions_dict.items():
        # Check if this is an imported transaction that needs transformation
        if 'transaction_type' in tx:
            # Transform imported transaction to expected schema
            transformed = _transform_imported_transaction(tx_key, tx)
            transactions_list.append(transformed)
        else:
            # Already in expected format (manual transaction)
            transactions_list.append(tx)

    # Sort by ID to maintain consistent ordering
    transactions_list.sort(key=lambda x: x.get('id', 0))

    return transactions_list


def _transform_imported_transaction(tx_key: str, tx: Dict) -> Dict:
    """
    Transform imported transaction (English fields) to expected schema (Spanish fields).

    Handles MercadoPago and other imported transactions with English field names.
    """
    from app.utils.week_calculator import get_week_number, get_week_year

    # Extract and transform date
    operation_date = tx.get('operation_date', '')
    if operation_date:
        # Parse ISO datetime and extract date part
        if 'T' in operation_date:
            dt = datetime.fromisoformat(operation_date.replace('Z', '+00:00'))
            fecha = dt.strftime('%Y-%m-%d')
            fecha_date = dt.date()
        else:
            fecha = operation_date
            fecha_date = datetime.strptime(operation_date, '%Y-%m-%d').date()
    else:
        # Fallback to current date
        fecha_date = datetime.now().date()
        fecha = fecha_date.strftime('%Y-%m-%d')

    # Calculate week
    week_number = get_week_number(fecha_date)
    year = get_week_year(fecha_date)

    # Build transformed transaction
    # Extract numeric ID from key (e.g., 'tx_203311db87bd' -> extract from external_id or generate)
    if tx_key.isdigit():
        tx_id = int(tx_key)
    else:
        # For imported transactions with non-numeric keys, use a hash of the key
        import hashlib
        hash_obj = hashlib.md5(tx_key.encode())
        tx_id = int(hash_obj.hexdigest()[:8], 16)  # Use first 8 hex chars as integer

    transformed = {
        'id': tx_id,
        'tipo': tx.get('transaction_type', 'gasto'),
        'monto': tx.get('real_amount') or tx.get('amount', 0.0),
        'descripcion': tx.get('description', 'Sin descripción'),
        'fecha': fecha,
        'week_number': week_number,
        'year': year,
        'source': tx.get('source', 'mercadopago')
    }

    # Add optional fields if present
    if 'categoria' in tx:
        transformed['categoria'] = tx['categoria']

    if 'payment_method' in tx:
        transformed['payment_method'] = tx['payment_method']

    if 'payment_method_type' in tx:
        transformed['payment_method_type'] = tx['payment_method_type']

    if 'mercadopago_id' in tx:
        transformed['mercadopago_id'] = tx['mercadopago_id']

    if 'status' in tx:
        transformed['status'] = tx['status']

    return transformed

def guardar_transacciones(transacciones: List[Dict]) -> None:
    """Guarda las transacciones en el archivo JSON"""
    with open(FILENAME, 'w', encoding='utf-8') as f:
        json.dump(transacciones, f, ensure_ascii=False, indent=2)

def agregar_transaccion(tipo: str, monto: float, descripcion: str, fecha: str = None, source: str = "manual") -> Dict:
    """Agrega una nueva transacción (now writes to finanzas.json)"""
    # Import week calculation utilities
    from app.utils.week_calculator import get_week_number, get_week_year

    # Read current data
    data = leer_datos()

    # Calculate next ID based on max existing ID
    transactions_dict = data.get('transactions', {})
    if transactions_dict:
        max_id = max(int(key) for key in transactions_dict.keys())
        new_id = max_id + 1
    else:
        new_id = 1

    # Get date (use provided fecha or current date)
    if fecha:
        # Parse provided fecha
        if 'T' in fecha:
            dt = datetime.fromisoformat(fecha.replace('Z', '+00:00'))
        else:
            dt = datetime.strptime(fecha, '%Y-%m-%d')
        fecha_date = dt.date()
        fecha_iso = fecha
    else:
        # Use current date
        now = datetime.now()
        fecha_date = now.date()
        fecha_iso = now.isoformat()

    # Calculate week
    week_number = get_week_number(fecha_date)
    year = get_week_year(fecha_date)

    # Create new transaction with all required fields
    nueva_transaccion = {
        "id": new_id,
        "tipo": tipo,
        "monto": monto,
        "descripcion": descripcion,
        "fecha": fecha_iso,
        "week_number": week_number,
        "year": year,
        "source": source
    }

    # Add to transactions dict
    data['transactions'][str(new_id)] = nueva_transaccion

    # Update metadata
    data['_metadata']['last_updated'] = datetime.utcnow().isoformat()

    # Save to finanzas.json
    guardar_datos(data)

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


def leer_datos() -> Dict:
    """Lee el archivo de datos JSON completo"""
    if not os.path.exists(DATA_FILE):
        # Return default structure if file doesn't exist
        return {
            "_metadata": {
                "schema_version": "2.0.0",
                "created_at": datetime.utcnow().isoformat(),
                "last_updated": datetime.utcnow().isoformat()
            },
            "transactions": {},
            "validated_weeks": {}
        }

    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {
            "_metadata": {
                "schema_version": "2.0.0",
                "created_at": datetime.utcnow().isoformat(),
                "last_updated": datetime.utcnow().isoformat()
            },
            "transactions": {},
            "validated_weeks": {}
        }


def guardar_datos(data: Dict) -> None:
    """Guarda el archivo de datos JSON completo"""
    # Ensure directory exists
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def update_transaction(transaction_id: int, updates: dict) -> dict:
    """
    Update a transaction by ID

    Args:
        transaction_id: ID of transaction to update
        updates: Dictionary of fields to update

    Returns:
        Updated transaction object

    Raises:
        ValueError: If transaction not found or validation fails
    """
    data = leer_datos()

    tx_key = str(transaction_id)
    if tx_key not in data['transactions']:
        raise ValueError(f"Transaction {transaction_id} not found")

    transaction = data['transactions'][tx_key]

    # Check source and restrict updates for mercadopago
    if transaction.get('source') == 'mercadopago':
        restricted_fields = ['monto', 'tipo', 'fecha']
        for field in restricted_fields:
            if field in updates:
                raise ValueError(f"Cannot update '{field}' for Mercado Pago transactions")

    # Apply updates
    for key, value in updates.items():
        if key != 'id':  # Don't allow ID changes
            transaction[key] = value

    # Recalculate week if fecha changed
    if 'fecha' in updates:
        from datetime import datetime
        from app.utils.week_calculator import get_week_number, get_week_year

        if 'T' in updates['fecha']:
            dt = datetime.fromisoformat(updates['fecha'].replace('Z', '+00:00'))
        else:
            dt = datetime.strptime(updates['fecha'], '%Y-%m-%d')

        d = dt.date()
        transaction['week_number'] = get_week_number(d)
        transaction['year'] = get_week_year(d)

    # Update metadata
    from datetime import datetime
    data['_metadata']['last_updated'] = datetime.utcnow().isoformat()

    guardar_datos(data)

    return transaction


def delete_transaction(transaction_id: int) -> None:
    """
    Delete a transaction by ID

    Args:
        transaction_id: ID of transaction to delete

    Raises:
        ValueError: If transaction not found
    """
    data = leer_datos()

    tx_key = str(transaction_id)
    if tx_key not in data['transactions']:
        raise ValueError(f"Transaction {transaction_id} not found")

    del data['transactions'][tx_key]

    # Update metadata
    from datetime import datetime
    data['_metadata']['last_updated'] = datetime.utcnow().isoformat()

    guardar_datos(data)


def validate_week(year: int, week_number: int) -> str:
    """
    Validate a week to make it immutable.

    Args:
        year: Year of the week
        week_number: Week number (1-53)

    Returns:
        ISO timestamp of validation

    Raises:
        ValueError: If week is already validated
    """
    data = leer_datos()

    # Ensure validated_weeks collection exists
    if 'validated_weeks' not in data:
        data['validated_weeks'] = {}

    # Create key for this week
    week_key = f"{year}-W{week_number:02d}"

    # Check if already validated
    if week_key in data['validated_weeks']:
        raise ValueError(f"Week {week_number} of {year} is already validated")

    # Add validation record
    validated_at = datetime.utcnow().isoformat()
    data['validated_weeks'][week_key] = {
        "year": year,
        "week_number": week_number,
        "validated_at": validated_at,
        "validated_by": "system"
    }

    # Update metadata
    data['_metadata']['last_updated'] = datetime.utcnow().isoformat()

    guardar_datos(data)

    return validated_at


def get_validated_weeks() -> list:
    """
    Get list of all validated weeks.

    Returns:
        List of validated week objects
    """
    data = leer_datos()

    # Ensure validated_weeks collection exists
    if 'validated_weeks' not in data:
        return []

    # Return list of validated weeks
    return list(data['validated_weeks'].values())


def is_week_validated(year: int, week_number: int) -> bool:
    """
    Check if a week is validated.

    Args:
        year: Year of the week
        week_number: Week number (1-53)

    Returns:
        True if week is validated, False otherwise
    """
    data = leer_datos()

    # Ensure validated_weeks collection exists
    if 'validated_weeks' not in data:
        return False

    # Create key for this week
    week_key = f"{year}-W{week_number:02d}"

    return week_key in data['validated_weeks']


def reset_all_data() -> None:
    """
    Reset all data in the database.

    Clears all collections but preserves the _metadata structure.
    """
    data = {
        "_metadata": {
            "schema_version": "2.0.0",
            "created_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat()
        },
        "transactions": {},
        "validated_weeks": {},
        "import_batches": {},
        "import_history": {}
    }

    guardar_datos(data)


def migrate_old_data() -> Dict:
    """
    Migrate data from old transacciones.json to new finanzas.json system.

    Returns:
        Dict with migration stats: {'migrated': int, 'skipped': int, 'errors': list}
    """
    from app.utils.week_calculator import get_week_number, get_week_year

    stats = {
        'migrated': 0,
        'skipped': 0,
        'errors': []
    }

    # Check if old file exists
    if not os.path.exists(FILENAME):
        return stats

    # Read old transactions
    try:
        with open(FILENAME, 'r', encoding='utf-8') as f:
            old_transactions = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        stats['errors'].append(f"Error reading old file: {str(e)}")
        return stats

    if not old_transactions:
        return stats

    # Read current data
    data = leer_datos()
    transactions_dict = data.get('transactions', {})

    # Migrate each transaction
    for tx in old_transactions:
        tx_id = tx.get('id')
        if not tx_id:
            stats['errors'].append(f"Transaction missing ID: {tx}")
            continue

        # Skip if already exists in new system
        if str(tx_id) in transactions_dict:
            stats['skipped'] += 1
            continue

        try:
            # Parse fecha to calculate week
            fecha_str = tx.get('fecha', '')
            if 'T' in fecha_str:
                dt = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
            else:
                dt = datetime.strptime(fecha_str, '%Y-%m-%d')

            fecha_date = dt.date()
            week_number = get_week_number(fecha_date)
            year = get_week_year(fecha_date)

            # Add missing fields
            migrated_tx = {
                "id": tx_id,
                "tipo": tx.get('tipo'),
                "monto": tx.get('monto'),
                "descripcion": tx.get('descripcion'),
                "fecha": fecha_str,
                "week_number": week_number,
                "year": year,
                "source": "manual"
            }

            # Add to new system
            transactions_dict[str(tx_id)] = migrated_tx
            stats['migrated'] += 1

        except Exception as e:
            stats['errors'].append(f"Error migrating transaction {tx_id}: {str(e)}")
            continue

    # Save migrated data
    if stats['migrated'] > 0:
        data['transactions'] = transactions_dict
        data['_metadata']['last_updated'] = datetime.utcnow().isoformat()
        guardar_datos(data)

        # Backup old file
        backup_file = FILENAME + '.backup'
        import shutil
        shutil.copy2(FILENAME, backup_file)

    return stats
