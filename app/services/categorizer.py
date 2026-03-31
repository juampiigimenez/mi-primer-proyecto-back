"""
Automatic transaction categorization based on keywords and patterns
"""
import re
from typing import Tuple, Optional


class TransactionCategorizer:
    """
    Automatic categorization for personal finance transactions
    """

    # Category rules: (category_name, keywords, min_confidence)
    # Updated with specific MercadoPago merchant patterns
    CATEGORY_RULES = [
        # Groceries - supermercados
        ('groceries', [
            'carrefour', 'coto', 'jumbo', 'dia', 'disco', 'vea', 'changomas',
            'supermercado', 'super', 'market', 'walmart', 'makro'
        ], 0.90),

        # Transporte - uber, cabify, taxi, sube
        ('transporte', [
            'uber', 'cabify', 'taxi', 'sube', 'didi', 'tren', 'colectivo',
            'peaje', 'toll', 'metrovias', 'trenes', 'subte', 'transporte'
        ], 0.90),

        # Comida - delivery y restaurantes
        ('comida', [
            'pedidosya', 'pedidos ya', 'rappi', 'cafe', 'restaurant', 'burger',
            'mc', 'mostaza', 'starbucks', 'havanna', 'freddo', 'grido',
            'subway', 'wendys', 'pizza', 'parrilla', 'sushi', 'comida',
            'bar', 'resto', 'delivery', 'glovo', 'uber eats'
        ], 0.85),

        # Compras online - mercadolibre, amazon
        ('compras_online', [
            'mercadolibre', 'mercado libre', 'ml', 'amazon', 'ebay',
            'aliexpress', 'tiendamia'
        ], 0.90),

        # Servicios - personal, movistar, claro, internet
        ('servicios', [
            'personal', 'movistar', 'claro', 'tuenti', 'internet', 'wifi',
            'fibertel', 'speedy', 'telecom', 'iplan', 'servicio'
        ], 0.90),

        # Suscripciones - netflix, spotify, youtube, google
        ('suscripciones', [
            'netflix', 'spotify', 'youtube premium', 'youtube', 'google one',
            'google', 'icloud', 'openai', 'chatgpt', 'claude', 'amazon prime',
            'disney', 'hbo', 'flow', 'telecentro', 'directv', 'suscripción',
            'suscripcion', 'subscription', 'mensualidad'
        ], 0.90),

        # Finanzas - binance, belo, ripio, lemon
        ('finanzas', [
            'binance', 'belo', 'ripio', 'lemon', 'buenbit', 'satoshitango',
            'broker', 'invertir', 'cedear', 'crypto', 'fci', 'fondo común',
            'fondo comun', 'plazo fijo', 'investment', 'inversión', 'inversion'
        ], 0.90),

        # Fuel
        ('fuel', [
            'ypf', 'shell', 'axion', 'estacion', 'combustible', 'nafta',
            'gasoil', 'gas oil', 'gnc', 'fuel', 'petrol'
        ], 0.95),

        # Shopping (general)
        ('shopping', [
            'tienda', 'shop', 'adidas', 'nike', 'zara', 'h&m', 'forever',
            'falabella', 'ripley', 'ropa', 'clothing'
        ], 0.75),

        # Health
        ('health', [
            'hospital', 'clinica', 'clínica', 'médico', 'medico', 'consulta',
            'osde', 'swiss medical', 'galeno', 'medicina prepaga', 'salud'
        ], 0.85),

        # Pharmacy
        ('pharmacy', [
            'farmacia', 'farmacity', 'pharmacy', 'farmacias del', 'cruz',
            'medicamento', 'medicine'
        ], 0.90),

        # Entertainment
        ('entertainment', [
            'cine', 'cinema', 'event', 'tickets', 'ticketek',
            'gaming', 'steam', 'playstation', 'xbox', 'nintendo', 'teatro',
            'recital', 'show', 'entretenimiento'
        ], 0.85),

        # Utilities
        ('utilities', [
            'edenor', 'edesur', 'metrogas', 'aysa', 'agua', 'luz', 'gas',
            'electricidad', 'aguas', 'camuzzi', 'litoral gas', 'absa'
        ], 0.95),

        # Rent
        ('rent', [
            'alquiler', 'renta', 'landlord', 'inmobiliaria', 'rent'
        ], 0.90),

        # Education
        ('education', [
            'curso', 'udemy', 'coursera', 'universidad', 'clase', 'colegio',
            'escuela', 'educación', 'educacion', 'capacitacion', 'training'
        ], 0.85),

        # Salary
        ('salary', [
            'sueldo', 'salario', 'payroll', 'haberes', 'salary', 'nómina',
            'nomina', 'remuneración', 'remuneracion'
        ], 0.95),

        # Savings
        ('savings', [
            'ahorro', 'savings', 'reserva', 'fondo propio', 'cuenta ahorro'
        ], 0.85),

        # Credit card payment
        ('credit_card_payment', [
            'pago tarjeta', 'tarjeta galicia', 'visa galicia', 'mastercard galicia',
            'pago tc', 'resumen tarjeta', 'credit card payment', 'pago resumen'
        ], 0.90),

        # Taxes
        ('taxes', [
            'impuesto', 'tax', 'arba', 'afip', 'monotributo', 'iva', 'ganancias',
            'bienes personales', 'municipal', 'patente', 'abm'
        ], 0.90),

        # Transfer (internal)
        ('transfer', [
            'transferencia propia', 'transferencia entre cuentas', 'movimiento',
            'internal transfer'
        ], 0.80),

        # Refund
        ('refund', [
            'devolución', 'devolucion', 'refund', 'reintegro', 'reversal'
        ], 0.95),
    ]

    def categorize(
        self,
        merchant_normalized: str = None,
        description: str = None,
        payment_method: str = None,
        transaction_type_str: str = None,
    ) -> Tuple[Optional[str], float, Optional[str]]:
        """
        Categorize transaction based on available data

        Args:
            merchant_normalized: Normalized merchant name
            description: Transaction description
            payment_method: Payment method
            transaction_type_str: Transaction type as string

        Returns:
            (category_id, confidence, reason)
        """
        # Combine all text for matching
        search_text = " ".join([
            merchant_normalized or "",
            description or "",
            payment_method or "",
            transaction_type_str or "",
        ]).lower()

        if not search_text.strip():
            return ('uncategorized', 0.0, 'No data to categorize')

        # Try to match against rules
        best_match = None
        best_confidence = 0.0
        best_reason = None

        for category, keywords, base_confidence in self.CATEGORY_RULES:
            for keyword in keywords:
                if keyword in search_text:
                    # Calculate match quality
                    # Exact match in merchant = higher confidence
                    if merchant_normalized and keyword in merchant_normalized.lower():
                        confidence = min(base_confidence + 0.05, 1.0)
                        reason = f"Matched '{keyword}' in merchant"
                    else:
                        confidence = base_confidence
                        reason = f"Matched '{keyword}' in description"

                    if confidence > best_confidence:
                        best_match = category
                        best_confidence = confidence
                        best_reason = reason

        if best_match:
            return (best_match, best_confidence, best_reason)

        # No match found
        return ('uncategorized', 0.0, 'No category match found')

    def get_category_display_name(self, category_id: str) -> str:
        """Get human-readable category name"""
        display_names = {
            'groceries': 'Supermercado',
            'transporte': 'Transporte',
            'comida': 'Comida (Restaurantes y Delivery)',
            'compras_online': 'Compras Online',
            'servicios': 'Servicios (Internet/Teléfono)',
            'suscripciones': 'Suscripciones',
            'finanzas': 'Finanzas (Inversiones y Crypto)',
            'fuel': 'Combustible',
            'shopping': 'Compras',
            'health': 'Salud',
            'pharmacy': 'Farmacia',
            'entertainment': 'Entretenimiento',
            'utilities': 'Servicios Públicos',
            'rent': 'Alquiler',
            'education': 'Educación',
            'salary': 'Salario',
            'transfer': 'Transferencia',
            'refund': 'Devolución',
            'savings': 'Ahorro',
            'credit_card_payment': 'Pago de Tarjeta',
            'taxes': 'Impuestos',
            'uncategorized': 'Sin Categorizar',
        }
        return display_names.get(category_id, category_id.replace('_', ' ').title())
