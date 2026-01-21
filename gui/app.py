"""
Main Application Class - Refactored with Legacy Layout
Coordinates the GUI application using refactored services but legacy UI layout
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Optional
import threading

# Import services
from services.analysis_service import AnalysisService
from services.recipe_service import RecipeService
from services.quality_control_service import QualityControlService
from services.prediction_service import PredictionService
from services.export_service import ExportService
from services.defect_service import DefectService

# Import controllers
from gui.controllers.analysis_controller import AnalysisController
from gui.controllers.recipe_controller import RecipeController
from gui.controllers.qc_controller import QCController
from gui.controllers.prediction_controller import PredictionController
from gui.controllers.export_controller import ExportController
from gui.controllers.defect_controller import DefectController

# Import theme
from gui.theme import ThemeManager

# Import repositories
from repositories.config_repository import ConfigRepository
from repositories.recipe_repository import RecipeRepository
from repositories.results_repository import ResultsRepository

# Import utilities
from utils.logger import get_logger
from utils.config_loader import ConfigLoader

logger = get_logger(__name__)



class BreadPorosityApp:
    # --- Placeholder callbacks for all main buttons ---
    def _on_log_recipe(self):
        messagebox.showinfo("Log Recipe", "This will log your recipe. (Feature coming soon!)")

    def _on_save_porosity(self):
        messagebox.showinfo("Save Porosity", "This will save the measured porosity for your recipe. (Feature coming soon!)")

    def _on_predict(self):
        messagebox.showinfo("Predict", "This will predict porosity from your recipe. (Feature coming soon!)")

    def _on_create_variant(self):
        messagebox.showinfo("Create Variant", "This will create a new recipe variant. (Feature coming soon!)")

    def _on_clone_recipe(self):
        messagebox.showinfo("Clone Recipe", "This will clone the selected recipe. (Feature coming soon!)")

    def _on_scale_recipe(self):
        messagebox.showinfo("Scale Recipe", "This will scale your recipe. (Feature coming soon!)")

    def _on_family_tree(self):
        messagebox.showinfo("Family Tree", "This will show the recipe family tree. (Feature coming soon!)")

    def _on_delete_recipe(self):
        messagebox.showinfo("Delete Recipe", "This will delete the selected recipe. (Feature coming soon!)")

    def _on_refresh_statistics(self):
        messagebox.showinfo("Refresh Statistics", "This will refresh the statistics. (Feature coming soon!)")

    def _on_compare_recipes(self):
        messagebox.showinfo("Compare Recipes", "This will compare selected recipes. (Feature coming soon!)")

    def _on_what_if_analysis(self):
        messagebox.showinfo("What-If Analysis", "This will run a what-if analysis. (Feature coming soon!)")

    def _on_export_csv(self):
        messagebox.showinfo("Export to CSV", "This will export results to CSV. (Feature coming soon!)")

    def _on_export_excel(self):
        messagebox.showinfo("Export to Excel", "This will export results to Excel. (Feature coming soon!)")

    def _on_generate_pdf(self):
        messagebox.showinfo("Generate PDF Report", "This will generate a PDF report. (Feature coming soon!)")

    def _on_create_charts(self):
        messagebox.showinfo("Create Summary Charts", "This will create summary charts. (Feature coming soon!)")

    def _on_evaluate_analysis(self):
        messagebox.showinfo("Evaluate Analysis", "This will evaluate the current analysis. (Feature coming soon!)")

    def _on_check_batch_consistency(self):
        messagebox.showinfo("Check Batch Consistency", "This will check batch consistency. (Feature coming soon!)")

    def _on_spc_statistics(self):
        messagebox.showinfo("SPC Statistics", "This will show SPC statistics. (Feature coming soon!)")

    def _on_view_alerts(self):
        messagebox.showinfo("View Alerts", "This will show quality control alerts. (Feature coming soon!)")

    def _on_configure_thresholds(self):
        messagebox.showinfo("Configure Thresholds", "This will let you configure QC thresholds. (Feature coming soon!)")

    def _on_analyze_defect(self):
        messagebox.showinfo("Analyze Defect", "This will analyze the current image for defects. (Feature coming soon!)")

    def _on_batch_defect(self):
        messagebox.showinfo("Batch Defect Analysis", "This will run defect analysis on a batch. (Feature coming soon!)")

    def _on_add_good_image(self):
        messagebox.showinfo("Add Good Image", "This will add a good bread image for ML training. (Feature coming soon!)")

    def _on_add_problem_image(self):
        messagebox.showinfo("Add Problem Image", "This will add a problem bread image for ML training. (Feature coming soon!)")

    def _on_train_model(self):
        messagebox.showinfo("Train Model", "This will train the ML model. (Feature coming soon!)")

    def _on_predict_current(self):
        messagebox.showinfo("Predict Current", "This will predict the quality of the current bread image. (Feature coming soon!)")

    def _on_add_photos(self):
        messagebox.showinfo("Add Photos", "This will let you add bread photos from your computer. (Feature coming soon!)")

    def _on_reload_list(self):
        messagebox.showinfo("Reload List", "This will reload the list of bread photos. (Feature coming soon!)")

    def _on_clear_photo_selection(self):
        self.image_listbox.selection_clear(0, tk.END)
        self.status_var.set("Photo selection cleared.")
    """Main application class with legacy layout and refactored code"""

    def __init__(self, root: tk.Tk):
        """Initialize the application"""
        self.root = root
        self.root.title("Bread Porosity Analysis Tool")
        self.root.geometry("1400x900")

        # Initialize theme
        self.theme_manager = ThemeManager()
        self.theme_manager.apply_to_root(self.root)
        self.colors = self.theme_manager.colors

        # Initialize repositories
        self.config_repo = ConfigRepository()
        self.recipe_repo = RecipeRepository()
        self.results_repo = ResultsRepository()

        # Initialize services
        self._init_services()

        # Initialize controllers
        self._init_controllers()

        # State variables
        self.current_image_path: Optional[str] = None
        self.current_recipe_id: Optional[str] = None

        # Initialize UI with legacy layout
        self._init_ui()

        # Load configuration
        self._load_config()

        # Initialize recipes and first-time setup
        self._load_initial_recipes()
        self._show_first_time_setup()

        logger.info("Bread Porosity Analysis Tool initialized")

    def _init_services(self) -> None:
        """Initialize all services"""
        try:
            self.analysis_service = AnalysisService(
                results_repo=self.results_repo
            )
            self.recipe_service = RecipeService(
                recipe_repo=self.recipe_repo
            )
            self.qc_service = QualityControlService(
                config_repo=self.config_repo
            )
            self.prediction_service = PredictionService(
                recipe_repo=self.recipe_repo
            )
            self.export_service = ExportService(
                output_dir="./output"
            )
            self.defect_service = DefectService()

            logger.info("All services initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            raise

    def _init_controllers(self) -> None:
        """Initialize all controllers"""
        try:
            self.analysis_controller = AnalysisController(
                analysis_service=self.analysis_service
            )
            self.recipe_controller = RecipeController(
                recipe_service=self.recipe_service
            )
            self.qc_controller = QCController(
                qc_service=self.qc_service
            )
            self.prediction_controller = PredictionController(
                prediction_service=self.prediction_service
            )
            self.export_controller = ExportController(
                export_service=self.export_service
            )
            self.defect_controller = DefectController(
                defect_service=self.defect_service
            )

            logger.info("All controllers initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize controllers: {e}")
            raise

    def _init_ui(self) -> None:
        """Initialize UI with legacy layout"""
        # Header
        header = ttk.Frame(self.root)
        header.pack(fill=tk.X, padx=0, pady=0)

        header_bg = tk.Frame(header, bg=self.colors.bg_accent, height=80)
        header_bg.pack(fill=tk.X)

        header_content = tk.Frame(header_bg, bg=self.colors.bg_accent)
        header_content.pack(fill=tk.BOTH, expand=True, padx=25, pady=0)

        tk.Label(
            header_content,
            text="  Bread Porosity Analysis",
            font=("Segoe UI", 20, "bold"),
            fg="white",
            bg=self.colors.bg_accent
        ).pack(anchor=tk.W, pady=(15, 5))

        tk.Label(
            header_content,
            text="Professional Analysis & Quality Control",
            font=("Segoe UI", 9),
            fg=self.colors.text_secondary,
            bg=self.colors.bg_accent
        ).pack(anchor=tk.W, pady=(0, 15))

        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

        # Left panel - Controls
        left_panel = ttk.Frame(main_container, width=340)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 12))

        # Image Management Section
        self._create_image_section(left_panel)

        # Parameters Section
        self._create_parameters_section(left_panel)

        # Analysis Mode Section
        self._create_mode_section(left_panel)

        # Action Buttons
        self._create_action_buttons(left_panel)

        # Status Section
        self._create_status_section(left_panel)

        # Right panel - Notebook with tabs
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create tabs
        self._create_tabs()

    def _create_image_section(self, parent):
        """Create image library section"""
        img_section_bg = tk.Frame(parent, bg=self.colors.bg_secondary, highlightthickness=0)
        img_section_bg.pack(fill=tk.BOTH, expand=True, pady=(0, 12))

        img_section = tk.Frame(img_section_bg, bg=self.colors.bg_secondary)
        img_section.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        img_header = tk.Label(
            img_section,
            text="🍞  Your Bread Photos",
            font=("Segoe UI", 11, "bold"),
            fg=self.colors.text_primary,
            bg=self.colors.bg_secondary
        )
        img_header.pack(anchor=tk.W, pady=(0, 12))

        listbox_frame = ttk.Frame(img_section)
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.image_listbox = tk.Listbox(
            listbox_frame,
            yscrollcommand=scrollbar.set,
            height=12,
            font=("Segoe UI", 9),
            bg=self.colors.bg_tertiary,
            fg=self.colors.text_primary,
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=1,
            highlightcolor=self.colors.bg_accent,
            selectbackground=self.colors.bg_accent,
            selectforeground="white",
            activestyle="none"
        )
        self.image_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.image_listbox.yview)
        self.image_listbox.bind("<<ListboxSelect>>", self._on_image_select)

        button_row = ttk.Frame(img_section)
        button_row.pack(fill=tk.X, pady=(8, 0))

        ttk.Button(button_row, text="📂 Add Photos", command=self._on_add_photos).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6)
        )
        ttk.Button(button_row, text="🔄 Reload List", command=self._on_reload_list).pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )

    def _create_parameters_section(self, parent):
        """Create analysis parameters section"""
        params_bg = tk.Frame(parent, bg=self.colors.bg_secondary, highlightthickness=0)
        params_bg.pack(fill=tk.X, pady=(0, 12))

        params_frame = tk.Frame(params_bg, bg=self.colors.bg_secondary)
        params_frame.pack(fill=tk.X, padx=12, pady=12)

        params_header = tk.Label(
            params_frame,
            text="  Settings for This Bread",
            font=("Segoe UI", 11, "bold"),
            fg=self.colors.text_primary,
            bg=self.colors.bg_secondary
        )
        params_header.pack(anchor=tk.W, pady=(0, 12))

        params_grid_frame = tk.Frame(params_frame, bg=self.colors.bg_secondary)
        params_grid_frame.pack(fill=tk.X)

        # Pixel size
        pixel_label = tk.Label(
            params_grid_frame,
            text="Pixel Size (mm):",
            font=("Segoe UI", 8, "bold"),
            fg=self.colors.text_secondary,
            bg=self.colors.bg_secondary
        )
        pixel_label.grid(row=0, column=0, sticky=tk.W, pady=8)
        self.pixel_size_var = tk.DoubleVar(value=0.1)
        ttk.Entry(params_grid_frame, textvariable=self.pixel_size_var, width=18).grid(
            row=0, column=1, sticky=tk.E, padx=(10, 0)
        )

        # Threshold method
        thresh_label = tk.Label(
            params_grid_frame,
            text="Threshold Method:",
            font=("Segoe UI", 8, "bold"),
            fg=self.colors.text_secondary,
            bg=self.colors.bg_secondary
        )
        thresh_label.grid(row=1, column=0, sticky=tk.W, pady=8)
        self.threshold_var = tk.StringVar(value="otsu")
        ttk.Combobox(
            params_grid_frame,
            textvariable=self.threshold_var,
            values=["otsu", "adaptive"],
            state="readonly",
            width=16
        ).grid(row=1, column=1, sticky=tk.E, padx=(10, 0))

        # Normalization
        norm_label = tk.Label(
            params_grid_frame,
            text="Normalization:",
            font=("Segoe UI", 8, "bold"),
            fg=self.colors.text_secondary,
            bg=self.colors.bg_secondary
        )
        norm_label.grid(row=2, column=0, sticky=tk.W, pady=8)
        self.normalize_var = tk.StringVar(value="clahe")
        ttk.Combobox(
            params_grid_frame,
            textvariable=self.normalize_var,
            values=["clahe", "morphology", "gaussian"],
            state="readonly",
            width=16
        ).grid(row=2, column=1, sticky=tk.E, padx=(10, 0))

    def _create_mode_section(self, parent):
        """Create analysis mode section"""
        mode_bg = tk.Frame(parent, bg=self.colors.bg_secondary, highlightthickness=0)
        mode_bg.pack(fill=tk.X, pady=(0, 12))

        mode_frame = tk.Frame(mode_bg, bg=self.colors.bg_secondary)
        mode_frame.pack(fill=tk.X, padx=12, pady=12)

        mode_header = tk.Label(
            mode_frame,
            text="  What Are You Analyzing?",
            font=("Segoe UI", 11, "bold"),
            fg=self.colors.text_primary,
            bg=self.colors.bg_secondary
        )
        mode_header.pack(anchor=tk.W, pady=(0, 10))

        self.mode_var = tk.StringVar(value="single")
        ttk.Radiobutton(
            mode_frame,
            text="One Bread Slice",
            variable=self.mode_var,
            value="single"
        ).pack(anchor=tk.W, pady=4)
        ttk.Radiobutton(
            mode_frame,
            text="Whole Loaf (Many Slices)",
            variable=self.mode_var,
            value="loaf"
        ).pack(anchor=tk.W, pady=4)

        loaf_label = tk.Label(
            mode_frame,
            text="Loaf Name:",
            font=("Segoe UI", 8, "bold"),
            fg=self.colors.text_secondary,
            bg=self.colors.bg_secondary
        )
        loaf_label.pack(anchor=tk.W, pady=(10, 4))
        self.loaf_name_var = tk.StringVar(value="my_loaf")
        ttk.Entry(mode_frame, textvariable=self.loaf_name_var, width=30).pack(fill=tk.X)

    def _create_action_buttons(self, parent):
        """Create action buttons"""
        action_bg = tk.Frame(parent, bg=self.colors.bg_secondary, highlightthickness=0)
        action_bg.pack(fill=tk.X, pady=(0, 12))

        action_frame = tk.Frame(action_bg, bg=self.colors.bg_secondary)
        action_frame.pack(fill=tk.X, padx=12, pady=12)

        self.analyze_btn = tk.Button(
            action_frame,
            text="▶  Analyze Bread",
            command=self._on_analyze,
            bg=self.colors.bg_accent,
            fg="white",
            font=("Segoe UI", 11, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=14,
            cursor="hand2",
            activebackground=self.colors.bg_accent_hover,
            activeforeground="white",
            bd=0,
            highlightthickness=0
        )
        self.analyze_btn.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(action_frame, text="✕ Clear Photo Selection", command=self._on_clear_photo_selection).pack(fill=tk.X)

    def _create_status_section(self, parent):
        """Create status section"""
        status_bg = tk.Frame(parent, bg=self.colors.bg_secondary, highlightthickness=0)
        status_bg.pack(fill=tk.X)

        status_frame = tk.Frame(status_bg, bg=self.colors.bg_secondary)
        status_frame.pack(fill=tk.X, padx=12, pady=(8, 8))

        status_header = tk.Label(
            status_frame,
            text="  Status",
            font=("Segoe UI", 10, "bold"),
            fg=self.colors.text_primary,
            bg=self.colors.bg_secondary
        )
        status_header.pack(anchor=tk.W, pady=(0, 4))

        self.status_var = tk.StringVar(value="Ready")
        self.status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            foreground=self.colors.bg_success,
            font=("Segoe UI", 9),
            bg=self.colors.bg_secondary,
            wraplength=300,
            justify=tk.LEFT
        )
        self.status_label.pack(fill=tk.X)

        self.progress_bar = ttk.Progressbar(status_frame, mode='indeterminate', length=280)
        self.progress_bar.pack(fill=tk.X, pady=(4, 0))

    def _create_tabs(self):
        """Create all notebook tabs with full feature set"""
        # Preview tab
        preview_tab = ttk.Frame(self.notebook)
        self.notebook.add(preview_tab, text="  Preview")
        preview_bg = tk.Frame(preview_tab, bg=self.colors.bg_secondary)
        preview_bg.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.preview_label = tk.Label(
            preview_bg,
            text="Select an image to preview",
            bg=self.colors.bg_secondary,
            fg=self.colors.text_tertiary,
            font=("Segoe UI", 11)
        )
        self.preview_label.pack(fill=tk.BOTH, expand=True)

        # Results tab
        results_tab = ttk.Frame(self.notebook)
        self.notebook.add(results_tab, text="  Results")
        results_scroll = ttk.Scrollbar(results_tab)
        results_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text = tk.Text(
            results_tab,
            yscrollcommand=results_scroll.set,
            font=("Consolas", 9),
            bg=self.colors.bg_secondary,
            fg=self.colors.text_primary,
            relief=tk.FLAT,
            borderwidth=0,
            padx=12,
            pady=12
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
        results_scroll.config(command=self.results_text.yview)

        # Metrics tab
        metrics_tab = ttk.Frame(self.notebook)
        self.notebook.add(metrics_tab, text="  Metrics")
        metrics_scroll = ttk.Scrollbar(metrics_tab)
        metrics_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.metrics_text = tk.Text(
            metrics_tab,
            yscrollcommand=metrics_scroll.set,
            font=("Consolas", 9),
            bg=self.colors.bg_secondary,
            fg=self.colors.text_primary,
            relief=tk.FLAT,
            borderwidth=0,
            padx=12,
            pady=12
        )
        self.metrics_text.pack(fill=tk.BOTH, expand=True)
        metrics_scroll.config(command=self.metrics_text.yview)

        # Recipes tab
        recipe_tab = ttk.Frame(self.notebook)
        self.notebook.add(recipe_tab, text="  Recipes")
        recipe_container = ttk.Frame(recipe_tab)
        recipe_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        # Left side - Recipe input
        left_recipe_bg = tk.Frame(recipe_container, bg=self.colors.bg_secondary, highlightthickness=0)
        left_recipe_bg.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))

        left_recipe = tk.Frame(left_recipe_bg, bg=self.colors.bg_secondary)
        left_recipe.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        recipe_header_left = tk.Label(
            left_recipe,
            text="  New Recipe",
            font=("Segoe UI", 11, "bold"),
            fg=self.colors.text_primary,
            bg=self.colors.bg_secondary
        )
        recipe_header_left.pack(anchor=tk.W, pady=(0, 10))

        recipe_scroll = ttk.Scrollbar(left_recipe)
        recipe_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.recipe_input_text = tk.Text(
            left_recipe,
            yscrollcommand=recipe_scroll.set,
            font=("Consolas", 10),
            bg=self.colors.bg_tertiary,
            fg=self.colors.text_primary,
            relief=tk.FLAT,
            borderwidth=0,
            padx=8,
            pady=8,
            height=20
        )
        self.recipe_input_text.pack(fill=tk.BOTH, expand=True)
        recipe_scroll.config(command=self.recipe_input_text.yview)

        # Insert recipe template
        recipe_template = """# RECIPE FORMAT (JSON)
