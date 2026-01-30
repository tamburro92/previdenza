"""
Interfaccia grafica Tkinter per calcolo contributi INPS
"""

import sys
import subprocess
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from .core import elabora_pdf


class App:
    """Applicazione GUI per calcolo contributi INPS"""

    def __init__(self, root):
        self.root = root
        self.root.title("Contributi INPS")
        self.root.geometry("500x420")
        self.root.resizable(False, False)

        self.pdf_path = None

        # Frame principale
        frame = ttk.Frame(root, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Selezione PDF
        ttk.Button(frame, text="Seleziona PDF", command=self.seleziona_pdf, width=20).pack(pady=(0, 5))
        self.label_pdf = ttk.Label(frame, text="Nessun file selezionato", foreground="gray", wraplength=450)
        self.label_pdf.pack(pady=(0, 15))

        # Tempo indeterminato
        self.var_ti = tk.BooleanVar()
        self.check_ti = ttk.Checkbutton(frame, text="Tempo indeterminato", variable=self.var_ti, command=self.toggle_data)
        self.check_ti.pack(anchor=tk.W)

        # Frame data
        self.frame_data = ttk.Frame(frame)
        self.frame_data.pack(anchor=tk.W, padx=20, pady=(0, 15))
        ttk.Label(self.frame_data, text="Dal (opzionale):").pack(side=tk.LEFT)
        self.entry_data = ttk.Entry(self.frame_data, width=12)
        self.entry_data.pack(side=tk.LEFT, padx=5)
        self.entry_data.insert(0, "GG/MM/AAAA")
        self.entry_data.config(state=tk.DISABLED)

        # Pulsante calcola
        self.btn_calcola = ttk.Button(frame, text="CALCOLA", command=self.calcola, width=20, state=tk.DISABLED)
        self.btn_calcola.pack(pady=10)

        # Output
        ttk.Label(frame, text="Output:", anchor=tk.W).pack(fill=tk.X, pady=(10, 0))
        self.text_output = tk.Text(frame, height=8, width=55, state=tk.DISABLED, bg="#f5f5f5")
        self.text_output.pack(pady=5)

        # Pulsante apri cartella
        self.btn_apri = ttk.Button(frame, text="Apri cartella output", command=self.apri_cartella, state=tk.DISABLED)
        self.btn_apri.pack(pady=5)

        self.output_dir = None

    def seleziona_pdf(self):
        """Apre dialogo per selezionare PDF"""
        path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if path:
            self.pdf_path = path
            self.label_pdf.config(text=path, foreground="black")
            self.btn_calcola.config(state=tk.NORMAL)

    def toggle_data(self):
        """Abilita/disabilita campo data"""
        if self.var_ti.get():
            self.entry_data.config(state=tk.NORMAL)
            if self.entry_data.get() == "GG/MM/AAAA":
                self.entry_data.delete(0, tk.END)
        else:
            self.entry_data.delete(0, tk.END)
            self.entry_data.insert(0, "GG/MM/AAAA")
            self.entry_data.config(state=tk.DISABLED)

    def calcola(self):
        """Esegue il calcolo"""
        if not self.pdf_path:
            return

        # Determina tempo indeterminato
        tempo_indeterminato_da = None
        if self.var_ti.get():
            data = self.entry_data.get().strip()
            if data and data != "GG/MM/AAAA" and re.match(r'\d{2}/\d{2}/\d{4}', data):
                tempo_indeterminato_da = data
            else:
                tempo_indeterminato_da = "sempre"

        try:
            self.btn_calcola.config(state=tk.DISABLED, text="Elaborazione...")
            self.root.update()

            risultato = elabora_pdf(self.pdf_path, tempo_indeterminato_da)

            # Mostra output
            self.text_output.config(state=tk.NORMAL)
            self.text_output.delete(1.0, tk.END)

            nome_completo = f"{risultato['cognome']} {risultato['nome']}" if risultato['cognome'] else risultato['codice_fiscale']
            output = f"Elaborato: {nome_completo}\n"
            output += f"Sesso: {risultato['sesso_label']}\n"
            output += f"Obiettivo: {risultato['obiettivo_label']}\n"
            output += f"Totale mesi: {risultato['totale_mesi']} ({risultato['totale_label']})\n"
            output += f"Giorni REALI: {risultato['totale_reale']}\n"
            output += f"Giorni TEORICI: {risultato['totale_teorico']}\n"
            output += f"\nFile generato:\n{risultato['excel_path']}"

            self.text_output.insert(tk.END, output)
            self.text_output.config(state=tk.DISABLED)

            self.output_dir = risultato['output_dir']
            self.btn_apri.config(state=tk.NORMAL)

        except Exception as e:
            messagebox.showerror("Errore", str(e))
        finally:
            self.btn_calcola.config(state=tk.NORMAL, text="CALCOLA")

    def apri_cartella(self):
        """Apre la cartella di output nel file manager"""
        if self.output_dir:
            if sys.platform == "darwin":
                subprocess.run(["open", self.output_dir])
            elif sys.platform == "win32":
                subprocess.run(["explorer", self.output_dir])
            else:
                subprocess.run(["xdg-open", self.output_dir])


def avvia_gui():
    """Avvia l'interfaccia grafica"""
    root = tk.Tk()
    App(root)
    root.mainloop()
