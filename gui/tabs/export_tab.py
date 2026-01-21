"""
Export Tab
Export analysis results to CSV, Excel, or PDF
"""

import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import List, Optional

from gui.controllers.export_controller import ExportController
from gui.theme import get_theme
from repositories.results_repository import ResultsRepository
from models.analysis_result import AnalysisResult


class ExportTab(ttk.Frame):
    """Tab for exporting results."""

    def __init__(self, parent, export_controller: ExportController, results_repo: ResultsRepository):
        super().__init__(parent)

        self.export_controller = export_controller
        self.results_repo = results_repo
        self.results: List[AnalysisResult] = []
        self.theme = get_theme()
        self.colors = self.theme.colors

        self.include_charts_var = tk.BooleanVar(value=True)
        self.status_text: scrolledtext.ScrolledText

        self._build_ui()
        self._load_results()

    def _build_ui(self) -> None:
        controls = ttk.Frame(self)
        controls.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(controls, text="Reload Results", command=self._load_results).pack(
            side=tk.LEFT
        )
        ttk.Checkbutton(
            controls, text="Include Charts (PDF)", variable=self.include_charts_var
        ).pack(side=tk.LEFT, padx=10)

        ttk.Button(controls, text="Export CSV", command=self._export_csv).pack(side=tk.LEFT)
        ttk.Button(controls, text="Export Excel", command=self._export_excel).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(controls, text="Export PDF", command=self._export_pdf).pack(side=tk.LEFT)

        self.status_text = scrolledtext.ScrolledText(
            self,
            wrap=tk.WORD,
            font=('Consolas', 9),
            height=12,
            bg=self.colors.bg_secondary,
            fg=self.colors.text_primary,
            insertbackground=self.colors.bg_accent
        )
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.status_text.insert(tk.END, "Load results to enable exports.")

    def _load_results(self) -> None:
        self.results = self.results_repo.find_all()
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(
            tk.END, f"Loaded {len(self.results)} result(s) for export.\n"
        )

    def reload_results(self) -> None:
        """Reload exportable results."""
        self._load_results()

    def _export_csv(self) -> None:
        if not self._validate_results():
            return
        filename = self.export_controller.export_csv(self.results)
        self._log_export("csv", filename)

    def _export_excel(self) -> None:
        if not self._validate_results():
            return
        filename = self.export_controller.export_excel(self.results)
        self._log_export("excel", filename)

    def _export_pdf(self) -> None:
        if not self._validate_results():
            return
        filename = self.export_controller.export_pdf(
            self.results, include_charts=self.include_charts_var.get()
        )
        self._log_export("pdf", filename)

    def _validate_results(self) -> bool:
        if not self.results:
            messagebox.showinfo("No Results", "No results available for export.")
            return False
        return True

    def _log_export(self, fmt: str, filename: Optional[str]) -> None:
        payload = {
            "format": fmt,
            "success": bool(filename),
            "filename": filename
        }
        self.status_text.insert(tk.END, json.dumps(payload) + "\n")
