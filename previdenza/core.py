"""
Orchestrazione elaborazione PDF INPS
"""

import os
import json

from .estrattore import EstrattorePDF
from .calcolatore import CalcolatoreContributi, decodifica_sesso_da_cf
from .generatore import GeneratoreExcel


def elabora_pdf(pdf_path, tempo_indeterminato_da=None, salva_json=False):
    """
    Elabora un PDF INPS e genera i file di output.
    I file vengono salvati nella STESSA cartella del PDF di input.

    Args:
        pdf_path: Percorso del file PDF INPS
        tempo_indeterminato_da: None, "sempre", o "DD/MM/YYYY"
        salva_json: Se True, salva anche il file JSON (default: False)

    Returns:
        Dizionario con i risultati e i path dei file generati.
    """
    # Output nella stessa cartella del PDF
    output_dir = os.path.dirname(os.path.abspath(pdf_path))

    # 1. Estrazione PDF
    estrattore = EstrattorePDF(pdf_path)
    dati = estrattore.estrai()

    # Decodifica sesso dal codice fiscale
    codice_fiscale = dati["metadata"].get("codice_fiscale")
    cognome = dati["metadata"].get("cognome")
    nome = dati["metadata"].get("nome")
    sesso = decodifica_sesso_da_cf(codice_fiscale)

    # Nome file basato su Cognome Nome, fallback a codice fiscale
    if cognome and nome:
        nome_file = f"{cognome} {nome}"
    elif codice_fiscale:
        nome_file = codice_fiscale
    else:
        nome_file = os.path.splitext(os.path.basename(pdf_path))[0]

    json_path = os.path.join(output_dir, f"{nome_file}.json")
    excel_path = os.path.join(output_dir, f"{nome_file}.xlsx")

    # 2. Salvataggio JSON (solo se richiesto)
    if salva_json:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(dati, f, indent=2, ensure_ascii=False)

    # 3. Calcolo contributi
    calcolatore = CalcolatoreContributi(dati, sesso=sesso, tempo_indeterminato_da=tempo_indeterminato_da)
    risultati = calcolatore.calcola()

    # 4. Generazione Excel
    generatore = GeneratoreExcel(risultati)
    generatore.genera(excel_path)

    # Riepilogo
    totale_mesi = sum(risultati["mesi"].values())

    return {
        "cognome": cognome,
        "nome": nome,
        "codice_fiscale": codice_fiscale,
        "sesso": sesso,
        "sesso_label": "Donna" if sesso == 'F' else "Uomo" if sesso == 'M' else "Non determinato",
        "totale_reale": sum(risultati["reale"].values()),
        "totale_teorico": sum(risultati["teorico"].values()),
        "totale_mesi": totale_mesi,
        "totale_label": f"{totale_mesi // 12}a {totale_mesi % 12}m",
        "obiettivo_label": risultati.get("obiettivo_label", "42a 10m"),
        "anno_min": risultati["anno_min"],
        "anno_max": risultati["anno_max"],
        "json_path": json_path,
        "excel_path": excel_path,
        "output_dir": output_dir
    }
