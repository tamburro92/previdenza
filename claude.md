# Calcolo Contributi Previdenziali INPS

## Obiettivo

Dato un documento con l'estratto previdenziale INPS, costruire un foglio Excel con:
- **Colonne REALI**: Anno + Giorni contributivi effettivamente versati
- **Colonne TEORICHE**: Anno + Giorni contributivi teorici secondo le regole previdenziali

Gli anni devono essere raggruppati (non ripetuti) e vanno mostrati tutti gli anni dal primo all'ultimo, inserendo 0 dove non ci sono contributi.

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

1. **Malattia/Infortunio**: I periodi di malattia vanno contati nel REALE ma NON nel TEORICO (sono già compresi nel periodo lavorativo principale)

2. **Anno 1997**: È un anno di transizione. Distinguere i periodi prima e dopo il 1° agosto:
   - Prima di agosto: usare le regole 1993-1997
   - Da agosto in poi: usare 312 giorni/anno (tempo indeterminato)

3. **Anni senza contributi**: Inserire 0 (non omettere l'anno)

4. **Gruppi**:
   - Gruppo 1: Artisti
   - Gruppo 2: Impiegati / Maestranze

5. **Codici qualifica comuni**:
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

| Anno | Giorni REALI | | Anno | Giorni TEORICI |
|------|--------------|--|------|----------------|
| 1981 | 102          | | 1981 | 104            |
| 1982 | 84           | | 1982 | 78             |
| ...  | ...          | | ...  | ...            |
| 1987 | 90           | | 1987 | 60             |

### Spiegazione calcoli:

**REALE 1981**: 17 settimane × 6 = 102 giorni
**TEORICO 1981**: 4 mesi (set-dic) × 26 = 104 giorni

**REALE 1987**: 90 giorni (già in giorni)
**TEORICO 1987**: Gruppo 2, anno ≤1992 → 180 gg/anno → (180/12) × 4 mesi = 60 giorni
