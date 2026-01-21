"""
Defect Tab
Run defect detection on analysis results
"""

import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import List

from gui.controllers.defect_controller import DefectController
from gui.theme import get_theme
from gui.components.results_display import ResultsDisplay
from repositories.results_repository import ResultsRepository
from models.analysis_result import AnalysisResult


class DefectTab(ttk.Frame):
    """Tab for defect detection workflows."""

    def __init__(self, parent, defect_controller: DefectController, results_repo: ResultsRepository):
        super().__init__(parent)

        self.defect_controller = defect_controller
        self.results_repo = results_repo
        self.results: List[AnalysisResult] = []
        self.theme = get_theme()
        self.colors = self.theme.colors

        self.listbox: tk.Listbox
        self.results_display: ResultsDisplay
        self.patterns_text: scrolledtext.ScrolledText

        self._build_ui()
        self._load_results()

    def _build_ui(self) -> None:
        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_frame = ttk.Frame(main_pane)
        right_frame = ttk.Frame(main_pane)
        main_pane.add(left_frame, weight=1)
        main_pane.add(right_frame, weight=3)

        controls = ttk.Frame(left_frame)
        controls.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(controls, text="Reload Results", command=self._load_results).pack(
            side=tk.LEFT
        )
        ttk.Button(controls, text="Detect Defects", command=self._detect_selected).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(controls, text="Analyze Patterns", command=self._analyze_patterns).pack(
            side=tk.LEFT
        )

        self.listbox = tk.Listbox(
            left_frame,
            height=12,
            bg=self.colors.bg_tertiary,
            fg=self.colors.text_primary,
            selectbackground=self.colors.bg_accent,
            highlightcolor=self.colors.border_color
        )
        self.listbox.pack(fill=tk.BOTH, expand=True)

        self.results_display = ResultsDisplay(right_frame)
        self.results_display.pack(fill=tk.BOTH, expand=True)

        self.patterns_text = scrolledtext.ScrolledText(
            right_frame,
            wrap=tk.WORD,
            font=('Consolas', 9),
            height=10,
            bg=self.colors.bg_secondary,
            fg=self.colors.text_primary,
            insertbackground=self.colors.bg_accent
        )
        self.patterns_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        self.patterns_text.insert(tk.END, "Pattern analysis will appear here.")

    def _load_results(self) -> None:
        self.results = self.results_repo.find_all()
        self.listbox.delete(0, tk.END)
        for result in self.results:
            label = f"{result.image_filename} ({result.timestamp})"
            self.listbox.insert(tk.END, label)

    def reload_results(self) -> None:
        """Reload available results."""
        self._load_results()

    def _detect_selected(self) -> None:
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showinfo("No Selection", "Select a result to analyze.")
            return

        result = self.results[selection[0]]
        defect_report = self.defect_controller.detect_defects(result)
        if not defect_report:
            messagebox.showwarning("Detection Failed", "Defect detection failed.")
            return

        self.results_display.display_defect_results(defect_report)

    def _analyze_patterns(self) -> None:
        if not self.results:
            messagebox.showinfo("No Results", "Load results before analyzing patterns.")
            return

        patterns = self.defect_controller.analyze_defect_patterns(self.results)
        self.patterns_text.delete(1.0, tk.END)
        self.patterns_text.insert(tk.END, json.dumps(patterns or {}, indent=2))

    def set_current_result(self, result: AnalysisResult) -> None:
        """Select a result in the list if present."""
        for idx, item in enumerate(self.results):
            if item.image_path == result.image_path:
                self.listbox.selection_clear(0, tk.END)
                self.listbox.selection_set(idx)
                break
