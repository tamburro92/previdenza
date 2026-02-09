# Calcolo Contributi Previdenziali INPS

## Obiettivo

Dato un documento con l'estratto previdenziale INPS, costruire un foglio Excel con:
- **Colonne REALI**: Anno + Giorni contributivi effettivamente versati
- **Colonne TEORICHE**: Anno + Giorni contributivi teorici + Mesi + Anni e Mesi Cumulativi

Gli anni devono essere raggruppati (non ripetuti) e vanno mostrati tutti gli anni dal primo all'ultimo, inserendo 0 dove non ci sono contributi.

**Obiettivo finale**: Estendere il calcolo fino a raggiungere l'obiettivo contributivo basato sul sesso:
- **Donna**: 41 anni e 10 mesi (502 mesi)
- **Uomo**: 42 anni e 10 mesi (514 mesi)

Il sesso viene decodificato automaticamente dal codice fiscale.

---

## Struttura del Documento INPS

Il documento può contenere due regimi:

1. **Regime Generale** - contributi espressi in **settimane**
2. **Lavoratori dello Spettacolo e Sportivi Professionisti** - contributi espressi in **giorni**

---

## Regole per il Calcolo REALE

### 1. Regime Generale
I contributi sono in settimane, quindi:
```
giorni_reali = settimane × 6
```

### 2. Lavoratori dello Spettacolo
I contributi sono già in giorni, usare il valore diretto.

### 3. Cap massimo annuo
Se i giorni reali di un anno superano 312, vanno troncati a 312.

### 4. Altri casi
Non procedere.

---

## Regole per il Calcolo TEORICO

### 1. Regime Generale
- 1 anno = 312 giorni
- 1 mese = 26 giorni
- Prendere i mesi lavorati, arrotondare per eccesso, moltiplicare per 26

```
giorni_teorici = mesi_lavorati × 26
```

### 2. Lavoratori dello Spettacolo e Sportivi Professionisti

Il calcolo varia in base al **Gruppo** e all'**anno**:

#### Fino al 1992 (incluso)
| Gruppo | Giorni/Anno |
|--------|-------------|
| 1      | 60          |
| 2      | 180         |

#### Dal 1993 al 31 luglio 1997
| Gruppo | Giorni/Anno |
|--------|-------------|
| 1      | 120         |
| 2      | 260         |

#### Dal 1° agosto 1997 in poi

**Tempo determinato:**
| Gruppo | Giorni/Anno |
|--------|-------------|
| 1      | 120         |
| 2      | 260         |

**Tempo indeterminato:**
| Gruppo | Giorni/Anno |
|--------|-------------|
| Tutti  | 312         |

**Nota**: Dal 1° agosto 1997, il calcolo dipende dal tipo di contratto. Se il lavoratore è a tempo indeterminato, si considera sempre 312 giorni/anno indipendentemente dal gruppo. Se è a tempo determinato, si usano le regole del periodo 1993-1997.

Per periodi parziali, calcolare proporzionalmente ai mesi:
```
giorni_teorici = (giorni_anno / 12) × mesi_lavorati
```

---

## Note Importanti

1. **Malattia/Infortunio/Maternità/Congedi**: I giorni vanno contati nel REALE ma NON nel TEORICO (sono già compresi nel periodo lavorativo principale). Nel calcolo TEORICO contano solo i record con **gruppo** (P.A.L.S. Obbligatoria)

2. **Record senza gruppo** (es. P.A.L.S. Serv. Militare): I giorni reali vengono copiati anche nel teorico (regola regime generale)

3. **Anno 1997**: È un anno di transizione. Calcolare proporzionalmente:
   - Gen-Lug (7 mesi): regole 1993-1997 (Gruppo 1 = 120, Gruppo 2 = 260)
   - Ago-Dic (5 mesi): nuove regole (dipende da tempo ind/det)
   - Esempio Gruppo 2 tempo indeterminato: (260 × 7 + 312 × 5) / 12 = 3380 / 12 = 281.67 → **282** (arrotonda)
   - Esempio Gruppo 2 tempo determinato: (260 × 7 + 260 × 5) / 12 = 3120 / 12 = **260**

