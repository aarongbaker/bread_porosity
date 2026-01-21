"""
Consistency Tab
SPC statistics and QC alerts
"""

import json
import tkinter as tk
from tkinter import ttk, scrolledtext

from gui.controllers.qc_controller import QCController
from gui.theme import get_theme


class ConsistencyTab(ttk.Frame):
    """Tab for SPC statistics and alerts."""

    def __init__(self, parent, qc_controller: QCController):
        super().__init__(parent)

        self.qc_controller = qc_controller
        self.theme = get_theme()
        self.colors = self.theme.colors
        self.output_text: scrolledtext.ScrolledText

        self._build_ui()

    def _build_ui(self) -> None:
        controls = ttk.Frame(self)
        controls.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(controls, text="SPC Statistics", command=self._load_spc).pack(
            side=tk.LEFT
        )
        ttk.Button(controls, text="QC Alerts", command=self._load_alerts).pack(
            side=tk.LEFT, padx=5
        )

        self.output_text = scrolledtext.ScrolledText(
            self,
            wrap=tk.WORD,
            font=('Consolas', 9),
            bg=self.colors.bg_secondary,
            fg=self.colors.text_primary,
            insertbackground=self.colors.bg_accent
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.output_text.insert(tk.END, "Select an action to view SPC stats or alerts.")

    def _load_spc(self) -> None:
        spc = self.qc_controller.get_spc_statistics()
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, json.dumps(spc or {}, indent=2))

    def _load_alerts(self) -> None:
        alerts = self.qc_controller.get_alerts()
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, json.dumps(alerts or [], indent=2))
