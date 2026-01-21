"""
GUI for Bread Porosity Analysis Tool
User-friendly interface for analyzing bread images, managing loaves, and logging recipes
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from pathlib import Path
import threading
from PIL import Image, ImageTk
import json
from datetime import datetime
from analyze import analyze_bread_image
from loaf_analyzer import analyze_loaf
from recipe_database import RecipeDatabase
from recipe_predictor import RecipePredictor
from export_reporting import ExportEngine
from quality_control import QualityControlManager
from defect_detection import DefectDetector
from ml_simple import SimpleMLClassifier
import traceback

# NEW: Import usability improvements
from first_run_wizard import FirstRunWizard
from image_quality_validator import ImageQualityValidator
from result_presenter import ResultPresenter
from recipe_builder_form import RecipeBuilderForm


class BreadPorositytoolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Bread Porosity Analysis Tool")
        self.root.geometry("1400x900")
        
        # Modern professional color scheme (Flat Design + Material Design inspired)
        self.bg_primary = "#0f1419"       # Dark navy background
        self.bg_secondary = "#1a1f2e"    # Dark card background
        self.bg_tertiary = "#252c3c"     # Light dark background
        self.bg_accent = "#1d9bf0"       # Modern blue
        self.bg_accent_hover = "#1a8cd8" # Darker blue on hover
        self.bg_success = "#17bf63"      # Modern green
        self.bg_warning = "#ffb81c"      # Modern yellow
        self.bg_error = "#f7555f"        # Modern red
        self.text_primary = "#ffffff"    # White text
        self.text_secondary = "#b0b9c1"  # Light gray text
        self.text_tertiary = "#8a91a1"   # Darker gray
        self.border_color = "#364558"    # Modern border
        self.success_color = "#17bf63"
        self.warning_color = "#ffb81c"
        self.error_color = "#f7555f"
        
        self.root.configure(bg=self.bg_primary)
        
        # Configure style with modern dark theme
        style = ttk.Style()
        style.theme_use('clam')
        
        # Define custom colors for ttk
        style.configure("TFrame", background=self.bg_primary)
        style.configure("Card.TFrame", background=self.bg_secondary, relief="flat")
        
        style.configure("TLabelframe", background=self.bg_secondary, foreground=self.text_primary, 
                       borderwidth=0, relief="flat")
        style.configure("TLabelframe.Label", background=self.bg_secondary, foreground=self.text_primary,
                       font=("Segoe UI", 11, "bold"))
        
        style.configure("TLabel", background=self.bg_primary, foreground=self.text_primary,
                       font=("Segoe UI", 9))
        style.configure("Header.TLabel", background=self.bg_primary, foreground=self.text_primary, 
                       font=("Segoe UI", 13, "bold"))
        style.configure("Subheader.TLabel", background=self.bg_secondary, foreground=self.text_secondary,
                       font=("Segoe UI", 8, "bold"))
        style.configure("Subtitle.TLabel", background=self.bg_secondary, foreground=self.text_secondary,
                       font=("Segoe UI", 8))
        
        # Modern button styling with rounded appearance
        style.configure("TButton", font=("Segoe UI", 9), relief="flat", padding=8,
                       background=self.bg_tertiary, foreground=self.text_primary, 
                       borderwidth=0)
        style.map("TButton",
                 background=[("pressed", self.bg_accent), ("active", self.bg_accent_hover), 
                            ("!active", self.bg_tertiary)],
                 foreground=[("pressed", "white"), ("active", "white"), ("!active", self.text_primary)],
                 relief=[("pressed", "flat"), ("active", "flat")])
        
        # Accent button style
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), relief="flat", 
                       padding=10, background=self.bg_accent, foreground="white", borderwidth=0)
        style.map("Accent.TButton",
                 background=[("pressed", self.bg_accent_hover), ("active", self.bg_accent_hover),
                            ("!active", self.bg_accent)],
                 foreground=[("pressed", "white"), ("active", "white"), ("!active", "white")])
        
        # Combobox styling
        style.configure("TCombobox", font=("Segoe UI", 9), fieldbackground=self.bg_tertiary,
                       background=self.bg_tertiary, foreground=self.text_primary)
        style.map("TCombobox",
                 fieldbackground=[("focus", self.bg_accent), ("!focus", self.bg_tertiary)],
                 background=[("focus", self.bg_accent), ("!focus", self.bg_tertiary)])
        
        # Notebook (tabs) styling
        style.configure("TNotebook", background=self.bg_primary, borderwidth=0)
        style.configure("TNotebook.Tab", padding=[16, 12], font=("Segoe UI", 10, "bold"),
                       background=self.bg_tertiary, foreground=self.text_secondary)
        style.map("TNotebook.Tab", 
                 background=[("selected", self.bg_accent), ("!selected", self.bg_tertiary)],
                 foreground=[("selected", "white"), ("!selected", self.text_secondary)])
        
        # Radio and Checkbutton styling
        style.configure("TRadiobutton", background=self.bg_secondary, foreground=self.text_primary,
                       font=("Segoe UI", 9))
        style.map("TRadiobutton",
                 background=[("active", self.bg_secondary), ("!active", self.bg_secondary)])
        
        style.configure("TCheckbutton", background=self.bg_secondary, foreground=self.text_primary,
                       font=("Segoe UI", 9))
        style.map("TCheckbutton",
                 background=[("active", self.bg_secondary), ("!active", self.bg_secondary)])
        
        # Scrollbar styling
        style.configure("Vertical.TScrollbar", background=self.bg_tertiary, troughcolor=self.bg_secondary,
                       arrowcolor=self.text_secondary, borderwidth=0)
        
        # Setup directories
        self.unprocessed_dir = Path("unprocessed")
        self.processed_dir = Path("processed")
        self.results_dir = Path("results")
        self.output_dir = Path("output")
        
        for d in [self.unprocessed_dir, self.processed_dir, self.results_dir, self.output_dir]:
            d.mkdir(exist_ok=True)
        
        # Initialize recipe database and predictor
        self.recipe_db = RecipeDatabase("recipes.json")
        self.recipe_predictor = RecipePredictor(self.recipe_db.get_recipes_with_porosity())
        
        # Initialize export and quality control managers
        self.export_engine = ExportEngine(output_dir=str(self.output_dir))
        self.qc_manager = QualityControlManager(config_file="qc_config.json")
        
        # NEW: Initialize usability modules
        self.image_quality_validator = ImageQualityValidator(verbose=False)
        self.result_presenter = ResultPresenter(simple_mode=True)  # Start in simple mode
        
        # NEW: Show first-run wizard if needed
        self._check_first_run()
        
        self.current_image = None
        self.current_image_path = None
        self.analysis_result = None
        self.analysis_history = []  # Track all analyses for batch operations
        self.current_recipe_id = None
        
        self.setup_ui()
        self.refresh_image_list()
    
    def setup_ui(self):
        """Setup the user interface with modern professional styling"""
        
        # Header with gradient-like effect using dark background
        header = ttk.Frame(self.root)
        header.pack(fill=tk.X, padx=0, pady=0)
        
        header_bg = tk.Frame(header, bg=self.bg_accent, height=80)
        header_bg.pack(fill=tk.X)
        
        # Header content with branding
        header_content = tk.Frame(header_bg, bg=self.bg_accent)
        header_content.pack(fill=tk.BOTH, expand=True, padx=25, pady=0)
        
        title_label = tk.Label(header_content, text="  Bread Porosity Analysis", 
                               font=("Segoe UI", 20, "bold"), fg="white", bg=self.bg_accent)
        title_label.pack(anchor=tk.W, pady=(15, 5))
        
        subtitle_label = tk.Label(header_content, text="Professional Analysis & Quality Control", 
                                 font=("Segoe UI", 9), fg=self.text_secondary, bg=self.bg_accent)
        subtitle_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Main container with padding
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        
        # Left panel - Controls with enhanced styling
        left_panel = ttk.Frame(main_container, width=340)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 12))
        
        # Image Management Section
        img_section_bg = tk.Frame(left_panel, bg=self.bg_secondary, highlightthickness=0)
        img_section_bg.pack(fill=tk.BOTH, expand=True, pady=(0, 12))
        
        img_section = tk.Frame(img_section_bg, bg=self.bg_secondary)
        img_section.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        img_header = tk.Label(img_section, text="📁  Image Library", 
                             font=("Segoe UI", 11, "bold"), fg=self.text_primary, bg=self.bg_secondary)
        img_header.pack(anchor=tk.W, pady=(0, 12))
        
        # Listbox with professional styling
        listbox_frame = ttk.Frame(img_section)
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.image_listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set, 
                                         height=12, font=("Segoe UI", 9), 
                                         bg=self.bg_tertiary, fg=self.text_primary,
                                         relief=tk.FLAT, borderwidth=0, highlightthickness=1,
                                         highlightcolor=self.bg_accent, selectbackground=self.bg_accent,
                                         selectforeground="white", activestyle="none")
        self.image_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.image_listbox.yview)
        self.image_listbox.bind("<<ListboxSelect>>", self.on_image_select)
        
        # Button row with better spacing
        button_row = ttk.Frame(img_section)
        button_row.pack(fill=tk.X, pady=(8, 0))
        
        ttk.Button(button_row, text="📂 Open Folder", 
                  command=self.open_folder).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        ttk.Button(button_row, text="🔄 Refresh", 
                  command=self.refresh_image_list).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Parameters Section
        params_bg = tk.Frame(left_panel, bg=self.bg_secondary, highlightthickness=0)
        params_bg.pack(fill=tk.X, pady=(0, 12))
        
        params_frame = tk.Frame(params_bg, bg=self.bg_secondary)
        params_frame.pack(fill=tk.X, padx=12, pady=12)
        
        params_header = tk.Label(params_frame, text="  Analysis Parameters", 
                                font=("Segoe UI", 11, "bold"), fg=self.text_primary, bg=self.bg_secondary)
        params_header.pack(anchor=tk.W, pady=(0, 12))
        
        # Grid frame for parameters (separate from pack-based layout)
        params_grid_frame = tk.Frame(params_frame, bg=self.bg_secondary)
        params_grid_frame.pack(fill=tk.X)
        
        # Pixel size with label styling
        pixel_label = tk.Label(params_grid_frame, text="Pixel Size (mm):", 
                              font=("Segoe UI", 8, "bold"), fg=self.text_secondary, bg=self.bg_secondary)
        pixel_label.grid(row=0, column=0, sticky=tk.W, pady=8)
        self.pixel_size_var = tk.DoubleVar(value=0.1)
        pixel_entry = ttk.Entry(params_grid_frame, textvariable=self.pixel_size_var, width=18)
        pixel_entry.grid(row=0, column=1, sticky=tk.E, padx=(10, 0))
        
        # Threshold method
        thresh_label = tk.Label(params_grid_frame, text="Threshold Method:", 
                               font=("Segoe UI", 8, "bold"), fg=self.text_secondary, bg=self.bg_secondary)
        thresh_label.grid(row=1, column=0, sticky=tk.W, pady=8)
        self.threshold_var = tk.StringVar(value="otsu")
        ttk.Combobox(params_grid_frame, textvariable=self.threshold_var, 
                    values=["otsu", "adaptive"], state="readonly", width=16).grid(
            row=1, column=1, sticky=tk.E, padx=(10, 0))
        
        # Normalization
        norm_label = tk.Label(params_grid_frame, text="Normalization:", 
                             font=("Segoe UI", 8, "bold"), fg=self.text_secondary, bg=self.bg_secondary)
        norm_label.grid(row=2, column=0, sticky=tk.W, pady=8)
        self.normalize_var = tk.StringVar(value="clahe")
        ttk.Combobox(params_grid_frame, textvariable=self.normalize_var,
                    values=["clahe", "morphology", "gaussian"], state="readonly", width=16).grid(
            row=2, column=1, sticky=tk.E, padx=(10, 0))
        
        # Mode Selection
        mode_bg = tk.Frame(left_panel, bg=self.bg_secondary, highlightthickness=0)
        mode_bg.pack(fill=tk.X, pady=(0, 12))
        
        mode_frame = tk.Frame(mode_bg, bg=self.bg_secondary)
        mode_frame.pack(fill=tk.X, padx=12, pady=12)
        
        mode_header = tk.Label(mode_frame, text="  Analysis Mode", 
                              font=("Segoe UI", 11, "bold"), fg=self.text_primary, bg=self.bg_secondary)
        mode_header.pack(anchor=tk.W, pady=(0, 10))
        
        self.mode_var = tk.StringVar(value="single")
        ttk.Radiobutton(mode_frame, text="Single Image", variable=self.mode_var, 
                       value="single", command=self.on_mode_change).pack(anchor=tk.W, pady=4)
        ttk.Radiobutton(mode_frame, text="Loaf (Multiple Slices)", variable=self.mode_var,
                       value="loaf", command=self.on_mode_change).pack(anchor=tk.W, pady=4)
        
        # Loaf name
        loaf_label = tk.Label(mode_frame, text="Loaf Name:", 
                             font=("Segoe UI", 8, "bold"), fg=self.text_secondary, bg=self.bg_secondary)
        loaf_label.pack(anchor=tk.W, pady=(10, 4))
        self.loaf_name_var = tk.StringVar(value="my_loaf")
        self.loaf_name_entry = ttk.Entry(mode_frame, textvariable=self.loaf_name_var, width=30)
        self.loaf_name_entry.pack(fill=tk.X)
        self.loaf_name_entry.config(state=tk.DISABLED)
        
        # Action Buttons with professional styling
        action_bg = tk.Frame(left_panel, bg=self.bg_secondary, highlightthickness=0)
        action_bg.pack(fill=tk.X, pady=(0, 12))
        
        action_frame = tk.Frame(action_bg, bg=self.bg_secondary)
        action_frame.pack(fill=tk.X, padx=12, pady=12)
        
        self.analyze_btn = tk.Button(action_frame, text="▶  Analyze", 
                                     command=self.start_analysis,
                                     bg=self.bg_accent, fg="white",
                                     font=("Segoe UI", 11, "bold"),
                                     relief=tk.FLAT, padx=20, pady=14,
                                     cursor="hand2", activebackground=self.bg_accent_hover,
                                     activeforeground="white", bd=0, highlightthickness=0)
        self.analyze_btn.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(action_frame, text="✕ Clear Selection", 
                  command=self.clear_selection).pack(fill=tk.X)
        
        # Status Section
        status_bg = tk.Frame(left_panel, bg=self.bg_secondary, highlightthickness=0)
        status_bg.pack(fill=tk.X)
        
        status_frame = tk.Frame(status_bg, bg=self.bg_secondary)
        status_frame.pack(fill=tk.X, padx=12, pady=(8, 8))
        
        status_header = tk.Label(status_frame, text="  Status", 
                                font=("Segoe UI", 10, "bold"), fg=self.text_primary, bg=self.bg_secondary)
        status_header.pack(anchor=tk.W, pady=(0, 4))
        
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = tk.Label(status_frame, textvariable=self.status_var, 
                                    foreground=self.success_color, 
                                    font=("Segoe UI", 9),
                                    bg=self.bg_secondary, wraplength=300, justify=tk.LEFT)
        self.status_label.pack(fill=tk.X)
        
        # Progress bar
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate', length=280)
        self.progress.pack(fill=tk.X, pady=(4, 0))
        
        # Right panel - Results with modern notebook
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Notebook with modern tabs
        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Preview tab
        preview_tab = ttk.Frame(self.notebook)
        self.notebook.add(preview_tab, text="  Preview")
        
        preview_bg = tk.Frame(preview_tab, bg=self.bg_secondary)
        preview_bg.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        self.preview_label = tk.Label(preview_bg, text="Select an image to preview", 
                                      bg=self.bg_secondary, fg=self.text_tertiary,
                                      font=("Segoe UI", 11))
        self.preview_label.pack(fill=tk.BOTH, expand=True)
        
        # Results tab
        results_tab = ttk.Frame(self.notebook)
        self.notebook.add(results_tab, text="  Results")
        
        results_scroll = ttk.Scrollbar(results_tab)
        results_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.results_text = tk.Text(results_tab, yscrollcommand=results_scroll.set,
                                    font=("Consolas", 9), bg=self.bg_secondary,
                                    fg=self.text_primary, relief=tk.FLAT, 
                                    borderwidth=0, padx=12, pady=12)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        results_scroll.config(command=self.results_text.yview)
        self.results_text.insert(1.0, "Analyze an image to see results here...")
        self.results_text.config(state=tk.DISABLED)  # Read-only until analysis
        
        # Metrics tab
        metrics_tab = ttk.Frame(self.notebook)
        self.notebook.add(metrics_tab, text="  Metrics")
        
        metrics_scroll = ttk.Scrollbar(metrics_tab)
        metrics_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.metrics_text = tk.Text(metrics_tab, yscrollcommand=metrics_scroll.set,
                                   font=("Consolas", 9), bg=self.bg_secondary,
                                   fg=self.text_primary, relief=tk.FLAT,
                                   borderwidth=0, padx=12, pady=12)
        self.metrics_text.pack(fill=tk.BOTH, expand=True)
        metrics_scroll.config(command=self.metrics_text.yview)
        self.metrics_text.insert(1.0, "Analyze an image to see metrics here...")
        self.metrics_text.config(state=tk.DISABLED)
        
        # Recipe Management tab
        recipe_tab = ttk.Frame(self.notebook)
        self.notebook.add(recipe_tab, text="  Recipes")
        
        recipe_container = ttk.Frame(recipe_tab)
        recipe_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        # Left side - Recipe input
        left_recipe_bg = tk.Frame(recipe_container, bg=self.bg_secondary, highlightthickness=0)
        left_recipe_bg.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))
        
        left_recipe = tk.Frame(left_recipe_bg, bg=self.bg_secondary)
        left_recipe.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        recipe_header_left = tk.Label(left_recipe, text="  New Recipe", 
                                      font=("Segoe UI", 11, "bold"), fg=self.text_primary, bg=self.bg_secondary)
        recipe_header_left.pack(anchor=tk.W, pady=(0, 10))
        
        recipe_scroll = ttk.Scrollbar(left_recipe)
        recipe_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.recipe_input_text = tk.Text(left_recipe, yscrollcommand=recipe_scroll.set,
                                        font=("Consolas", 12), bg=self.bg_tertiary,
                                        fg=self.text_primary, relief=tk.FLAT,
                                        borderwidth=0, padx=8, pady=8, height=25,
                                        insertbackground=self.bg_accent)
        self.recipe_input_text.pack(fill=tk.BOTH, expand=True)
        recipe_scroll.config(command=self.recipe_input_text.yview)
        
        # Insert template
        template = """# RECIPE FORMAT (JSON)
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
  "measured_porosity": null,
  "steps": [
    "Mix flour and water, autolyse for 30 minutes",
    "Add starter and salt, mix until combined",
    "Perform 4 sets of stretch and folds, 30 min apart",
    "Bulk ferment at room temp until doubled",
    "Pre-shape and rest 20 minutes",
    "Final shape and place in banneton",
    "Cold retard in fridge overnight",
    "Preheat dutch oven at 450°F/230°C for 1 hour",
    "Score dough and bake covered for 20 minutes",
    "Remove lid and bake 20 more minutes",
    "Cool on wire rack before slicing"
  ]
}"""
        self.recipe_input_text.insert(1.0, template)
        
        # Right side - Recipe management and prediction
        right_recipe_bg = tk.Frame(recipe_container, bg=self.bg_secondary, highlightthickness=0)
        right_recipe_bg.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        right_recipe = tk.Frame(right_recipe_bg, bg=self.bg_secondary)
        right_recipe.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        recipe_header_right = tk.Label(right_recipe, text="  Recipe Management", 
                                       font=("Segoe UI", 11, "bold"), fg=self.text_primary, bg=self.bg_secondary)
        recipe_header_right.pack(anchor=tk.W, pady=(0, 10))
        
        # Recipe list label
        recipe_list_label = tk.Label(right_recipe, text="Saved Recipes:", 
                                     font=("Segoe UI", 9), fg=self.text_secondary, bg=self.bg_secondary)
        recipe_list_label.pack(anchor=tk.W, pady=(0, 8))
        
        recipe_listbox_frame = tk.Frame(right_recipe, bg=self.bg_secondary)
        recipe_listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 12))
        
        recipe_scrollbar = ttk.Scrollbar(recipe_listbox_frame)
        recipe_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.recipe_listbox = tk.Listbox(recipe_listbox_frame, yscrollcommand=recipe_scrollbar.set,
                                        font=("Segoe UI", 9), bg=self.bg_tertiary,
                                        fg=self.text_primary, relief=tk.FLAT,
                                        borderwidth=0, highlightthickness=1,
                                        highlightcolor=self.bg_accent, selectbackground=self.bg_accent,
                                        selectforeground="white", activestyle="none")
        self.recipe_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.recipe_listbox.bind("<<ListboxSelect>>", self.on_recipe_select)
        recipe_scrollbar.config(command=self.recipe_listbox.yview)
        
        # Recipe buttons
        recipe_btn_frame = tk.Frame(right_recipe, bg=self.bg_secondary)
        recipe_btn_frame.pack(fill=tk.X)
        
        ttk.Button(recipe_btn_frame, text=" Log Recipe", 
                  command=self.log_new_recipe).pack(fill=tk.X, pady=(0, 6))
        ttk.Button(recipe_btn_frame, text=" Save Porosity", 
                  command=self.save_recipe_porosity).pack(fill=tk.X, pady=(0, 6))
        ttk.Button(recipe_btn_frame, text=" Predict", 
                  command=self.predict_from_recipe).pack(fill=tk.X, pady=(0, 6))
        ttk.Button(recipe_btn_frame, text=" Create Variant", 
                  command=self.create_recipe_variant).pack(fill=tk.X, pady=(0, 6))
        ttk.Button(recipe_btn_frame, text=" Clone Recipe", 
                  command=self.clone_recipe).pack(fill=tk.X, pady=(0, 6))
        ttk.Button(recipe_btn_frame, text="📐 Scale Recipe", 
                  command=self.scale_recipe_gui).pack(fill=tk.X, pady=(0, 6))
        ttk.Button(recipe_btn_frame, text=" Family Tree", 
                  command=self.display_recipe_family).pack(fill=tk.X, pady=(0, 6))
        ttk.Button(recipe_btn_frame, text="  Delete", 
                  command=self.delete_recipe).pack(fill=tk.X)
        
        # Prediction results
        ttk.Label(right_recipe, text="Prediction Results:").pack(anchor=tk.W, pady=(10, 0))
        
        pred_scroll = ttk.Scrollbar(right_recipe)
        pred_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.prediction_text = tk.Text(right_recipe, yscrollcommand=pred_scroll.set,
                                      font=("Consolas", 9), bg=self.bg_secondary,
                                      fg=self.text_primary, relief=tk.FLAT,
                                      borderwidth=0, padx=8, pady=8, height=10)
        self.prediction_text.pack(fill=tk.BOTH, expand=True)
        pred_scroll.config(command=self.prediction_text.yview)
        
        # Statistics Dashboard tab
        stats_tab = ttk.Frame(self.notebook)
        self.notebook.add(stats_tab, text="  Statistics")
        
        stats_scroll = ttk.Scrollbar(stats_tab)
        stats_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.stats_text = tk.Text(stats_tab, yscrollcommand=stats_scroll.set,
                                 font=("Consolas", 9), bg=self.bg_secondary,
                                 fg=self.text_primary, relief=tk.FLAT,
                                 borderwidth=0, padx=12, pady=12,
                                 insertbackground=self.bg_accent)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        stats_scroll.config(command=self.stats_text.yview)
        self.stats_text.insert(1.0, "Click 'Refresh Statistics' to view statistics...")
        self.stats_text.config(state=tk.DISABLED)
        
        # Button to refresh stats
        stats_btn_frame = ttk.Frame(stats_tab)
        stats_btn_frame.pack(fill=tk.X, padx=12, pady=(0, 12))
        ttk.Button(stats_btn_frame, text="🔄 Refresh Statistics", 
                  command=self.display_statistics_dashboard).pack(side=tk.LEFT)
        
        # Loaf Consistency Tracking tab
        consist_tab = ttk.Frame(self.notebook)
        self.notebook.add(consist_tab, text="  Consistency")
        
        consist_scroll = ttk.Scrollbar(consist_tab)
        consist_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.consist_text = tk.Text(consist_tab, yscrollcommand=consist_scroll.set,
                                   font=("Consolas", 9), bg=self.bg_secondary,
                                   fg=self.text_primary, relief=tk.FLAT,
                                   borderwidth=0, padx=12, pady=12,
                                   insertbackground=self.bg_accent)
        self.consist_text.pack(fill=tk.BOTH, expand=True)
        consist_scroll.config(command=self.consist_text.yview)
        self.consist_text.insert(1.0, "Analyze a loaf to see consistency data here...")
        self.consist_text.config(state=tk.DISABLED)
        
        # Comparison Tools tab
        compare_tab = ttk.Frame(self.notebook)
        self.notebook.add(compare_tab, text="  Compare")
        
        compare_scroll = ttk.Scrollbar(compare_tab)
        compare_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.compare_text = tk.Text(compare_tab, yscrollcommand=compare_scroll.set,
                                   font=("Consolas", 9), bg=self.bg_secondary,
                                   fg=self.text_primary, relief=tk.FLAT,
                                   borderwidth=0, padx=12, pady=12,
                                   insertbackground=self.bg_accent)
        self.compare_text.pack(fill=tk.BOTH, expand=True)
        compare_scroll.config(command=self.compare_text.yview)
        self.compare_text.insert(1.0, "Click 'Compare Recipes' or 'What-If Analysis' to see comparisons...")
        self.compare_text.config(state=tk.DISABLED)
        
        # Buttons for comparison
        compare_btn_frame = ttk.Frame(compare_tab)
        compare_btn_frame.pack(fill=tk.X, padx=12, pady=(0, 12))
        ttk.Button(compare_btn_frame, text=" Compare Recipes", 
                  command=self.compare_recipes).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(compare_btn_frame, text=" What-If Analysis", 
                  command=self.what_if_analysis).pack(side=tk.LEFT)
        
        # Export & Reporting tab
        export_tab = ttk.Frame(self.notebook)
        self.notebook.add(export_tab, text="  Export")
        
        export_container = ttk.Frame(export_tab)
        export_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        # Export options
        export_options_bg = tk.Frame(export_container, bg=self.bg_secondary, highlightthickness=0)
        export_options_bg.pack(fill=tk.X, pady=(0, 12))
        
        export_options_frame = tk.Frame(export_options_bg, bg=self.bg_secondary)
        export_options_frame.pack(fill=tk.X, padx=12, pady=12)
        
        export_header = tk.Label(export_options_frame, text="  Export Format", 
                                font=("Segoe UI", 11, "bold"), fg=self.text_primary, bg=self.bg_secondary)
        export_header.pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Button(export_options_frame, text=" Export to CSV", 
                  command=self.export_batch_csv).pack(fill=tk.X, pady=(0, 6))
        ttk.Button(export_options_frame, text=" Export to Excel", 
                  command=self.export_batch_excel).pack(fill=tk.X, pady=(0, 6))
        ttk.Button(export_options_frame, text="📄 Generate PDF Report", 
                  command=self.export_batch_pdf).pack(fill=tk.X, pady=(0, 6))
        ttk.Button(export_options_frame, text="📉 Create Summary Charts", 
                  command=self.create_summary_charts).pack(fill=tk.X)
        
        # Export results display
        export_scroll = ttk.Scrollbar(export_container)
        export_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.export_text = tk.Text(export_container, yscrollcommand=export_scroll.set,
                                   font=("Consolas", 9), bg=self.bg_tertiary,
                                   fg=self.text_primary, relief=tk.FLAT,
                                   borderwidth=0, padx=12, pady=12,
                                   insertbackground=self.bg_accent)
        self.export_text.pack(fill=tk.BOTH, expand=True)
        export_scroll.config(command=self.export_text.yview)
        
        # Quality Control tab
        qc_tab = ttk.Frame(self.notebook)
        self.notebook.add(qc_tab, text="  Quality Control")
        
        qc_container = ttk.Frame(qc_tab)
        qc_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        # Bread Type Selector
        bread_type_bg = tk.Frame(qc_container, bg=self.bg_secondary, highlightthickness=0)
        bread_type_bg.pack(fill=tk.X, pady=(0, 12))
        
        bread_type_frame = tk.Frame(bread_type_bg, bg=self.bg_secondary)
        bread_type_frame.pack(fill=tk.X, padx=12, pady=12)
        
        bread_header = tk.Label(bread_type_frame, text="  Bread Type Profile", 
                               font=("Segoe UI", 11, "bold"), fg=self.text_primary, bg=self.bg_secondary)
        bread_header.pack(anchor=tk.W, pady=(0, 10))
        
        bread_selector_row = tk.Frame(bread_type_frame, bg=self.bg_secondary)
        bread_selector_row.pack(fill=tk.X)
        
        selector_label = tk.Label(bread_selector_row, text="Select type:", 
                                 font=("Segoe UI", 9), fg=self.text_secondary, bg=self.bg_secondary)
        selector_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.bread_type_var = tk.StringVar(value="sourdough")
        bread_types = self.qc_manager.get_all_bread_types()
        self.bread_type_combo = ttk.Combobox(bread_selector_row, textvariable=self.bread_type_var,
                                            values=list(bread_types.values()),
                                            state="readonly", width=18)
        self.bread_type_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.bread_type_combo.bind("<<ComboboxSelected>>", self._on_bread_type_change)
        
        ttk.Button(bread_selector_row, text="  View Profile", 
                  command=self.qc_view_bread_profile).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(bread_selector_row, text="  Edit Profile", 
                  command=self.qc_edit_bread_profile).pack(side=tk.LEFT)
        
        # QC Controls frame
        qc_controls_bg = tk.Frame(qc_container, bg=self.bg_secondary, highlightthickness=0)
        qc_controls_bg.pack(fill=tk.X, pady=(0, 12))
        
        qc_controls_frame = tk.Frame(qc_controls_bg, bg=self.bg_secondary)
        qc_controls_frame.pack(fill=tk.X, padx=12, pady=12)
        
        qc_controls_header = tk.Label(qc_controls_frame, text="  Quality Control Tools", 
                                      font=("Segoe UI", 11, "bold"), fg=self.text_primary, bg=self.bg_secondary)
        qc_controls_header.pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Button(qc_controls_frame, text=" Evaluate Current Analysis", 
                  command=self.qc_evaluate_current).pack(fill=tk.X, pady=(0, 6))
        ttk.Button(qc_controls_frame, text="📦 Check Batch Consistency", 
                  command=self.qc_batch_consistency).pack(fill=tk.X, pady=(0, 6))
        ttk.Button(qc_controls_frame, text=" SPC Statistics", 
                  command=self.qc_spc_statistics).pack(fill=tk.X, pady=(0, 6))
        ttk.Button(qc_controls_frame, text="⚠  View Alerts", 
                  command=self.qc_view_alerts).pack(fill=tk.X, pady=(0, 6))
        ttk.Button(qc_controls_frame, text="  Configure Thresholds", 
                  command=self.qc_configure_thresholds).pack(fill=tk.X)
        
        # QC Results display
        qc_scroll = ttk.Scrollbar(qc_container)
        qc_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.qc_text = tk.Text(qc_container, yscrollcommand=qc_scroll.set,
                               font=("Consolas", 9), bg=self.bg_tertiary,
                               fg=self.text_primary, relief=tk.FLAT,
                               borderwidth=0, padx=12, pady=12,
                               insertbackground=self.bg_accent)
        self.qc_text.pack(fill=tk.BOTH, expand=True)
        qc_scroll.config(command=self.qc_text.yview)
        
        # Defect Detection Tab
        defect_tab = ttk.Frame(self.notebook)
        self.notebook.add(defect_tab, text="  Defects")
        
        defect_container = tk.Frame(defect_tab, bg=self.bg_secondary)
        defect_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        defect_header = tk.Label(defect_container, text="Defect Detection", 
                                font=("Segoe UI", 11, "bold"), fg=self.text_primary, bg=self.bg_secondary)
        defect_header.pack(anchor=tk.W, pady=(0, 10))
        
        defect_controls = tk.Frame(defect_container, bg=self.bg_secondary)
        defect_controls.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(defect_controls, text="Analyze Current Image", 
                  command=self.detect_defects_current).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(defect_controls, text="Batch Analysis", 
                  command=self.detect_defects_batch).pack(side=tk.LEFT, padx=(0, 5))
        
        defect_scroll = ttk.Scrollbar(defect_container)
        defect_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.defect_text = tk.Text(defect_container, yscrollcommand=defect_scroll.set,
                                  font=("Consolas", 9), bg=self.bg_tertiary,
                                  fg=self.text_primary, relief=tk.FLAT,
                                  borderwidth=0, padx=12, pady=12,
                                  insertbackground=self.bg_accent)
        self.defect_text.pack(fill=tk.BOTH, expand=True)
        defect_scroll.config(command=self.defect_text.yview)
        
        self.defect_detector = DefectDetector(verbose=False)
        
        # ML Training Tab
        ml_tab = ttk.Frame(self.notebook)
        self.notebook.add(ml_tab, text="  ML Training")
        
        ml_container = tk.Frame(ml_tab, bg=self.bg_secondary)
        ml_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        ml_header = tk.Label(ml_container, text="Machine Learning Classifier", 
                            font=("Segoe UI", 11, "bold"), fg=self.text_primary, bg=self.bg_secondary)
        ml_header.pack(anchor=tk.W, pady=(0, 10))
        
        ml_top_frame = tk.Frame(ml_container, bg=self.bg_secondary)
        ml_top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Training data status
        ml_status_label = tk.Label(ml_top_frame, text="Training Data:", 
                                  font=("Segoe UI", 9), fg=self.text_secondary, bg=self.bg_secondary)
        ml_status_label.pack(anchor=tk.W)
        
        self.ml_status_text = tk.Label(ml_top_frame, text="No data loaded", 
                                      font=("Segoe UI", 8), fg=self.text_secondary, bg=self.bg_secondary)
        self.ml_status_text.pack(anchor=tk.W)
        
        # Training buttons
        ml_buttons = tk.Frame(ml_top_frame, bg=self.bg_secondary)
        ml_buttons.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(ml_buttons, text="Add Good Image", 
                  command=lambda: self.ml_add_image("good")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(ml_buttons, text="Add Problem Image", 
                  command=lambda: self.ml_add_image("problem")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(ml_buttons, text="Train Model", 
                  command=self.ml_train).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(ml_buttons, text="Predict Current", 
                  command=self.ml_predict_current).pack(side=tk.LEFT)
        
        ml_scroll = ttk.Scrollbar(ml_container)
        ml_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.ml_text = tk.Text(ml_container, yscrollcommand=ml_scroll.set,
                              font=("Consolas", 9), bg=self.bg_tertiary,
                              fg=self.text_primary, relief=tk.FLAT,
                              borderwidth=0, padx=12, pady=12,
                              insertbackground=self.bg_accent)
        self.ml_text.pack(fill=tk.BOTH, expand=True)
        ml_scroll.config(command=self.ml_text.yview)
        
        self.ml_classifier = SimpleMLClassifier(verbose=False)
        self.update_ml_status()
    
    def detect_defects_current(self):
        """Analyze current image for defects"""
        if not self.current_image_path:
            messagebox.showwarning("Warning", "Please select an image first")
            return
        
        self.defect_text.delete(1.0, tk.END)
        self.set_status("Analyzing defects...", color=self.bg_accent)
        
        try:
            result = self.defect_detector.detect_defects(str(self.current_image_path))
            
            output = f"DEFECT ANALYSIS REPORT\n"
            output += f"{'=' * 60}\n\n"
            output += f"Image: {Path(self.current_image_path).name}\n"
            output += f"Overall Severity: {result['overall_severity']:.1f}/100\n"
            output += f"Grade: {result['defect_grade']}\n\n"
            
            output += f"UNEVEN RISE\n{'-' * 60}\n"
            output += f"  Detected: {'Yes' if result['uneven_rise']['detected'] else 'No'}\n"
            output += f"  Severity: {result['uneven_rise']['severity']:.1f}/100\n"
            output += f"  Center Brightness: {result['uneven_rise']['center_brightness']:.0f}\n"
            output += f"  Edge Brightness: {result['uneven_rise']['edge_brightness']:.0f}\n\n"
            
            output += f"DENSE SPOTS\n{'-' * 60}\n"
            output += f"  Detected: {'Yes' if result['dense_spots']['detected'] else 'No'}\n"
            output += f"  Severity: {result['dense_spots']['severity']:.1f}/100\n"
            output += f"  Dense Percentage: {result['dense_spots']['dense_percentage']:.2f}%\n"
            output += f"  Number of Clusters: {result['dense_spots']['num_clusters']}\n\n"
            
            output += f"RECOMMENDATIONS\n{'-' * 60}\n"
            for rec in result['recommendations']:
                output += f"  - {rec}\n"
            
            self.defect_text.insert(1.0, output)
            self.set_status("Defect analysis complete", color=self.success_color)
            
        except Exception as e:
            self.defect_text.insert(1.0, f"Error: {str(e)}\n{traceback.format_exc()}")
            self.set_status(f"Error: {str(e)}", color=self.error_color)
    
    def detect_defects_batch(self):
        """Analyze batch for defects"""
        if not self.unprocessed_dir.exists():
            messagebox.showwarning("Warning", "No images directory found")
            return
        
        self.defect_text.delete(1.0, tk.END)
        self.set_status("Analyzing batch defects...", color=self.bg_accent)
        
        try:
            results = self.defect_detector.batch_detect(str(self.unprocessed_dir))
            
            if 'error' in results:
                self.defect_text.insert(1.0, f"Error: {results['error']}")
                return
            
            output = f"BATCH DEFECT ANALYSIS\n"
            output += f"{'=' * 60}\n\n"
            output += f"Images Analyzed: {results['num_images']}\n"
            output += f"Average Severity: {results['avg_severity']:.1f}/100\n"
            output += f"Batch Grade: {results['batch_grade']}\n"
            output += f"Pass Rate: {results['pass_rate']:.1f}%\n\n"
            
            output += f"DEFECT SUMMARY\n{'-' * 60}\n"
            output += f"  Uneven Rise: {results['uneven_rise_count']} images\n"
            output += f"  Dense Spots: {results['dense_spots_count']} images\n\n"
            
            output += f"INDIVIDUAL RESULTS\n{'-' * 60}\n"
            for i, result in enumerate(results['results'], 1):
                output += f"\n{i}. {Path(result['image_path']).name}\n"
                output += f"   Severity: {result['overall_severity']:.1f} ({result['defect_grade']})\n"
            
            self.defect_text.insert(1.0, output)
            self.set_status("Batch analysis complete", color=self.success_color)
            
        except Exception as e:
            self.defect_text.insert(1.0, f"Error: {str(e)}\n{traceback.format_exc()}")
            self.set_status(f"Error: {str(e)}", color=self.error_color)
    
    def update_ml_status(self):
        """Update ML training status display"""
        status = self.ml_classifier.get_training_status()
        status_str = (f"Good: {status['good_images']} | Problem: {status['problem_images']} | "
                     f"Total: {status['total_training_images']}")
        if status['model_trained']:
            status_str += " | Model: TRAINED"
        self.ml_status_text.config(text=status_str)
    
    def ml_add_image(self, label):
        """Add image to ML training set"""
        if not self.current_image_path:
            messagebox.showwarning("Warning", "Please select an image first")
            return
        
        success = self.ml_classifier.add_training_image(str(self.current_image_path), label)
        if success:
            self.update_ml_status()
            self.ml_text.insert(tk.END, f"Added {label} image: {self.current_image_path.name}\n")
            self.ml_text.see(tk.END)
            messagebox.showinfo("Success", f"Added image as '{label}'")
        else:
            messagebox.showerror("Error", "Could not add image")
    
    def ml_train(self):
        """Train ML model"""
        status = self.ml_classifier.get_training_status()
        if not status['ready_to_train']:
            messagebox.showwarning("Not Ready", 
                f"Need at least 1 good and 1 problem image\nCurrent: {status['good_images']} good, {status['problem_images']} problem")
            return
        
        result = self.ml_classifier.train()
        if result:
            self.ml_text.delete(1.0, tk.END)
            output = f"MODEL TRAINING COMPLETE\n"
            output += f"{'=' * 60}\n"
            output += f"Good Images: {result['good_count']}\n"
            output += f"Problem Images: {result['problem_count']}\n"
            output += f"Total Training Images: {result['total_training_images']}\n"
            output += f"Model Status: READY\n\n"
            output += f"You can now make predictions on new images!"
            self.ml_text.insert(1.0, output)
            self.update_ml_status()
            messagebox.showinfo("Success", "Model trained successfully!")
    
    def ml_predict_current(self):
        """Predict on current image"""
        if not self.current_image_path:
            messagebox.showwarning("Warning", "Please select an image first")
            return
        
        status = self.ml_classifier.get_training_status()
        if not status['model_trained']:
            messagebox.showwarning("Not Ready", "Please train the model first")
            return
        
        result = self.ml_classifier.predict(str(self.current_image_path))
        
        self.ml_text.delete(1.0, tk.END)
        output = f"PREDICTION RESULT\n"
        output += f"{'=' * 60}\n"
        output += f"Image: {Path(self.current_image_path).name}\n"
        output += f"Prediction: {result['prediction'].upper()}\n"
        output += f"Confidence: {result['confidence']:.1f}%\n\n"
        output += f"Confidence Breakdown\n{'-' * 60}\n"
        output += f"  Good Match: {result['confidence_good']:.1f}%\n"
        output += f"  Problem Match: {result['confidence_problem']:.1f}%\n"
        
        self.ml_text.insert(1.0, output)
        messagebox.showinfo("Prediction", f"{result['prediction'].upper()}\nConfidence: {result['confidence']:.0f}%")
    
    
    def refresh_image_list(self):
        """Refresh list of unprocessed images"""
        self.image_listbox.delete(0, tk.END)
        
        if not self.unprocessed_dir.exists():
            return
        
        image_extensions = ['.jpg', '.jpeg', '.png', '.JPG', '.PNG']
        images = sorted([
            f.name for f in self.unprocessed_dir.iterdir()
            if f.suffix in image_extensions
        ])
        
        for img in images:
            self.image_listbox.insert(tk.END, img)
    
    def on_image_select(self, event):
        """Handle image selection from listbox"""
        selection = self.image_listbox.curselection()
        if not selection:
            return
        
        filename = self.image_listbox.get(selection[0])
        self.current_image_path = self.unprocessed_dir / filename
        
        # Load and display preview
        try:
            img = Image.open(self.current_image_path)
            img.thumbnail((400, 400), Image.Resampling.LANCZOS)
            self.current_image = ImageTk.PhotoImage(img)
            
            self.preview_label.config(image=self.current_image, text="")
        except Exception as e:
            self.preview_label.config(text=f"Error loading image: {e}", bg=self.bg_secondary)
        
        self.set_status(f"Selected: {filename}", color=self.text_primary)
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, "Analyze an image to see results here...")
        self.results_text.config(state=tk.DISABLED)
        self.metrics_text.config(state=tk.NORMAL)
        self.metrics_text.delete(1.0, tk.END)
        self.metrics_text.insert(1.0, "Analyze an image to see metrics here...")
        self.metrics_text.config(state=tk.DISABLED)
    
    def start_analysis(self):
        """Start image analysis in a separate thread"""
        if self.mode_var.get() == "single":
            if not self.current_image_path:
                messagebox.showwarning("Warning", "Please select an image first")
                return
            
            # Start analysis thread
            thread = threading.Thread(target=self.analyze_single_image)
            thread.daemon = True
            thread.start()
        
        elif self.mode_var.get() == "loaf":
            loaf_name = self.loaf_name_var.get()
            if not loaf_name:
                messagebox.showwarning("Warning", "Please enter a loaf name")
                return
            
            thread = threading.Thread(target=self.analyze_loaf_images, args=(loaf_name,))
            thread.daemon = True
            thread.start()
    
    def analyze_single_image(self):
        """Analyze single image"""
        try:
            # NEW: Validate image quality first
            if not self._validate_image_quality_before_analysis(str(self.current_image_path)):
                self.set_status("✗ Image quality insufficient", color=self.warning_color)
                return
            
            self.progress.start()
            self.analyze_btn.config(state=tk.DISABLED)
            self.set_status("Analyzing image...", color=self.warning_color)
            self.root.update()
            
            output_dir = self.results_dir / self.current_image_path.stem
            
            result = analyze_bread_image(
                str(self.current_image_path),
                output_dir=str(output_dir),
                pixel_size_mm=self.pixel_size_var.get(),
                threshold_method=self.threshold_var.get(),
                normalize_method=self.normalize_var.get(),
                verbose=False
            )
            
            self.analysis_result = result
            
            # Display results
            self.display_results(result)
            
            # Move image to processed
            import shutil
            destination = self.processed_dir / self.current_image_path.name
            shutil.move(str(self.current_image_path), str(destination))
            
            self.set_status(" Analysis complete!", color=self.success_color)
            self.refresh_image_list()
            
            porosity = result['metrics']['porosity_percent']
            hole_count = result['metrics']['num_holes']
            messagebox.showinfo("Analysis Complete", 
                              f"Image analyzed successfully!\n\n"
                              f"Porosity: {porosity:.1f}%\n"
                              f"Hole Count: {hole_count}\n\n"
                              f"Results saved to: {output_dir}")
            
        except Exception as e:
            self.set_status("✗ Analysis failed", color=self.error_color)
            error_msg = f"Analysis failed:\n\n{str(e)}"
            messagebox.showerror("Analysis Error", error_msg)
        
        finally:
            self.progress.stop()
            self.analyze_btn.config(state=tk.NORMAL)
    
    def analyze_loaf_images(self, loaf_name):
        """Analyze all images in loaf folder"""
        try:
            self.progress.start()
            self.analyze_btn.config(state=tk.DISABLED)
            self.set_status(f"Analyzing loaf: {loaf_name}...", color=self.warning_color)
            self.root.update()
            
            result = analyze_loaf(loaf_name=loaf_name, 
                                pixel_size_mm=self.pixel_size_var.get(),
                                verbose=False)
            
            if result:
                self.analysis_result = result
                self.display_loaf_results(result)
                
                self.set_status(f" Loaf analysis complete!", color=self.success_color)
                
                mean_porosity = result['porosity']['mean']
                num_slices = result['num_slices']
                messagebox.showinfo("Loaf Analysis Complete",
                                  f"Loaf analysis complete!\n\n"
                                  f"Slices analyzed: {num_slices}\n"
                                  f"Mean porosity: {mean_porosity:.1f}%\n"
                                  f"Porosity range: {result['porosity']['min']:.1f}% - {result['porosity']['max']:.1f}%")
            else:
                self.set_status("✗ No slices found for loaf", color=self.error_color)
                messagebox.showwarning("No Images", f"No images found for loaf: {loaf_name}")
            
        except Exception as e:
            self.set_status("✗ Loaf analysis failed", color=self.error_color)
            messagebox.showerror("Analysis Error", f"Loaf analysis failed:\n\n{str(e)}")
        
        finally:
            self.progress.stop()
            self.analyze_btn.config(state=tk.NORMAL)
    
    def display_results(self, result):
        """Display single image analysis results"""
        self.analysis_result = result
        
        # NEW: Use result presenter for formatted output
        formatted_results = self.result_presenter.format_results(result)
        
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, formatted_results)
        self.results_text.config(state=tk.DISABLED)
        
        # Display metrics JSON in metrics tab
        metrics_json = json.dumps(result.get('metrics', {}), indent=2)
        self.metrics_text.config(state=tk.NORMAL)
        self.metrics_text.delete(1.0, tk.END)
        self.metrics_text.insert(1.0, metrics_json)
        self.metrics_text.config(state=tk.DISABLED)
        
        self.notebook.select(1)  # Switch to results tab
    
    def display_loaf_results(self, result):
        """Display loaf analysis results"""
        results_text = f"""
