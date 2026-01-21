"""
GUI Main Entry Point
Launches the Bread Porosity Analysis Tool GUI
"""

import tkinter as tk
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from gui.app import BreadPorosityApp
from utils.logger import setup_logging


def main():
    """Main entry point for the GUI application"""
    # Setup logging
    setup_logging()

    # Create root window
    root = tk.Tk()

    # Create and run application
    try:
        app = BreadPorosityApp(root)
        app.run()
    except Exception as e:
        # Show error dialog if initialization fails
        import tkinter.messagebox as messagebox
        error_msg = f"Failed to start application:\n\n{str(e)}"
        messagebox.showerror("Application Error", error_msg)
        root.destroy()
        sys.exit(1)


if __name__ == "__main__":
    main()