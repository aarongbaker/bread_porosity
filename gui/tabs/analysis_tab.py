"""
Analysis Tab
GUI tab for single-image analysis workflow
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Optional, Callable, Dict, Any

from gui.components.image_preview import ImagePreview
from gui.components.results_display import ResultsDisplay
from models.analysis_result import AnalysisResult


class AnalysisTab(ttk.Frame):
    """Tab for running porosity analysis on a single image."""

    def __init__(
        self,
        parent,
        analysis_controller,
        status_callback: Optional[Callable[[str, str], None]] = None,
        show_preview: bool = True,
        show_results: bool = True,
        image_selected_callback: Optional[Callable[[str], None]] = None
    ):
        super().__init__(parent)

        self.analysis_controller = analysis_controller
        self.status_callback = status_callback
        self.image_selected_callback = image_selected_callback

        self.image_path_var = tk.StringVar()
        self.pixel_size_var = tk.StringVar(value="0.1")
        self.threshold_var = tk.StringVar(value="otsu")
        self.normalize_var = tk.StringVar(value="clahe")
        self.output_dir_var = tk.StringVar(value="")
        self.save_results_var = tk.BooleanVar(value=True)
        self.generate_visuals_var = tk.BooleanVar(value=True)

        self.status_label: Optional[ttk.Label] = None
        self.progress_bar: Optional[ttk.Progressbar] = None
        self.image_preview: Optional[ImagePreview] = None
        self.results_display: Optional[ResultsDisplay] = None
        self.show_preview = show_preview
        self.show_results = show_results

        self._build_ui()

    def _build_ui(self) -> None:
        """Build the analysis tab layout."""
        controls_frame = ttk.LabelFrame(self, text="Analysis Controls", padding=10)
        controls_frame.pack(fill=tk.X, padx=10, pady=10)

        # Configure grid weights for proper column sizing
        controls_frame.columnconfigure(0, weight=0)
        controls_frame.columnconfigure(1, weight=1)
        controls_frame.columnconfigure(2, weight=0)
        controls_frame.columnconfigure(3, weight=1)
        controls_frame.columnconfigure(4, weight=0)

        ttk.Label(controls_frame, text="Image").grid(row=0, column=0, sticky="w")
        image_entry = ttk.Entry(controls_frame, textvariable=self.image_path_var)
        image_entry.grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Button(controls_frame, text="Browse", command=self.select_image).grid(
            row=0, column=2, padx=5
        )
        ttk.Button(controls_frame, text="Clear", command=self._clear_image).grid(
            row=0, column=3
        )

        ttk.Label(controls_frame, text="Pixel Size (mm)").grid(
            row=1, column=0, sticky="w", pady=(8, 0)
        )
        ttk.Entry(controls_frame, textvariable=self.pixel_size_var, width=10).grid(
            row=1, column=1, sticky="w", padx=5, pady=(8, 0)
        )

        ttk.Label(controls_frame, text="Threshold Method").grid(
            row=1, column=2, sticky="e", pady=(8, 0)
        )
        threshold_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.threshold_var,
            values=["otsu", "adaptive"],
            state="readonly",
            width=12
        )
        threshold_combo.grid(row=1, column=3, sticky="w", padx=5, pady=(8, 0))

        ttk.Label(controls_frame, text="Normalize Method").grid(
            row=2, column=0, sticky="w", pady=(8, 0)
        )
        normalize_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.normalize_var,
            values=["clahe", "morphology", "gaussian"],
            state="readonly",
            width=12
        )
        normalize_combo.grid(row=2, column=1, sticky="w", padx=5, pady=(8, 0))

        ttk.Label(controls_frame, text="Output Directory").grid(
            row=2, column=2, sticky="e", pady=(8, 0)
        )
        output_entry = ttk.Entry(controls_frame, textvariable=self.output_dir_var)
        output_entry.grid(row=2, column=3, sticky="ew", padx=5, pady=(8, 0))
        ttk.Button(controls_frame, text="Choose", command=self.select_output_dir).grid(
            row=2, column=4, padx=5, pady=(8, 0)
        )

        options_frame = ttk.Frame(controls_frame)
        options_frame.grid(row=3, column=0, columnspan=5, sticky="w", pady=(8, 0))
        ttk.Checkbutton(
            options_frame,
            text="Save Results",
            variable=self.save_results_var
        ).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(
            options_frame,
            text="Generate Visualizations",
            variable=self.generate_visuals_var
        ).pack(side=tk.LEFT)

        action_frame = ttk.Frame(self)
        action_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        ttk.Button(
            action_frame,
            text="Analyze Image",
            command=self.start_analysis,
            style="Accent.TButton"
        ).pack(side=tk.LEFT)
        self.status_label = ttk.Label(action_frame, text="Ready")
        self.status_label.pack(side=tk.LEFT, padx=10)
        self.progress_bar = ttk.Progressbar(action_frame, mode="indeterminate", length=200)
        self.progress_bar.pack(side=tk.RIGHT)

        if self.show_preview or self.show_results:
            content_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
            content_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

            if self.show_preview:
                preview_frame = ttk.Frame(content_pane)
                content_pane.add(preview_frame, weight=2)
                self.image_preview = ImagePreview(preview_frame)
                self.image_preview.pack(fill=tk.BOTH, expand=True)

            if self.show_results:
                results_frame = ttk.Frame(content_pane)
                content_pane.add(results_frame, weight=3)
                self.results_display = ResultsDisplay(results_frame)
                self.results_display.pack(fill=tk.BOTH, expand=True)

    def select_image(self) -> Optional[str]:
        """Prompt for an image and preview it."""
        path = filedialog.askopenfilename(
            title="Select Bread Image",
            filetypes=[
                ("Image Files", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff"),
                ("All Files", "*.*")
            ]
        )
        if not path:
            return None

        self.image_path_var.set(path)
        if self.image_preview:
            self.image_preview.load_image_async(path)
        self._set_status("Image loaded", "success")
        if self.image_selected_callback:
            self.image_selected_callback(path)
        return path

    def select_output_dir(self) -> None:
        """Prompt for an output directory."""
        directory = filedialog.askdirectory(title="Choose Output Directory")
        if directory:
            self.output_dir_var.set(directory)

    def start_analysis(self) -> None:
        """Kick off analysis using the controller."""
        image_path = self.image_path_var.get().strip()
        if not image_path:
            messagebox.showwarning("Missing Image", "Please select an image to analyze.")
            return

        try:
            pixel_size = float(self.pixel_size_var.get().strip())
        except ValueError:
            messagebox.showwarning("Invalid Pixel Size", "Pixel size must be a number.")
            return

        threshold_method = self.threshold_var.get().strip() or "otsu"
        normalize_method = self.normalize_var.get().strip() or "clahe"
        output_dir = self.output_dir_var.get().strip() or None
        save_results = self.save_results_var.get()
        generate_visualizations = self.generate_visuals_var.get()

        self._set_status("Starting analysis...", "warning")

        def progress_callback(message: str, level: str) -> None:
            self.after(0, lambda: self._set_status(message, level))

        def completion_callback(result: AnalysisResult) -> None:
            self.after(0, lambda: self._handle_result(result))

        self.analysis_controller.analyze_single_image_async(
            image_path=image_path,
            pixel_size_mm=pixel_size,
            threshold_method=threshold_method,
            normalize_method=normalize_method,
            output_dir=output_dir,
            progress_callback=progress_callback,
            completion_callback=completion_callback
        )

    def _handle_result(self, result: AnalysisResult) -> None:
        """Handle a completed analysis result."""
        if not result:
            self._set_status("Analysis failed", "error")
            return

        display_dict = self._result_to_display_dict(result)
        if self.results_display:
            self.results_display.display_results(display_dict)

        preview_path = result.output_annotated_path or result.image_path
        if preview_path and self.image_preview:
            if Path(preview_path).exists():
                self.image_preview.load_image_async(preview_path)

        self._set_status("Analysis complete", "success")

    def _result_to_display_dict(self, result: AnalysisResult) -> Dict[str, Any]:
        """Convert AnalysisResult to the format expected by ResultsDisplay."""
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

    def _set_status(self, message: str, level: str = "info") -> None:
        """Update the tab and app status."""
        if self.status_label:
            self.status_label.config(text=message)

        if self.progress_bar:
            if level == "warning":
                self.progress_bar.start(10)
            else:
                self.progress_bar.stop()

        if self.status_callback:
            self.status_callback(message, level)

    def _clear_image(self) -> None:
        """Clear the current image selection."""
        self.image_path_var.set("")
        if self.image_preview:
            self.image_preview.clear_image()
        if self.results_display:
            self.results_display.clear_results()
        self._set_status("Ready", "info")
