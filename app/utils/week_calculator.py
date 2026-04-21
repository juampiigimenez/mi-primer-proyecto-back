"""
ISO 8601 week calculation utilities
"""
from datetime import date, timedelta
import re


def get_week_number(d: date) -> int:
    """
    Calculate ISO 8601 week number for a given date.

    ISO 8601 rules:
    - Week starts on Monday
    - Week 1 is the first week with at least 4 days in the new year
    - Equivalently, Week 1 contains the first Thursday of the year

    Args:
        d: Date to calculate week number for

    Returns:
        Week number (1-53)
    """
    # Find Thursday of the week
    thursday = d + timedelta(days=(3 - d.weekday()))

    # Find first Thursday of the year
    year_start = date(thursday.year, 1, 1)
    first_thursday = year_start + timedelta(days=(3 - year_start.weekday()) % 7)

    # Calculate week number
    week_number = 1 + (thursday - first_thursday).days // 7

    return week_number


def get_week_year(d: date) -> int:
    """
    Get the year that the week belongs to.
    This might differ from the date's year for dates near year boundaries.

    Args:
        d: Date to check

    Returns:
        Year number
    """
    # Find Thursday of the week (determines which year the week belongs to)
    thursday = d + timedelta(days=(3 - d.weekday()))
    return thursday.year


def extract_week_from_filename(filename: str) -> tuple[int, int] | None:
    """
    Extract week number and year from Mercado Pago filename.

    Expected format: settlement-x-YYYY-MM-DD.csv

    Args:
        filename: The filename to parse

    Returns:
        Tuple of (year, week_number) or None if parsing fails
    """
    pattern = r'settlement-x-(\d{4})-(\d{2})-(\d{2})\.'
    match = re.search(pattern, filename)

    if not match:
        return None

    try:
        year, month, day = match.groups()
        d = date(int(year), int(month), int(day))
    except (ValueError, AttributeError):
        return None

    week_year = get_week_year(d)
    week_number = get_week_number(d)

    return (week_year, week_number)
