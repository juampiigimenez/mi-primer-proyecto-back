"""
Week validation router - Validate weeks for immutability
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
from datetime import datetime

import storage

router = APIRouter()


class ValidateWeekRequest(BaseModel):
    """Request body for week validation"""
    year: int
    week_number: int


class ValidatedWeek(BaseModel):
    """Response model for validated week"""
    year: int
    week_number: int
    validated_at: str
    validated_by: str = "system"


@router.post("/validate")
async def validate_week(request: ValidateWeekRequest) -> Dict[str, Any]:
    """
    Validate a week to make it immutable.

    Once a week is validated, transactions from that week cannot be edited or deleted.

    Args:
        request: ValidateWeekRequest with year and week_number

    Returns:
        JSON with validation confirmation

    Raises:
        HTTPException: If week is already validated
    """
    year = request.year
    week_number = request.week_number

    # Check if already validated
    if storage.is_week_validated(year, week_number):
        raise HTTPException(
            status_code=400,
            detail=f"Week {week_number} of {year} is already validated"
        )

    # Validate the week
    validated_at = storage.validate_week(year, week_number)

    return {
        "success": True,
        "message": f"Week {week_number} of {year} has been validated",
        "validated_week": {
            "year": year,
            "week_number": week_number,
            "validated_at": validated_at,
            "validated_by": "system"
        }
    }


@router.get("/validated")
async def get_validated_weeks() -> Dict[str, Any]:
    """
    Get list of all validated weeks.

    Returns:
        JSON with list of validated weeks, ordered by year and week_number
    """
    validated_weeks = storage.get_validated_weeks()

    # Sort by year and week_number
    validated_weeks.sort(key=lambda w: (w['year'], w['week_number']))

    return {
        "success": True,
        "validated_weeks": validated_weeks
    }


@router.get("/validated/{year}/{week_number}")
async def check_week_validated(year: int, week_number: int) -> Dict[str, Any]:
    """
    Check if a specific week is validated.

    Args:
        year: Year to check
        week_number: Week number to check

    Returns:
        JSON with validation status
    """
    is_validated = storage.is_week_validated(year, week_number)

    return {
        "success": True,
        "year": year,
        "week_number": week_number,
        "is_validated": is_validated
    }
