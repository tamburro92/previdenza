"""
===============================================================================
CALCOLO CONTRIBUTI PREVIDENZIALI INPS
===============================================================================
Script per estrarre dati da PDF Estratto Conto Previdenziale INPS,
calcolare i contributi REALI e TEORICI, e generare Excel e JSON.

Uso:
    python contributi_inps.py <percorso_pdf> [--output-dir <cartella>]

Esempio:
    python contributi_inps.py certificazione.pdf
    python contributi_inps.py certificazione.pdf --output-dir ./risultati

Output:
    - contributi_estratti.json  (dati grezzi estratti dal PDF)
    - contributi_previdenziali.xlsx (calcolo REALE e TEORICO per anno)

Requisiti:
    pip install pdfplumber openpyxl
===============================================================================
"""

import pdfplumber
import json
import re
import sys
import os
import math
import argparse
from collections import defaultdict
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side


# =============================================================================
# ESTRAZIONE PDF
# =============================================================================

class EstrattorePDF:
    """Classe per estrarre i dati contributivi da PDF INPS"""
    
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.dati = {
            "regime_generale": [],
            "spettacolo": [],
            "metadata": {
                "file": pdf_path,
                "codice_fiscale": None
            }
        }
    
    def estrai(self):
        """Estrae tutti i dati dal PDF"""
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                self._estrai_metadata(page, page_num)
                self._estrai_tabelle(page)
        
        return self.dati
    
    def _estrai_metadata(self, page, page_num):
        """Estrae metadata dalla prima pagina"""
        if page_num == 0:
            text = page.extract_text()
            cf_match = re.search(r'([A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z])', text)
            if cf_match:
                self.dati["metadata"]["codice_fiscale"] = cf_match.group(1)
    
    def _estrai_tabelle(self, page):
        """Estrae le tabelle dalla pagina"""
        tables = page.extract_tables()
        
        for table in tables:
            if not table or len(table) < 3:
                continue
            
            header = table[0] if table[0] else []
            header_str = ' '.join([str(h) for h in header if h])
            data_rows = table[2:] if len(table) > 2 else []
            
            for row in data_rows:
                self._processa_riga(row, header_str)
    
    def _processa_riga(self, row, header_str):
        """Processa una singola riga della tabella"""
        if not row or not row[0]:
            return
        
        dal = row[0]
        al = row[1]
        tipo = row[2]
        
        # Verifica data valida
        if not re.match(r'\d{2}/\d{2}/\d{4}', str(dal)):
            return
        
        # Regime Generale (settimane)
        if 'sett.' in str(row[3]) or row[3] == 'sett.':
            self._processa_regime_generale(row, dal, al, tipo)
        
        # Spettacolo (giorni)
        elif 'Giorni' in header_str or 'P.A.L.S.' in str(tipo) or 'Malattia' in str(tipo):
            self._processa_spettacolo(row, dal, al, tipo)
    
    def _processa_regime_generale(self, row, dal, al, tipo):
        """Processa record Regime Generale"""
        settimane = None
        for val in row[3:]:
            if val and re.match(r'^\d+$', str(val)):
                settimane = int(val)
                break
        
        if settimane:
            record = {
                "dal": dal,
                "al": al,
                "tipo": tipo,
                "settimane": settimane,
                "unita": "settimane"
            }
            self._aggiungi_retribuzione(record, row)
            self.dati["regime_generale"].append(record)
    
    def _processa_spettacolo(self, row, dal, al, tipo):
        """Processa record Lavoratori Spettacolo"""
        giorni = None
        gruppo = None
        codice_qualifica = None
        retribuzione = None
        
        # Giorni in posizione 3
        if row[3] and str(row[3]).strip():
            try:
                giorni = int(row[3])
            except:
                pass
        
        # Retribuzione in posizione 4
        if len(row) > 4 and row[4]:
            retribuzione = row[4]
        
        # Gruppo in posizione 6
        if len(row) > 6 and row[6]:
            try:
                gruppo = int(row[6])
            except:
                pass
        
        # Codice qualifica in posizione 7
        if len(row) > 7 and row[7]:
            codice_qualifica = str(row[7]).replace('\n', '')
        
        record = {
            "dal": dal,
            "al": al,
            "tipo": tipo,
            "giorni": giorni,
            "unita": "giorni"
        }
        
        if gruppo:
            record["gruppo"] = gruppo
        if codice_qualifica:
            record["codice_qualifica"] = codice_qualifica
        if retribuzione:
            record["retribuzione"] = retribuzione
        
        self.dati["spettacolo"].append(record)
    
    def _aggiungi_retribuzione(self, record, row):
        """Aggiunge la retribuzione al record se presente"""
        for val in row:
            if val and re.match(r'[\d.,]+$', str(val).replace('.', '').replace(',', '')):
                try:
                    ret = float(str(val).replace('.', '').replace(',', '.'))
                    if ret > 100:
                        record["retribuzione"] = val
                        break
                except:
                    pass


