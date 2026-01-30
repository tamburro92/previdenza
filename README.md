# Calcolo Contributi Previdenziali INPS

Estrae dati contributivi da PDF INPS (Regime Generale e Spettacolo), calcola giorni REALI e TEORICI, e proietta il calcolo fino all'obiettivo pensionistico.

## Installazione

```bash
pip install pdfplumber openpyxl
```

## Uso

```bash
# Avvia GUI
python -m previdenza

# CLI - Tempo determinato (default)
python -m previdenza estratto_conto.pdf

# CLI - Tempo indeterminato (sempre)
python -m previdenza estratto_conto.pdf -ti

# CLI - Tempo indeterminato da una data
python -m previdenza estratto_conto.pdf -ti 01/08/2000
```

## Output

I file vengono salvati nella stessa cartella del PDF di input:
- `{Cognome} {Nome}.xlsx` - calcolo contributi
- `{Cognome} {Nome}.json` - dati grezzi (solo CLI)

Il calcolo include:
- **Giorni REALI**: contributi effettivamente versati
- **Giorni TEORICI**: contributi convenzionali
- **Proiezione**: estende fino a 41a 10m (donne) o 42a 10m (uomini)
