# Schema Mismatch Fix Summary

## Problem
The imported transactions from MercadoPago used English field names (`transaction_type`, `amount`, `description`, `operation_date`), but the frontend and Pydantic models expected Spanish field names (`tipo`, `monto`, `descripcion`, `fecha`).

This caused:
1. KeyError: 'tipo' in calcular_balance() line 91
2. ResponseValidationError: 240 validation errors in GET /transacciones

## Root Cause
The `leer_transacciones()` function in storage.py was returning raw imported transaction objects without field transformation.

## Solution Implemented

### File: c:\proyectos\finanzas-back\storage.py

#### 1. Modified leer_transacciones()
- Added detection for imported vs manual transactions (checks for 'transaction_type' field)
- Calls transformation function for imported transactions
- Returns manual transactions as-is (already in correct format)

#### 2. Added _transform_imported_transaction()
New helper function that transforms imported transactions:

**Field Mappings:**
- `transaction_type` -> `tipo`
- `amount` or `real_amount` -> `monto`
- `description` -> `descripcion`
- `operation_date` -> `fecha` (extracts date part only, format: YYYY-MM-DD)
- Transaction key -> `id` (parsed as int)

**Calculated Fields:**
- `week_number` (calculated from fecha)
- `year` (calculated from fecha)
- `source` (defaults to 'mercadopago')

**Preserved Optional Fields:**
- `categoria`
- `payment_method`
- `payment_method_type`
- `mercadopago_id`
- `status`

### Example Transformation

**Input (imported format):**
```json
{
  "transaction_type": "gasto",
  "amount": 3200.0,
  "description": "Sin descripción",
  "operation_date": "2025-11-24T15:35:20-03:00",
  "payment_method": "available_money",
  "payment_method_type": "account"
}
```

**Output (expected format):**
```json
{
  "id": 1,
  "tipo": "gasto",
  "monto": 3200.0,
  "descripcion": "Sin descripción",
  "fecha": "2025-11-24",
  "week_number": 48,
  "year": 2025,
  "source": "mercadopago",
  "payment_method": "available_money",
  "payment_method_type": "account"
}
```

## Verification Status

### reset_all_data() Verification
Confirmed that `reset_all_data()` includes clearing `import_history` collection (line 389).

The function properly resets:
- `_metadata`
- `transactions`
- `validated_weeks`
- `import_batches`
- `import_history`

## Testing

A test script was created at `c:\proyectos\finanzas-back\test_transformation.py` to verify:
1. Field mapping correctness
2. Date extraction and formatting
3. Week calculation
4. Optional field preservation

## Impact

This fix resolves:
- GET /transacciones endpoint will now return properly formatted transactions
- calcular_balance() will no longer throw KeyError for 'tipo'
- Frontend can successfully consume transaction data
- Both imported (MercadoPago) and manual transactions work correctly

## Notes

- The transformation is transparent - imported transactions in the database keep their original format
- Transformation happens at read time in leer_transacciones()
- Manual transactions added via agregar_transaccion() already use Spanish fields
- The confirm_batch_transactions() endpoint calls agregar_transaccion(), which writes Spanish fields directly