# =============================================================================
# CALCOLO CONTRIBUTI
# =============================================================================

class CalcolatoreContributi:
    """Classe per calcolare i contributi REALI e TEORICI"""
    
    def __init__(self, dati_estratti):
        self.dati = dati_estratti
        self.reale_per_anno = defaultdict(int)
        self.teorico_per_anno = defaultdict(int)
        self.anno_min = None
        self.anno_max = None
    
    def calcola(self):
        """Esegue tutti i calcoli"""
        self._calcola_regime_generale()
        self._calcola_spettacolo()
        self._determina_range_anni()
        
        return {
            "reale": dict(self.reale_per_anno),
            "teorico": dict(self.teorico_per_anno),
            "anno_min": self.anno_min,
            "anno_max": self.anno_max
        }
    
    def _parse_data(self, data_str):
        """Converte stringa data in (anno, mese, giorno)"""
        giorno, mese, anno = map(int, data_str.split('/'))
        return anno, mese, giorno
    
    def _conta_mesi(self, dal, al):
        """Conta i mesi tra due date (arrotondato per eccesso)"""
        y1, m1, _ = self._parse_data(dal)
        y2, m2, _ = self._parse_data(al)
        return (y2 - y1) * 12 + (m2 - m1) + 1
    
    def _calcola_regime_generale(self):
        """Calcola contributi Regime Generale"""
        for record in self.dati["regime_generale"]:
            anno = self._parse_data(record["dal"])[0]
            settimane = record["settimane"]
            
            # REALE: settimane * 6
            giorni_reali = settimane * 6
            self.reale_per_anno[anno] += giorni_reali
            
            # TEORICO: mesi * 26
            mesi = self._conta_mesi(record["dal"], record["al"])
            giorni_teorici = mesi * 26
            self.teorico_per_anno[anno] += giorni_teorici
    
    def _calcola_spettacolo(self):
        """Calcola contributi Lavoratori Spettacolo"""
        for record in self.dati["spettacolo"]:
            anno, mese, _ = self._parse_data(record["dal"])
            giorni = record.get("giorni")
            gruppo = record.get("gruppo")
            
            # REALE: giorni diretti (se presenti)
            if giorni:
                self.reale_per_anno[anno] += giorni
            
            # TEORICO: solo per record con giorni (no malattia)
            if giorni and gruppo:
                mesi = self._conta_mesi(record["dal"], record["al"])
                giorni_teorici = self._calcola_teorico_spettacolo(anno, mese, mesi, gruppo)
                self.teorico_per_anno[anno] += giorni_teorici
    
    def _calcola_teorico_spettacolo(self, anno, mese_inizio, mesi, gruppo):
        """
        Calcola giorni teorici per Spettacolo in base alle regole:
        - Fino al 1992: Gruppo 1 = 60 gg/anno, Gruppo 2 = 180 gg/anno
        - 1993 - luglio 1997: Gruppo 1 = 120 gg/anno, Gruppo 2 = 260 gg/anno
        - Da agosto 1997 (tempo indeterminato): 312 gg/anno per tutti
        """
        # Fino al 1992 compreso
        if anno <= 1992:
            if gruppo == 1:
                giorni_anno = 60
            else:
                giorni_anno = 180
        
        # Dal 1993 al 31 luglio 1997
        elif anno < 1997 or (anno == 1997 and mese_inizio < 8):
            if gruppo == 1:
                giorni_anno = 120
            else:
                giorni_anno = 260
        
        # Dal 1 agosto 1997 in poi (tempo indeterminato)
        else:
            giorni_anno = 312
        
        return math.ceil((giorni_anno / 12) * mesi)
    
    def _determina_range_anni(self):
        """Determina anno minimo e massimo dai dati"""
        tutti_anni = set(self.reale_per_anno.keys()) | set(self.teorico_per_anno.keys())
        if tutti_anni:
            self.anno_min = min(tutti_anni)
            self.anno_max = max(tutti_anni)


