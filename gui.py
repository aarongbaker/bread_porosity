"""
GUI for Bread Porosity Analysis Tool
User-friendly interface for analyzing bread images, managing loaves, and logging recipes
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
from PIL import Image, ImageTk
import json
from analyze import analyze_bread_image
from loaf_analyzer import analyze_loaf
from recipe_database import RecipeDatabase
from recipe_predictor import RecipePredictor
import traceback


class BreadPorositytoolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Bread Porosity Analysis Tool")
        self.root.geometry("1400x900")
        
        # Professional color scheme
        self.bg_primary = "#f8f9fa"
        self.bg_secondary = "#ffffff"
        self.bg_accent = "#007bff"
        self.text_primary = "#212529"
        self.text_secondary = "#6c757d"
        self.border_color = "#dee2e6"
        self.success_color = "#28a745"
        self.warning_color = "#ffc107"
        self.error_color = "#dc3545"
        
        self.root.configure(bg=self.bg_primary)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame and Label styling
        style.configure("TFrame", background=self.bg_primary)
        style.configure("TLabelframe", background=self.bg_primary, foreground=self.text_primary, 
                       borderwidth=1, relief="flat")
        style.configure("TLabelframe.Label", background=self.bg_primary, foreground=self.text_primary,
                       font=("Segoe UI", 10, "bold"))
        style.configure("TLabel", background=self.bg_primary, foreground=self.text_primary)
        style.configure("Header.TLabel", background=self.bg_primary, foreground=self.text_primary, 
                       font=("Segoe UI", 12, "bold"))
        style.configure("Subheader.TLabel", background=self.bg_primary, foreground=self.text_primary,
                       font=("Segoe UI", 9, "bold"))
        
        # Button styling
        style.configure("TButton", font=("Segoe UI", 9), relief="flat", padding=6)
        style.map("TButton",
                 background=[("pressed", self.bg_accent), ("active", "#0056b3"), ("!active", "#e9ecef")],
                 foreground=[("pressed", "white"), ("active", "white"), ("!active", self.text_primary)])
        
        # Combobox styling
        style.configure("TCombobox", font=("Segoe UI", 9), fieldbackground=self.bg_secondary)
        
        # Notebook styling
        style.configure("TNotebook", background=self.bg_primary, borderwidth=0)
        style.configure("TNotebook.Tab", padding=[16, 12], font=("Segoe UI", 10))
        style.map("TNotebook.Tab", 
                 background=[("selected", self.bg_secondary)])
        
        # Radio and Checkbutton styling
        style.configure("TRadiobutton", background=self.bg_primary, foreground=self.text_primary,
                       font=("Segoe UI", 9))
        style.configure("TCheckbutton", background=self.bg_primary, foreground=self.text_primary,
                       font=("Segoe UI", 9))
        
        # Setup directories
        self.unprocessed_dir = Path("unprocessed")
        self.processed_dir = Path("processed")
        self.results_dir = Path("results")
        
        for d in [self.unprocessed_dir, self.processed_dir, self.results_dir]:
            d.mkdir(exist_ok=True)
        
        # Initialize recipe database and predictor
        self.recipe_db = RecipeDatabase("recipes.json")
        self.recipe_predictor = RecipePredictor(self.recipe_db.get_recipes_with_porosity())
        
        self.current_image = None
        self.current_image_path = None
        self.analysis_result = None
        self.current_recipe_id = None
        
        self.setup_ui()
        self.refresh_image_list()
    
    def setup_ui(self):
        """Setup the user interface"""
        
        # Header
        header = ttk.Frame(self.root)
        header.pack(fill=tk.X, padx=0, pady=0)
        
        header_bg = tk.Frame(header, bg=self.bg_accent, height=70)
        header_bg.pack(fill=tk.X)
        
        title_label = tk.Label(header_bg, text="Bread Porosity Analysis Tool", 
                               font=("Segoe UI", 18, "bold"), fg="white", bg=self.bg_accent)
        title_label.pack(pady=15)
        
        # Main container with padding
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Left panel - Controls
        left_panel = ttk.Frame(main_container, width=320)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 15))
        
        # Image Management Section
        img_section = ttk.LabelFrame(left_panel, text="Image Library", padding=12)
        img_section.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Listbox with professional styling
        listbox_frame = ttk.Frame(img_section)
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.image_listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set, 
                                         height=12, font=("Segoe UI", 9), 
                                         bg=self.bg_secondary, fg=self.text_primary,
                                         relief=tk.FLAT, borderwidth=0, highlightthickness=1,
                                         highlightcolor=self.bg_accent)
        self.image_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.image_listbox.yview)
        self.image_listbox.bind("<<ListboxSelect>>", self.on_image_select)
        
        # Button row
        button_row = ttk.Frame(img_section)
        button_row.pack(fill=tk.X)
        
        ttk.Button(button_row, text="Open Folder", 
                  command=self.open_folder).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(button_row, text="Refresh", 
                  command=self.refresh_image_list).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Parameters Section
        params_frame = ttk.LabelFrame(left_panel, text="Analysis Parameters", padding=12)
        params_frame.pack(fill=tk.X, pady=10)
        
        # Pixel size
        ttk.Label(params_frame, text="Pixel Size (mm):", style="Subheader.TLabel").grid(
            row=0, column=0, sticky=tk.W, pady=8)
        self.pixel_size_var = tk.DoubleVar(value=0.1)
        pixel_entry = ttk.Entry(params_frame, textvariable=self.pixel_size_var, width=15)
        pixel_entry.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # Threshold
        ttk.Label(params_frame, text="Threshold Method:", style="Subheader.TLabel").grid(
            row=1, column=0, sticky=tk.W, pady=8)
        self.threshold_var = tk.StringVar(value="otsu")
        ttk.Combobox(params_frame, textvariable=self.threshold_var, 
                    values=["otsu", "adaptive"], state="readonly", width=13).grid(
            row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        # Normalize
        ttk.Label(params_frame, text="Normalization:", style="Subheader.TLabel").grid(
            row=2, column=0, sticky=tk.W, pady=8)
        self.normalize_var = tk.StringVar(value="clahe")
        ttk.Combobox(params_frame, textvariable=self.normalize_var,
                    values=["clahe", "morphology", "gaussian"], state="readonly", width=13).grid(
            row=2, column=1, sticky=tk.W, padx=(10, 0))
        
        # Mode Selection
        mode_frame = ttk.LabelFrame(left_panel, text="Analysis Mode", padding=12)
        mode_frame.pack(fill=tk.X, pady=10)
        
        self.mode_var = tk.StringVar(value="single")
        ttk.Radiobutton(mode_frame, text="Single Image", variable=self.mode_var, 
                       value="single", command=self.on_mode_change).pack(anchor=tk.W, pady=5)
        ttk.Radiobutton(mode_frame, text="Loaf (Multiple Slices)", variable=self.mode_var,
                       value="loaf", command=self.on_mode_change).pack(anchor=tk.W, pady=5)
        
        # Loaf name
        ttk.Label(mode_frame, text="Loaf Name:", style="Subheader.TLabel").pack(anchor=tk.W, pady=(10, 5))
        self.loaf_name_var = tk.StringVar(value="my_loaf")
        self.loaf_name_entry = ttk.Entry(mode_frame, textvariable=self.loaf_name_var, width=30)
        self.loaf_name_entry.pack(fill=tk.X)
        self.loaf_name_entry.config(state=tk.DISABLED)
        
        # Action Buttons
        action_frame = ttk.Frame(left_panel)
        action_frame.pack(fill=tk.X, pady=15)
        
        self.analyze_btn = tk.Button(action_frame, text="Analyze", 
                                     command=self.start_analysis,
                                     bg=self.bg_accent, fg="white",
                                     font=("Segoe UI", 11, "bold"),
                                     relief=tk.FLAT, padx=20, pady=12,
                                     cursor="hand2", activebackground="#0056b3")
        self.analyze_btn.pack(fill=tk.X, pady=(0, 8))
        
        ttk.Button(action_frame, text="Clear Selection", 
                  command=self.clear_selection).pack(fill=tk.X)
        
        # Status Section
        status_frame = ttk.LabelFrame(left_panel, text="Status", padding=12)
        status_frame.pack(fill=tk.X, pady=10)
        
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = tk.Label(status_frame, textvariable=self.status_var, 
                                    foreground=self.success_color, 
                                    font=("Segoe UI", 9, "bold"),
                                    bg=self.bg_primary, wraplength=280, justify=tk.LEFT)
        self.status_label.pack(fill=tk.X)
        
        # Progress bar
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate', length=280)
        self.progress.pack(fill=tk.X, pady=(10, 0))
        
        # Right panel - Results
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Notebook with modern tabs
        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Preview tab
        preview_tab = ttk.Frame(self.notebook)
        self.notebook.add(preview_tab, text="Preview")
        
        preview_bg = tk.Frame(preview_tab, bg=self.bg_secondary)
        preview_bg.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        self.preview_label = tk.Label(preview_bg, text="Select an image to preview", 
                                      bg=self.bg_secondary, fg=self.text_secondary,
                                      font=("Segoe UI", 10))
        self.preview_label.pack(fill=tk.BOTH, expand=True)
        
        # Results tab
        results_tab = ttk.Frame(self.notebook)
        self.notebook.add(results_tab, text="Results")
        
        results_scroll = ttk.Scrollbar(results_tab)
        results_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.results_text = tk.Text(results_tab, yscrollcommand=results_scroll.set,
                                    font=("Consolas", 9), bg=self.bg_secondary,
                                    fg=self.text_primary, relief=tk.FLAT, 
                                    borderwidth=0, padx=10, pady=10)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        results_scroll.config(command=self.results_text.yview)
        
        # Metrics tab
        metrics_tab = ttk.Frame(self.notebook)
        self.notebook.add(metrics_tab, text="Metrics (JSON)")
        
        metrics_scroll = ttk.Scrollbar(metrics_tab)
        metrics_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.metrics_text = tk.Text(metrics_tab, yscrollcommand=metrics_scroll.set,
                                   font=("Consolas", 9), bg=self.bg_secondary,
                                   fg=self.text_primary, relief=tk.FLAT,
                                   borderwidth=0, padx=10, pady=10)
        self.metrics_text.pack(fill=tk.BOTH, expand=True)
        metrics_scroll.config(command=self.metrics_text.yview)
        
        # Recipe Management tab
        recipe_tab = ttk.Frame(self.notebook)
        self.notebook.add(recipe_tab, text="Recipes & Prediction")
        
        recipe_container = ttk.Frame(recipe_tab)
        recipe_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left side - Recipe input
        left_recipe = ttk.LabelFrame(recipe_container, text="New Recipe", padding=12)
        left_recipe.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        recipe_scroll = ttk.Scrollbar(left_recipe)
        recipe_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.recipe_input_text = tk.Text(left_recipe, yscrollcommand=recipe_scroll.set,
                                        font=("Consolas", 9), bg=self.bg_secondary,
                                        fg=self.text_primary, relief=tk.FLAT,
                                        borderwidth=0, padx=8, pady=8, height=25)
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
  "measured_porosity": null
}"""
        self.recipe_input_text.insert(1.0, template)
        
        # Right side - Recipe management and prediction
        right_recipe = ttk.LabelFrame(recipe_container, text="Recipe Management", padding=12)
        right_recipe.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Recipe list
        ttk.Label(right_recipe, text="Saved Recipes:").pack(anchor=tk.W)
        recipe_listbox_frame = ttk.Frame(right_recipe)
        recipe_listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
        recipe_scrollbar = ttk.Scrollbar(recipe_listbox_frame)
        recipe_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.recipe_listbox = tk.Listbox(recipe_listbox_frame, yscrollcommand=recipe_scrollbar.set,
                                        font=("Segoe UI", 9), bg=self.bg_secondary,
                                        fg=self.text_primary, relief=tk.FLAT,
                                        borderwidth=0, highlightthickness=1,
                                        highlightcolor=self.bg_accent)
        self.recipe_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.recipe_listbox.bind("<<ListboxSelect>>", self.on_recipe_select)
        recipe_scrollbar.config(command=self.recipe_listbox.yview)
        
        # Recipe buttons
        recipe_btn_frame = ttk.Frame(right_recipe)
        recipe_btn_frame.pack(fill=tk.X, pady=(10, 10))
        
        ttk.Button(recipe_btn_frame, text="Log Recipe", 
                  command=self.log_new_recipe).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(recipe_btn_frame, text="Save Porosity", 
                  command=self.save_recipe_porosity).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(recipe_btn_frame, text="Predict", 
                  command=self.predict_from_recipe).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(recipe_btn_frame, text="Create Variant", 
                  command=self.create_recipe_variant).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(recipe_btn_frame, text="Clone Recipe", 
                  command=self.clone_recipe).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(recipe_btn_frame, text="Scale Recipe", 
                  command=self.scale_recipe_gui).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(recipe_btn_frame, text="Family Tree", 
                  command=self.display_recipe_family).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(recipe_btn_frame, text="Delete", 
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
        self.notebook.add(stats_tab, text="Statistics Dashboard")
        
        stats_scroll = ttk.Scrollbar(stats_tab)
        stats_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.stats_text = tk.Text(stats_tab, yscrollcommand=stats_scroll.set,
                                 font=("Consolas", 9), bg=self.bg_secondary,
                                 fg=self.text_primary, relief=tk.FLAT,
                                 borderwidth=0, padx=10, pady=10)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        stats_scroll.config(command=self.stats_text.yview)
        
        # Button to refresh stats
        stats_btn_frame = ttk.Frame(stats_tab)
        stats_btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        ttk.Button(stats_btn_frame, text="Refresh Statistics", 
                  command=self.display_statistics_dashboard).pack(side=tk.LEFT)
        
        # Loaf Consistency Tracking tab
        consist_tab = ttk.Frame(self.notebook)
        self.notebook.add(consist_tab, text="Loaf Consistency")
        
        consist_scroll = ttk.Scrollbar(consist_tab)
        consist_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.consist_text = tk.Text(consist_tab, yscrollcommand=consist_scroll.set,
                                   font=("Consolas", 9), bg=self.bg_secondary,
                                   fg=self.text_primary, relief=tk.FLAT,
                                   borderwidth=0, padx=10, pady=10)
        self.consist_text.pack(fill=tk.BOTH, expand=True)
        consist_scroll.config(command=self.consist_text.yview)
        
        # Comparison Tools tab
        compare_tab = ttk.Frame(self.notebook)
        self.notebook.add(compare_tab, text="Comparison Tools")
        
        compare_scroll = ttk.Scrollbar(compare_tab)
        compare_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.compare_text = tk.Text(compare_tab, yscrollcommand=compare_scroll.set,
                                   font=("Consolas", 9), bg=self.bg_secondary,
                                   fg=self.text_primary, relief=tk.FLAT,
                                   borderwidth=0, padx=10, pady=10)
        self.compare_text.pack(fill=tk.BOTH, expand=True)
        compare_scroll.config(command=self.compare_text.yview)
        
        # Buttons for comparison
        compare_btn_frame = ttk.Frame(compare_tab)
        compare_btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        ttk.Button(compare_btn_frame, text="Compare Recipes", 
                  command=self.compare_recipes).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(compare_btn_frame, text="What-If Analysis", 
                  command=self.what_if_analysis).pack(side=tk.LEFT)
    
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
        self.results_text.delete(1.0, tk.END)
        self.metrics_text.delete(1.0, tk.END)
    
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
            
            self.set_status("✓ Analysis complete!", color=self.success_color)
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
                
                self.set_status(f"✓ Loaf analysis complete!", color=self.success_color)
                
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
        metrics = result['metrics']
        
        results_text = f"""
BREAD POROSITY ANALYSIS RESULTS
{'='*50}

IMAGE: {Path(result['image_path']).name}
Pixel Size: {result['pixel_size_mm']:.2f} mm

POROSITY
────────────────────────────────
  Porosity:           {metrics['porosity_percent']:.2f}%
  Hole pixels:        {metrics['hole_pixels']:,}
  Crumb pixels:       {metrics['crumb_pixels']:,}

HOLE METRICS
────────────────────────────────
  Number of holes:    {metrics['num_holes']}
  Mean diameter:      {metrics['mean_hole_diameter_mm']:.2f} mm
  Max diameter:       {metrics['largest_hole_diameter_mm']:.2f} mm
  Min diameter:       {metrics['smallest_hole_diameter_mm']:.2f} mm
  Uniformity (CV):    {metrics['hole_area_cv']:.3f}
  Holes per cm²:      {metrics['holes_per_cm2']:.1f}

SHAPE ANALYSIS
────────────────────────────────
  Mean aspect ratio:  {metrics['mean_aspect_ratio']:.2f}
  Aspect ratio std:   {metrics['aspect_ratio_std']:.2f}
  Mean orientation:   {metrics['mean_orientation_deg']:.1f}°
  Orientation entropy:{metrics['orientation_entropy']:.2f} / 4.17

CRUMB UNIFORMITY
────────────────────────────────
  Brightness mean:    {metrics['crumb_brightness_mean']:.1f}
  Brightness std:     {metrics['crumb_brightness_std']:.1f}
  Brightness CV:      {metrics['crumb_brightness_cv']:.3f}
  Brightness skew:    {metrics['crumb_brightness_skewness']:.2f}

OUTPUT FILES
────────────────────────────────
  Comparison:         {Path(result['output_files']['comparison']).name}
  Distributions:      {Path(result['output_files']['distributions']).name}
  Annotated:          {Path(result['output_files']['annotated']).name}
  Metrics JSON:       {Path(result['output_files']['metrics_json']).name}

"""
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, results_text)
        
        # Display metrics JSON
        metrics_json = json.dumps(metrics, indent=2)
        self.metrics_text.delete(1.0, tk.END)
        self.metrics_text.insert(1.0, metrics_json)
        
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
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, results_text)
        
        # Display full report JSON
        report_json = json.dumps(result, indent=2)
        self.metrics_text.delete(1.0, tk.END)
        self.metrics_text.insert(1.0, report_json)
        
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
        """Parse and log a new recipe from the input text"""
        try:
            recipe_text = self.recipe_input_text.get(1.0, tk.END).strip()
            
            # Extract JSON content
            import json
            start = recipe_text.find('{')
            end = recipe_text.rfind('}') + 1
            
            if start == -1 or end == 0:
                messagebox.showerror("Error", "Could not find JSON in recipe input")
                return
            
            json_str = recipe_text[start:end]
            recipe_data = json.loads(json_str)
            
            # Validate required fields
            required = ['name', 'ingredients', 'mixing_time_min', 'proof_time_min',
                       'oven_temp_c', 'cooking_vessel', 'cook_time_min']
            for field in required:
                if field not in recipe_data:
                    messagebox.showerror("Error", f"Missing required field: {field}")
                    return
            
            # Add recipe to database with environmental parameters
            recipe = self.recipe_db.add_recipe(
                recipe_name=recipe_data['name'],
                ingredients=recipe_data['ingredients'],
                mixing_time_min=float(recipe_data['mixing_time_min']),
                proof_time_min=float(recipe_data['proof_time_min']),
                oven_temp_c=float(recipe_data['oven_temp_c']),
                cooking_vessel=recipe_data['cooking_vessel'],
                cook_time_min=float(recipe_data['cook_time_min']),
                notes=recipe_data.get('notes', ''),
                room_temp_c=float(recipe_data.get('room_temp_c')) if recipe_data.get('room_temp_c') else None,
                room_humidity_pct=float(recipe_data.get('room_humidity_pct')) if recipe_data.get('room_humidity_pct') else None,
                altitude_m=float(recipe_data.get('altitude_m')) if recipe_data.get('altitude_m') else None
            )
            
            self.refresh_recipe_list()
            self.set_status(f"✓ Recipe logged: {recipe['name']}", self.success_color)
            messagebox.showinfo("Success", f"Recipe '{recipe['name']}' saved!\n\nRecipe ID: {recipe['id']}\n\nNow analyze an image and save the porosity result.")
        
        except json.JSONDecodeError as e:
            messagebox.showerror("JSON Error", f"Invalid JSON format:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not log recipe:\n{str(e)}")
    
    def create_recipe_variant(self):
        """Create a variant of the current recipe"""
        if self.current_recipe_id is None:
            messagebox.showwarning("Warning", "Please select a recipe first")
            return
        
        parent = self.recipe_db.get_recipe(self.current_recipe_id)
        if not parent:
            return
        
        # Create a simple variant dialog
        variant_name = messagebox.showinput("Create Variant", f"Enter name for variant of '{parent['name']}':")
        
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
            self.set_status(f"✓ Variant created: {variant_name}", self.success_color)
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
        self.set_status("✓ Recipe family displayed", self.success_color)

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
            self.set_status(f"✓ Porosity saved: {porosity:.2f}%", self.success_color)
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
        
        self.set_status(f"✓ Prediction: {predicted_porosity:.1f}%", self.success_color)
    
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
            self.set_status("✓ Recipe deleted", self.success_color)
    
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
                self.set_status(f"✓ Recipe cloned: {cloned['name']}", self.success_color)
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
                
                self.set_status(f"✓ Recipe scaled: {scaled['name']}", self.success_color)
                messagebox.showinfo("Success", f"Recipe scaled and saved as '{scaled['name']}'")
            else:
                messagebox.showerror("Error", "Could not scale recipe")
                
        except ValueError:
            messagebox.showerror("Error", "Invalid scale factor. Please enter a number (e.g., 0.5, 2.0)")
        except Exception as e:
            messagebox.showerror("Error", f"Scale failed:\n{str(e)}")
    
    def display_statistics_dashboard(self):
        """Display comprehensive statistics dashboard"""
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
            self.set_status("✓ Statistics dashboard refreshed", self.success_color)
            
        except Exception as e:
            output = f"Error generating statistics dashboard:\n\n{str(e)}\n\n{traceback.format_exc()}"
            self.stats_text.insert("1.0", output)
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
        
        self.compare_text.delete("1.0", tk.END)
        self.compare_text.insert("1.0", output)
        self.notebook.select(5)  # Switch to comparison tab
        self.set_status("✓ Recipes compared", self.success_color)
    
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
        
        self.compare_text.delete("1.0", tk.END)
        self.compare_text.insert("1.0", output)
        self.notebook.select(5)  # Switch to comparison tab
        self.set_status("✓ What-if analysis complete", self.success_color)
    
    def display_loaf_consistency(self):
        """Display loaf consistency analysis for multi-slice data"""
        if not self.analysis_result:
            self.consist_text.delete("1.0", tk.END)
            self.consist_text.insert("1.0", "No loaf analysis data available.\n\nPerform a loaf analysis first by:\n1. Selecting 'Loaf Analysis' mode\n2. Entering a loaf name\n3. Ensuring multiple slices exist in the results")
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
        
        self.consist_text.delete("1.0", tk.END)
        self.consist_text.insert("1.0", output)



def main():
    root = tk.Tk()
    app = BreadPorositytoolGUI(root)
    app.refresh_recipe_list()
    root.mainloop()


if __name__ == "__main__":
    main()