LOAF ANALYSIS RESULTS
{'='*50}

LOAF: {result['loaf_name']}
Slices analyzed: {result['num_slices']}

POROSITY ANALYSIS
────────────────────────────────
  Mean:           {result['porosity']['mean']:.1f}%
  Std deviation:  {result['porosity']['std']:.1f}%
  Min:            {result['porosity']['min']:.1f}%
  Max:            {result['porosity']['max']:.1f}%
  Range:          {result['porosity']['range']:.1f}%

HOLE ANALYSIS
────────────────────────────────
  Mean hole count:    {result['holes']['mean_count']:.0f}
  Mean diameter:      {result['holes']['mean_diameter_mm']:.2f} mm
  Diameter range:     {min([s['mean_diameter_mm'] for s in result['slices']]):.2f} - {max([s['mean_diameter_mm'] for s in result['slices']]):.2f} mm

SHAPE ANALYSIS
────────────────────────────────
  Mean aspect ratio:  {result['shape']['mean_aspect_ratio']:.2f}

SLICE-BY-SLICE
────────────────────────────────
"""
        
        results_text += f"{'Slice':<8} {'Porosity':<12} {'Holes':<10} {'Diameter':<12}\n"
        results_text += "-" * 50 + "\n"
        
        for s in result['slices']:
            results_text += f"{s['slice']:<8} {s['porosity']:<11.1f}% {s['num_holes']:<10.0f} {s['mean_diameter_mm']:<11.2f}mm\n"
        
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, results_text)
        self.results_text.config(state=tk.DISABLED)
        
        # Display full report JSON
        report_json = json.dumps(result, indent=2)
        self.metrics_text.config(state=tk.NORMAL)
        self.metrics_text.delete(1.0, tk.END)
        self.metrics_text.insert(1.0, report_json)
        self.metrics_text.config(state=tk.DISABLED)
        
        # Display consistency analysis
        self.display_loaf_consistency()
        
        self.notebook.select(1)  # Switch to results tab
    
    def open_folder(self):
        """Open unprocessed folder"""
        import os
        import subprocess
        folder = self.unprocessed_dir
        folder.mkdir(exist_ok=True)
        
        if os.name == 'nt':  # Windows
            os.startfile(folder)
        elif os.name == 'posix':  # macOS and Linux
            subprocess.Popen(['open' if os.uname().sysname == 'Darwin' else 'xdg-open', str(folder)])
    
    def view_results(self):
        """View analysis results folder"""
        import os
        import subprocess
        folder = self.results_dir
        
        if not folder.exists() or not list(folder.iterdir()):
            messagebox.showinfo("Info", "No results yet. Analyze an image first.")
            return
        
        if os.name == 'nt':  # Windows
            os.startfile(folder)
        elif os.name == 'posix':  # macOS and Linux
            subprocess.Popen(['open' if os.uname().sysname == 'Darwin' else 'xdg-open', str(folder)])
    
    def clear_selection(self):
        """Clear current selection"""
        self.current_image = None
        self.current_image_path = None
        self.image_listbox.selection_clear(0, tk.END)
        self.preview_label.config(image="", text="No image selected", fg=self.text_secondary)
        self.results_text.delete(1.0, tk.END)
        self.metrics_text.delete(1.0, tk.END)
        self.set_status("Ready", color=self.success_color)
    
    def set_status(self, message, color=None):
        """Update status label with optional color"""
        if color is None:
            color = self.text_primary
        self.status_var.set(message)
        self.status_label.config(foreground=color)
    
    def on_mode_change(self):
        """Handle analysis mode change"""
        if self.mode_var.get() == "loaf":
            self.loaf_name_entry.config(state=tk.NORMAL)
            self.set_status("Loaf analysis mode", self.bg_accent)
        else:
            self.loaf_name_entry.config(state=tk.DISABLED)
            self.set_status("Single image mode", self.success_color)
    
    def refresh_recipe_list(self):
        """Refresh the recipe listbox"""
        self.recipe_listbox.delete(0, tk.END)
        recipes = self.recipe_db.get_all_recipes()
        for recipe in recipes:
            label = f"{recipe['name']} (ID: {recipe['id']})"
            if recipe.get('measured_porosity'):
                label += f" - {recipe['measured_porosity']:.1f}%"
            self.recipe_listbox.insert(tk.END, label)
    
    def on_recipe_select(self, event):
        """Handle recipe selection"""
        selection = self.recipe_listbox.curselection()
        if not selection:
            return
        
        recipes = self.recipe_db.get_all_recipes()
        if selection[0] < len(recipes):
            self.current_recipe_id = recipes[selection[0]]['id']
    
    def log_new_recipe(self):
        """Show recipe builder form to create new recipe"""
        # Use the form-based recipe builder instead of JSON
        self.show_recipe_builder()
    
    def _on_recipe_saved(self, recipe_data):
        """Callback when recipe builder form saves a recipe"""
        try:
            # Add recipe to database with environmental parameters
            recipe = self.recipe_db.add_recipe(
                recipe_name=recipe_data['name'],
                ingredients=recipe_data['ingredients'],
                mixing_time_min=float(recipe_data.get('mixing_time_min', 0)),
                proof_time_min=float(recipe_data.get('proof_time_min', 0)),
                oven_temp_c=float(recipe_data.get('oven_temp_c', 0)),
                cooking_vessel=recipe_data.get('cooking_vessel', 'dutch oven'),
                cook_time_min=float(recipe_data.get('cook_time_min', 0)),
                notes=recipe_data.get('notes', ''),
                room_temp_c=float(recipe_data.get('room_temp_c')) if recipe_data.get('room_temp_c') else None,
                room_humidity_pct=float(recipe_data.get('room_humidity_pct')) if recipe_data.get('room_humidity_pct') else None,
                altitude_m=float(recipe_data.get('altitude_m')) if recipe_data.get('altitude_m') else None,
                bread_type=recipe_data.get('type', 'other'),
                steps=recipe_data.get('steps', [])
            )
            
            self.refresh_recipe_list()
            self.set_status(f" Recipe logged: {recipe['name']}", self.success_color)
            messagebox.showinfo("Success", f"Recipe '{recipe['name']}' saved!\n\nRecipe ID: {recipe['id']}\n\nNow analyze an image and save the porosity result.")
        
        except Exception as e:
            messagebox.showerror("Error", f"Could not save recipe:\n{str(e)}")
    
    def create_recipe_variant(self):
        """Create a variant of the current recipe"""
        if self.current_recipe_id is None:
            messagebox.showwarning("Warning", "Please select a recipe first")
            return
        
        parent = self.recipe_db.get_recipe(self.current_recipe_id)
        if not parent:
            return
        
        # Create a simple variant dialog
        variant_name = simpledialog.askstring("Create Variant", f"Enter name for variant of '{parent['name']}':")
        
        if not variant_name:
            return
        
        # Create variant with minor modifications for demo
        variant = self.recipe_db.create_recipe_variant(
            parent_recipe_id=self.current_recipe_id,
            variant_name=variant_name,
            modifications={}
        )
        
        if variant:
            self.refresh_recipe_list()
            self.set_status(f" Variant created: {variant_name}", self.success_color)
            messagebox.showinfo("Success", f"Variant '{variant_name}' created from '{parent['name']}'")
        else:
            messagebox.showerror("Error", "Could not create variant")
    
    def display_recipe_family(self):
        """Display recipe family tree and variants"""
        if self.current_recipe_id is None:
            messagebox.showwarning("Warning", "Please select a recipe first")
            return
        
        family = self.recipe_db.get_recipe_family(self.current_recipe_id)
        if not family:
            return
        
        output = "RECIPE FAMILY TREE\n"
        output += "=" * 60 + "\n\n"
        
        recipe = family['recipe']
        output += f"CURRENT RECIPE: {recipe['name']}\n"
        output += f"  ID: {recipe['id']}\n"
        output += f"  Version: {recipe.get('version', 1)}\n"
        output += f"  Porosity: {recipe.get('measured_porosity', 'Not measured')}%\n"
        
        if recipe.get('room_temp_c'):
            output += f"  Room Temp: {recipe['room_temp_c']}°C\n"
        if recipe.get('room_humidity_pct'):
            output += f"  Room Humidity: {recipe['room_humidity_pct']}%\n"
        if recipe.get('altitude_m'):
            output += f"  Altitude: {recipe['altitude_m']}m\n"
        output += "\n"
        
        # Parent
        if family['parent']:
            output += "PARENT RECIPE:\n"
            parent = family['parent']
            output += f"  {parent['name']} (ID: {parent['id']})\n"
            output += f"  Porosity: {parent.get('measured_porosity', 'Not measured')}%\n\n"
        
        # Variants
        if family['variants']:
            output += f"VARIANTS ({len(family['variants'])}):\n"
            for variant in family['variants']:
                output += f"  • {variant['name']} (ID: {variant['id']}, v{variant.get('version', 1)})\n"
                output += f"    Porosity: {variant.get('measured_porosity', 'Not measured')}%\n"
        else:
            output += "VARIANTS: None\n"
        
        self.prediction_text.delete("1.0", tk.END)
        self.prediction_text.insert("1.0", output)
        self.set_status(" Recipe family displayed", self.success_color)

    def save_recipe_porosity(self):
        """Save measured porosity to the selected recipe"""
        if self.current_recipe_id is None:
            messagebox.showwarning("Warning", "Please select a recipe first")
            return
        
        if not self.analysis_result:
            messagebox.showwarning("Warning", "Please analyze an image first")
            return
        
        porosity = self.analysis_result['metrics']['porosity_percent']
        
        success = self.recipe_db.update_recipe(
            self.current_recipe_id,
            measured_porosity=porosity,
            notes=f"Measured from image analysis"
        )
        
        if success:
            # Re-train predictor with new data
            self.recipe_predictor = RecipePredictor(self.recipe_db.get_recipes_with_porosity())
            
            self.refresh_recipe_list()
            self.set_status(f" Porosity saved: {porosity:.2f}%", self.success_color)
            messagebox.showinfo("Success", f"Porosity {porosity:.2f}% saved to recipe!\n\nRecipe now has training data for predictions.")
        else:
            messagebox.showerror("Error", "Could not save porosity to recipe")
    
    def predict_from_recipe(self):
        """Predict porosity for the selected recipe"""
        if self.current_recipe_id is None:
            messagebox.showwarning("Warning", "Please select a recipe first")
            return
        
        recipe = self.recipe_db.get_recipe(self.current_recipe_id)
        if not recipe:
            messagebox.showerror("Error", "Recipe not found")
            return
        
        # Make prediction
        predicted_porosity, confidence_info = self.recipe_predictor.predict_porosity(recipe)
        
        # Display prediction results
        result_text = f"""
