"""
Seed data for initial setup
Creates default categories, sample accounts, etc.
"""
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.repositories import get_db
from app.models.enums import AccountType, Currency


def seed_categories():
    """Create default category structure"""
    db = get_db()

    categories = [
        # Income categories
        {
            'id': 'cat_income_salary',
            'name': 'Salario',
            'parent_id': None,
            'color': '#10b981',
            'icon': '💰',
            'is_active': True,
        },
        {
            'id': 'cat_income_freelance',
            'name': 'Freelance',
            'parent_id': None,
            'color': '#3b82f6',
            'icon': '💼',
            'is_active': True,
        },
        {
            'id': 'cat_income_investment',
            'name': 'Inversiones',
            'parent_id': None,
            'color': '#8b5cf6',
            'icon': '📈',
            'is_active': True,
        },
        # Fixed expense categories
        {
            'id': 'cat_expense_housing',
            'name': 'Vivienda',
            'parent_id': None,
            'color': '#ef4444',
            'icon': '🏠',
            'is_active': True,
        },
        {
            'id': 'cat_expense_rent',
            'name': 'Alquiler',
            'parent_id': 'cat_expense_housing',
            'color': '#ef4444',
            'icon': '🔑',
            'is_active': True,
        },
        {
            'id': 'cat_expense_utilities',
            'name': 'Servicios',
            'parent_id': 'cat_expense_housing',
            'color': '#f59e0b',
            'icon': '⚡',
            'is_active': True,
        },
        {
            'id': 'cat_expense_internet',
            'name': 'Internet',
            'parent_id': 'cat_expense_utilities',
            'color': '#f59e0b',
            'icon': '🌐',
            'is_active': True,
        },
        # Variable expense categories
        {
            'id': 'cat_expense_food',
            'name': 'Alimentación',
            'parent_id': None,
            'color': '#f97316',
            'icon': '🍽️',
            'is_active': True,
        },
        {
            'id': 'cat_expense_groceries',
            'name': 'Supermercado',
            'parent_id': 'cat_expense_food',
            'color': '#f97316',
            'icon': '🛒',
            'is_active': True,
        },
        {
            'id': 'cat_expense_restaurants',
            'name': 'Restaurantes',
            'parent_id': 'cat_expense_food',
            'color': '#f97316',
            'icon': '🍔',
            'is_active': True,
        },
        {
            'id': 'cat_expense_transport',
            'name': 'Transporte',
            'parent_id': None,
            'color': '#06b6d4',
            'icon': '🚗',
            'is_active': True,
        },
        {
            'id': 'cat_expense_entertainment',
            'name': 'Entretenimiento',
            'parent_id': None,
            'color': '#ec4899',
            'icon': '🎮',
            'is_active': True,
        },
        {
            'id': 'cat_expense_health',
            'name': 'Salud',
            'parent_id': None,
            'color': '#14b8a6',
            'icon': '🏥',
            'is_active': True,
        },
        {
            'id': 'cat_expense_education',
            'name': 'Educación',
            'parent_id': None,
            'color': '#6366f1',
            'icon': '📚',
            'is_active': True,
        },
        {
            'id': 'cat_expense_shopping',
            'name': 'Compras',
            'parent_id': None,
            'color': '#a855f7',
            'icon': '🛍️',
            'is_active': True,
        },
        {
            'id': 'cat_expense_other',
            'name': 'Otros Gastos',
            'parent_id': None,
            'color': '#6b7280',
            'icon': '📦',
            'is_active': True,
        },
    ]

    for cat in categories:
        cat['created_at'] = datetime.now().isoformat()
        cat['updated_at'] = datetime.now().isoformat()
        db.data['categories'][cat['id']] = cat

    db.save()
    print(f"✅ Created {len(categories)} default categories")


def seed_sample_account():
    """Create a sample account"""
    db = get_db()

    account = {
        'id': 'acc_main_checking',
        'name': 'Cuenta Principal',
        'account_type': AccountType.CHECKING.value,
        'currency': Currency.ARS.value,
        'balance': 0.0,
        'bank_name': 'Banco Ejemplo',
        'account_number': '1234',
        'is_active': True,
        'notes': 'Cuenta principal para operaciones diarias',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
    }

    db.data['accounts'][account['id']] = account
    db.save()
    print(f"✅ Created sample account: {account['name']}")


def run_seed():
    """Run all seed functions"""
    print("🌱 Starting seed data creation...\n")

    seed_categories()
    seed_sample_account()

    print("\n✅ Seed data creation completed!")


if __name__ == "__main__":
    run_seed()
