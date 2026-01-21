"""
Centralized Theme Management
All styling, colors, and theme configuration in one place
"""

import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class ThemeColors:
    """Color palette for the application"""
    bg_primary: str = "#0f1419"        # Dark navy background
    bg_secondary: str = "#1a1f2e"      # Dark card background
    bg_tertiary: str = "#252c3c"       # Light dark background
    bg_accent: str = "#1d9bf0"         # Modern blue
    bg_accent_hover: str = "#1a8cd8"   # Darker blue on hover
    bg_success: str = "#17bf63"        # Modern green
    bg_warning: str = "#ffb81c"        # Modern yellow
    bg_error: str = "#f7555f"          # Modern red
    text_primary: str = "#ffffff"      # White text
    text_secondary: str = "#b0b9c1"    # Light gray text
    text_tertiary: str = "#8a91a1"     # Darker gray
    border_color: str = "#364558"      # Modern border


class ThemeManager:
    """Centralized theme configuration and application"""
    
    def __init__(self):
        self.colors = ThemeColors()
    
    def apply_to_root(self, root: tk.Tk) -> None:
        """Apply theme to root window"""
        root.configure(bg=self.colors.bg_primary)
        self._configure_styles()
    
    def _configure_styles(self) -> None:
        """Configure all ttk styles with theme colors"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame styling
        style.configure("TFrame", background=self.colors.bg_primary)
        style.configure("Card.TFrame", background=self.colors.bg_secondary, relief="flat")
        
        # Label styling
        style.configure("TLabelframe", background=self.colors.bg_secondary, 
                       foreground=self.colors.text_primary, borderwidth=0, relief="flat")
        style.configure("TLabelframe.Label", background=self.colors.bg_secondary,
                       foreground=self.colors.text_primary, font=("Segoe UI", 11, "bold"))
        
        style.configure("TLabel", background=self.colors.bg_primary,
                       foreground=self.colors.text_primary, font=("Segoe UI", 9))
        style.configure("Header.TLabel", background=self.colors.bg_primary,
                       foreground=self.colors.text_primary, font=("Segoe UI", 13, "bold"))
        style.configure("Subheader.TLabel", background=self.colors.bg_secondary,
                       foreground=self.colors.text_secondary, font=("Segoe UI", 8, "bold"))
        style.configure("Subtitle.TLabel", background=self.colors.bg_secondary,
                       foreground=self.colors.text_secondary, font=("Segoe UI", 8))
        
        # Button styling
        style.configure("TButton", font=("Segoe UI", 9), relief="flat", padding=8,
                       background=self.colors.bg_tertiary, foreground=self.colors.text_primary,
                       borderwidth=0)
        style.map("TButton",
                 background=[("pressed", self.colors.bg_accent),
                            ("active", self.colors.bg_accent_hover),
                            ("!active", self.colors.bg_tertiary)],
                 foreground=[("pressed", "white"), ("active", "white"),
                            ("!active", self.colors.text_primary)])
        
        # Accent button style
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), relief="flat",
                       padding=10, background=self.colors.bg_accent, foreground="white",
                       borderwidth=0)
        style.map("Accent.TButton",
                 background=[("pressed", self.colors.bg_accent_hover),
                            ("active", self.colors.bg_accent_hover),
                            ("!active", self.colors.bg_accent)],
                 foreground=[("pressed", "white"), ("active", "white"),
                            ("!active", "white")])
        
        # Combobox styling
        style.configure("TCombobox", font=("Segoe UI", 9),
                       fieldbackground=self.colors.bg_tertiary,
                       background=self.colors.bg_tertiary,
                       foreground=self.colors.text_primary)
        style.map("TCombobox",
                 fieldbackground=[("focus", self.colors.bg_accent),
                                 ("!focus", self.colors.bg_tertiary)],
                 background=[("focus", self.colors.bg_accent),
                            ("!focus", self.colors.bg_tertiary)])

        # Entry styling
        style.configure("TEntry",
                       fieldbackground=self.colors.bg_tertiary,
                       foreground=self.colors.text_primary,
                       background=self.colors.bg_tertiary)
        style.map("TEntry",
                 fieldbackground=[("focus", self.colors.bg_accent),
                                 ("!focus", self.colors.bg_tertiary)])
        
        # Notebook (tabs) styling
        style.configure("TNotebook", background=self.colors.bg_primary, borderwidth=0)
        style.configure("TNotebook.Tab", padding=[16, 12],
                       font=("Segoe UI", 10, "bold"),
                       background=self.colors.bg_tertiary,
                       foreground=self.colors.text_secondary)
        style.map("TNotebook.Tab",
                 background=[("selected", self.colors.bg_accent),
                            ("!selected", self.colors.bg_tertiary)],
                 foreground=[("selected", "white"),
                            ("!selected", self.colors.text_secondary)])
        
        # Radio and Checkbutton styling
        style.configure("TRadiobutton", background=self.colors.bg_secondary,
                       foreground=self.colors.text_primary, font=("Segoe UI", 9))
        style.map("TRadiobutton",
                 background=[("active", self.colors.bg_secondary),
                            ("!active", self.colors.bg_secondary)])
        
        style.configure("TCheckbutton", background=self.colors.bg_secondary,
                       foreground=self.colors.text_primary, font=("Segoe UI", 9))
        style.map("TCheckbutton",
                 background=[("active", self.colors.bg_secondary),
                            ("!active", self.colors.bg_secondary)])
        
        # Scrollbar styling
        style.configure("Vertical.TScrollbar", background=self.colors.bg_tertiary,
                       troughcolor=self.colors.bg_secondary,
                       arrowcolor=self.colors.text_secondary, borderwidth=0)
    
    def get_button_style(self) -> Dict[str, Any]:
        """Get common button style kwargs"""
        return {
            'bg': self.colors.bg_accent,
            'fg': 'white',
            'font': ('Segoe UI', 11, 'bold'),
            'relief': tk.FLAT,
            'bd': 0,
            'activebackground': self.colors.bg_accent_hover,
            'activeforeground': 'white',
            'padx': 20,
            'pady': 14,
            'cursor': 'hand2',
            'highlightthickness': 0
        }
    
    def get_card_style(self) -> Dict[str, Any]:
        """Get common card background style"""
        return {
            'bg': self.colors.bg_secondary,
            'highlightthickness': 0
        }
    
    def get_text_style(self) -> Dict[str, Any]:
        """Get common text widget style"""
        return {
            'font': ('Consolas', 9),
            'bg': self.colors.bg_secondary,
            'fg': self.colors.text_primary,
            'relief': tk.FLAT,
            'borderwidth': 0,
            'padx': 12,
            'pady': 12
        }


# Global theme instance
_theme_instance = None


def get_theme() -> ThemeManager:
    """Get global theme instance (singleton)"""
    global _theme_instance
    if _theme_instance is None:
        _theme_instance = ThemeManager()
    return _theme_instance
