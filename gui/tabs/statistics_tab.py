"""
Statistics Tab
Batch statistics for analysis results
"""

import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import List

from gui.controllers.qc_controller import QCController
from gui.theme import get_theme
from repositories.results_repository import ResultsRepository
from models.analysis_result import AnalysisResult


class StatisticsTab(ttk.Frame):
    """Tab for computing batch statistics."""

    def __init__(self, parent, qc_controller: QCController, results_repo: ResultsRepository):
        super().__init__(parent)

        self.qc_controller = qc_controller
        self.results_repo = results_repo
        self.results: List[AnalysisResult] = []
        self.theme = get_theme()
        self.colors = self.theme.colors

        self.output_text: scrolledtext.ScrolledText

        self._build_ui()

    def _build_ui(self) -> None:
        controls = ttk.Frame(self)
        controls.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(controls, text="Load Latest Results", command=self._load_results).pack(
            side=tk.LEFT
        )
        ttk.Button(controls, text="Compute Batch Stats", command=self._compute_stats).pack(
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
        self.output_text.insert(tk.END, "Load results to compute batch statistics.")

    def _load_results(self) -> None:
        self.results = self.results_repo.find_all()
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(
            tk.END, f"Loaded {len(self.results)} result(s).\n"
        )

    def reload_results(self) -> None:
        """Reload results from repository."""
        self._load_results()

    def _compute_stats(self) -> None:
        if not self.results:
            messagebox.showinfo("No Results", "Load results before computing statistics.")
            return

        stats = self.qc_controller.get_batch_statistics(self.results)
        if not stats:
            messagebox.showwarning("No Stats", "Failed to compute batch statistics.")
            return

        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, json.dumps(stats, indent=2))
