"""
GUI Package - Bread Porosity Analysis Tool
Main user interface for analyzing bread images and managing recipes
"""

__version__ = "1.0.0"

# Import legacy GUI class from parent directory
import sys
from pathlib import Path

# Add parent directory to path to import gui.py
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Import the legacy GUI class
try:
    # Try importing directly from the gui.py file in parent directory
    import importlib.util
    spec = importlib.util.spec_from_file_location("gui_legacy", str(parent_dir / "gui.py"))
    gui_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gui_module)
    BreadPorositytoolGUI = gui_module.BreadPorositytoolGUI
except:
    # Fallback: try to import the class
    try:
        from gui import BreadPorositytoolGUI
    except ImportError:
        BreadPorositytoolGUI = None

__all__ = ['BreadPorositytoolGUI']