# Copy and edit this template

{
  "name": "Sourdough",
  "ingredients": {
    "flour": 500,
    "water": 350,
    "salt": 10,
    "starter": 50
  },
  "mixing_time_min": 10,
  "proof_time_min": 480,
  "oven_temp_c": 450,
  "cooking_vessel": "dutch oven",
  "cook_time_min": 40,
  "notes": "High hydration sourdough",
  "room_temp_c": 22.5,
  "room_humidity_pct": 65,
  "altitude_m": 100,
  "measured_porosity": null
}"""
        self.recipe_input_text.insert(1.0, recipe_template)
        self._setup_recipe_input_tags()

        # Right side - Recipe management
        right_recipe_bg = tk.Frame(recipe_container, bg=self.colors.bg_secondary, highlightthickness=0)
        right_recipe_bg.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        right_recipe = tk.Frame(right_recipe_bg, bg=self.colors.bg_secondary)
        right_recipe.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        recipe_header_right = tk.Label(
            right_recipe,
            text="  Recipe Management",
            font=("Segoe UI", 11, "bold"),
            fg=self.colors.text_primary,
            bg=self.colors.bg_secondary
        )
        recipe_header_right.pack(anchor=tk.W, pady=(0, 10))

        ttk.Label(right_recipe, text="Saved Recipes:").pack(anchor=tk.W, pady=(0, 8))

        recipe_listbox_frame = tk.Frame(right_recipe, bg=self.colors.bg_secondary)
        recipe_listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 12))

        recipe_scrollbar = ttk.Scrollbar(recipe_listbox_frame)
        recipe_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.recipe_listbox = tk.Listbox(
            recipe_listbox_frame,
            yscrollcommand=recipe_scrollbar.set,
            font=("Segoe UI", 9),
            bg=self.colors.bg_tertiary,
            fg=self.colors.text_primary,
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=1,
            highlightcolor=self.colors.bg_accent,
            selectbackground=self.colors.bg_accent,
            selectforeground="white",
            activestyle="none"
        )
        self.recipe_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.recipe_listbox.bind("<<ListboxSelect>>", self._on_recipe_select)
        recipe_scrollbar.config(command=self.recipe_listbox.yview)

        recipe_btn_frame = tk.Frame(right_recipe, bg=self.colors.bg_secondary)
        recipe_btn_frame.pack(fill=tk.X)

        ttk.Button(recipe_btn_frame, text=" Log Recipe", command=self._on_log_recipe).pack(fill=tk.X, pady=(0, 6))
        ttk.Button(recipe_btn_frame, text=" Save Porosity", command=self._on_save_porosity).pack(fill=tk.X, pady=(0, 6))
        ttk.Button(recipe_btn_frame, text=" Predict", command=self._on_predict).pack(fill=tk.X, pady=(0, 6))
        ttk.Button(recipe_btn_frame, text=" Create Variant", command=self._on_create_variant).pack(fill=tk.X, pady=(0, 6))
        ttk.Button(recipe_btn_frame, text=" Clone Recipe", command=self._on_clone_recipe).pack(fill=tk.X, pady=(0, 6))
        ttk.Button(recipe_btn_frame, text="📐 Scale Recipe", command=self._on_scale_recipe).pack(fill=tk.X, pady=(0, 6))
        ttk.Button(recipe_btn_frame, text=" Family Tree", command=self._on_family_tree).pack(fill=tk.X, pady=(0, 6))
        ttk.Button(recipe_btn_frame, text="  Delete", command=self._on_delete_recipe).pack(fill=tk.X)

        ttk.Label(right_recipe, text="Prediction Results:").pack(anchor=tk.W, pady=(10, 0))

        pred_scroll = ttk.Scrollbar(right_recipe)
        pred_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.prediction_text = tk.Text(
            right_recipe,
            yscrollcommand=pred_scroll.set,
            font=("Consolas", 9),
            bg=self.colors.bg_secondary,
            fg=self.colors.text_primary,
            relief=tk.FLAT,
            borderwidth=0,
            padx=8,
            pady=8,
            height=10
        )
        self.prediction_text.pack(fill=tk.BOTH, expand=True)
        pred_scroll.config(command=self.prediction_text.yview)

        # Statistics tab
        stats_tab = ttk.Frame(self.notebook)
        self.notebook.add(stats_tab, text="  Statistics")
        stats_scroll = ttk.Scrollbar(stats_tab)
        stats_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.stats_text = tk.Text(
            stats_tab,
            yscrollcommand=stats_scroll.set,
            font=("Consolas", 9),
            bg=self.colors.bg_secondary,
            fg=self.colors.text_primary,
            relief=tk.FLAT,
            borderwidth=0,
            padx=12,
            pady=12
        )
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        stats_scroll.config(command=self.stats_text.yview)

        stats_btn_frame = ttk.Frame(stats_tab)
        stats_btn_frame.pack(fill=tk.X, padx=12, pady=(0, 12))
        ttk.Button(stats_btn_frame, text="🔄 Refresh Statistics", command=self._on_refresh_statistics).pack(side=tk.LEFT)

        # Consistency tab
        consist_tab = ttk.Frame(self.notebook)
        self.notebook.add(consist_tab, text="  Consistency")
        consist_scroll = ttk.Scrollbar(consist_tab)
        consist_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.consist_text = tk.Text(
            consist_tab,
            yscrollcommand=consist_scroll.set,
            font=("Consolas", 9),
            bg=self.colors.bg_secondary,
            fg=self.colors.text_primary,
            relief=tk.FLAT,
            borderwidth=0,
            padx=12,
            pady=12
        )
        self.consist_text.pack(fill=tk.BOTH, expand=True)
        consist_scroll.config(command=self.consist_text.yview)

        # Compare tab
        compare_tab = ttk.Frame(self.notebook)
        self.notebook.add(compare_tab, text="  Compare")
        compare_scroll = ttk.Scrollbar(compare_tab)
        compare_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.compare_text = tk.Text(
            compare_tab,
            yscrollcommand=compare_scroll.set,
            font=("Consolas", 9),
            bg=self.colors.bg_secondary,
            fg=self.colors.text_primary,
            relief=tk.FLAT,
            borderwidth=0,
            padx=12,
            pady=12
        )
        self.compare_text.pack(fill=tk.BOTH, expand=True)
        compare_scroll.config(command=self.compare_text.yview)

        compare_btn_frame = ttk.Frame(compare_tab)
        compare_btn_frame.pack(fill=tk.X, padx=12, pady=(0, 12))
        ttk.Button(compare_btn_frame, text=" Compare Recipes", command=self._on_compare_recipes).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(compare_btn_frame, text=" What-If Analysis", command=self._on_what_if_analysis).pack(side=tk.LEFT)

        # Export tab
        export_tab = ttk.Frame(self.notebook)
        self.notebook.add(export_tab, text="  Export")
        export_container = ttk.Frame(export_tab)
        export_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        export_options_bg = tk.Frame(export_container, bg=self.colors.bg_secondary, highlightthickness=0)
        export_options_bg.pack(fill=tk.X, pady=(0, 12))

        export_options_frame = tk.Frame(export_options_bg, bg=self.colors.bg_secondary)
        export_options_frame.pack(fill=tk.X, padx=12, pady=12)

        export_header = tk.Label(
            export_options_frame,
            text="  Export Format",
            font=("Segoe UI", 11, "bold"),
            fg=self.colors.text_primary,
            bg=self.colors.bg_secondary
        )
        export_header.pack(anchor=tk.W, pady=(0, 10))

        ttk.Button(export_options_frame, text=" Export to CSV", command=self._on_export_csv).pack(fill=tk.X, pady=(0, 6))
        ttk.Button(export_options_frame, text=" Export to Excel", command=self._on_export_excel).pack(fill=tk.X, pady=(0, 6))
        ttk.Button(export_options_frame, text="📄 Generate PDF Report", command=self._on_generate_pdf).pack(fill=tk.X, pady=(0, 6))
        ttk.Button(export_options_frame, text="📉 Create Summary Charts", command=self._on_create_charts).pack(fill=tk.X)

        export_scroll = ttk.Scrollbar(export_container)
        export_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.export_text = tk.Text(
            export_container,
            yscrollcommand=export_scroll.set,
            font=("Consolas", 9),
            bg=self.colors.bg_tertiary,
            fg=self.colors.text_primary,
            relief=tk.FLAT,
            borderwidth=0,
            padx=12,
            pady=12
        )
        self.export_text.pack(fill=tk.BOTH, expand=True)
        export_scroll.config(command=self.export_text.yview)

        # Quality Control tab
        qc_tab = ttk.Frame(self.notebook)
        self.notebook.add(qc_tab, text="  Quality Control")
        qc_container = ttk.Frame(qc_tab)
        qc_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        qc_controls_frame = tk.Frame(qc_container, bg=self.colors.bg_secondary)
        qc_controls_frame.pack(fill=tk.X, pady=(0, 12))

        qc_header = tk.Label(
            qc_controls_frame,
            text="  Quality Control Tools",
            font=("Segoe UI", 11, "bold"),
            fg=self.colors.text_primary,
            bg=self.colors.bg_secondary
        )
        qc_header.pack(anchor=tk.W, pady=(0, 10))

        ttk.Button(qc_controls_frame, text=" Evaluate Current Analysis", command=self._on_evaluate_analysis).pack(fill=tk.X, pady=(0, 6))
        ttk.Button(qc_controls_frame, text="📦 Check Batch Consistency", command=self._on_check_batch_consistency).pack(fill=tk.X, pady=(0, 6))
        ttk.Button(qc_controls_frame, text=" SPC Statistics", command=self._on_spc_statistics).pack(fill=tk.X, pady=(0, 6))
        ttk.Button(qc_controls_frame, text="⚠  View Alerts", command=self._on_view_alerts).pack(fill=tk.X, pady=(0, 6))
        ttk.Button(qc_controls_frame, text="  Configure Thresholds", command=self._on_configure_thresholds).pack(fill=tk.X)

        qc_scroll = ttk.Scrollbar(qc_container)
        qc_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.qc_text = tk.Text(
            qc_container,
            yscrollcommand=qc_scroll.set,
            font=("Consolas", 9),
            bg=self.colors.bg_tertiary,
            fg=self.colors.text_primary,
            relief=tk.FLAT,
            borderwidth=0,
            padx=12,
            pady=12
        )
        self.qc_text.pack(fill=tk.BOTH, expand=True)
        qc_scroll.config(command=self.qc_text.yview)

        # Defects tab
        defect_tab = ttk.Frame(self.notebook)
        self.notebook.add(defect_tab, text="  Defects")
        defect_container = tk.Frame(defect_tab, bg=self.colors.bg_secondary)
        defect_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        defect_header = tk.Label(
            defect_container,
            text="Defect Detection",
            font=("Segoe UI", 11, "bold"),
            fg=self.colors.text_primary,
            bg=self.colors.bg_secondary
        )
        defect_header.pack(anchor=tk.W, pady=(0, 10))

        defect_controls = tk.Frame(defect_container, bg=self.colors.bg_secondary)
        defect_controls.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(defect_controls, text="Analyze Current Image", command=self._on_analyze_defect).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(defect_controls, text="Batch Analysis", command=self._on_batch_defect).pack(side=tk.LEFT, padx=(0, 5))

        defect_scroll = ttk.Scrollbar(defect_container)
        defect_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.defect_text = tk.Text(
            defect_container,
            yscrollcommand=defect_scroll.set,
            font=("Consolas", 9),
            bg=self.colors.bg_tertiary,
            fg=self.colors.text_primary,
            relief=tk.FLAT,
            borderwidth=0,
            padx=12,
            pady=12
        )
        self.defect_text.pack(fill=tk.BOTH, expand=True)
        defect_scroll.config(command=self.defect_text.yview)

        # ML Training tab
        ml_tab = ttk.Frame(self.notebook)
        self.notebook.add(ml_tab, text="  ML Training")
        ml_container = tk.Frame(ml_tab, bg=self.colors.bg_secondary)
        ml_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        ml_header = tk.Label(
            ml_container,
            text="Machine Learning Classifier",
            font=("Segoe UI", 11, "bold"),
            fg=self.colors.text_primary,
            bg=self.colors.bg_secondary
        )
        ml_header.pack(anchor=tk.W, pady=(0, 10))

        ml_buttons = tk.Frame(ml_container, bg=self.colors.bg_secondary)
        ml_buttons.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(ml_buttons, text="Add Good Image", command=self._on_add_good_image).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(ml_buttons, text="Add Problem Image", command=self._on_add_problem_image).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(ml_buttons, text="Train Model", command=self._on_train_model).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(ml_buttons, text="Predict Current", command=self._on_predict_current).pack(side=tk.LEFT)

        ml_scroll = ttk.Scrollbar(ml_container)
        ml_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.ml_text = tk.Text(
            ml_container,
            yscrollcommand=ml_scroll.set,
            font=("Consolas", 9),
            bg=self.colors.bg_tertiary,
            fg=self.colors.text_primary,
            relief=tk.FLAT,
            borderwidth=0,
            padx=12,
            pady=12
        )
        self.ml_text.pack(fill=tk.BOTH, expand=True)
        ml_scroll.config(command=self.ml_text.yview)

    def _setup_recipe_input_tags(self):
        """Setup syntax highlighting tags for recipe input"""
        # Configure tags for JSON highlighting
        self.recipe_input_text.tag_config("comment", foreground=self.colors.text_tertiary, font=("Consolas", 10, "italic"))
        self.recipe_input_text.tag_config("string", foreground=self.colors.bg_success)
        self.recipe_input_text.tag_config("key", foreground=self.colors.bg_accent)
        self.recipe_input_text.tag_config("value", foreground=self.colors.text_primary)
        
        # Highlight comment lines
        content = self.recipe_input_text.get("1.0", "end")
        start_idx = "1.0"
        for line in content.split('\n'):
            end_idx = f"{start_idx.split('.')[0]}.end"
            if line.strip().startswith('#'):
                self.recipe_input_text.tag_add("comment", start_idx, end_idx)
            start_idx = f"{int(start_idx.split('.')[0]) + 1}.0"

    def _show_first_time_setup(self):
        """Show first-time setup wizard for initial configuration"""
        # Check if first-run setup should be shown
        from first_run_wizard import FirstRunWizard
        
        try:
            wizard = FirstRunWizard(self.root, "config.json")
            if wizard.should_show_wizard():
                # Run the interactive wizard
                wizard.run_wizard()
                logger.info("First-run wizard completed")
            else:
                # Not first run - show brief startup message
                self._show_startup_message()
        except Exception as e:
            logger.warning(f"Could not launch first-run wizard: {e}")
            self._show_startup_message()

    def _show_startup_message(self):
        """Show welcome message in results tab"""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        
        startup_msg = """
