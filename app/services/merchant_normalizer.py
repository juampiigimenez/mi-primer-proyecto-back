"""
Merchant name normalization for better categorization and deduplication
"""
import re
from typing import Optional


class MerchantNormalizer:
    """
    Normalizes merchant names for better matching and categorization
    """

    # Common merchant patterns and their normalized forms
    MERCHANT_PATTERNS = [
        # Supermarkets
        (r'carrefour\s*(express|market|maxi)?.*', 'carrefour'),
        (r'coto.*', 'coto'),
        (r'jumbo.*', 'jumbo'),
        (r'dia.*', 'dia'),
        (r'disco.*', 'disco'),
        (r'vea.*', 'vea'),

        # Food delivery
        (r'pedidos\s*ya.*', 'pedidosya'),
        (r'rappi.*', 'rappi'),
        (r'uber\s*eats.*', 'uber eats'),
        (r'glovo.*', 'glovo'),

        # Restaurants
        (r'mc\s*donald.*', 'mcdonalds'),
        (r'burger\s*king.*', 'burger king'),
        (r'mostaza.*', 'mostaza'),
        (r'starbucks.*', 'starbucks'),
        (r'subway.*', 'subway'),

        # Transport
        (r'uber\s*\*.*', 'uber'),
        (r'cabify.*', 'cabify'),
        (r'didi.*', 'didi'),

        # Fuel
        (r'ypf.*', 'ypf'),
        (r'shell.*', 'shell'),
        (r'axion.*', 'axion'),

        # Shopping
        (r'mercado\s*libre.*', 'mercadolibre'),
        (r'meli.*', 'mercadolibre'),
        (r'amazon.*', 'amazon'),

        # Pharmacy
        (r'farmacity.*', 'farmacity'),
        (r'farmacia.*', 'farmacia'),

        # Services
        (r'netflix.*', 'netflix'),
        (r'spotify.*', 'spotify'),
        (r'youtube.*', 'youtube'),
        (r'google\s*one.*', 'google one'),
        (r'icloud.*', 'icloud'),

        # Utilities
        (r'edenor.*', 'edenor'),
        (r'edesur.*', 'edesur'),
        (r'metrogas.*', 'metrogas'),
        (r'aysa.*', 'aysa'),

        # Telecom
        (r'personal.*', 'personal'),
        (r'movistar.*', 'movistar'),
        (r'claro.*', 'claro'),
        (r'fibertel.*', 'fibertel'),

        # Crypto
        (r'binance.*', 'binance'),
        (r'buenbit.*', 'buenbit'),
        (r'ripio.*', 'ripio'),
        (r'lemon.*', 'lemon'),
    ]

    # Noise patterns to remove
    NOISE_PATTERNS = [
        r'\s+\d+$',  # Trailing numbers (e.g., "CARREFOUR 1234")
        r'\s+srl$',  # Company suffixes
        r'\s+sa$',
        r'\s+s\.a\.$',
        r'\s+ltda$',
        r'\s+inc$',
        r'\s+\*\w+$',  # Trailing asterisk codes (e.g., "UBER *TRIP")
        r'\s+-\s*$',  # Trailing dashes
        r'^\*+\s*',  # Leading asterisks
    ]

    def normalize(self, raw_merchant: str) -> Optional[str]:
        """
        Normalize merchant name

        Args:
            raw_merchant: Raw merchant name from source

        Returns:
            Normalized merchant name or None if empty
        """
        if not raw_merchant or not raw_merchant.strip():
            return None

        # Start with lowercase
        normalized = raw_merchant.lower().strip()

        # Remove noise patterns
        for pattern in self.NOISE_PATTERNS:
            normalized = re.sub(pattern, '', normalized, flags=re.IGNORECASE)

        # Trim again
        normalized = normalized.strip()

        # Try to match against known patterns
        for pattern, canonical_name in self.MERCHANT_PATTERNS:
            if re.match(pattern, normalized, flags=re.IGNORECASE):
                return canonical_name

        # If no pattern matched, clean up generic noise
        # Remove excessive whitespace
        normalized = re.sub(r'\s+', ' ', normalized)

        # Remove special characters but keep spaces and hyphens
        normalized = re.sub(r'[^\w\s\-áéíóúñü]', '', normalized, flags=re.IGNORECASE)

        # Trim to reasonable length
        if len(normalized) > 50:
            normalized = normalized[:50].strip()

        return normalized if normalized else None

    def extract_from_description(self, description: str) -> Optional[str]:
        """
        Extract merchant from description using common separators

        Args:
            description: Full transaction description

        Returns:
            Extracted merchant name or None
        """
        if not description:
            return None

        # Common separators in MercadoPago descriptions
        separators = [' - ', ' / ', ' | ', '  ']

        for sep in separators:
            if sep in description:
                parts = description.split(sep)
                # Take first non-empty part
                for part in parts:
                    if part.strip():
                        return self.normalize(part.strip())

        # No separator found, use first N characters
        return self.normalize(description[:50])
