"""
Preview Tab
Displays the current image or annotated output
"""

import tkinter as tk
from tkinter import ttk
from pathlib import Path
from typing import Optional

from gui.components.image_preview import ImagePreview
from models.analysis_result import AnalysisResult


class PreviewTab(ttk.Frame):
    """Tab for image preview."""

    def __init__(self, parent):
        super().__init__(parent)

        self.image_preview = ImagePreview(self)
        self.image_preview.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def show_image(self, image_path: str) -> None:
        """Display an image path in the preview."""
        if Path(image_path).exists():
            self.image_preview.load_image_async(image_path)

    def show_result(self, result: Optional[AnalysisResult]) -> None:
        """Display the annotated image if available."""
        if not result:
            return
        preview_path = result.output_annotated_path or result.image_path
        if preview_path:
            self.show_image(preview_path)
