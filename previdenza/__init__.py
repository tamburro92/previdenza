"""
Calcolo Contributi Previdenziali INPS
=====================================

Package per estrarre dati da PDF INPS, calcolare contributi
REALI e TEORICI, e generare file Excel.

Uso:
    python -m previdenza                         # Avvia GUI
    python -m previdenza file.pdf                # CLI tempo determinato
    python -m previdenza file.pdf -ti            # CLI tempo indeterminato
    python -m previdenza file.pdf -ti DD/MM/YYYY # CLI tempo indet. da data
"""

__version__ = "1.0.0"

from .estrattore import EstrattorePDF
from .calcolatore import CalcolatoreContributi, decodifica_sesso_da_cf
from .generatore import GeneratoreExcel
from .core import elabora_pdf

__all__ = [
    "EstrattorePDF",
    "CalcolatoreContributi",
    "GeneratoreExcel",
    "decodifica_sesso_da_cf",
    "elabora_pdf",
]
