"""
Migration script to add new fields to existing transactions:
- categoria: category name (default "Sin categoría")
- week_number: ISO 8601 week number
- year: year the week belongs to
- source: "manual" or "mercadopago"
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.week_calculator import get_week_number, get_week_year
from datetime import datetime
import json
import shutil


def migrate_transactions():
    """Add new fields to all existing transactions"""
    data_file = Path(__file__).parent.parent / 'data' / 'finanzas.json'

    # Check if file exists
    if not data_file.exists():
        print(f"Error: {data_file} not found")
        return

    # Create backup before any modifications
    backup_file = data_file.parent / f'finanzas_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    shutil.copy2(data_file, backup_file)
    print(f"Created backup: {backup_file.name}")

    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    transactions = data.get('transactions', {})
    migrated_count = 0

    for tx_id, tx in transactions.items():
        changed = False

        # Add categoria if missing
        if 'categoria' not in tx:
            tx['categoria'] = 'Sin categoría'
            changed = True

        # Add week_number and year if missing
        if 'week_number' not in tx or 'year' not in tx:
            if 'fecha' in tx:
                try:
                    # Parse fecha (format: YYYY-MM-DD or ISO datetime)
                    if 'T' in tx['fecha']:
                        dt = datetime.fromisoformat(tx['fecha'].replace('Z', '+00:00'))
                    else:
                        dt = datetime.strptime(tx['fecha'], '%Y-%m-%d')

                    d = dt.date()
                    tx['week_number'] = get_week_number(d)
                    tx['year'] = get_week_year(d)
                    changed = True
                except (ValueError, TypeError, AttributeError) as e:
                    print(f"Warning: Could not parse fecha for transaction {tx_id}: {e}")
                    # Set defaults for unparseable dates
                    tx['week_number'] = 0
                    tx['year'] = 0
                    changed = True

        # Add source if missing
        if 'source' not in tx:
            # If it has batch_id, it's from Mercado Pago import
            if 'batch_id' in tx or 'payment_method' in tx:
                tx['source'] = 'mercadopago'
            else:
                tx['source'] = 'manual'
            changed = True

        if changed:
            migrated_count += 1

    # Ensure validated_weeks collection exists
    if 'validated_weeks' not in data:
        data['validated_weeks'] = {}

    # Update metadata
    if '_metadata' not in data:
        data['_metadata'] = {'schema_version': '2.0.0', 'created_at': datetime.utcnow().isoformat()}
    data['_metadata']['last_updated'] = datetime.utcnow().isoformat()

    # Write back to file
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Migration complete: {migrated_count} transactions updated")
    print(f"Total transactions: {len(transactions)}")


if __name__ == '__main__':
    migrate_transactions()
