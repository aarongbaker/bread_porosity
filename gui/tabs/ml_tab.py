"""
ML Tab
Prediction model status and info
"""

import json
import tkinter as tk
from tkinter import ttk, scrolledtext

from gui.controllers.prediction_controller import PredictionController
from gui.theme import get_theme


class MLTab(ttk.Frame):
    """Tab for ML model status and diagnostics."""

    def __init__(self, parent, prediction_controller: PredictionController):
        super().__init__(parent)

        self.prediction_controller = prediction_controller
        self.theme = get_theme()
        self.colors = self.theme.colors
        self.output_text: scrolledtext.ScrolledText

        self._build_ui()

    def _build_ui(self) -> None:
        controls = ttk.Frame(self)
        controls.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(controls, text="Training Status", command=self._load_status).pack(
            side=tk.LEFT
        )
        ttk.Button(controls, text="Model Info", command=self._load_info).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(controls, text="Retrain", command=self._retrain).pack(
            side=tk.LEFT
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
        self.output_text.insert(tk.END, "Select an action to view ML status.")

    def _load_status(self) -> None:
        status = self.prediction_controller.get_training_status()
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, json.dumps(status, indent=2))

    def _load_info(self) -> None:
        info = self.prediction_controller.get_model_info() or {}
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, json.dumps(info, indent=2))

    def _retrain(self) -> None:
        success = self.prediction_controller.retrain_model()
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(
            tk.END, json.dumps({"retrained": bool(success)}, indent=2)
        )