POROSITY PREDICTION FOR: {recipe['name']}
{'='*50}

PREDICTED POROSITY: {predicted_porosity:.1f}%

CONFIDENCE LEVEL:
  {confidence_info.get('confidence_level', 'Unknown')}
  Training samples: {confidence_info.get('training_samples', 0)}
  Mean porosity: {confidence_info.get('mean_porosity', 'N/A')}%

FEATURE CONTRIBUTIONS:
"""
        
        contributions = confidence_info.get('feature_contributions', {})
        for feature, contribution in contributions.items():
            result_text += f"  {feature:20} {contribution:+.3f}\n"
        
        if recipe.get('measured_porosity'):
            result_text += f"\nACTUAL MEASURED: {recipe['measured_porosity']:.1f}%"
            error = abs(predicted_porosity - recipe['measured_porosity'])
            result_text += f"\nPREDICTION ERROR: {error:.1f}%"
        
        self.prediction_text.delete(1.0, tk.END)
        self.prediction_text.insert(1.0, result_text)
        
        self.set_status(f" Prediction: {predicted_porosity:.1f}%", self.success_color)
    
    def delete_recipe(self):
        """Delete the selected recipe"""
        if self.current_recipe_id is None:
            messagebox.showwarning("Warning", "Please select a recipe first")
            return
        
        recipe = self.recipe_db.get_recipe(self.current_recipe_id)
        if not recipe:
            return
        
        if messagebox.askyesno("Confirm", f"Delete recipe '{recipe['name']}'?"):
            self.recipe_db.delete_recipe(self.current_recipe_id)
            self.current_recipe_id = None
            self.refresh_recipe_list()
            self.set_status(" Recipe deleted", self.success_color)
    
    def clone_recipe(self):
        """Clone the selected recipe"""
        if self.current_recipe_id is None:
            messagebox.showwarning("Warning", "Please select a recipe first")
            return
        
        recipe = self.recipe_db.get_recipe(self.current_recipe_id)
        if not recipe:
            return
        
        # Optional: ask for custom name
        clone_name = messagebox.askstring("Clone Recipe", 
                                         f"Enter name for clone of '{recipe['name']}':\n(leave blank for default)",
                                         initialvalue=f"{recipe['name']} (Clone)")
        
        if clone_name is None:  # User cancelled
            return
        
        try:
            cloned = self.recipe_db.clone_recipe(self.current_recipe_id, clone_name if clone_name else None)
            if cloned:
                self.refresh_recipe_list()
                self.set_status(f" Recipe cloned: {cloned['name']}", self.success_color)
                messagebox.showinfo("Success", f"Recipe cloned as '{cloned['name']}'\n\nID: {cloned['id']}")
            else:
                messagebox.showerror("Error", "Could not clone recipe")
        except Exception as e:
            messagebox.showerror("Error", f"Clone failed:\n{str(e)}")
    
    def scale_recipe_gui(self):
        """Scale the selected recipe"""
        if self.current_recipe_id is None:
            messagebox.showwarning("Warning", "Please select a recipe first")
            return
        
        recipe = self.recipe_db.get_recipe(self.current_recipe_id)
        if not recipe:
            return
        
        # Ask for scale factor
        scale_str = messagebox.askstring("Scale Recipe",
                                        f"Scale '{recipe['name']}'\n\nEnter scale factor:\n"
                                        "  0.5 = half batch\n"
                                        "  1.0 = same size\n"
                                        "  2.0 = double batch",
                                        initialvalue="2.0")
        
        if scale_str is None:  # User cancelled
            return
        
        try:
            scale_factor = float(scale_str)
            if scale_factor <= 0:
                messagebox.showerror("Error", "Scale factor must be positive")
                return
            
            scaled_name = messagebox.askstring("Scale Recipe",
                                              "Enter name for scaled recipe:\n(leave blank for default)",
                                              initialvalue=f"{recipe['name']} (×{scale_factor})")
            
            if scaled_name is None:  # User cancelled
                return
            
            scaled = self.recipe_db.scale_recipe(self.current_recipe_id, scale_factor, 
                                                scaled_name if scaled_name else None)
            
            if scaled:
                self.refresh_recipe_list()
                
                # Show ingredient comparison
                output = f"RECIPE SCALED: ×{scale_factor}\n"
                output += "=" * 60 + "\n\n"
                output += f"Original: {recipe['name']}\n"
                output += f"Scaled: {scaled['name']}\n\n"
                output += "INGREDIENTS COMPARISON:\n"
                output += "-" * 60 + "\n"
                output += f"{'Ingredient':<20} {'Original':<15} {'Scaled':<15}\n"
                output += "-" * 60 + "\n"
                
                for ingredient, original_amount in recipe.get('ingredients', {}).items():
                    scaled_amount = scaled.get('ingredients', {}).get(ingredient, 0)
                    output += f"{ingredient:<20} {original_amount:<15.1f} {scaled_amount:<15.1f}\n"
                
                output += "\nNOTE: Cooking times and temperatures do not scale.\n"
                output += "You may need to adjust cooking times.\n"
                
                self.prediction_text.delete("1.0", tk.END)
                self.prediction_text.insert("1.0", output)
                
                self.set_status(f" Recipe scaled: {scaled['name']}", self.success_color)
                messagebox.showinfo("Success", f"Recipe scaled and saved as '{scaled['name']}'")
            else:
                messagebox.showerror("Error", "Could not scale recipe")
                
        except ValueError:
            messagebox.showerror("Error", "Invalid scale factor. Please enter a number (e.g., 0.5, 2.0)")
        except Exception as e:
            messagebox.showerror("Error", f"Scale failed:\n{str(e)}")
    
    def display_statistics_dashboard(self):
        """Display comprehensive statistics dashboard"""
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete("1.0", tk.END)
        
        try:
            stats_data = self.recipe_predictor.get_statistics_dashboard()
            
            output = "STATISTICS DASHBOARD\n"
            output += "=" * 60 + "\n\n"
            
            # Training statistics
            output += "TRAINING DATA\n"
            output += "-" * 60 + "\n"
            train_stats = stats_data.get("training_stats", {})
            output += f"Total Training Samples: {train_stats.get('training_samples', 0)}\n"
            output += f"Mean Porosity: {train_stats.get('mean_porosity', 'N/A')}%\n"
            output += f"Std Deviation: {train_stats.get('porosity_std', 'N/A')}%\n"
            output += f"Range: {train_stats.get('porosity_min', 'N/A')}% - {train_stats.get('porosity_max', 'N/A')}%\n\n"
            
            # Model quality metrics
            output += "MODEL QUALITY\n"
            output += "-" * 60 + "\n"
            output += f"R² (Coefficient of Determination): {stats_data.get('r_squared', 0):.3f}\n"
            output += "  (1.0 = Perfect fit, 0.0 = Random)\n\n"
            
            # Confidence intervals
            output += "95% CONFIDENCE INTERVALS\n"
            output += "-" * 60 + "\n"
            ci_data = stats_data.get("confidence_intervals", {})
            if ci_data:
                for feature, (lower, upper) in ci_data.items():
                    output += f"{feature:20} [{lower:6.2f}, {upper:6.2f}]\n"
            output += "\n"
            
            # Residual analysis
            output += "RESIDUAL ANALYSIS\n"
            output += "-" * 60 + "\n"
            residuals = stats_data.get("residuals", {})
            res_stats = residuals.get("statistics", {})
            output += f"Mean Residual: {res_stats.get('mean_residual', 'N/A')}\n"
            output += f"Std of Residuals: {res_stats.get('std_residual', 'N/A')}\n"
            output += f"Mean Absolute Error: {res_stats.get('mean_abs_error', 'N/A')}%\n"
            output += f"Max Error: {res_stats.get('max_error', 'N/A')}%\n"
            output += f"RMSE: {res_stats.get('rmse', 'N/A')}%\n\n"
            
            # Feature importance
            output += "FEATURE IMPORTANCE RANKING\n"
            output += "-" * 60 + "\n"
            importance = stats_data.get("feature_importance", [])
            if importance:
                for i, (fname, corr, score) in enumerate(importance, 1):
                    output += f"{i}. {fname:20} (corr={corr:+.3f}, score={score:.3f})\n"
            else:
                output += "No features computed yet\n"
            output += "\n"
            
            # Feature correlations with p-values
            output += "FEATURE CORRELATIONS WITH POROSITY\n"
            output += "-" * 60 + "\n"
            correlations = stats_data.get("correlations", {})
            if correlations:
                for fname, info in correlations.items():
                    corr = info.get("correlation", 0)
                    p_val = info.get("p_value", 1)
                    sig = "***" if p_val < 0.05 else ("**" if p_val < 0.1 else "")
                    output += f"{fname:20} {corr:+.3f}  (p={p_val:.3f}) {sig}\n"
            output += "\n(*** p<0.05 = significant, ** p<0.1 = marginally significant)\n"
            
            self.stats_text.insert("1.0", output)
            self.stats_text.config(state=tk.DISABLED)
            self.set_status(" Statistics dashboard refreshed", self.success_color)
            
        except Exception as e:
            output = f"Error generating statistics dashboard:\n\n{str(e)}\n\n{traceback.format_exc()}"
            self.stats_text.insert("1.0", output)
            self.stats_text.config(state=tk.DISABLED)
            self.set_status("✗ Statistics dashboard error", self.error_color)
    
    def compare_recipes(self):
        """Compare multiple recipes side-by-side"""
        recipes = self.recipe_db.get_recipes_with_porosity()
        
        if len(recipes) < 2:
            messagebox.showinfo("Comparison", "Need at least 2 recipes with measured porosity to compare")
            return
        
        output = "RECIPE COMPARISON\n"
        output += "=" * 80 + "\n\n"
        
        # Header row
        output += f"{'Recipe':<25} {'Mixing':<8} {'Proof':<8} {'Temp':<6} {'Cook':<6} {'Vessel':<15} {'Porosity':<10}\n"
        output += "-" * 80 + "\n"
        
        # Data rows
        for recipe in recipes:
            name = recipe.get("name", "Unknown")[:24]
            mixing = recipe.get("mixing_time_min", 0)
            proof = recipe.get("proof_time_min", 0)
            temp = recipe.get("oven_temp_c", 0)
            cook = recipe.get("cook_time_min", 0)
            vessel = recipe.get("cooking_vessel", "?")[:14]
            porosity = recipe.get("measured_porosity", "?")
            
            porosity_str = f"{porosity:.1f}%" if isinstance(porosity, (int, float)) else str(porosity)
            
            output += f"{name:<25} {mixing:<8.0f} {proof:<8.0f} {temp:<6.0f} {cook:<6.0f} {vessel:<15} {porosity_str:<10}\n"
        
        output += "\n" + "-" * 80 + "\n"
        
        # Statistics
        porosities = [r.get("measured_porosity") for r in recipes if isinstance(r.get("measured_porosity"), (int, float))]
        if porosities:
            output += f"\nAverage Porosity: {sum(porosities)/len(porosities):.1f}%\n"
            output += f"Best Porosity: {max(porosities):.1f}%\n"
            output += f"Worst Porosity: {min(porosities):.1f}%\n"
        
        self.compare_text.config(state=tk.NORMAL)
        self.compare_text.delete("1.0", tk.END)
        self.compare_text.insert("1.0", output)
        self.compare_text.config(state=tk.DISABLED)
        self.notebook.select(5)  # Switch to comparison tab
        self.set_status(" Recipes compared", self.success_color)
    
    def what_if_analysis(self):
        """Perform what-if analysis on recipe modifications"""
        if self.current_recipe_id is None:
            messagebox.showwarning("Warning", "Please select a recipe first")
            return
        
        recipe = self.recipe_db.get_recipe(self.current_recipe_id)
        if not recipe:
            return
        
        output = f"WHAT-IF ANALYSIS: {recipe.get('name', 'Unknown')}\n"
        output += "=" * 80 + "\n\n"
        
        output += "Current Recipe:\n"
        output += f"  Mixing Time: {recipe.get('mixing_time_min', 0):.0f} min\n"
        output += f"  Proof Time: {recipe.get('proof_time_min', 0):.0f} min\n"
        output += f"  Oven Temp: {recipe.get('oven_temp_c', 0):.0f}°C\n"
        output += f"  Cook Time: {recipe.get('cook_time_min', 0):.0f} min\n"
        output += f"  Current Porosity: {recipe.get('measured_porosity', 'N/A')}\n\n"
        
        output += "SIMULATED MODIFICATIONS:\n"
        output += "-" * 80 + "\n\n"
        
        # Test variations
        variations = [
            {"mixing_time_min": recipe.get("mixing_time_min", 0) + 2},
            {"mixing_time_min": max(0, recipe.get("mixing_time_min", 0) - 2)},
            {"proof_time_min": recipe.get("proof_time_min", 0) + 10},
            {"proof_time_min": max(0, recipe.get("proof_time_min", 0) - 10)},
            {"oven_temp_c": recipe.get("oven_temp_c", 0) + 10},
            {"oven_temp_c": max(100, recipe.get("oven_temp_c", 0) - 10)},
        ]
        
        for i, mods in enumerate(variations, 1):
            variant = recipe.copy()
            variant.update(mods)
            
            pred_porosity, pred_info = self.recipe_predictor.predict_porosity(variant)
            
            mod_key = list(mods.keys())[0]
            mod_value = mods[mod_key]
            old_value = recipe.get(mod_key, 0)
            
            change = "+" if mod_value > old_value else ""
            output += f"Scenario {i}: {mod_key} {old_value:.0f} → {mod_value:.0f}{change}\n"
            
            if pred_porosity:
                original_pred, _ = self.recipe_predictor.predict_porosity(recipe)
                diff = pred_porosity - original_pred if original_pred else 0
                output += f"  Predicted Porosity: {pred_porosity:.1f}% (Δ {diff:+.1f}%)\n"
            output += "\n"
        
        self.compare_text.config(state=tk.NORMAL)
        self.compare_text.delete("1.0", tk.END)
        self.compare_text.insert("1.0", output)
        self.compare_text.config(state=tk.DISABLED)
        self.notebook.select(5)  # Switch to comparison tab
        self.set_status(" What-if analysis complete", self.success_color)
    
    def display_loaf_consistency(self):
        """Display loaf consistency analysis for multi-slice data"""
        if not self.analysis_result:
            self.consist_text.config(state=tk.NORMAL)
            self.consist_text.delete("1.0", tk.END)
            self.consist_text.insert("1.0", "No loaf analysis data available.\n\nPerform a loaf analysis first by:\n1. Selecting 'Loaf Analysis' mode\n2. Entering a loaf name\n3. Ensuring multiple slices exist in the results")
            self.consist_text.config(state=tk.DISABLED)
            return
        
        result = self.analysis_result
        output = "LOAF CONSISTENCY & QUALITY ANALYSIS\n"
        output += "=" * 80 + "\n\n"
        
        if "num_slices" in result:
            # Multi-slice loaf analysis
            output += f"Loaf: {result.get('loaf_name', 'Unknown')}\n"
            output += f"Total Slices Analyzed: {result['num_slices']}\n"
            output += f"Analysis Date: {result.get('timestamp', 'Unknown')}\n\n"
            
            # Porosity statistics
            porosity_data = result.get("porosity", {})
            output += "POROSITY UNIFORMITY METRICS:\n"
            output += "-" * 80 + "\n"
            output += f"Mean Porosity: {porosity_data.get('mean', 0):.1f}%\n"
            output += f"Std Deviation: {porosity_data.get('std', 0):.1f}%\n"
            output += f"Range: {porosity_data.get('min', 0):.1f}% - {porosity_data.get('max', 0):.1f}%\n"
            output += f"Coefficient of Variation: {(porosity_data.get('std', 0) / porosity_data.get('mean', 1)) * 100:.1f}%\n\n"
            
            # Uniformity scoring
            cv = (porosity_data.get('std', 0) / porosity_data.get('mean', 1)) * 100 if porosity_data.get('mean', 0) > 0 else 100
            
            if cv < 10:
                uniformity_score = "Excellent (cv < 10%)"
                score_color = self.success_color
            elif cv < 20:
                uniformity_score = "Good (cv < 20%)"
                score_color = self.success_color
            elif cv < 30:
                uniformity_score = "Fair (cv < 30%)"
                score_color = self.warning_color
            else:
                uniformity_score = "Poor (cv >= 30%)"
                score_color = self.error_color
            
            output += "QUALITY ASSESSMENT:\n"
            output += "-" * 80 + "\n"
            output += f"Uniformity Score: {uniformity_score}\n"
            output += f"  (Coefficient of Variation = std/mean)\n\n"
            
            # Slice-by-slice analysis
            output += "SLICE-BY-SLICE POROSITY:\n"
            output += "-" * 80 + "\n"
            
            slices = result.get("slices", [])
            if slices:
                output += f"{'Slice':<10} {'Porosity':<12} {'Status':<20}\n"
                output += "-" * 42 + "\n"
                
                mean_poro = porosity_data.get('mean', 0)
                std_poro = porosity_data.get('std', 1)
                
                for i, slice_data in enumerate(slices, 1):
                    poro = slice_data.get("porosity", 0)
                    
                    # Determine if above/below mean
                    z_score = (poro - mean_poro) / std_poro if std_poro > 0 else 0
                    
                    if z_score > 0.5:
                        status = "High porosity"
                    elif z_score < -0.5:
                        status = "Low porosity"
                    else:
                        status = "Normal"
                    
                    output += f"Slice {i:<6} {poro:<12.1f}% {status:<20}\n"
                
                output += "\n"
            
            # Texture analysis if available
            if "texture_metrics" in result:
                output += "TEXTURE UNIFORMITY:\n"
                output += "-" * 80 + "\n"
                texture = result["texture_metrics"]
                output += f"Hole Size Uniformity: {texture.get('hole_uniformity', 'N/A')}\n"
                output += f"Crumb Distribution: {texture.get('crumb_distribution', 'N/A')}\n\n"
            
            # Recommendations
            output += "RECOMMENDATIONS:\n"
            output += "-" * 80 + "\n"
            if cv > 25:
                output += "• Consider adjusting fermentation temperature/humidity for better uniformity\n"
            if porosity_data.get('max', 0) > 45:
                output += "• High-porosity slices detected - may need reduced proofing time\n"
            if porosity_data.get('min', 0) < 15:
                output += "• Low-porosity slices detected - may need increased proofing time\n"
            output += "• Ensure consistent oven temperature throughout baking\n"
            output += "• Check for hot spots in your oven\n"
            
        else:
            # Single image analysis
            output += "Single Slice Analysis\n"
            output += "-" * 80 + "\n"
            metrics = result.get("metrics", {})
            output += f"Porosity: {metrics.get('porosity', 'N/A'):.1f}%\n"
            output += f"Perimeter: {metrics.get('perimeter', 'N/A'):.0f} pixels\n"
            output += f"Area: {metrics.get('area', 'N/A'):.0f} pixels²\n"
        
        self.consist_text.config(state=tk.NORMAL)
        self.consist_text.delete("1.0", tk.END)
        self.consist_text.insert("1.0", output)
        self.consist_text.config(state=tk.DISABLED)

    # ==================== BREAD TYPE PROFILE METHODS ====================
    
    def _on_bread_type_change(self, event=None):
        """Handle bread type selection change"""
        selected_display_name = self.bread_type_var.get()
        bread_types = self.qc_manager.get_all_bread_types()
        
        # Find the key for this display name
        for key, display_name in bread_types.items():
            if display_name == selected_display_name:
                self.qc_manager.set_bread_type(key)
                self.set_status(f" Switched to {display_name} profile", self.success_color)
                break
    
    def qc_view_bread_profile(self):
        """Display the current bread type profile"""
        profile = self.qc_manager.get_current_profile()
        bread_type = self.qc_manager.current_bread_type
        
        output = f"BREAD TYPE PROFILE: {profile.get('display_name', bread_type).upper()}\n"
        output += "=" * 70 + "\n\n"
        
        output += "POROSITY STANDARDS:\n"
        output += "-" * 70 + "\n"
        output += f"  Target Range:   {profile['porosity_target_min']:.1f}% - {profile['porosity_target_max']:.1f}%\n"
        output += f"  Warning Range:  {profile['porosity_warning_min']:.1f}% - {profile['porosity_warning_max']:.1f}%\n\n"
        
        output += "HOLE METRICS:\n"
        output += "-" * 70 + "\n"
        output += f"  Count Target:   {profile['hole_count_target_min']:.0f} - {profile['hole_count_target_max']:.0f} holes\n"
        output += f"  Diameter Target: {profile['hole_diameter_target_min']:.1f}mm - {profile['hole_diameter_target_max']:.1f}mm\n\n"
        
        output += "UNIFORMITY:\n"
        output += "-" * 70 + "\n"
        output += f"  Minimum Score:  {profile['uniformity_acceptable_min']:.2f}\n"
        output += f"  Batch CV Max:   {profile['consistency_cv_max']*100:.1f}%\n\n"
        
        output += "QUALITY GRADES:\n"
        output += "-" * 70 + "\n"
        grades = profile['quality_grades']
        for grade_name in ['excellent', 'good', 'fair', 'poor']:
            grade_spec = grades[grade_name]
            p_min, p_max = grade_spec['porosity']
            u_min, u_max = grade_spec['uniformity']
            output += f"  {grade_name.upper():<10} Porosity: {p_min:.0f}-{p_max:.0f}%  Uniformity: {u_min:.2f}-{u_max:.2f}\n"
        
        self.qc_text.delete(1.0, tk.END)
        self.qc_text.insert(1.0, output)
        self.set_status(f" Profile displayed: {profile.get('display_name', bread_type)}", self.success_color)
    
    def qc_edit_bread_profile(self):
        """Edit the current bread type profile"""
        profile = self.qc_manager.get_current_profile()
        bread_type = self.qc_manager.current_bread_type
        
        try:
            # Create a configuration dialog
            config_window = tk.Toplevel(self.root)
            config_window.title(f"Edit Profile: {profile.get('display_name', bread_type)}")
            config_window.geometry("700x800")
            
            # Profile name
            ttk.Label(config_window, text="Profile Name:").pack(anchor=tk.W, padx=10, pady=(10, 0))
            name_entry = ttk.Entry(config_window)
            name_entry.insert(0, profile.get('display_name', bread_type))
            name_entry.pack(fill=tk.X, padx=10, pady=(0, 10))
            
            # Editable fields display
            config_text = tk.Text(config_window, font=("Consolas", 9), height=25)
            config_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
            
            # Show key settings as text
            config_display = f"""POROSITY TARGETS (%)
