Sei un esperto di previdenza INPS
Il tuo compito è dato il documento con l'estratto previdenziale costruire un foglio excel in cui sono sono rappresentati per ogni anno lavorativo il valore reale ( cioe i contributi effettivamente versati in giorni) ed il valore teorico che segue regole successive
Alla fine mostra il totale dei giorni sommati negli anni.

Fammi 2 colonne 1 con gli anni (raggruppa i contributi per anno, non devono essere ripetuti gli anni) e la seconda con i contributi giornaliri REALI

Fammi altre 4 colonne 1 con gli anni (raggruppa i contributi per anno, non devono essere ripetuti gli anni) e la seconda con i contributi giornaliri TEORICI
a fianco alla colonne dei contributi TEORICI, aggiungi anche il numero di mesi arrtondati per eccesso di quell'anno
a fianco a questa colonna aggiungi anche un'altra che rappresenta il numero di anni e mesi complessivi degli sommati, basta sommare nelle colonne.
Sempre nella colonna del teorico, continua ad elencare gli anni fino al raggiungimento di 42 anni e 10 mesi contando i mesi e gli anni rimanenti fino all'anno in cui ha lavorato elencando anche i contributi teorici di quell'anno.
Alla fine ricorda che ho bisogno del totale in giorni di contributi teorici di 42 anni e 10 mesi

Nel documento previdenziale, ci sono i diversei "Regimi generali" e "lavoratori dello spettacolo e sportivi professionisti"

Per calcolare il REALE segui queste regole per ogni anno

1- Regime generale
i contributi utili pensione sono esperessi in settimane, quindi devi convertirli in giorni, il calcolo è contributi_settimanli x 6 ( moltiplicare per 6)

2- Lavoratori dello Spettacolo e Sportivi Professionisti
i contributi sono già espressi in giorni

3- Negli altri casi non procedere


---
Per calcolare il TEORICO segui queste regole per ogni anno

1-Regime generale
1 anno equivale 312 giorni, ovvero 1 mese sono 26 giorni
prendi i mesi lavorati dal documento per ogni qnno arrotonda sempre per eccesso e moltiplica per 26

2-Lavoratori dello Spettacolo e Sportivi Professionisti
il calcolo cambia a seconda del gruppo e dell'anno:
- fino al 1992 compreso, se è gruppo 1, 1 anno equivale a 60 giorni, se è gruppo 2 equivale 180 ( ricorda di contare il numero di mesi e moltiplicare o dividere se ha non ha fatto anno intero)
- dal 1993 al 31 luglio 1997, se è gruppo 1, 1 anno = 120 giorni, se gruppo 2, 1 anno = 260 giorni
- dal 1 agosto 1997, se è gruppo 1, 1 anno = 120 giorni, se è gruppo 2, 1 anno è 312
-- in realta se è a tempo inderminato dal 1 agosto 1997 1 anno è sempre 312 indipendemente del gruppo, se è gruppo 2 l'anno è di 260 giorni fin tanto che non diventa a tempo indermintato

---

Esempio
Regime Ordinario
01/09/1981 - 31/12/1981 17 settimane
01/01/1982 - 31/12/1982 14 settimane

Regime Lavoratori dello Spettacolo e Sportivi Professionisti
01/09/1987 - 31/12/1987 90 giorni
01/01/1988 - 31/12/1988 312 giorni

Diventa in excel:

reale	
1981	102
1982	78
1987	90
1988	312

teorico anticipata
1981	104	4	4
1982	78	3	7
1987	60  4	11
1988	180	11	1 anno 10 mesi

