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

### 3. Altri casi
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

#### Dal 1° agosto 1997 in poi (tempo indeterminato)
| Gruppo | Giorni/Anno |
|--------|-------------|
| Tutti  | 312         |

**Nota**: Dal 1° agosto 1997, se il lavoratore è a tempo indeterminato, si considera sempre 312 giorni/anno indipendentemente dal gruppo.

Per periodi parziali, calcolare proporzionalmente ai mesi:
```
giorni_teorici = (giorni_anno / 12) × mesi_lavorati
```

---

## Note Importanti

1. **Malattia/Infortunio/Maternità/Congedi**: I giorni vanno contati nel REALE ma NON nel TEORICO (sono già compresi nel periodo lavorativo principale). Nel calcolo TEORICO contano solo i record con **gruppo** (P.A.L.S. Obbligatoria)

2. **Anno 1997**: È un anno di transizione. Calcolare proporzionalmente:
   - Gen-Lug (7 mesi): regole 1993-1997 (Gruppo 1 = 120, Gruppo 2 = 260)
   - Ago-Dic (5 mesi): nuove regole (Gruppo 1 = 120, Gruppo 2 = 312)
   - Esempio Gruppo 2: (260 × 7 / 12) + (312 × 5 / 12) = 151 + 130 = 281 (arrotonda per difetto)

3. **Ultimo anno lavorato**: Sempre completato a 12 mesi nel TEORICO (anche se ha lavorato solo parte dell'anno)

4. **Anni senza contributi**: Inserire 0 (non omettere l'anno)

5. **Gruppi**:
   - Gruppo 1: Artisti
   - Gruppo 2: Impiegati / Maestranze

6. **Codici qualifica comuni**:
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

## Struttura Output

```
previdenza/
├── contributi_inps.py
├── CLAUDE.md
├── output/
│   ├── mario_rossi_estratto.json
│   ├── mario_rossi_contributi.xlsx
│   ├── luigi_bianchi_estratto.json
│   └── luigi_bianchi_contributi.xlsx
```

### Uso

```bash
python contributi_inps.py <nome_file.pdf>
```

I file di output vengono salvati nella cartella `output/` con il nome del PDF come prefisso:
- `{nome}_estratto.json` - dati grezzi estratti dal PDF
- `{nome}_contributi.xlsx` - calcolo finale con estensione a 42a 10m
