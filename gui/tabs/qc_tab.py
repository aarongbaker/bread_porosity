"""
QC Tab
Evaluate analysis results against quality control profiles
"""

import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import List, Dict

from gui.controllers.qc_controller import QCController
from gui.theme import get_theme
from gui.components.results_display import ResultsDisplay
from repositories.results_repository import ResultsRepository
from models.analysis_result import AnalysisResult


class QCTab(ttk.Frame):
    """Tab for quality control evaluation."""

    def __init__(self, parent, qc_controller: QCController, results_repo: ResultsRepository):
        super().__init__(parent)

        self.qc_controller = qc_controller
        self.results_repo = results_repo
        self.results: List[AnalysisResult] = []
        self.theme = get_theme()
        self.colors = self.theme.colors

        self.listbox: tk.Listbox
        self.profile_text: scrolledtext.ScrolledText
        self.bread_type_var = tk.StringVar()
        self.bread_type_labels: Dict[str, str] = {}
        self.results_display: ResultsDisplay

        self._build_ui()
        self._load_results()
        self._load_profile()

    def _build_ui(self) -> None:
        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_frame = ttk.Frame(main_pane)
        right_frame = ttk.Frame(main_pane)
        main_pane.add(left_frame, weight=1)
        main_pane.add(right_frame, weight=3)

        controls = ttk.Frame(left_frame)
        controls.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(controls, text="Reload Results", command=self._load_results).pack(side=tk.LEFT)
        ttk.Button(controls, text="Evaluate", command=self._evaluate_selected).pack(side=tk.LEFT, padx=5)

        self.bread_type_combo = ttk.Combobox(controls, textvariable=self.bread_type_var, state="readonly")
        self.bread_type_combo.pack(side=tk.RIGHT)
        ttk.Button(controls, text="Set Bread Type", command=self._set_bread_type).pack(
            side=tk.RIGHT, padx=5
        )

        self.listbox = tk.Listbox(
            left_frame,
            height=10,
            bg=self.colors.bg_tertiary,
            fg=self.colors.text_primary,
            selectbackground=self.colors.bg_accent,
            highlightcolor=self.colors.border_color
        )
        self.listbox.pack(fill=tk.BOTH, expand=True)

        self.profile_text = scrolledtext.ScrolledText(
            left_frame,
            wrap=tk.WORD,
            font=('Consolas', 8),
            height=8,
            bg=self.colors.bg_secondary,
            fg=self.colors.text_primary,
            insertbackground=self.colors.bg_accent
        )
        self.profile_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        self.results_display = ResultsDisplay(right_frame)
        self.results_display.pack(fill=tk.BOTH, expand=True)

    def _load_results(self) -> None:
        self.results = self.results_repo.find_all()
        self.listbox.delete(0, tk.END)
        for result in self.results:
            label = f"{result.image_filename} ({result.timestamp})"
            self.listbox.insert(tk.END, label)

    def reload_results(self) -> None:
        """Reload available results."""
        self._load_results()

    def _load_profile(self) -> None:
        self._load_bread_types()
        profile = self.qc_controller.get_current_profile()
        self.profile_text.delete(1.0, tk.END)
        if profile:
            self.profile_text.insert(tk.END, json.dumps(profile.to_dict(), indent=2))
        else:
            self.profile_text.insert(tk.END, "No profile loaded.")

    def _evaluate_selected(self) -> None:
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showinfo("No Selection", "Select a result to evaluate.")
            return

        result = self.results[selection[0]]
        evaluation = self.qc_controller.evaluate_result(result)
        if not evaluation:
            messagebox.showwarning("QC Failed", "Unable to evaluate QC for this result.")
            return

        self.results_display.display_qc_results(evaluation)

    def _load_bread_types(self) -> None:
        self.bread_type_labels = self.qc_controller.get_available_bread_type_labels()
        values = list(self.bread_type_labels.values())
        self.bread_type_combo["values"] = values

        current = self.qc_controller.get_current_profile()
        if current:
            label = self.bread_type_labels.get(current.bread_type, current.bread_type)
            self.bread_type_var.set(label)

    def _set_bread_type(self) -> None:
        label = self.bread_type_var.get()
        if not label:
            return

        key = next((k for k, v in self.bread_type_labels.items() if v == label), None)
        if not key:
            messagebox.showwarning("Invalid Selection", "Select a valid bread type.")
            return

        success = self.qc_controller.set_bread_type(key)
        if success:
            self._load_profile()

    def set_current_result(self, result: AnalysisResult) -> None:
        """Select a result in the list if present."""
        for idx, item in enumerate(self.results):
            if item.image_path == result.image_path:
                self.listbox.selection_clear(0, tk.END)
                self.listbox.selection_set(idx)
                break
