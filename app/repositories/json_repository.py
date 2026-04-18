"""
JSON-based repository with schema versioning and migrations
"""
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Type, TypeVar
from pydantic import BaseModel

from config.settings import DB_FILE, SCHEMA_VERSION, DATA_DIR

T = TypeVar('T', bound=BaseModel)


class JSONDatabase:
    """
    JSON-based database with schema versioning and automatic migrations
    """

    def __init__(self, db_file: Path = DB_FILE):
        self.db_file = db_file
        self.data: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        """Load data from JSON file with migration support"""
        if not self.db_file.exists():
            return self._initialize_schema()

        try:
            with open(self.db_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Check schema version and migrate if needed
            current_version = data.get('_metadata', {}).get('schema_version', '1.0.0')
            if current_version != SCHEMA_VERSION:
                data = self._migrate(data, current_version)

            return data

        except json.JSONDecodeError:
            # Backup corrupted file
            backup_path = self.db_file.with_suffix('.json.backup')
            shutil.copy(self.db_file, backup_path)
            return self._initialize_schema()

    def _initialize_schema(self) -> Dict[str, Any]:
        """Initialize empty database schema"""
        return {
            '_metadata': {
                'schema_version': SCHEMA_VERSION,
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
            },
            'accounts': {},
            'credit_cards': {},
            'categories': {},
            'transactions': {},
            'transaction_import_batches': {},
            'raw_import_rows': {},
            'import_history': {},  # NEW - Track confirmed imports
            'recurring_expenses': {},
            'budgets': {},
            'assets': {},
            'liabilities': {},
            'net_worth_snapshots': {},
            'crypto_wallets': {},
            'crypto_positions': {},
            'processed_source_ids': {},  # Para deduplicación persistente
        }

    def _migrate(self, data: Dict[str, Any], from_version: str) -> Dict[str, Any]:
        """
        Migrate data from old schema to new schema
        """
        print(f"Migrating data from version {from_version} to {SCHEMA_VERSION}")

        # Backup before migration
        backup_path = self.db_file.with_suffix(f'.json.v{from_version}.backup')
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # Migration from v1.0.0 (old simple schema) to v2.0.0
        if from_version == '1.0.0' or 'transacciones' in data:
            data = self._migrate_v1_to_v2(data)

        # Update metadata
        if '_metadata' not in data:
            data['_metadata'] = {}

        data['_metadata']['schema_version'] = SCHEMA_VERSION
        data['_metadata']['migrated_at'] = datetime.now().isoformat()
        data['_metadata']['migrated_from'] = from_version

        self._save(data)
        print(f"Migration completed. Backup saved to {backup_path}")

        return data

    def _migrate_v1_to_v2(self, old_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate from v1.0.0 (simple transactions list) to v2.0.0 (full schema)
        """
        new_data = self._initialize_schema()

        # Migrate old transactions if they exist
        old_transactions = old_data.get('transacciones', [])

        # Create default account for migrated transactions
        default_account_id = 'acc_migrated_default'
        new_data['accounts'][default_account_id] = {
            'id': default_account_id,
            'name': 'Cuenta Principal (Migrada)',
            'account_type': 'cuenta_corriente',
            'currency': 'ARS',
            'balance': 0.0,
            'is_active': True,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
        }

        # Create default category
        default_category_id = 'cat_migrated_default'
        new_data['categories'][default_category_id] = {
            'id': default_category_id,
            'name': 'Sin categoría (Migrado)',
            'is_active': True,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
        }

        # Migrate each transaction
        for idx, old_tx in enumerate(old_transactions, 1):
            tx_id = f"tx_migrated_{idx:06d}"
            tx_type = 'ingreso' if old_tx.get('tipo') == 'ingreso' else 'gasto'

            new_data['transactions'][tx_id] = {
                'id': tx_id,
                'transaction_type': tx_type,
                'amount': old_tx.get('monto', 0),
                'currency': 'ARS',
                'operation_date': old_tx.get('fecha', datetime.now().isoformat()),
                'posting_date': old_tx.get('fecha', datetime.now().isoformat()),
                'description': old_tx.get('descripcion', 'Transacción migrada'),
                'account_id': default_account_id,
                'category_id': default_category_id,
                'source_type': 'manual',
                'status': 'confirmada',
                'tags': ['migrado'],
                'raw_metadata': {
                    'migrated_from_v1': True,
                    'original_data': old_tx
                },
                'created_at': old_tx.get('fecha', datetime.now().isoformat()),
                'updated_at': datetime.now().isoformat(),
            }

        print(f"Migrated {len(old_transactions)} transactions from v1.0.0")

        return new_data

    def _save(self, data: Optional[Dict[str, Any]] = None) -> None:
        """Save data to JSON file"""
        if data is None:
            data = self.data

        # Update last_updated timestamp
        if '_metadata' in data:
            data['_metadata']['last_updated'] = datetime.now().isoformat()

        # Ensure data directory exists
        self.db_file.parent.mkdir(parents=True, exist_ok=True)

        # Write to temp file first, then rename (atomic operation)
        temp_file = self.db_file.with_suffix('.json.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # Rename temp file to actual file
        temp_file.replace(self.db_file)

    def save(self) -> None:
        """Public save method"""
        self._save()

    def get_collection(self, collection_name: str) -> Dict[str, Any]:
        """Get a collection by name"""
        if collection_name not in self.data:
            raise ValueError(f"Collection '{collection_name}' does not exist")
        return self.data[collection_name]

    def add(self, collection_name: str, item_id: str, item: BaseModel) -> None:
        """Add item to collection"""
        collection = self.get_collection(collection_name)
        collection[item_id] = item.model_dump(mode='json')
        self._save()

    def get(self, collection_name: str, item_id: str) -> Optional[Dict[str, Any]]:
        """Get item from collection"""
        collection = self.get_collection(collection_name)
        return collection.get(item_id)

    def get_all(self, collection_name: str) -> List[Dict[str, Any]]:
        """Get all items from collection"""
        collection = self.get_collection(collection_name)
        return list(collection.values())

    def update(self, collection_name: str, item_id: str, updates: Dict[str, Any]) -> None:
        """Update item in collection"""
        collection = self.get_collection(collection_name)
        if item_id not in collection:
            raise ValueError(f"Item '{item_id}' not found in collection '{collection_name}'")

        collection[item_id].update(updates)
        collection[item_id]['updated_at'] = datetime.now().isoformat()
        self._save()

    def delete(self, collection_name: str, item_id: str) -> None:
        """Delete item from collection"""
        collection = self.get_collection(collection_name)
        if item_id in collection:
            del collection[item_id]
            self._save()

    def query(self, collection_name: str, filter_fn) -> List[Dict[str, Any]]:
        """Query collection with filter function"""
        collection = self.get_collection(collection_name)
        return [item for item in collection.values() if filter_fn(item)]


# Singleton instance
_db_instance: Optional[JSONDatabase] = None


def get_db() -> JSONDatabase:
    """Get or create database singleton instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = JSONDatabase()
    return _db_instance