4. **Ultimo anno lavorato**: Sempre completato a 12 mesi nel TEORICO (anche se ha lavorato solo parte dell'anno)

5. **Anni senza contributi**: Inserire 0 (non omettere l'anno)

6. **Mesi sovrapposti**: Quando ci sono più record nello stesso anno con periodi sovrapposti, i mesi vengono unificati (merge) per evitare di contare più di 12 mesi per anno

7. **Gruppi**:
   - Gruppo 1: Artisti
   - Gruppo 2: Impiegati / Maestranze

8. **Codici qualifica comuni**:
   - 110: Gruppo tecnici
   - 113: Tecnici del montaggio, del suono e sound designer
   - 201: Impiegati amministrativi e tecnici

---

## Esempio

### Input (dal documento INPS)

**Regime Ordinario:**
- 01/09/1981 - 31/12/1981: 17 settimane
- 01/01/1982 - 31/12/1982: 14 settimane

**Lavoratori dello Spettacolo:**
- 01/09/1987 - 31/12/1987: 90 giorni, Gruppo 2

### Output Excel

| Anno | Giorni REALI | | Anno | Giorni TEORICI | Mesi | Anni e Mesi Cumulativi |
|------|--------------|--|------|----------------|------|------------------------|
| 1981 | 102          | | 1981 | 104            | 4    | 0a 4m                  |
| 1982 | 84           | | 1982 | 78             | 3    | 0a 7m                  |
| ...  | ...          | | ...  | ...            | ...  | ...                    |
| 1987 | 90           | | 1987 | 60             | 4    | 1a 3m                  |
| ...  | ...          | | ...  | ...            | ...  | ...                    |
| 2024 | 0            | | 2024 | 312            | 12   | 42a 10m                |
| TOTALE | XXXX       | | TOTALE | XXXXX        | 514  | 42a 10m                |

### Spiegazione calcoli:

**REALE 1981**: 17 settimane × 6 = 102 giorni
**TEORICO 1981**: 4 mesi (set-dic) × 26 = 104 giorni

**REALE 1987**: 90 giorni (già in giorni)
**TEORICO 1987**: Gruppo 2, anno ≤1992 → 180 gg/anno → (180/12) × 4 mesi = 60 giorni

**Anni futuri**: Gli anni dopo l'ultimo lavorato vengono estesi fino a raggiungere l'obiettivo (41a 10m per donne, 42a 10m per uomini), usando l'ultimo regime (Generale o Spettacolo con relativo gruppo).

---

## Decodifica Sesso dal Codice Fiscale

Il codice fiscale italiano contiene il giorno di nascita nelle posizioni 9-10:
- Se il giorno <= 40: **Uomo**
- Se il giorno > 40: **Donna** (al giorno reale viene aggiunto 40)

Esempio:
- `RSSMRA80A01H501Z` - giorno = 01 -> Uomo
- `CNSRLA68P52H501X` - giorno = 52 -> Donna (52 - 40 = 12)

---

## Struttura Progetto

```
previdenza/
├── CLAUDE.md
├── requirements.txt
├── previdenza/
│   ├── __init__.py
│   ├── __main__.py
│   ├── estrattore.py
│   ├── calcolatore.py
│   ├── generatore.py
│   ├── core.py
│   ├── cli.py
│   └── gui.py
```

### Uso

```bash
# Avvia GUI
python -m previdenza

# Tempo determinato (default)
python -m previdenza <nome_file.pdf>

# Sempre tempo indeterminato
python -m previdenza <nome_file.pdf> -ti

# Tempo indeterminato da una data specifica
python -m previdenza <nome_file.pdf> -ti DD/MM/YYYY
```

**Parametro `-ti` (tempo indeterminato):**
- Non specificato: sempre tempo determinato
- `-ti` senza data: sempre tempo indeterminato
- `-ti DD/MM/YYYY`: tempo indeterminato da quella data in poi

### Output

I file di output vengono salvati nella **stessa cartella del PDF di input**:
- `{Cognome} {Nome}.json` - dati grezzi estratti dal PDF
- `{Cognome} {Nome}.xlsx` - calcolo finale con estensione all'obiettivo

Se il nome non viene trovato, viene usato il codice fiscale come fallback.
