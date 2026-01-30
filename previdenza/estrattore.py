"""
Estrazione dati contributivi da PDF INPS
"""

import pdfplumber
import re


class EstrattorePDF:
    """Classe per estrarre i dati contributivi da PDF INPS"""

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.dati = {
            "regime_generale": [],
            "spettacolo": [],
            "metadata": {
                "file": pdf_path,
                "codice_fiscale": None,
                "cognome": None,
                "nome": None
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

            # Estrai codice fiscale
            cf_match = re.search(r'([A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z])', text)
            if cf_match:
                self.dati["metadata"]["codice_fiscale"] = cf_match.group(1)

            # Estrai cognome e nome da "Estratto conto di COGNOME NOME CODICEFISCALE"
            nome_match = re.search(r'Estratto\s+conto\s+di\s+([A-Z][A-Z\s]+?)\s+([A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z])', text)
            if nome_match:
                nome_completo = nome_match.group(1).strip()
                parti = nome_completo.split()
                if len(parti) >= 2:
                    self.dati["metadata"]["cognome"] = parti[0]
                    self.dati["metadata"]["nome"] = ' '.join(parti[1:])

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
