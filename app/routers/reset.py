"""
Reset router - Reset all data
"""
from fastapi import APIRouter
from typing import Dict, Any

import storage

router = APIRouter()


@router.post("/reset-all")
async def reset_all_data() -> Dict[str, Any]:
    """
    Reset all data in the database.

    This will:
    - Clear all transactions
    - Clear all import batches
    - Clear all import history
    - Clear all validated weeks
    - Preserve the _metadata structure

    Returns:
        JSON with success confirmation
    """
    storage.reset_all_data()

    return {
        "success": True,
        "message": "All data has been reset successfully"
    }
