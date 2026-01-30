"""
Entry point per python -m previdenza
"""

import sys


def main():
    """Dispatch a GUI o CLI in base agli argomenti"""
    if len(sys.argv) == 1:
        # Nessun argomento: avvia GUI
        from .gui import avvia_gui
        avvia_gui()
    else:
        # Con argomenti: esegui CLI
        from .cli import main as cli_main
        cli_main()


if __name__ == "__main__":
    main()
