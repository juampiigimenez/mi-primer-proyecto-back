"""
Quick verification that all imports work correctly
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

def verify_imports():
    """Verify all critical imports work"""

    print("=" * 60)
    print("VERIFYING IMPORTS")
    print("=" * 60)

    errors = []

    # Test 1: Import storage module
    print("\n1. Importing storage module...")
    try:
        import storage
        print("   SUCCESS: storage imported")

        # Check key functions
        functions = ['leer_transacciones', 'agregar_transaccion', 'calcular_balance',
                    'update_transaction', 'delete_transaction', 'migrate_old_data']
        for func in functions:
            if hasattr(storage, func):
                print(f"   - {func}: OK")
            else:
                errors.append(f"storage.{func} not found")
                print(f"   - {func}: MISSING")
    except Exception as e:
        errors.append(f"Failed to import storage: {e}")
        print(f"   ERROR: {e}")

    # Test 2: Import routers
    print("\n2. Importing routers...")
    try:
        from app.routers import imports, transactions, weeks, reset
        print("   SUCCESS: All routers imported")
        print("   - imports: OK")
        print("   - transactions: OK")
        print("   - weeks: OK")
        print("   - reset: OK")
    except Exception as e:
        errors.append(f"Failed to import routers: {e}")
        print(f"   ERROR: {e}")

    # Test 3: Import main app
    print("\n3. Importing main app...")
    try:
        from app.main import app
        print("   SUCCESS: app imported")
    except Exception as e:
        errors.append(f"Failed to import app: {e}")
        print(f"   ERROR: {e}")

    # Test 4: Import week calculator utilities
    print("\n4. Importing week calculator...")
    try:
        from app.utils.week_calculator import get_week_number, get_week_year
        print("   SUCCESS: week_calculator imported")
    except Exception as e:
        errors.append(f"Failed to import week_calculator: {e}")
        print(f"   ERROR: {e}")

    # Summary
    print("\n" + "=" * 60)
    if errors:
        print("VERIFICATION FAILED")
        print("=" * 60)
        for error in errors:
            print(f"ERROR: {error}")
        return False
    else:
        print("VERIFICATION SUCCESSFUL - All imports work correctly")
        print("=" * 60)
        return True

if __name__ == "__main__":
    success = verify_imports()
    sys.exit(0 if success else 1)
