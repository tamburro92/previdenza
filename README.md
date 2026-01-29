# Calcolo Contributi Previdenziali INPS

Estrae dati contributivi da PDF INPS (Regime Generale e Spettacolo), calcola giorni REALI e TEORICI, e proietta il calcolo fino all'obiettivo pensionistico.

## Installazione

```bash
pip install pdfplumber openpyxl
```

## Uso

```bash
# Tempo determinato (default)
python contributi_inps.py estratto_conto.pdf

# Tempo indeterminato (sempre)
python contributi_inps.py estratto_conto.pdf -ti

# Tempo indeterminato da una data
python contributi_inps.py estratto_conto.pdf -ti 01/08/2000
```

## Output

I file vengono salvati in `output/` con nome `{Cognome} {Nome}.xlsx` e `.json`:

- **Giorni REALI**: contributi effettivamente versati
- **Giorni TEORICI**: contributi convenzionali (regole spettacolo/generale)
- **Proiezione**: estende fino a 41a 10m (donne) o 42a 10m (uomini)

## Regimi supportati

| Regime | Unità | Conversione |
|--------|-------|-------------|
| Generale | Settimane | 1 sett = 6 giorni |
| Spettacolo | Giorni | Varia per gruppo e periodo |