# =============================================================================
# GENERAZIONE EXCEL
# =============================================================================

class GeneratoreExcel:
    """Classe per generare il file Excel con i risultati"""
    
    def __init__(self, risultati_calcolo):
        self.risultati = risultati_calcolo
        self.wb = Workbook()
        self.ws = self.wb.active
        self.ws.title = "Contributi Previdenziali"
    
    def genera(self, output_path):
        """Genera il file Excel"""
        self._applica_stili()
        self._crea_headers()
        self._popola_dati()
        self._aggiungi_totali()
        self._imposta_larghezza_colonne()
        self.wb.save(output_path)
    
    def _applica_stili(self):
        """Definisce gli stili"""
        self.header_font = Font(bold=True, color="FFFFFF")
        self.header_fill = PatternFill("solid", fgColor="4472C4")
        self.border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        self.center = Alignment(horizontal='center')
    
    def _crea_headers(self):
        """Crea le intestazioni"""
        headers = ["Anno", "Giorni REALI", "", "Anno", "Giorni TEORICI"]
        for col, header in enumerate(headers, 1):
            cell = self.ws.cell(row=1, column=col, value=header)
            if header:
                cell.font = self.header_font
                cell.fill = self.header_fill
                cell.alignment = self.center
                cell.border = self.border
    
    def _popola_dati(self):
        """Popola i dati per ogni anno"""
        anno_min = self.risultati["anno_min"]
        anno_max = self.risultati["anno_max"]
        
        if not anno_min or not anno_max:
            return
        
        for i, anno in enumerate(range(anno_min, anno_max + 1), 2):
            reale = self.risultati["reale"].get(anno, 0)
            teorico = self.risultati["teorico"].get(anno, 0)
            
            # Colonne REALI
            self.ws.cell(row=i, column=1, value=anno).border = self.border
            self.ws.cell(row=i, column=1).alignment = self.center
            self.ws.cell(row=i, column=2, value=reale).border = self.border
            self.ws.cell(row=i, column=2).alignment = self.center
            
            # Colonne TEORICI
            self.ws.cell(row=i, column=4, value=anno).border = self.border
            self.ws.cell(row=i, column=4).alignment = self.center
            self.ws.cell(row=i, column=5, value=teorico).border = self.border
            self.ws.cell(row=i, column=5).alignment = self.center
    
    def _aggiungi_totali(self):
        """Aggiunge la riga dei totali"""
        anno_min = self.risultati["anno_min"]
        anno_max = self.risultati["anno_max"]
        
        if not anno_min or not anno_max:
            return
        
        num_anni = anno_max - anno_min + 1
        last_row = num_anni + 2
        
        # Totale REALE
        self.ws.cell(row=last_row, column=1, value="TOTALE").font = Font(bold=True)
        self.ws.cell(row=last_row, column=1).border = self.border
        self.ws.cell(row=last_row, column=2, value=f"=SUM(B2:B{last_row-1})").font = Font(bold=True)
        self.ws.cell(row=last_row, column=2).border = self.border
        self.ws.cell(row=last_row, column=2).alignment = self.center
        
        # Totale TEORICO
        self.ws.cell(row=last_row, column=4, value="TOTALE").font = Font(bold=True)
        self.ws.cell(row=last_row, column=4).border = self.border
        self.ws.cell(row=last_row, column=5, value=f"=SUM(E2:E{last_row-1})").font = Font(bold=True)
        self.ws.cell(row=last_row, column=5).border = self.border
        self.ws.cell(row=last_row, column=5).alignment = self.center
    
    def _imposta_larghezza_colonne(self):
        """Imposta la larghezza delle colonne"""
        self.ws.column_dimensions['A'].width = 12
        self.ws.column_dimensions['B'].width = 15
        self.ws.column_dimensions['C'].width = 5
        self.ws.column_dimensions['D'].width = 12
        self.ws.column_dimensions['E'].width = 18


