"""
Test script to verify unified storage system
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

import storage
import json

def test_storage_unified():
    """Test that all storage functions use the unified finanzas.json system"""

    print("=" * 60)
    print("TESTING UNIFIED STORAGE SYSTEM")
    print("=" * 60)

    # Test 1: Read transactions (should read from finanzas.json)
    print("\n1. Testing leer_transacciones()...")
    transactions = storage.leer_transacciones()
    print(f"   Found {len(transactions)} transactions")

    # Test 2: Add new transaction (should write to finanzas.json)
    print("\n2. Testing agregar_transaccion()...")
    new_tx = storage.agregar_transaccion(
        tipo="ingreso",
        monto=999.99,
        descripcion="Test transaction unified storage"
    )
    print(f"   Created transaction ID: {new_tx['id']}")
    print(f"   Week: {new_tx.get('week_number')} Year: {new_tx.get('year')}")
    print(f"   Source: {new_tx.get('source')}")

    # Test 3: Verify transaction is in finanzas.json
    print("\n3. Verifying transaction is in finanzas.json...")
    data = storage.leer_datos()
    tx_key = str(new_tx['id'])
    if tx_key in data['transactions']:
        print(f"   SUCCESS: Transaction {tx_key} found in finanzas.json")
    else:
        print(f"   ERROR: Transaction {tx_key} NOT found in finanzas.json")

    # Test 4: Read transactions again to verify it appears
    print("\n4. Reading transactions again...")
    transactions_after = storage.leer_transacciones()
    print(f"   Found {len(transactions_after)} transactions")

    # Test 5: Calculate balance (should work with unified system)
    print("\n5. Testing calcular_balance()...")
    balance = storage.calcular_balance()
    print(f"   Ingresos: {balance['ingresos']}")
    print(f"   Gastos: {balance['gastos']}")
    print(f"   Balance: {balance['balance']}")

    # Test 6: Update transaction
    print("\n6. Testing update_transaction()...")
    try:
        updated = storage.update_transaction(
            new_tx['id'],
            {'descripcion': 'Updated description for test'}
        )
        print(f"   SUCCESS: Updated transaction {new_tx['id']}")
        print(f"   New description: {updated['descripcion']}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test 7: Check migration function exists
    print("\n7. Checking migration function...")
    migration_stats = storage.migrate_old_data()
    print(f"   Migrated: {migration_stats['migrated']}")
    print(f"   Skipped: {migration_stats['skipped']}")
    print(f"   Errors: {len(migration_stats['errors'])}")
    if migration_stats['errors']:
        for error in migration_stats['errors']:
            print(f"      - {error}")

    # Test 8: Delete test transaction
    print("\n8. Cleaning up test transaction...")
    try:
        storage.delete_transaction(new_tx['id'])
        print(f"   SUCCESS: Deleted transaction {new_tx['id']}")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n" + "=" * 60)
    print("TESTS COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_storage_unified()
