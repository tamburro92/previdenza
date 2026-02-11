import unittest

from previdenza.calcolatore import CalcolatoreContributi


def _calcola_senza_estensione(dati, sesso="M"):
    calcolatore = CalcolatoreContributi(dati, sesso=sesso, tempo_indeterminato_da="sempre")
    # Evita estensione a obiettivo per questi test di un sottoinsieme.
    calcolatore.obiettivo_mesi = 0
    return calcolatore.calcola()


class TestRegimeGenerale(unittest.TestCase):
    def test_regime_generale_multi_anno(self):
        dati = {
            "regime_generale": [
                {
                    "dal": "01/11/1981",
                    "al": "31/12/1981",
                    "settimane": 8,
                },
                {
                    "dal": "01/01/1982",
                    "al": "31/03/1982",
                    "settimane": 12,
                },
                {
                    "dal": "01/07/1983",
                    "al": "31/12/1983",
                    "settimane": 10,
                },
            ],
            "spettacolo": [],
        }

        risultati = _calcola_senza_estensione(dati)

        self.assertEqual(risultati["reale"][1981], 48)
        self.assertEqual(risultati["teorico"][1981], 52)
        self.assertEqual(risultati["mesi"][1981], 2)

        self.assertEqual(risultati["reale"][1982], 72)
        self.assertEqual(risultati["teorico"][1982], 78)
        self.assertEqual(risultati["mesi"][1982], 3)

        # Ultimo anno completato a 12 mesi nel teorico
        self.assertEqual(risultati["teorico"][1983], 312)
        self.assertEqual(risultati["mesi"][1983], 12)


class TestRegimeSpettacolo(unittest.TestCase):
    def test_regime_spettacolo_multi_anno(self):
        dati = {
            "regime_generale": [],
            "spettacolo": [
                {
                    "dal": "01/09/1987",
                    "al": "31/12/1987",
                    "giorni": 90,
                    "gruppo": 2,
                },
                {
                    "dal": "01/01/1988",
                    "al": "31/12/1988",
                    "giorni": 312,
                    "gruppo": 2,
                },
            ],
        }

        risultati = _calcola_senza_estensione(dati)

        self.assertEqual(risultati["reale"][1987], 90)
        self.assertEqual(risultati["teorico"][1987], 60)
        self.assertEqual(risultati["mesi"][1987], 4)

        self.assertEqual(risultati["reale"][1988], 312)
        self.assertEqual(risultati["teorico"][1988], 180)
        self.assertEqual(risultati["mesi"][1988], 12)

    def test_regime_spettacolo_sovrapposizioni(self):
        dati = {
            "regime_generale": [],
            "spettacolo": [
                {
                    "dal": "01/01/1990",
                    "al": "30/06/1990",
                    "giorni": 100,
                    "gruppo": 1,
                },
                {
                    "dal": "01/04/1990",
                    "al": "31/12/1990",
                    "giorni": 120,
                    "gruppo": 1,
                },
            ],
        }

        risultati = _calcola_senza_estensione(dati)

        # Mesi unificati (max 12), non sommati.
        self.assertEqual(risultati["mesi"][1990], 12)
        self.assertEqual(risultati["teorico"][1990], 60)
        self.assertEqual(risultati["reale"][1990], 220)


class TestRegimiCombinati(unittest.TestCase):
    def test_regimi_combinati_stesso_anno(self):
        dati = {
            "regime_generale": [
                {
                    "dal": "01/01/1982",
                    "al": "31/03/1982",
                    "settimane": 10,
                },
            ],
            "spettacolo": [
                {
                    "dal": "01/07/1982",
                    "al": "31/12/1982",
                    "giorni": 120,
                    "gruppo": 2,
                },
                {
                    "dal": "01/01/1983",
                    "al": "30/06/1983",
                    "giorni": 130,
                    "gruppo": 2,
                },
            ],
        }

        risultati = _calcola_senza_estensione(dati)

        self.assertEqual(risultati["reale"][1982], 180)
        self.assertEqual(risultati["teorico"][1982], 168)
        self.assertEqual(risultati["mesi"][1982], 9)


