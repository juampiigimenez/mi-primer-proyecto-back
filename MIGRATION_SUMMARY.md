# Storage System Unification - Migration Summary

## Overview
Fixed two critical backend issues in the finanzas application:
1. Missing router registrations (weeks, reset)
2. Dual storage system inconsistency

## Changes Made

### 1. Router Registrations Fixed (app/main.py)

#### Changes:
- Added imports for weeks and reset routers (line 20)
- Registered both routers in the application (lines 80-81)
- Added startup event to run data migration automatically (lines 41-49)

#### Result:
All /api/v1/weeks/* and /api/v1/reset/* endpoints now work correctly.

### 2. Storage System Unified (storage.py)

#### Modified Functions:

**leer_transacciones()** (lines 9-22)
- Now reads from data/finanzas.json instead of transacciones.json
- Extracts transactions from data['transactions'] dict
- Converts to list and sorts by ID
- Maintains backward compatibility

**agregar_transaccion()** (lines 29-85)
- Now writes to data/finanzas.json instead of transacciones.json
- Generates ID based on max existing ID + 1
- Automatically calculates week_number and year from date
- Accepts optional fecha parameter to preserve import dates
- Accepts optional source parameter ('manual' or 'mercadopago')
- Adds all required fields: id, tipo, monto, descripcion, fecha, week_number, year, source
- Updates metadata timestamp

**calcular_balance()** (lines 87-99)
- No changes needed - automatically works with new system through leer_transacciones()

**New Function: migrate_old_data()** (lines 327-416)
- Migrates data from old transacciones.json to finanzas.json
- Calculates week_number and year for all old transactions
- Sets source='manual' for migrated transactions
- Creates backup file (transacciones.json.backup)
- Returns migration statistics
- Handles errors gracefully

### 3. Import Confirmation Fixed (app/routers/imports.py)

#### Changes (lines 213-237):
- Now passes operation_date to agregar_transaccion() to preserve original transaction dates
- Sets source='mercadopago' for imported transactions
- Ensures week_number and year are calculated from actual transaction dates

## Data Structure

### Old System (transacciones.json):
```json
[
  {
    "id": 1,
    "tipo": "ingreso",
    "monto": 1500.5,
    "descripcion": "Salario",
    "fecha": "2026-04-18T19:17:37.334457"
  }
]
```

### New System (data/finanzas.json):
```json
{
  "_metadata": {
    "schema_version": "2.0.0",
    "created_at": "...",
    "last_updated": "..."
  },
  "transactions": {
    "1": {
      "id": 1,
      "tipo": "ingreso",
      "monto": 1500.5,
      "descripcion": "Salario",
      "fecha": "2026-04-18T19:17:37.334457",
      "week_number": 16,
      "year": 2026,
      "source": "manual"
    }
  },
  "validated_weeks": {},
  "import_batches": {},
  "import_history": {}
}
```

## Key Features

1. **Automatic Migration**: On application startup, old data is automatically migrated
2. **Data Integrity**: Original transacciones.json is backed up before migration
3. **Week Calculation**: All transactions now have week_number and year fields
4. **Source Tracking**: Transactions are tagged with source ('manual' or 'mercadopago')
5. **Date Preservation**: Import confirmation preserves original transaction dates
6. **Unified System**: All CRUD operations now use finanzas.json consistently

## Testing

Run the test script to verify all changes:
```bash
python test_unified_storage.py
```

## Files Modified

1. c:\proyectos\finanzas-back\app\main.py
2. c:\proyectos\finanzas-back\storage.py
3. c:\proyectos\finanzas-back\app\routers\imports.py

## Files Created

1. c:\proyectos\finanzas-back\test_unified_storage.py
2. c:\proyectos\finanzas-back\MIGRATION_SUMMARY.md

## Backward Compatibility

- GET /transacciones still works (reads from finanzas.json)
- POST /transacciones still works (writes to finanzas.json)
- GET /balance still works (calculates from finanzas.json)
- UPDATE and DELETE operations work on same data as GET

## Status

DONE - Both critical issues have been fixed:
- Router registrations are complete
- Storage system is unified
- Data migration is automatic
- All endpoints use consistent storage