# =============================================================================
# MAIN
# =============================================================================

def main():
    # Parser argomenti
    parser = argparse.ArgumentParser(
        description="Estrae e calcola contributi previdenziali da PDF INPS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempio:
    python contributi_inps.py certificazione.pdf
    python contributi_inps.py certificazione.pdf --output-dir ./risultati
        """
    )
    parser.add_argument("pdf", help="Percorso del file PDF INPS")
    parser.add_argument("--output-dir", "-o", default=".", help="Cartella di output (default: corrente)")
    
    args = parser.parse_args()
    
    # Verifica esistenza PDF
    if not os.path.exists(args.pdf):
        print(f"Errore: File non trovato: {args.pdf}")
        sys.exit(1)
    
    # Crea cartella output se non esiste
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    # Percorsi output
    json_path = os.path.join(args.output_dir, "contributi_estratti.json")
    excel_path = os.path.join(args.output_dir, "contributi_previdenziali.xlsx")
    
    print("=" * 60)
    print("CALCOLO CONTRIBUTI PREVIDENZIALI INPS")
    print("=" * 60)
    
    # 1. Estrazione PDF
    print(f"\n[1/3] Estrazione dati da: {args.pdf}")
    estrattore = EstrattorePDF(args.pdf)
    dati = estrattore.estrai()
    
    print(f"      - Regime generale: {len(dati['regime_generale'])} record")
    print(f"      - Spettacolo: {len(dati['spettacolo'])} record")
    
    # 2. Salvataggio JSON
    print(f"\n[2/3] Salvataggio JSON: {json_path}")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(dati, f, indent=2, ensure_ascii=False)
    
    # 3. Calcolo contributi
    print(f"\n[3/3] Calcolo contributi e generazione Excel: {excel_path}")
    calcolatore = CalcolatoreContributi(dati)
    risultati = calcolatore.calcola()
    
    # 4. Generazione Excel
    generatore = GeneratoreExcel(risultati)
    generatore.genera(excel_path)
    
    # Riepilogo
    totale_reale = sum(risultati["reale"].values())
    totale_teorico = sum(risultati["teorico"].values())
    num_anni = risultati["anno_max"] - risultati["anno_min"] + 1 if risultati["anno_min"] else 0
    
    print("\n" + "=" * 60)
    print("RIEPILOGO")
    print("=" * 60)
    print(f"Anni elaborati:      {num_anni} ({risultati['anno_min']} - {risultati['anno_max']})")
    print(f"Totale giorni REALI: {totale_reale}")
    print(f"Totale giorni TEORICI: {totale_teorico}")
    print(f"\nFile generati:")
    print(f"  - {json_path}")
    print(f"  - {excel_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()