porosity_target_min: {profile.get('porosity_target_min', 20.0)}
porosity_target_max: {profile.get('porosity_target_max', 35.0)}
porosity_warning_min: {profile.get('porosity_warning_min', 18.0)}
porosity_warning_max: {profile.get('porosity_warning_max', 37.0)}

HOLE METRICS
hole_count_target_min: {profile.get('hole_count_target_min', 100)}
hole_count_target_max: {profile.get('hole_count_target_max', 400)}
hole_diameter_target_min: {profile.get('hole_diameter_target_min', 2.0)}
hole_diameter_target_max: {profile.get('hole_diameter_target_max', 8.0)}

UNIFORMITY & CONSISTENCY
uniformity_acceptable_min: {profile.get('uniformity_acceptable_min', 0.7)}
consistency_cv_max: {profile.get('consistency_cv_max', 0.15)}

Edit values above (format: key: value)
"""
            config_text.insert(1.0, config_display)
            
            # Buttons
            button_frame = ttk.Frame(config_window)
            button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
            
            def save_profile_changes():
                """Save changes to the profile"""
                try:
                    # Parse the edited values
                    edited_text = config_text.get(1.0, tk.END)
                    
                    # Simple parser for key: value format
                    for line in edited_text.split('\n'):
                        if ':' in line and not line.strip().startswith('#'):
                            key, value = line.split(':', 1)
                            key = key.strip()
                            value_str = value.strip()
                            
                            # Try to convert to appropriate type
                            try:
                                if '_min' in key or '_max' in key:
                                    value = float(value_str)
                                    self.qc_manager.update_threshold(key, min_val=value if '_min' in key else None,
                                                                    max_val=value if '_max' in key else None,
                                                                    bread_type=bread_type)
                            except (ValueError, KeyError):
                                pass
                    
                    messagebox.showinfo("Success", "Profile updated!")
                    config_window.destroy()
                    self.qc_view_bread_profile()  # Refresh display
                
                except Exception as e:
                    messagebox.showerror("Error", f"Could not save profile:\n\n{str(e)}")
            
            ttk.Button(button_frame, text="Save Changes", command=save_profile_changes).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(button_frame, text="Cancel", command=config_window.destroy).pack(side=tk.LEFT)
        
        except Exception as e:
            messagebox.showerror("Error", f"Could not open profile editor:\n\n{str(e)}")

    # ==================== EXPORT & REPORTING METHODS ====================
    
    def export_batch_csv(self):
        """Export analysis history to CSV"""
        if not self.analysis_history:
            messagebox.showwarning("No Data", "Please analyze at least one image first")
            return
        
        try:
            output_path = self.export_engine.export_to_csv(
                self.analysis_history,
                filename=f"batch_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            
            result_msg = f" CSV export successful!\n\nFile: {output_path.name}\n\nLocation: {self.output_dir}"
            self.export_text.delete(1.0, tk.END)
            self.export_text.insert(1.0, result_msg)
            
            messagebox.showinfo("Export Complete", result_msg)
            self.set_status(f" CSV exported: {output_path.name}", self.success_color)
        
        except Exception as e:
            error_msg = f"CSV export failed:\n\n{str(e)}"
            self.export_text.delete(1.0, tk.END)
            self.export_text.insert(1.0, error_msg)
            messagebox.showerror("Export Error", error_msg)
            self.set_status("✗ CSV export failed", self.error_color)
    
    def export_batch_excel(self):
        """Export analysis history to Excel with charts"""
        if not self.analysis_history:
            messagebox.showwarning("No Data", "Please analyze at least one image first")
            return
        
        try:
            output_path = self.export_engine.export_to_excel(
                self.analysis_history,
                filename=f"batch_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )
            
            if output_path:
                result_msg = f" Excel export successful!\n\nFile: {output_path.name}\n\nLocation: {self.output_dir}\n\nFeatures:\n• Summary sheet with statistics\n• Detailed results sheet\n• Analysis data"
                self.export_text.delete(1.0, tk.END)
                self.export_text.insert(1.0, result_msg)
                
                messagebox.showinfo("Export Complete", result_msg)
                self.set_status(f" Excel exported: {output_path.name}", self.success_color)
            else:
                messagebox.showwarning("Export", "Excel export not available. Install openpyxl:\npip install openpyxl")
        
        except Exception as e:
            error_msg = f"Excel export failed:\n\n{str(e)}"
            self.export_text.delete(1.0, tk.END)
            self.export_text.insert(1.0, error_msg)
            messagebox.showerror("Export Error", error_msg)
            self.set_status("✗ Excel export failed", self.error_color)
    
    def export_batch_pdf(self):
        """Generate PDF report from analysis history"""
        if not self.analysis_history:
            messagebox.showwarning("No Data", "Please analyze at least one image first")
            return
        
        try:
            output_path = self.export_engine.export_to_pdf(
                self.analysis_history,
                filename=f"batch_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                title="Bread Porosity Analysis Report"
            )
            
            if output_path:
                result_msg = f" PDF report generated successfully!\n\nFile: {output_path.name}\n\nLocation: {self.output_dir}\n\nReport includes:\n• Summary statistics\n• Detailed results table\n• Analysis information"
                self.export_text.delete(1.0, tk.END)
                self.export_text.insert(1.0, result_msg)
                
                messagebox.showinfo("Export Complete", result_msg)
                self.set_status(f" PDF report generated: {output_path.name}", self.success_color)
            else:
                messagebox.showwarning("Export", "PDF export not available. Install reportlab:\npip install reportlab")
        
        except Exception as e:
            error_msg = f"PDF export failed:\n\n{str(e)}"
            self.export_text.delete(1.0, tk.END)
            self.export_text.insert(1.0, error_msg)
            messagebox.showerror("Export Error", error_msg)
            self.set_status("✗ PDF export failed", self.error_color)
    
    def create_summary_charts(self):
        """Create summary charts from analysis history"""
        if not self.analysis_history:
            messagebox.showwarning("No Data", "Please analyze at least one image first")
            return
        
        try:
            chart_paths = self.export_engine.create_summary_charts(self.analysis_history)
            
            if chart_paths:
                result_msg = " Summary charts created!\n\n"
                result_msg += "Charts generated:\n"
                for chart_name, path in chart_paths.items():
                    result_msg += f"  • {chart_name}: {path.name}\n"
                result_msg += f"\nLocation: {self.output_dir}"
                
                self.export_text.delete(1.0, tk.END)
                self.export_text.insert(1.0, result_msg)
                
                messagebox.showinfo("Charts Created", result_msg)
                self.set_status(f" {len(chart_paths)} charts created", self.success_color)
            else:
                messagebox.showwarning("Charts", "No charts were created")
        
        except Exception as e:
            error_msg = f"Chart creation failed:\n\n{str(e)}"
            self.export_text.delete(1.0, tk.END)
            self.export_text.insert(1.0, error_msg)
            messagebox.showerror("Error", error_msg)
            self.set_status("✗ Chart creation failed", self.error_color)
    
    # ==================== QUALITY CONTROL METHODS ====================
    
    def qc_evaluate_current(self):
        """Evaluate the current analysis with quality control"""
        if not self.analysis_result:
            messagebox.showwarning("No Analysis", "Please analyze an image first")
            return
        
        try:
            metrics = self.analysis_result.get('metrics', {})
            evaluation = self.qc_manager.evaluate_analysis(metrics, recipe_id=self.current_recipe_id)
            
            # Add to history
            analysis_with_qc = self.analysis_result.copy()
            analysis_with_qc['qc_evaluation'] = evaluation
            self.analysis_history.append(analysis_with_qc)
            
            # Display evaluation
            output = "QUALITY CONTROL EVALUATION\n"
            output += "=" * 70 + "\n\n"
            
            output += "ACCEPTANCE STATUS:\n"
            output += "-" * 70 + "\n"
            acceptance = evaluation['acceptance']
            output += f"  Porosity:    {' PASS' if acceptance['porosity_ok'] else ' FAIL'}\n"
            output += f"  Holes:       {' PASS' if acceptance['holes_ok'] else ' FAIL'}\n"
            output += f"  Uniformity:  {' PASS' if acceptance['uniformity_ok'] else ' FAIL'}\n"
            output += f"  OVERALL:     {' ACCEPT' if acceptance['overall_ok'] else '⚠  REVIEW NEEDED'}\n\n"
            
            output += f"QUALITY GRADE: {evaluation['grade']}\n\n"
            
            # Scores
            output += "QUALITY SCORES:\n"
            output += "-" * 70 + "\n"
            for param, score in evaluation['scores'].items():
                bar = "█" * int(score * 10) + "░" * (10 - int(score * 10))
                output += f"  {param:15} {score:.2f}  [{bar}]\n"
            output += "\n"
            
            # Alerts
            if evaluation['alerts']:
                output += "⚠  ALERTS:\n"
                output += "-" * 70 + "\n"
                for alert in evaluation['alerts']:
                    output += f"  {alert}\n"
                output += "\n"
            
            # Recommendations
            if evaluation['recommendations']:
                output += "💡 RECOMMENDATIONS:\n"
                output += "-" * 70 + "\n"
                for rec in evaluation['recommendations']:
                    output += f"  {rec}\n"
            
            self.qc_text.delete(1.0, tk.END)
            self.qc_text.insert(1.0, output)
            
            self.set_status(f" QC evaluation complete: {evaluation['grade']}", self.success_color)
        
        except Exception as e:
            error_msg = f"QC evaluation failed:\n\n{str(e)}"
            self.qc_text.delete(1.0, tk.END)
            self.qc_text.insert(1.0, error_msg)
            messagebox.showerror("QC Error", error_msg)
            self.set_status("✗ QC evaluation failed", self.error_color)
    
    def qc_batch_consistency(self):
        """Check consistency across batch of analyses"""
        if not self.analysis_history:
            messagebox.showwarning("No Data", "Please analyze multiple images first")
            return
        
        try:
            report = self.qc_manager.check_batch_consistency(self.analysis_history)
            
            output = "BATCH CONSISTENCY ANALYSIS\n"
            output += "=" * 70 + "\n\n"
            
            output += f"Samples Analyzed: {report.get('num_samples', 0)}\n"
            output += f"Status: {report.get('consistency_verdict', 'N/A')}\n"
            output += f"Message: {report.get('message', 'N/A')}\n\n"
            
            output += "POROSITY STATISTICS:\n"
            output += "-" * 70 + "\n"
            porosity = report.get('porosity', {})
            output += f"  Mean:          {porosity.get('mean', 0):.2f}%\n"
            output += f"  Std Dev:       {porosity.get('stdev', 0):.2f}%\n"
            output += f"  CV (Target <15%): {porosity.get('cv_percent', 0):.2f}%\n"
            output += f"  Range:         {porosity.get('min', 0):.2f}% - {porosity.get('max', 0):.2f}%\n\n"
            
            output += "HOLE METRICS:\n"
            output += "-" * 70 + "\n"
            holes = report.get('holes', {})
            output += f"  Mean Count:    {holes.get('mean', 0):.0f}\n"
            output += f"  Std Dev:       {holes.get('stdev', 0):.0f}\n"
            output += f"  Range:         {holes.get('min', 0):.0f} - {holes.get('max', 0):.0f}\n\n"
            
            output += "UNIFORMITY METRICS:\n"
            output += "-" * 70 + "\n"
            uniformity = report.get('uniformity', {})
            output += f"  Mean:          {uniformity.get('mean', 0):.2f}\n"
            output += f"  Range:         {uniformity.get('min', 0):.2f} - {uniformity.get('max', 0):.2f}\n"
            
            self.qc_text.delete(1.0, tk.END)
            self.qc_text.insert(1.0, output)
            
            verdict = "" if report.get('is_consistent') else "⚠"
            self.set_status(f"{verdict} Batch consistency check complete", self.success_color)
        
        except Exception as e:
            error_msg = f"Batch consistency check failed:\n\n{str(e)}"
            self.qc_text.delete(1.0, tk.END)
            self.qc_text.insert(1.0, error_msg)
            messagebox.showerror("Error", error_msg)
            self.set_status("✗ Consistency check failed", self.error_color)
    
    def qc_spc_statistics(self):
        """Display SPC (Statistical Process Control) statistics"""
        try:
            spc = self.qc_manager.get_spc_statistics()
            
            output = "STATISTICAL PROCESS CONTROL (SPC)\n"
            output += "=" * 70 + "\n\n"
            
            if spc.get('status') == 'no_data':
                output += "No historical data yet. Analyze more images to build SPC charts.\n"
            else:
                output += f"Samples in History: {spc.get('samples', 0)}\n"
                output += f"Mean Porosity: {spc.get('mean', 0):.2f}%\n"
                output += f"Std Deviation: {spc.get('stdev', 0):.2f}%\n\n"
                
                output += "CONTROL LIMITS (±3σ):\n"
                output += "-" * 70 + "\n"
                cl = spc.get('control_limits', {})
                output += f"  Upper Control Limit (UCL): {cl.get('ucl', 0):.2f}%\n"
                output += f"  Lower Control Limit (LCL): {cl.get('lcl', 0):.2f}%\n\n"
                
                output += "WARNING LIMITS (±2σ):\n"
                output += "-" * 70 + "\n"
                wl = spc.get('warning_limits', {})
                output += f"  Upper Warning Limit (UWL): {wl.get('uwl', 0):.2f}%\n"
                output += f"  Lower Warning Limit (LWL): {wl.get('lwl', 0):.2f}%\n\n"
                
                output += f"RECENT TREND: {spc.get('recent_trend', 'unknown')}\n"
                output += "\nUse these limits to monitor process stability over time.\n"
                output += "Points outside control limits indicate process drift.\n"
            
            self.qc_text.delete(1.0, tk.END)
            self.qc_text.insert(1.0, output)
            
            self.set_status(" SPC statistics displayed", self.success_color)
        
        except Exception as e:
            error_msg = f"SPC calculation failed:\n\n{str(e)}"
            self.qc_text.delete(1.0, tk.END)
            self.qc_text.insert(1.0, error_msg)
            messagebox.showerror("Error", error_msg)
            self.set_status("✗ SPC calculation failed", self.error_color)
    
    def qc_view_alerts(self):
        """View all active QC alerts"""
        try:
            alerts = self.qc_manager.get_alerts(limit=20)
            
            output = "QUALITY CONTROL ALERTS\n"
            output += "=" * 70 + "\n\n"
            
            if alerts:
                output += f"Total Active Alerts: {len(alerts)}\n\n"
                for i, alert in enumerate(alerts, 1):
                    output += f"{i}. {alert}\n"
            else:
                output += " No active alerts\n"
            
            self.qc_text.delete(1.0, tk.END)
            self.qc_text.insert(1.0, output)
            
            status_msg = f" Viewing {len(alerts)} alerts"
            self.set_status(status_msg, self.success_color)
        
        except Exception as e:
            error_msg = f"Alert retrieval failed:\n\n{str(e)}"
            self.qc_text.delete(1.0, tk.END)
            self.qc_text.insert(1.0, error_msg)
    
    def qc_configure_thresholds(self):
        """Configure QC thresholds"""
        try:
            # Create a simple configuration dialog
            config_window = tk.Toplevel(self.root)
            config_window.title("Quality Control Configuration")
            config_window.geometry("600x700")
            
            # Current config display
            config_frame = ttk.LabelFrame(config_window, text="Current Thresholds", padding=12)
            config_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            config_text = tk.Text(config_frame, font=("Consolas", 9), height=20)
            config_text.pack(fill=tk.BOTH, expand=True)
            
            # Display current config
            config_display = json.dumps(self.qc_manager.config, indent=2)
            config_text.insert(1.0, config_display)
            
            # Buttons
            button_frame = ttk.Frame(config_window)
            button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
            
            ttk.Button(button_frame, text="Save Changes", 
                      command=lambda: self._save_qc_config(config_text, config_window)).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(button_frame, text="Reset to Defaults", 
                      command=lambda: self._reset_qc_config(config_text)).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(button_frame, text="Close", 
                      command=config_window.destroy).pack(side=tk.LEFT)
        
        except Exception as e:
            messagebox.showerror("Configuration Error", f"Error opening QC config:\n\n{str(e)}")
    
    def _save_qc_config(self, config_text, window):
        """Save modified QC configuration"""
        try:
            config_str = config_text.get(1.0, tk.END)
            new_config = json.loads(config_str)
            self.qc_manager.config = new_config
            self.qc_manager.save_config()
            
            messagebox.showinfo("Success", "QC configuration saved!")
            self.set_status(" QC thresholds updated", self.success_color)
            window.destroy()
        
        except json.JSONDecodeError as e:
            messagebox.showerror("JSON Error", f"Invalid JSON format:\n\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save config:\n\n{str(e)}")
    
    def _reset_qc_config(self, config_text):
        """Reset QC configuration to defaults"""
        try:
            # Recreate default config
            self.qc_manager.config = {
                "porosity_target_min": 20.0,
                "porosity_target_max": 35.0,
                "porosity_warning_min": 18.0,
                "porosity_warning_max": 37.0,
                "hole_count_target_min": 100,
                "hole_count_target_max": 400,
                "hole_diameter_target_min": 2.0,
                "hole_diameter_target_max": 8.0,
                "uniformity_acceptable_min": 0.7,
                "consistency_cv_max": 0.15,
                "consecutive_failures_limit": 3,
                "quality_grades": {
                    "excellent": {"porosity": [25, 32], "uniformity": [0.85, 1.0]},
                    "good": {"porosity": [22, 35], "uniformity": [0.75, 0.95]},
                    "fair": {"porosity": [18, 38], "uniformity": [0.65, 0.85]},
                    "poor": {"porosity": [0, 100], "uniformity": [0.0, 1.0]},
                }
            }
            
            config_text.delete(1.0, tk.END)
            config_text.insert(1.0, json.dumps(self.qc_manager.config, indent=2))
            messagebox.showinfo("Reset", "Configuration reset to defaults")
        
        except Exception as e:
            messagebox.showerror("Error", f"Could not reset config:\n\n{str(e)}")

    # ==================== NEW: FIRST-RUN & USABILITY FEATURES ====================
    
    def _check_first_run(self):
        """Check if first-run wizard should be shown."""
        config_path = Path("config.json")
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    if not config.get("first_run_complete", False):
                        self._show_first_run_wizard()
            except:
                self._show_first_run_wizard()
        else:
            self._show_first_run_wizard()
    
    def _show_first_run_wizard(self):
        """Launch first-run setup wizard."""
        wizard = FirstRunWizard(self.root, "config.json")
        if wizard.should_show_wizard():
            wizard.run_wizard()
    
    def _validate_image_quality_before_analysis(self, image_path: str) -> bool:
        """
        Validate image quality before analysis. Show user feedback.
        Returns True if image is good enough to analyze.
        """
        validation = self.image_quality_validator.validate_image(image_path)
        
        # Show validation report
        self.image_quality_validator.print_report(validation)
        
        if not validation['can_proceed']:
            messagebox.showwarning("Image Quality",
                                 f"Image quality score: {validation['score']}/1.0\n\n"
                                 f"Status: {validation['overall_status']}\n\n"
                                 f"Recommendations:\n" +
                                 "\n".join(validation['recommendations'][:3]))
            return False
        
        if validation['score'] < 0.85:
            result = messagebox.askyesno("Suboptimal Image",
                                        f"Image quality is {validation['score']:.0%}.\n\n"
                                        f"Continue anyway?")
            return result
        
        return True
    
    def toggle_results_view(self):
        """Toggle between simple and advanced results view."""
        self.result_presenter.toggle_mode()
        mode = "SIMPLE" if self.result_presenter.simple_mode else "ADVANCED"
        messagebox.showinfo("View Toggled", f"Switched to {mode} view")
        
        # Refresh results if available
        if self.analysis_result:
            self._display_results_formatted()
    
    def _display_results_formatted(self):
        """Display results using formatted presenter."""
        if not self.analysis_result:
            return
        
        formatted = self.result_presenter.format_results(self.analysis_result)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, formatted)
    
    def show_recipe_builder(self):
        """Show form-based recipe builder instead of JSON input."""
        def on_save(recipe_dict):
            try:
                saved_recipe = self.recipe_db.add_recipe(
                    recipe_name=recipe_dict.get('name'),
                    ingredients=recipe_dict.get('ingredients', {}),
                    mixing_time_min=recipe_dict.get('mixing_time_min', 10),
                    proof_time_min=recipe_dict.get('proof_time_min', 480),
                    oven_temp_c=recipe_dict.get('oven_temp_c', 450),
                    cooking_vessel=recipe_dict.get('cooking_vessel', 'Dutch oven'),
                    cook_time_min=recipe_dict.get('cook_time_min', 40),
                    notes=recipe_dict.get('notes', ''),
                    room_temp_c=recipe_dict.get('room_temp_c'),
                    room_humidity_pct=recipe_dict.get('room_humidity_pct'),
                    altitude_m=recipe_dict.get('altitude_m')
                )
                self.refresh_recipe_list()
                return True
            except Exception as e:
                messagebox.showerror("Error", f"Could not save recipe: {str(e)}")
                return False
        
        builder = RecipeBuilderForm(self.root, on_save_callback=on_save)
        builder.show()



def main():
    from datetime import datetime
    root = tk.Tk()
    app = BreadPorositytoolGUI(root)
    app.refresh_recipe_list()
    root.mainloop()


if __name__ == "__main__":
    main()