class TestDisoccupazione(unittest.TestCase):
    def test_disoccupazione_azzera_teorico_spettacolo_2007(self):
        dati = {
            "regime_generale": [
                {
                    "dal": "01/01/2007",
                    "al": "31/12/2007",
                    "tipo": "Disoccupazione",
                    "settimane": 5,
                },
            ],
            "spettacolo": [
                {
                    "dal": "01/04/2007",
                    "al": "30/06/2007",
                    "tipo": "P.A.L.S. Obbligatoria",
                    "giorni": 78,
                    "gruppo": 1,
                },
                {
                    "dal": "01/06/2007",
                    "al": "31/10/2007",
                    "tipo": "P.A.L.S. Obbligatoria",
                    "giorni": 26,
                    "gruppo": 1,
                },
                {
                    "dal": "01/08/2007",
                    "al": "31/12/2007",
                    "tipo": "P.A.L.S. Obbligatoria",
                    "giorni": 108,
                    "gruppo": 1,
                },
            ],
        }

        risultati = _calcola_senza_estensione(dati)

        self.assertEqual(risultati["mesi"].get(2007, 0), 0)
        self.assertEqual(risultati["teorico"].get(2007, 0), 0)
        self.assertEqual(risultati["reale"][2007], 30 + 78 + 26 + 108)

    def test_buchi_disoccupazione_spettacolo_2008(self):
        dati = {
            "regime_generale": [
                {
                    "dal": "12/01/2008",
                    "al": "03/02/2008",
                    "tipo": "Disoccupazione",
                    "settimane": 4,
                },
                {
                    "dal": "08/07/2008",
                    "al": "27/08/2008",
                    "tipo": "Disoccupazione",
                    "settimane": 8,
                },
            ],
            "spettacolo": [
                {
                    "dal": "01/01/2008",
                    "al": "31/12/2008",
                    "tipo": "P.A.L.S. Obbligatoria",
                    "giorni": 188,
                    "gruppo": 1,
                },
                {
                    "dal": "11/02/2008",
                    "al": "10/06/2008",
                    "tipo": "P.A.L.S. Obbligatoria",
                    "giorni": 42,
                    "gruppo": 1,
                },
            ],
        }

        risultati = _calcola_senza_estensione(dati)

        self.assertEqual(risultati["mesi"][2008], 8)
        self.assertEqual(risultati["teorico"][2008], 80)
        self.assertEqual(risultati["reale"][2008], 72 + 188 + 42)


class TestSpettacoloPost1997(unittest.TestCase):
    def test_post_1997_tempo_indeterminato(self):
        dati = {
            "regime_generale": [],
            "spettacolo": [
                {
                    "dal": "01/01/1998",
                    "al": "31/12/1998",
                    "tipo": "P.A.L.S. Obbligatoria",
                    "giorni": 312,
                    "gruppo": 1,
                },
            ],
        }

        risultati = _calcola_senza_estensione(dati)

        self.assertEqual(risultati["mesi"][1998], 12)
        self.assertEqual(risultati["teorico"][1998], 312)
        self.assertEqual(risultati["reale"][1998], 312)

    def test_cambio_regime_1996_1997(self):
        dati = {
            "regime_generale": [],
            "spettacolo": [
                {
                    "dal": "01/01/1996",
                    "al": "31/12/1996",
                    "tipo": "P.A.L.S. Obbligatoria",
                    "giorni": 312,
                    "gruppo": 1,
                },
                {
                    "dal": "01/01/1997",
                    "al": "31/07/1997",
                    "tipo": "P.A.L.S. Obbligatoria",
                    "giorni": 182,
                    "unita": "giorni",
                    "gruppo": 1,
                    "codice_qualifica": "113",
                    "retribuzione": "19.041,88"
                    },
                    {
                    "dal": "01/01/1997",
                    "al": "31/12/1997",
                    "tipo": "P.A.L.S. Obblig.Cong.",
                    "giorni": None,
                    "unita": "giorni",
                    "gruppo": 2,
                    "codice_qualifica": "201",
                    "retribuzione": "1.624,77"
                    },
                    {
                    "dal": "01/01/1997",
                    "al": "30/06/1998",
                    "tipo": "P.A.L.S. Obblig.Cong.",
                    "giorni": None,
                    "unita": "giorni",
                    "gruppo": 1,
                    "codice_qualifica": "113",
                    "retribuzione": "2.318,38"
                    },
                    {
                    "dal": "01/08/1997",
                    "al": "30/09/1997",
                    "tipo": "P.A.L.S. Obbligatoria",
                    "giorni": 52,
                    "unita": "giorni",
                    "gruppo": 1,
                    "codice_qualifica": "113",
                    "retribuzione": "4.307,16"
                    },
                    {
                    "dal": "01/10/1997",
                    "al": "31/12/1997",
                    "tipo": "P.A.L.S. Obbligatoria",
                    "giorni": 78,
                    "unita": "giorni",
                    "gruppo": 2,
                    "codice_qualifica": "201",
                    "retribuzione": "10.034,18"
                    }
            ],
        }

        risultati = _calcola_senza_estensione(dati)

        self.assertEqual(risultati["mesi"][1996], 12)
        self.assertEqual(risultati["teorico"][1996], 120)
        self.assertEqual(risultati["reale"][1996], 312)

        self.assertEqual(risultati["mesi"][1997], 12)
        self.assertEqual(risultati["teorico"][1997], 282)
        self.assertEqual(risultati["reale"][1997], 338)
