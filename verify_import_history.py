#!/usr/bin/env python3
"""
Verification script for ImportHistory model
This script tests that the model can be imported and instantiated correctly.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from datetime import datetime
from app.models.import_history import ImportHistory

def verify_model():
    """Verify ImportHistory model works correctly"""
    print("Testing ImportHistory model...")

    try:
        # Test model instantiation
        history = ImportHistory(
            id="hist-abc123",
            filename="settlement-x-2024-04-18.csv",
            uploaded_at=datetime(2024, 4, 18, 14, 25, 0),
            confirmed_at=datetime(2024, 4, 18, 14, 30, 0),
            batch_id="batch-xyz789",
            status="confirmed",
            total_transactions=24,
            total_ingresos=15000.50,
            total_gastos=8500.75,
            week_number=16,
            display_name="Semana 16 - 2024"
        )

        # Verify attributes
        assert history.id == "hist-abc123", "ID mismatch"
        assert history.filename == "settlement-x-2024-04-18.csv", "Filename mismatch"
        assert history.week_number == 16, "Week number mismatch"
        assert history.display_name == "Semana 16 - 2024", "Display name mismatch"
        assert history.total_transactions == 24, "Total transactions mismatch"
        assert history.total_ingresos == 15000.50, "Total ingresos mismatch"
        assert history.total_gastos == 8500.75, "Total gastos mismatch"
        assert history.status == "confirmed", "Status mismatch"

        print("✅ ImportHistory model works correctly!")
        print(f"   - ID: {history.id}")
        print(f"   - Filename: {history.filename}")
        print(f"   - Week: {history.week_number}")
        print(f"   - Display: {history.display_name}")
        print(f"   - Transactions: {history.total_transactions}")
        print(f"   - Ingresos: ${history.total_ingresos:.2f}")
        print(f"   - Gastos: ${history.total_gastos:.2f}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_model()
    sys.exit(0 if success else 1)
