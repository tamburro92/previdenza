"""
Calcolo contributi previdenziali INPS
"""

from collections import defaultdict


def decodifica_sesso_da_cf(codice_fiscale):
    """
    Decodifica il sesso dal codice fiscale italiano.
    Il giorno di nascita e' nelle posizioni 9-10 (indice 9-11).
    Se il giorno > 40, e' donna (si aggiunge 40 al giorno reale).

    Returns: 'F' per femmina, 'M' per maschio, None se non decodificabile
    """
    if not codice_fiscale or len(codice_fiscale) < 11:
        return None

    try:
        giorno = int(codice_fiscale[9:11])
        if giorno > 40:
            return 'F'  # Donna
        else:
            return 'M'  # Uomo
    except (ValueError, IndexError):
        return None


class CalcolatoreContributi:
    """Classe per calcolare i contributi REALI e TEORICI"""

    # Obiettivi contributivi per sesso
    OBIETTIVO_DONNA = 41 * 12 + 10  # 41 anni e 10 mesi = 502 mesi
    OBIETTIVO_UOMO = 42 * 12 + 10   # 42 anni e 10 mesi = 514 mesi

    def __init__(self, dati_estratti, sesso=None, tempo_indeterminato_da=None):
        self.dati = dati_estratti
        self.sesso = sesso  # 'M' o 'F'
        self.tempo_indeterminato_da = tempo_indeterminato_da  # None, "sempre", o "DD/MM/YYYY"
        self.reale_per_anno = defaultdict(int)
        self.teorico_per_anno = defaultdict(int)
        self.mesi_per_anno = defaultdict(int)  # Mesi teorici per anno
        self.ultimo_regime = None  # Per estensione anni futuri
        self.ultimo_gruppo = None  # Gruppo spettacolo se applicabile
        self.anno_min = None
        self.anno_max = None

        # Determina obiettivo in base al sesso
        if sesso == 'F':
            self.obiettivo_mesi = self.OBIETTIVO_DONNA
            self.obiettivo_label = "41a 10m"
        else:
            self.obiettivo_mesi = self.OBIETTIVO_UOMO
            self.obiettivo_label = "42a 10m"

    def calcola(self):
        """Esegue tutti i calcoli"""
        self._calcola_regime_generale()
        self._calcola_spettacolo()
        self._applica_cap_giorni_reali()
        self._determina_range_anni()
        self._estendi_a_obiettivo()

        return {
            "reale": dict(self.reale_per_anno),
            "teorico": dict(self.teorico_per_anno),
            "mesi": dict(self.mesi_per_anno),
            "anno_min": self.anno_min,
            "anno_max": self.anno_max,
            "sesso": self.sesso,
            "obiettivo_mesi": self.obiettivo_mesi,
            "obiettivo_label": self.obiettivo_label
        }

    def _applica_cap_giorni_reali(self):
        """Applica il cap massimo annuo ai giorni reali (312)"""
        for anno, reale_per_anno in list(self.reale_per_anno.items()):
            if reale_per_anno > 312:
                self.reale_per_anno[anno] = 312

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
            self.mesi_per_anno[anno] += mesi

            self.ultimo_regime = "generale"

    def _calcola_spettacolo(self):
        """Calcola contributi Lavoratori Spettacolo"""
        # Raccogli periodi per anno: con gruppo e senza gruppo separatamente
        periodi_con_gruppo = defaultdict(list)  # anno -> [(mese_inizio, mese_fine, gruppo)]
        periodi_senza_gruppo = defaultdict(list)  # anno -> [(mese_inizio, mese_fine, giorni)]
        giorni_senza_gruppo_per_anno = defaultdict(int)  # anno -> giorni totali (per record senza gruppo)

        for record in self.dati["spettacolo"]:
            anno_inizio, mese_inizio, _ = self._parse_data(record["dal"])
            anno_fine, mese_fine, _ = self._parse_data(record["al"])
            giorni = record.get("giorni")
            gruppo = record.get("gruppo")

            # REALE: somma tutti i giorni (inclusi malattia, maternita', ecc.)
            if giorni:
                self.reale_per_anno[anno_inizio] += giorni

            if gruppo:
                # Record CON gruppo: calcola in base alle regole spettacolo
                if anno_inizio == anno_fine:
                    periodi_con_gruppo[anno_inizio].append((mese_inizio, mese_fine, gruppo))
                else:
                    # Periodo che attraversa anni: spezza per anno
                    periodi_con_gruppo[anno_inizio].append((mese_inizio, 12, gruppo))
                    for anno in range(anno_inizio + 1, anno_fine):
                        periodi_con_gruppo[anno].append((1, 12, gruppo))
                    periodi_con_gruppo[anno_fine].append((1, mese_fine, gruppo))

                self.ultimo_regime = "spettacolo"
                self.ultimo_gruppo = gruppo

            elif giorni:
                # Record SENZA gruppo (es. Servizio Militare): raccogli periodi
                if anno_inizio == anno_fine:
                    periodi_senza_gruppo[anno_inizio].append((mese_inizio, mese_fine))
                    giorni_senza_gruppo_per_anno[anno_inizio] += giorni
                else:
                    # Periodo che attraversa anni: spezza per anno
                    periodi_senza_gruppo[anno_inizio].append((mese_inizio, 12))
                    periodi_senza_gruppo[anno_fine].append((1, mese_fine))
                    # Dividi giorni proporzionalmente (semplificato: tutto al primo anno)
                    giorni_senza_gruppo_per_anno[anno_inizio] += giorni

        # Calcola TEORICO per record CON gruppo (regole spettacolo)
        for anno, periodi in periodi_con_gruppo.items():
            # Unifica i mesi coperti (evita duplicati)
            mesi_coperti = set()
            gruppo_anno = None
            for mese_inizio, mese_fine, gruppo in periodi:
                for m in range(mese_inizio, mese_fine + 1):
                    mesi_coperti.add(m)
                gruppo_anno = gruppo

            # Unifica anche con eventuali periodi senza gruppo dello stesso anno
            if anno in periodi_senza_gruppo:
                for mese_inizio, mese_fine in periodi_senza_gruppo[anno]:
                    for m in range(mese_inizio, mese_fine + 1):
                        mesi_coperti.add(m)
                # Rimuovi da periodi_senza_gruppo perche' gia' conteggiato
                del periodi_senza_gruppo[anno]

            mesi = len(mesi_coperti)
            if mesi > 0 and gruppo_anno:
                giorni_teorici = self._calcola_teorico_spettacolo_con_mesi(anno, mesi_coperti, gruppo_anno)
                self.teorico_per_anno[anno] += giorni_teorici
                self.mesi_per_anno[anno] += mesi

        # Calcola TEORICO per record SENZA gruppo rimasti (non sovrapposti con gruppo)
        # Es. Servizio Militare: giorni reali = giorni teorici
        for anno, periodi in periodi_senza_gruppo.items():
            mesi_coperti = set()
            for mese_inizio, mese_fine in periodi:
                for m in range(mese_inizio, mese_fine + 1):
                    mesi_coperti.add(m)

            mesi = len(mesi_coperti)
            if mesi > 0:
                # Usa i giorni reali come teorici
                self.teorico_per_anno[anno] += giorni_senza_gruppo_per_anno[anno]
                self.mesi_per_anno[anno] += mesi

    def _conta_mesi_per_contratto(self, anno, mesi_coperti):
        """
        Conta quanti mesi sono a tempo determinato e quanti a tempo indeterminato.
        Restituisce (mesi_determinato, mesi_indeterminato).
        """
        if self.tempo_indeterminato_da is None:
            return len(mesi_coperti), 0  # Tutti tempo determinato
        if self.tempo_indeterminato_da == "sempre":
            return 0, len(mesi_coperti)  # Tutti tempo indeterminato

        # Trova il mese di passaggio a tempo indeterminato
        _, m_ti, a_ti = map(int, self.tempo_indeterminato_da.split('/'))

        if anno < a_ti:
            return len(mesi_coperti), 0  # Tutto tempo determinato
        if anno > a_ti:
            return 0, len(mesi_coperti)  # Tutto tempo indeterminato

        # anno == a_ti: conta i mesi prima e dopo la data
        mesi_det = len([m for m in mesi_coperti if m < m_ti])
        mesi_indet = len([m for m in mesi_coperti if m >= m_ti])
        return mesi_det, mesi_indet

    def _calcola_teorico_spettacolo_con_mesi(self, anno, mesi_coperti, gruppo):
        """
        Calcola giorni teorici per Spettacolo considerando i mesi effettivi.

        Regole:
        - Fino al 1992: Gruppo 1 = 60 gg/anno, Gruppo 2 = 180 gg/anno
        - 1993 - luglio 1997: Gruppo 1 = 120 gg/anno, Gruppo 2 = 260 gg/anno
        - Dal 1 agosto 1997 in poi:
          - Tempo determinato: Gruppo 1 = 120 gg/anno, Gruppo 2 = 260 gg/anno
          - Tempo indeterminato: sempre 312 gg/anno (indipendente dal gruppo)
        """
        giorni_det = 120 if gruppo == 1 else 260  # Giorni/anno tempo determinato
        giorni_indet = 312  # Giorni/anno tempo indeterminato

        if anno <= 1992:
            giorni_anno = 60 if gruppo == 1 else 180
            return round((giorni_anno / 12) * len(mesi_coperti))

        if anno >= 1993 and anno < 1997:
            return round((giorni_det / 12) * len(mesi_coperti))

        if anno == 1997:
            # Anno di transizione: Gen-Lug regole vecchie, Ago-Dic nuove regole
            mesi_prima_agosto = [m for m in mesi_coperti if m <= 7]
            mesi_da_agosto = [m for m in mesi_coperti if m >= 8]

            # Prima di agosto: sempre regole 1993-1997 (tempo determinato)
            totale_prima = (giorni_det / 12) * len(mesi_prima_agosto)

            # Da agosto: dipende dal tipo contratto
            mesi_det, mesi_indet = self._conta_mesi_per_contratto(anno, mesi_da_agosto)
            totale_dopo = (giorni_det / 12) * mesi_det + (giorni_indet / 12) * mesi_indet

            return round(totale_prima + totale_dopo)

        # anno >= 1998: calcola direttamente senza iterare
        mesi_det, mesi_indet = self._conta_mesi_per_contratto(anno, mesi_coperti)
        return round((giorni_det / 12) * mesi_det + (giorni_indet / 12) * mesi_indet)

    def _calcola_teorico_spettacolo(self, anno, mese_inizio, mesi, gruppo):
        """
        Versione per estensione anni futuri.
        Usa le regole post-1997 con gestione tempo indeterminato.
        """
        mesi_coperti = set(range(mese_inizio, mese_inizio + mesi))
        return self._calcola_teorico_spettacolo_con_mesi(anno, mesi_coperti, gruppo)

    def _determina_range_anni(self):
        """Determina anno minimo e massimo dai dati"""
        tutti_anni = set(self.reale_per_anno.keys()) | set(self.teorico_per_anno.keys())
        if tutti_anni:
            self.anno_min = min(tutti_anni)
            self.anno_max = max(tutti_anni)

    def _estendi_a_obiettivo(self):
        """Estende il calcolo fino a raggiungere l'obiettivo contributivo (basato sul sesso)"""
        # Prima: completa l'ultimo anno lavorato a 12 mesi
        self._completa_ultimo_anno()

        # Calcola mesi gia' accumulati
        mesi_accumulati = sum(self.mesi_per_anno.values())

        if mesi_accumulati >= self.obiettivo_mesi:
            return  # Gia' raggiunto obiettivo

        mesi_mancanti = self.obiettivo_mesi - mesi_accumulati
        anno_corrente = self.anno_max + 1

        while mesi_mancanti > 0:
            mesi_anno = min(12, mesi_mancanti)
            self.mesi_per_anno[anno_corrente] = mesi_anno

            # Calcola giorni teorici in base all'ultimo regime
            if self.ultimo_regime == "generale":
                giorni_teorici = mesi_anno * 26
            else:  # spettacolo
                giorni_teorici = self._calcola_teorico_spettacolo(
                    anno_corrente, 1, mesi_anno, self.ultimo_gruppo or 2
                )

            self.teorico_per_anno[anno_corrente] = giorni_teorici
            self.reale_per_anno[anno_corrente] = 0  # Nessun contributo reale

            mesi_mancanti -= mesi_anno
            anno_corrente += 1

        self.anno_max = anno_corrente - 1

    def _completa_ultimo_anno(self):
        """Completa l'ultimo anno lavorato a 12 mesi nel TEORICO"""
        if not self.anno_max:
            return

        mesi_ultimo_anno = self.mesi_per_anno.get(self.anno_max, 0)
        if mesi_ultimo_anno > 0 and mesi_ultimo_anno < 12:
            # Completa a 12 mesi
            self.mesi_per_anno[self.anno_max] = 12

            # Ricalcola giorni teorici per l'anno completo (tutti i 12 mesi)
            if self.ultimo_regime == "generale":
                self.teorico_per_anno[self.anno_max] = 12 * 26  # 312
            else:  # spettacolo
                gruppo = self.ultimo_gruppo or 2
                mesi_completi = set(range(1, 13))  # tutti i 12 mesi
                self.teorico_per_anno[self.anno_max] = self._calcola_teorico_spettacolo_con_mesi(
                    self.anno_max, mesi_completi, gruppo
                )
