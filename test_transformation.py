"""
Test script to verify transaction transformation logic.

This tests that imported transactions (English fields) are properly
transformed to the expected schema (Spanish fields).
"""
import json
import os
from datetime import datetime

# Test data: imported transaction format
test_imported_transaction = {
    'transaction_type': 'gasto',
    'amount': 3200.0,
    'description': 'Sin descripción',
    'operation_date': '2025-11-24T15:35:20-03:00',
    'payment_method': 'available_money',
    'payment_method_type': 'account',
    'mercadopago_id': '12345',
    'status': 'approved',
    'source': 'mercadopago'
}

# Test data: manual transaction format
test_manual_transaction = {
    'id': 999,
    'tipo': 'ingreso',
    'monto': 5000.0,
    'descripcion': 'Salario',
    'fecha': '2025-11-25',
    'week_number': 48,
    'year': 2025,
    'source': 'manual'
}

# Expected output format
expected_transformed = {
    'id': 1,
    'tipo': 'gasto',
    'monto': 3200.0,
    'descripcion': 'Sin descripción',
    'fecha': '2025-11-24',
    'week_number': 48,
    'year': 2025,
    'source': 'mercadopago',
    'payment_method': 'available_money',
    'payment_method_type': 'account',
    'mercadopago_id': '12345',
    'status': 'approved'
}

def test_transformation():
    """Test the transformation logic"""
    from storage import _transform_imported_transaction

    # Test imported transaction transformation
    print("Testing imported transaction transformation...")
    result = _transform_imported_transaction('1', test_imported_transaction)

    print("\nInput (imported format):")
    print(json.dumps(test_imported_transaction, indent=2))

    print("\nOutput (expected format):")
    print(json.dumps(result, indent=2))

    # Verify required fields are present
    required_fields = ['id', 'tipo', 'monto', 'descripcion', 'fecha', 'week_number', 'year', 'source']
    missing_fields = [f for f in required_fields if f not in result]

    if missing_fields:
        print(f"\nERROR: Missing required fields: {missing_fields}")
        return False

    # Verify field mappings
    assert result['tipo'] == test_imported_transaction['transaction_type'], "tipo mapping failed"
    assert result['monto'] == test_imported_transaction['amount'], "monto mapping failed"
    assert result['descripcion'] == test_imported_transaction['description'], "descripcion mapping failed"
    assert result['fecha'] == '2025-11-24', "fecha extraction failed"
    assert result['payment_method'] == test_imported_transaction['payment_method'], "payment_method not preserved"

    print("\nAll checks passed!")
    return True

def test_full_read():
    """Test reading transactions from finanzas.json"""
    print("\n\nTesting full leer_transacciones() function...")

    # Check if finanzas.json exists
    data_file = "data/finanzas.json"
    if not os.path.exists(data_file):
        print(f"WARNING: {data_file} not found, skipping full read test")
        return True

    from storage import leer_transacciones

    try:
        transactions = leer_transacciones()
        print(f"\nLoaded {len(transactions)} transactions")

        if transactions:
            print("\nFirst transaction:")
            print(json.dumps(transactions[0], indent=2))

            # Verify all required fields are present
            required_fields = ['id', 'tipo', 'monto', 'descripcion', 'fecha']
            for tx in transactions:
                missing = [f for f in required_fields if f not in tx]
                if missing:
                    print(f"\nERROR: Transaction {tx.get('id')} missing fields: {missing}")
                    return False

        print("\nAll transactions have required fields!")
        return True

    except Exception as e:
        print(f"\nERROR reading transactions: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = True

    # Run tests
    success = test_transformation() and success
    success = test_full_read() and success

    if success:
        print("\n\n=== ALL TESTS PASSED ===")
    else:
        print("\n\n=== TESTS FAILED ===")
        exit(1)
