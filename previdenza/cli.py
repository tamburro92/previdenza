"""
Interfaccia linea di comando per calcolo contributi INPS
"""

import argparse
import sys
import os
import re

from .core import elabora_pdf


def main():
    """Entry point CLI"""
    parser = argparse.ArgumentParser(
        description="Estrae e calcola contributi previdenziali da PDF INPS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempio:
    python -m previdenza                                       # Avvia GUI
    python -m previdenza certificazione.pdf                    # Tempo determinato
    python -m previdenza certificazione.pdf -ti                # Sempre tempo indeterminato
    python -m previdenza certificazione.pdf -ti 01/08/1997     # Tempo indeterminato dal 1/8/1997
        """
    )
    parser.add_argument("pdf", help="Percorso del file PDF INPS")
    parser.add_argument("-ti", "--tempo-indeterminato", nargs="?", const="sempre",
                        metavar="DD/MM/YYYY",
                        help="Tempo indeterminato: senza data = sempre, con data = da quella data")

    args = parser.parse_args()

    # Parsing tempo indeterminato
    tempo_indeterminato_da = None
    if args.tempo_indeterminato:
        if args.tempo_indeterminato == "sempre":
            tempo_indeterminato_da = "sempre"
        else:
            if not re.match(r'\d{2}/\d{2}/\d{4}', args.tempo_indeterminato):
                print(f"Errore: Formato data non valido: {args.tempo_indeterminato}")
                print("Usare formato DD/MM/YYYY")
                sys.exit(1)
            tempo_indeterminato_da = args.tempo_indeterminato

    # Verifica esistenza PDF
    if not os.path.exists(args.pdf):
        print(f"Errore: File non trovato: {args.pdf}")
        sys.exit(1)

    print("=" * 60)
    print("CALCOLO CONTRIBUTI PREVIDENZIALI INPS")
    print("=" * 60)

    try:
        risultato = elabora_pdf(args.pdf, tempo_indeterminato_da, salva_json=True)

        print("\n" + "=" * 60)
        print("RIEPILOGO")
        print("=" * 60)
        if risultato['cognome'] and risultato['nome']:
            print(f"Cognome e Nome:      {risultato['cognome']} {risultato['nome']}")
        print(f"Codice Fiscale:      {risultato['codice_fiscale']}")
        print(f"Sesso:               {risultato['sesso_label']}")
        print(f"Obiettivo:           {risultato['obiettivo_label']}")
        num_anni = risultato['anno_max'] - risultato['anno_min'] + 1 if risultato['anno_min'] else 0
        print(f"Anni elaborati:      {num_anni} ({risultato['anno_min']} - {risultato['anno_max']})")
        print(f"Totale giorni REALI: {risultato['totale_reale']}")
        print(f"Totale giorni TEORICI: {risultato['totale_teorico']}")
        print(f"Totale mesi teorici: {risultato['totale_mesi']} ({risultato['totale_label']})")
        print(f"\nFile generati:")
        print(f"  - {risultato['json_path']}")
        print(f"  - {risultato['excel_path']}")
        print("=" * 60)

    except Exception as e:
        print(f"Errore: {e}")
        sys.exit(1)