═══════════════════════════════════════════════════════════════════
           BREAD POROSITY ANALYSIS TOOL - Ready to analyze
═══════════════════════════════════════════════════════════════════

Application started successfully.

QUICK START:

1. IMAGE LIBRARY
   • Add bread images using the Image Library panel
   • Ensure consistent lighting and positioning

2. RECIPES
   • Go to the "Recipes" tab
   • Edit the JSON template with your recipe details
   • Click "Log Recipe" to save

3. ANALYZE
   • Select an image and adjust parameters
   • Click "Analyze" button
   • Review results in the Results tab

4. OPTIMIZE
   • Use "Compare" tab for recipe variations
   • Use "Predict" for porosity estimates
   • Track consistency over time

Next steps:
• Select an image to analyze
• Go to Recipes tab to manage your recipes
• Click "Analyze" when ready

For help, check the documentation or hover over buttons.

═══════════════════════════════════════════════════════════════════
"""
        self.results_text.insert(1.0, startup_msg)
        self.results_text.config(state=tk.DISABLED)

    def _load_initial_recipes(self):
        """Load initial recipes from database if available"""
        try:
            recipes = self.recipe_service.get_all_recipes()
            if recipes:
                self.recipe_listbox.delete(0, tk.END)
                for recipe in recipes:
                    recipe_name = recipe.get('name', 'Unnamed Recipe')
                    self.recipe_listbox.insert(tk.END, recipe_name)
        except Exception as e:
            logger.warning(f"Could not load initial recipes: {e}")

    def _on_recipe_select(self, event):
        """Handle recipe selection from listbox"""
        selection = self.recipe_listbox.curselection()
        if selection:
            recipe_idx = selection[0]
            # Load recipe details - to be integrated with recipe service
            pass

    def _on_image_select(self, event):
        """Handle image selection"""
        selection = self.image_listbox.curselection()
        if selection:
            index = selection[0]
            filename = self.image_listbox.get(index)
            self.status_var.set(f"Selected: {filename}")

    def _on_analyze(self):
        """Handle analyze button click"""
        self.status_var.set("Analysis started...")
        self.progress_bar.start()

    def _update_status(self, message: str, status_type: str = 'info') -> None:
        """Update status message"""
        color_map = {
            'success': self.colors.bg_success,
            'warning': self.colors.bg_warning,
            'error': self.colors.bg_error,
            'info': self.colors.text_primary
        }
        self.status_var.set(message)
        self.status_label.config(foreground=color_map.get(status_type, self.colors.text_primary))

    def _load_config(self) -> None:
        """Load configuration"""
        try:
            config = self.config_repo.load_config()
            logger.info("Configuration loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load config: {e}")

    def run(self) -> None:
        """Start the application main loop"""
        logger.info("Starting Bread Porosity Analysis Tool")
        self.root.mainloop()

    def quit(self) -> None:
        """Quit the application"""
        logger.info("Shutting down Bread Porosity Analysis Tool")
        self.root.quit()
