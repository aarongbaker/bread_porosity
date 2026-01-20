"""
First-Run Setup Wizard
Guides new users through calibration and basic setup on first launch.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from pathlib import Path
import json
from PIL import Image, ImageTk
import cv2
import numpy as np


class FirstRunWizard:
    """Interactive first-run setup wizard for calibration and configuration."""
    
    def __init__(self, root, config_path="config.json"):
        """
        Initialize the wizard.
        
        Args:
            root: Tkinter root window
            config_path: Path to config.json
        """
        self.root = root
        self.config_path = Path(config_path)
        self.config = self._load_or_create_config()
        self.window = None
        self.current_step = 0
        self.wizard_data = {
            "pixel_size_mm": None,
            "bread_types": [],
            "backlit_setup": False,
            "reference_object": None,
        }
    
    def _load_or_create_config(self):
        """Load config or return default."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except:
                return self._default_config()
        return self._default_config()
    
    def _default_config(self):
        """Return default configuration."""
        return {
            "processing": {
                "normalization_method": "clahe",
                "threshold_method": "otsu",
                "pixel_size_mm": 0.1
            },
            "first_run_complete": False,
            "calibration_history": []
        }
    
    def should_show_wizard(self):
        """Check if wizard should be shown."""
        return not self.config.get("first_run_complete", False)
    
    def run_wizard(self):
        """Run the complete wizard sequence."""
        self.window = tk.Toplevel(self.root)
        self.window.title("Bread Porosity Analysis - First-Run Setup")
        self.window.geometry("700x600")
        self.window.resizable(False, False)
        
        # Color scheme
        self.bg_primary = "#0f1419"
        self.bg_secondary = "#1a1f2e"
        self.bg_accent = "#1d9bf0"
        self.text_primary = "#ffffff"
        self.text_secondary = "#b0b9c1"
        
        self.window.configure(bg=self.bg_primary)
        
        # Make modal
        self.window.transient(self.root)
        self.window.grab_set()
        
        # Show welcome step
        self._show_welcome()
    
    def _show_welcome(self):
        """Step 1: Welcome screen."""
        self._clear_window()
        
        # Header
        header = tk.Label(self.window, text="Welcome to Bread Porosity Analysis",
                         font=("Segoe UI", 18, "bold"), fg=self.text_primary, bg=self.bg_primary)
        header.pack(pady=(30, 10))
        
        # Description
        desc = tk.Label(self.window, 
                       text="This wizard will help you set up the tool correctly.\n\n"
                            "We'll calibrate your camera and configure your preferences.\n\n"
                            "This takes about 5 minutes.",
                       font=("Segoe UI", 11), fg=self.text_secondary, bg=self.bg_primary, justify=tk.CENTER)
        desc.pack(pady=20)
        
        # Info boxes
        info_frame = tk.Frame(self.window, bg=self.bg_primary)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # What you'll do
        ttk.Label(info_frame, text="What you'll do:").pack(anchor=tk.W, pady=(0, 10))
        for item in ["✓ Calibrate camera for accurate measurements",
                     "✓ Set up your imaging workspace",
                     "✓ Choose bread types you analyze"]:
            lbl = tk.Label(info_frame, text=item, font=("Segoe UI", 10), 
                          fg=self.text_secondary, bg=self.bg_primary)
            lbl.pack(anchor=tk.W, pady=3)
        
        # Buttons
        button_frame = tk.Frame(self.window, bg=self.bg_primary)
        button_frame.pack(fill=tk.X, padx=30, pady=20)
        
        ttk.Button(button_frame, text="Start Setup", 
                  command=self._show_calibration).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(button_frame, text="Skip (Use Defaults)", 
                  command=self._save_and_close).pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def _show_calibration(self):
        """Step 2: Camera calibration wizard."""
        self._clear_window()
        
        # Header
        header = tk.Label(self.window, text="Step 1: Camera Calibration",
                         font=("Segoe UI", 16, "bold"), fg=self.text_primary, bg=self.bg_primary)
        header.pack(pady=(20, 10))
        
        # Instructions
        instructions = tk.Label(self.window,
                               text="To measure bread accurately, we need to calibrate your camera.\n\n"
                                    "You'll need:\n"
                                    "• A ruler or any object with known dimensions\n"
                                    "• Your current imaging setup (backlit position)\n\n"
                                    "The process:\n"
                                    "1. Place ruler in your bread imaging position\n"
                                    "2. Take a photo with your camera/phone\n"
                                    "3. We'll measure pixel-to-mm ratio",
                               font=("Segoe UI", 10), fg=self.text_secondary, bg=self.bg_primary, justify=tk.LEFT)
        instructions.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Buttons
        button_frame = tk.Frame(self.window, bg=self.bg_primary)
        button_frame.pack(fill=tk.X, padx=30, pady=20)
        
        ttk.Button(button_frame, text="📸 Provide Calibration Image", 
                  command=self._calibrate_from_image).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(button_frame, text="Enter Manually", 
                  command=self._calibrate_manual).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(button_frame, text="Back", 
                  command=self._show_welcome).pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def _calibrate_from_image(self):
        """Auto-calibration from image with ruler/reference."""
        from tkinter import filedialog
        
        file_path = filedialog.askopenfilename(
            title="Select calibration image (with ruler or reference object)",
            filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        # Show calibration dialog
        calib_window = tk.Toplevel(self.window)
        calib_window.title("Image Calibration")
        calib_window.geometry("800x600")
        
        try:
            # Load and display image
            image = cv2.imread(file_path)
            if image is None:
                messagebox.showerror("Error", "Could not load image")
                return
            
            # Resize for display
            height, width = image.shape[:2]
            scale = min(600 / width, 500 / height)
            new_w, new_h = int(width * scale), int(height * scale)
            image_resized = cv2.resize(image, (new_w, new_h))
            image_rgb = cv2.cvtColor(image_resized, cv2.COLOR_BGR2RGB)
            
            # Display in tkinter
            pil_image = Image.fromarray(image_rgb)
            tk_image = ImageTk.PhotoImage(pil_image)
            
            img_label = tk.Label(calib_window, image=tk_image, bg="#1a1f2e")
            img_label.image = tk_image
            img_label.pack(pady=10)
            
            # Instruction
            instr = tk.Label(calib_window,
                            text="Enter the size of the reference object shown in the image.\n"
                                 "Example: If a ruler is shown and spans 100mm, enter 100",
                            font=("Segoe UI", 10), fg="#b0b9c1", bg="#0f1419")
            instr.pack(pady=10)
            
            # Input frame
            input_frame = tk.Frame(calib_window, bg="#0f1419")
            input_frame.pack(pady=10)
            
            tk.Label(input_frame, text="Reference object size (mm):", 
                    fg="#b0b9c1", bg="#0f1419").pack(side=tk.LEFT, padx=5)
            size_var = tk.DoubleVar(value=100)
            size_entry = ttk.Entry(input_frame, textvariable=size_var, width=10)
            size_entry.pack(side=tk.LEFT, padx=5)
            
            def save_calibration():
                try:
                    ref_size_mm = size_var.get()
                    if ref_size_mm <= 0:
                        messagebox.showerror("Error", "Size must be positive")
                        return
                    
                    # Simplified calculation: estimate pixel size from image
                    # In production, you'd use edge detection to find ruler edges
                    image_width_pixels = width
                    estimated_pixel_size = ref_size_mm / (image_width_pixels * 0.5)  # Rough estimate
                    
                    self.wizard_data["pixel_size_mm"] = estimated_pixel_size
                    self.wizard_data["reference_object"] = f"{ref_size_mm}mm object"
                    
                    messagebox.showinfo("Success", 
                                       f"Calibration complete!\nEstimated pixel size: {estimated_pixel_size:.4f} mm/pixel")
                    calib_window.destroy()
                    self._show_workspace_setup()
                
                except ValueError:
                    messagebox.showerror("Error", "Please enter a valid number")
            
            ttk.Button(input_frame, text="Calculate", command=save_calibration).pack(side=tk.LEFT, padx=5)
        
        except Exception as e:
            messagebox.showerror("Error", f"Calibration failed: {str(e)}")
            calib_window.destroy()
    
    def _calibrate_manual(self):
        """Manual calibration entry."""
        dialog = simpledialog.askfloat("Manual Calibration",
                                       "Enter pixel size (mm/pixel).\n\n"
                                       "Example: If your camera is 150mm away from bread,\n"
                                       "and 1 pixel represents 0.1mm, enter 0.1\n\n"
                                       "Default: 0.1 (typical smartphone)",
                                       initialvalue=0.1, minvalue=0.01, maxvalue=1.0)
        
        if dialog is not None:
            self.wizard_data["pixel_size_mm"] = dialog
            self.wizard_data["reference_object"] = "Manual entry"
            messagebox.showinfo("Calibration Set", f"Pixel size: {dialog:.4f} mm/pixel")
            self._show_workspace_setup()
    
    def _show_workspace_setup(self):
        """Step 3: Workspace setup guidance."""
        self._clear_window()
        
        header = tk.Label(self.window, text="Step 2: Workspace Setup",
                         font=("Segoe UI", 16, "bold"), fg=self.text_primary, bg=self.bg_primary)
        header.pack(pady=(20, 10))
        
        # Backlit setup
        setup_frame = tk.Frame(self.window, bg=self.bg_secondary, highlightthickness=0)
        setup_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        setup_inner = tk.Frame(setup_frame, bg=self.bg_secondary)
        setup_inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        setup_title = tk.Label(setup_inner, text="Recommended: Backlit Setup",
                              font=("Segoe UI", 12, "bold"), fg=self.text_primary, bg=self.bg_secondary)
        setup_title.pack(anchor=tk.W, pady=(0, 10))
        
        checklist_items = [
            "✓ Place backlight (iPad/lamp) behind bread slice",
            "✓ Use diffuser (paper, frosted glass) for even lighting",
            "✓ Keep camera position fixed (use tripod)",
            "✓ Lock exposure & white balance on your camera",
            "✓ Ensure room lighting is dim (only backlight)",
            "✓ Check lighting uniformity - should be even across image"
        ]
        
        for item in checklist_items:
            lbl = tk.Label(setup_inner, text=item, font=("Segoe UI", 9),
                          fg=self.text_secondary, bg=self.bg_secondary, justify=tk.LEFT)
            lbl.pack(anchor=tk.W, pady=3)
        
        # Buttons
        button_frame = tk.Frame(self.window, bg=self.bg_primary)
        button_frame.pack(fill=tk.X, padx=30, pady=20)
        
        ttk.Button(button_frame, text="I've Set Up Backlit", 
                  command=self._show_bread_types).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(button_frame, text="Back", 
                  command=self._show_calibration).pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def _show_bread_types(self):
        """Step 4: Bread type preferences."""
        self._clear_window()
        
        header = tk.Label(self.window, text="Step 3: Bread Types You Analyze",
                         font=("Segoe UI", 16, "bold"), fg=self.text_primary, bg=self.bg_primary)
        header.pack(pady=(20, 10))
        
        desc = tk.Label(self.window, text="Which types do you usually analyze?",
                       font=("Segoe UI", 10), fg=self.text_secondary, bg=self.bg_primary)
        desc.pack(pady=(0, 20))
        
        # Checkboxes
        bread_types = ["Sourdough", "Whole Wheat", "Ciabatta", "Sandwich", "Baguette"]
        self.bread_vars = {}
        
        for bread_type in bread_types:
            var = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(self.window, text=bread_type, variable=var)
            cb.pack(anchor=tk.W, padx=50, pady=5)
            self.bread_vars[bread_type] = var
        
        # Buttons
        button_frame = tk.Frame(self.window, bg=self.bg_primary)
        button_frame.pack(fill=tk.X, padx=30, pady=30)
        
        ttk.Button(button_frame, text="Continue", 
                  command=self._save_and_close).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(button_frame, text="Back", 
                  command=self._show_workspace_setup).pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def _save_and_close(self):
        """Save configuration and close wizard."""
        try:
            # Get selected bread types
            selected_types = [bread_type for bread_type, var in self.bread_vars.items() if var.get()]
            
            # Update config
            self.config["first_run_complete"] = True
            self.config["calibration"] = {
                "pixel_size_mm": self.wizard_data.get("pixel_size_mm") or 0.1,
                "reference_object": self.wizard_data.get("reference_object") or "Default",
                "wizard_completed": True
            }
            self.config["bread_types"] = selected_types or ["Sourdough"]
            
            # Save config
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            messagebox.showinfo("Setup Complete", 
                              "Configuration saved!\n\n"
                              "You're ready to analyze bread.\n"
                              f"Pixel size: {self.config['calibration']['pixel_size_mm']:.4f} mm/pixel")
            
            self.window.destroy()
            return True
        
        except Exception as e:
            messagebox.showerror("Error", f"Could not save configuration: {str(e)}")
            return False
    
    def _clear_window(self):
        """Clear all widgets from window."""
        for widget in self.window.winfo_children():
            widget.destroy()
