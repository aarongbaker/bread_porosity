"""
Results Tab
Displays saved analysis results from the repository
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, List

from gui.components.results_display import ResultsDisplay
from gui.theme import get_theme
from repositories.results_repository import ResultsRepository
from models.analysis_result import AnalysisResult


class ResultsTab(ttk.Frame):
    """Tab for browsing and viewing analysis results."""

    def __init__(self, parent, results_repo: ResultsRepository):
        super().__init__(parent)

        self.results_repo = results_repo
        self.results: List[AnalysisResult] = []
        self.theme = get_theme()
        self.colors = self.theme.colors

        self.listbox: tk.Listbox
        self.results_display: ResultsDisplay

        self._build_ui()
        self.refresh_results()

    def _build_ui(self) -> None:
        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_frame = ttk.Frame(main_pane)
        right_frame = ttk.Frame(main_pane)
        main_pane.add(left_frame, weight=1)
        main_pane.add(right_frame, weight=3)

        controls = ttk.Frame(left_frame)
        controls.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(controls, text="Refresh", command=self.refresh_results).pack(side=tk.LEFT)
        ttk.Button(controls, text="View", command=self._view_selected).pack(side=tk.LEFT, padx=5)

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

    def refresh_results(self) -> None:
        """Reload results from repository."""
        self.results = self.results_repo.find_all()
        self.listbox.delete(0, tk.END)

        for result in self.results:
            label = f"{result.image_filename} ({result.timestamp})"
            self.listbox.insert(tk.END, label)

    def show_result(self, result: AnalysisResult) -> None:
        """Show a specific result in the display."""
        if result not in self.results:
            self.refresh_results()

        for idx, item in enumerate(self.results):
            if item.image_path == result.image_path:
                self.listbox.selection_clear(0, tk.END)
                self.listbox.selection_set(idx)
                break

        self.results_display.display_results(self._result_to_display_dict(result))

    def _view_selected(self) -> None:
        """Display the selected result."""
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showinfo("No Selection", "Select a result to view.")
            return

        result = self.results[selection[0]]
        self.results_display.display_results(self._result_to_display_dict(result))

    @staticmethod
    def _result_to_display_dict(result: AnalysisResult) -> Dict[str, Any]:
        return {
            "image_path": result.image_path,
            "processing_time_sec": result.processing_time_sec,
            "metrics": {
                "porosity_percent": result.porosity_percent,
                "hole_count_total": result.hole_count_total,
                "hole_diameter_mean_mm": result.hole_diameter_mean_mm,
                "hole_diameter_std_mm": result.hole_diameter_std_mm,
                "hole_diameter_min_mm": result.hole_diameter_min_mm,
                "hole_diameter_max_mm": result.hole_diameter_max_mm,
                "holes_per_cm2": result.holes_per_cm2,
                "anisotropy_ratio": result.anisotropy_ratio,
                "orientation_mean_deg": result.orientation_mean_deg,
                "uniformity_score": result.uniformity_score
            }
        }
