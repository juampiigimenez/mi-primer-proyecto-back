"""
Script de prueba para verificar las correcciones del importador
"""
from pathlib import Path
from app.models.enums import SourceType
from app.services.importer_simple import MercadoPagoImporterSimple

def test_importador():
    print("=" * 80)
    print("TEST: Importador de Mercado Pago - Verificación de Correcciones")
    print("=" * 80)

    # Crear importador
    importer = MercadoPagoImporterSimple()

    # Importar archivo de ejemplo
    file_path = Path("example_mercadopago.csv")

    if not file_path.exists():
        print("ERROR: No se encuentra example_mercadopago.csv")
        return

    print(f"\n1. Importando archivo: {file_path}")
    result = importer.import_file(
        file_path=file_path,
        source_type=SourceType.MERCADOPAGO_CSV
    )

    print("\n2. Resultado de importación:")
    print(f"   - Total filas: {result['batch']['total_rows']}")
    print(f"   - Procesadas: {result['batch']['processed_rows']}")
    print(f"   - Duplicadas: {result['batch']['duplicated_rows']}")
    print(f"   - Fallidas: {result['batch']['failed_rows']}")

    # Obtener transacciones del batch
    batch_id = result['batch']['id']
    from app.repositories import get_db
    db = get_db()
    batch = db.data['import_batches'][batch_id]
    transactions = batch.get('transactions', [])

    print(f"\n3. Análisis de transacciones procesadas ({len(transactions)} total):")

    ingresos = [tx for tx in transactions if tx['transaction_type'] == 'ingreso']
    gastos = [tx for tx in transactions if tx['transaction_type'] == 'gasto']

    print(f"\n   INGRESOS ({len(ingresos)}):")
    for tx in ingresos:
        print(f"   - {tx['description'][:40]:40} | ${tx['amount']:10.2f} ARS | Real: ${tx['real_amount']:10.2f}")
        if 'all_columns' in tx:
            payment_method_type = tx.get('payment_method_type', 'N/A')
            print(f"     Método: {payment_method_type} | SOURCE_ID: {tx.get('source_id', 'N/A')}")

    print(f"\n   GASTOS ({len(gastos)}):")
    for tx in gastos:
        print(f"   - {tx['description'][:40]:40} | ${tx['amount']:10.2f} ARS | Real: ${tx['real_amount']:10.2f}")
        if 'all_columns' in tx:
            payment_method_type = tx.get('payment_method_type', 'N/A')
            print(f"     Método: {payment_method_type} | SOURCE_ID: {tx.get('source_id', 'N/A')}")

    print("\n4. Verificaciones:")

    # Verificación 1: No hay duplicados en el mismo archivo
    source_ids = [tx.get('source_id') for tx in transactions if tx.get('source_id')]
    duplicados = len(source_ids) - len(set(source_ids))
    print(f"   ✓ Duplicados en archivo: {duplicados} (debe ser 0)")

    # Verificación 2: Clasificación por REAL_AMOUNT
    clasificacion_correcta = True
    for tx in transactions:
        if tx['real_amount'] > 0 and tx['transaction_type'] != 'ingreso':
            clasificacion_correcta = False
            print(f"   ✗ ERROR: REAL_AMOUNT positivo pero tipo {tx['transaction_type']}")
        if tx['real_amount'] < 0 and tx['transaction_type'] != 'gasto':
            clasificacion_correcta = False
            print(f"   ✗ ERROR: REAL_AMOUNT negativo pero tipo {tx['transaction_type']}")

    if clasificacion_correcta:
        print(f"   ✓ Clasificación por REAL_AMOUNT: Correcta")

    # Verificación 3: Excepción credit_card
    # Buscar si hay algún ingreso con payment_method_type = credit_card
    ingresos_credit_card = [
        tx for tx in ingresos
        if tx.get('payment_method_type', '').lower() == 'credit'
    ]

    if len(ingresos_credit_card) == 0:
        print(f"   ✓ Excepción credit_card: Correcta (no hay ingresos con tarjeta de crédito)")
    else:
        print(f"   ✗ ERROR: Se encontraron {len(ingresos_credit_card)} ingresos con credit_card")
        for tx in ingresos_credit_card:
            print(f"      - {tx['description']} | ${tx['amount']}")

    # Verificación 4: Moneda en ARS
    no_ars = [tx for tx in transactions if tx.get('currency') != 'ARS']
    if len(no_ars) == 0:
        print(f"   ✓ Moneda en ARS: Todas las transacciones están en ARS")
    else:
        print(f"   ✗ ERROR: {len(no_ars)} transacciones no están en ARS")

    # Verificación 5: Todas las columnas originales
    tienen_all_columns = [tx for tx in transactions if 'all_columns' in tx]
    if len(tienen_all_columns) == len(transactions):
        print(f"   ✓ Columnas originales: Todas las transacciones tienen 'all_columns'")
        # Verificar que hay datos en all_columns
        ejemplo = transactions[0]['all_columns']
        print(f"     Ejemplo: {len(ejemplo)} columnas conservadas")
    else:
        print(f"   ✗ ERROR: Solo {len(tienen_all_columns)}/{len(transactions)} tienen 'all_columns'")

    # Verificación 6: Sin estado "pendiente"
    pendientes = [tx for tx in transactions if tx.get('status') == 'pendiente']
    if len(pendientes) == 0:
        print(f"   ✓ Estado: Ninguna transacción está 'pendiente'")
    else:
        print(f"   ✗ ERROR: {len(pendientes)} transacciones están 'pendiente'")

    print("\n5. Resumen:")
    total_ingresos = sum(tx['amount'] for tx in ingresos)
    total_gastos = sum(tx['amount'] for tx in gastos)
    print(f"   - Total Ingresos: ${total_ingresos:,.2f} ARS")
    print(f"   - Total Gastos: ${total_gastos:,.2f} ARS")
    print(f"   - Balance: ${(total_ingresos - total_gastos):,.2f} ARS")

    print("\n" + "=" * 80)
    print("TEST COMPLETADO")
    print("=" * 80)

if __name__ == "__main__":
    test_importador()
