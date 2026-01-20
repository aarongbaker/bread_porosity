"""
Recipe Builder Form
Form-based recipe input instead of JSON editing for non-technical users.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json


class RecipeBuilderForm:
    """User-friendly form for creating and editing recipes."""
    
    def __init__(self, parent, on_save_callback, existing_recipe=None):
        """
        Initialize recipe builder form.
        
        Args:
            parent: Parent Tkinter widget
            on_save_callback: Function to call when recipe is saved
            existing_recipe: Existing recipe dict to edit (None for new)
        """
        self.parent = parent
        self.on_save = on_save_callback
        self.recipe = existing_recipe or {}
        self.window = None
        self.fields = {}
        self.ingredients_list = []
    
    def show(self):
        """Show the recipe builder form."""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Recipe Builder")
        self.window.geometry("600x800")
        
        # Color scheme
        self.bg_primary = "#0f1419"
        self.bg_secondary = "#1a1f2e"
        self.text_primary = "#ffffff"
        self.text_secondary = "#b0b9c1"
        
        self.window.configure(bg=self.bg_primary)
        
        # Create notebook for sections
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Basic Info
        self._create_basic_info_tab(notebook)
        
        # Tab 2: Ingredients
        self._create_ingredients_tab(notebook)
        
        # Tab 3: Process
        self._create_process_tab(notebook)
        
        # Tab 4: Environment
        self._create_environment_tab(notebook)
        
        # Buttons at bottom
        button_frame = tk.Frame(self.window, bg=self.bg_primary)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(button_frame, text="Save Recipe", 
                  command=self._save_recipe).pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        ttk.Button(button_frame, text="Cancel", 
                  command=self.window.destroy).pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def _create_basic_info_tab(self, notebook):
        """Create basic recipe info tab."""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Basic Info")
        
        inner = tk.Frame(frame, bg=self.bg_secondary)
        inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Recipe name
        tk.Label(inner, text="Recipe Name", font=("Segoe UI", 10, "bold"),
                fg=self.text_primary, bg=self.bg_secondary).pack(anchor=tk.W, pady=(0, 5))
        self.fields['name'] = ttk.Entry(inner, width=40)
        self.fields['name'].pack(fill=tk.X, pady=(0, 15))
        self.fields['name'].insert(0, self.recipe.get('name', 'My Recipe'))
        
        # Recipe type
        tk.Label(inner, text="Bread Type", font=("Segoe UI", 10, "bold"),
                fg=self.text_primary, bg=self.bg_secondary).pack(anchor=tk.W, pady=(0, 5))
        self.fields['type'] = ttk.Combobox(inner, 
                                          values=["Sourdough", "Whole Wheat", "Ciabatta", 
                                                 "Sandwich", "Baguette", "Other"],
                                          state="readonly", width=37)
        self.fields['type'].pack(fill=tk.X, pady=(0, 15))
        self.fields['type'].set(self.recipe.get('type', 'Sourdough'))
        
        # Notes
        tk.Label(inner, text="Notes (optional)", font=("Segoe UI", 10, "bold"),
                fg=self.text_primary, bg=self.bg_secondary).pack(anchor=tk.W, pady=(0, 5))
        self.fields['notes'] = tk.Text(inner, height=5, width=40, bg=self.bg_secondary,
                                      fg=self.text_primary, relief=tk.FLAT)
        self.fields['notes'].pack(fill=tk.BOTH, expand=True)
        self.fields['notes'].insert(1.0, self.recipe.get('notes', ''))
    
    def _create_ingredients_tab(self, notebook):
        """Create ingredients tab."""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Ingredients")
        
        inner = tk.Frame(frame, bg=self.bg_secondary)
        inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Common ingredients with typical amounts
        common_ingredients = [
            ("Bread Flour", "g"),
            ("Water", "g"),
            ("Salt", "g"),
            ("Yeast (instant)", "g"),
            ("Yeast (starter)", "g"),
            ("Olive Oil", "ml"),
            ("Sugar", "g"),
            ("Whole Wheat Flour", "g"),
            ("Rye Flour", "g")
        ]
        
        # Header
        tk.Label(inner, text="Add Common Ingredients", font=("Segoe UI", 9, "bold"),
                fg=self.text_primary, bg=self.bg_secondary).pack(anchor=tk.W, pady=(0, 10))
        
        # Grid for ingredient inputs
        grid_frame = tk.Frame(inner, bg=self.bg_secondary)
        grid_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        tk.Label(grid_frame, text="Ingredient", font=("Segoe UI", 8, "bold"),
                fg=self.text_secondary, bg=self.bg_secondary).grid(row=0, column=0, sticky=tk.W, padx=5)
        tk.Label(grid_frame, text="Amount", font=("Segoe UI", 8, "bold"),
                fg=self.text_secondary, bg=self.bg_secondary).grid(row=0, column=1, sticky=tk.W, padx=5)
        
        self.ingredient_fields = {}
        existing_ingredients = self.recipe.get('ingredients', {})
        
        for i, (ingredient, unit) in enumerate(common_ingredients, 1):
            # Ingredient name
            tk.Label(grid_frame, text=ingredient, fg=self.text_primary, 
                    bg=self.bg_secondary).grid(row=i, column=0, sticky=tk.W, padx=5, pady=3)
            
            # Amount entry
            var = tk.DoubleVar(value=existing_ingredients.get(ingredient, 0))
            entry = ttk.Entry(grid_frame, textvariable=var, width=10)
            entry.grid(row=i, column=1, sticky=tk.W, padx=5, pady=3)
            
            # Unit label
            tk.Label(grid_frame, text=unit, fg=self.text_secondary,
                    bg=self.bg_secondary).grid(row=i, column=2, sticky=tk.W, padx=5, pady=3)
            
            self.ingredient_fields[ingredient] = var
        
        # Custom ingredient
        ttk.Button(grid_frame, text="Add Custom Ingredient",
                  command=self._add_custom_ingredient).pack(anchor=tk.W, pady=(10, 0))
    
    def _add_custom_ingredient(self):
        """Add a custom ingredient."""
        ingredient = simpledialog.askstring("Add Ingredient", "Ingredient name:")
        if not ingredient:
            return
        
        amount = simpledialog.askfloat("Add Ingredient", f"Amount for {ingredient} (in g or ml):")
        if amount is None:
            return
        
        self.ingredient_fields[ingredient] = tk.DoubleVar(value=amount)
        messagebox.showinfo("Added", f"Added {ingredient}: {amount}g/ml")
    
    def _create_process_tab(self, notebook):
        """Create baking process tab."""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Process")
        
        inner = tk.Frame(frame, bg=self.bg_secondary)
        inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Mixing
        tk.Label(inner, text="Mixing Time (minutes)", font=("Segoe UI", 10, "bold"),
                fg=self.text_primary, bg=self.bg_secondary).pack(anchor=tk.W, pady=(0, 5))
        self.fields['mixing_time_min'] = ttk.Entry(inner, width=10)
        self.fields['mixing_time_min'].pack(fill=tk.X, pady=(0, 15))
        self.fields['mixing_time_min'].insert(0, str(self.recipe.get('mixing_time_min', 10)))
        
        # Proof time
        tk.Label(inner, text="Proof/Fermentation Time (minutes)", font=("Segoe UI", 10, "bold"),
                fg=self.text_primary, bg=self.bg_secondary).pack(anchor=tk.W, pady=(0, 5))
        self.fields['proof_time_min'] = ttk.Entry(inner, width=10)
        self.fields['proof_time_min'].pack(fill=tk.X, pady=(0, 15))
        self.fields['proof_time_min'].insert(0, str(self.recipe.get('proof_time_min', 480)))
        
        # Oven temperature
        tk.Label(inner, text="Oven Temperature (°C)", font=("Segoe UI", 10, "bold"),
                fg=self.text_primary, bg=self.bg_secondary).pack(anchor=tk.W, pady=(0, 5))
        self.fields['oven_temp_c'] = ttk.Entry(inner, width=10)
        self.fields['oven_temp_c'].pack(fill=tk.X, pady=(0, 15))
        self.fields['oven_temp_c'].insert(0, str(self.recipe.get('oven_temp_c', 450)))
        
        # Cooking vessel
        tk.Label(inner, text="Cooking Vessel", font=("Segoe UI", 10, "bold"),
                fg=self.text_primary, bg=self.bg_secondary).pack(anchor=tk.W, pady=(0, 5))
        self.fields['cooking_vessel'] = ttk.Combobox(inner,
                                                     values=["Dutch Oven", "Baking Stone", 
                                                            "Loaf Pan", "Sheet Pan", "Cloche", "Other"],
                                                     state="readonly", width=37)
        self.fields['cooking_vessel'].pack(fill=tk.X, pady=(0, 15))
        self.fields['cooking_vessel'].set(self.recipe.get('cooking_vessel', 'Dutch Oven'))
        
        # Cook time
        tk.Label(inner, text="Cooking Time (minutes)", font=("Segoe UI", 10, "bold"),
                fg=self.text_primary, bg=self.bg_secondary).pack(anchor=tk.W, pady=(0, 5))
        self.fields['cook_time_min'] = ttk.Entry(inner, width=10)
        self.fields['cook_time_min'].pack(fill=tk.X, pady=(0, 15))
        self.fields['cook_time_min'].insert(0, str(self.recipe.get('cook_time_min', 40)))
    
    def _create_environment_tab(self, notebook):
        """Create environment conditions tab."""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Environment")
        
        inner = tk.Frame(frame, bg=self.bg_secondary)
        inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Room temperature
        tk.Label(inner, text="Room Temperature (°C) - Optional", font=("Segoe UI", 10, "bold"),
                fg=self.text_primary, bg=self.bg_secondary).pack(anchor=tk.W, pady=(0, 5))
        self.fields['room_temp_c'] = ttk.Entry(inner, width=10)
        self.fields['room_temp_c'].pack(fill=tk.X, pady=(0, 15))
        room_temp = self.recipe.get('room_temp_c')
        if room_temp:
            self.fields['room_temp_c'].insert(0, str(room_temp))
        
        # Humidity
        tk.Label(inner, text="Room Humidity (%) - Optional", font=("Segoe UI", 10, "bold"),
                fg=self.text_primary, bg=self.bg_secondary).pack(anchor=tk.W, pady=(0, 5))
        self.fields['room_humidity_pct'] = ttk.Entry(inner, width=10)
        self.fields['room_humidity_pct'].pack(fill=tk.X, pady=(0, 15))
        humidity = self.recipe.get('room_humidity_pct')
        if humidity:
            self.fields['room_humidity_pct'].insert(0, str(humidity))
        
        # Altitude
        tk.Label(inner, text="Altitude (meters) - Optional", font=("Segoe UI", 10, "bold"),
                fg=self.text_primary, bg=self.bg_secondary).pack(anchor=tk.W, pady=(0, 5))
        self.fields['altitude_m'] = ttk.Entry(inner, width=10)
        self.fields['altitude_m'].pack(fill=tk.X, pady=(0, 15))
        altitude = self.recipe.get('altitude_m')
        if altitude:
            self.fields['altitude_m'].insert(0, str(altitude))
        
        # Help text
        help_text = ("These optional fields help track how environmental\n"
                    "conditions affect fermentation and baking.\n\n"
                    "Typical values:\n"
                    "• Temperature: 18-25°C\n"
                    "• Humidity: 40-70%\n"
                    "• Altitude: 0-2000m")
        tk.Label(inner, text=help_text, font=("Segoe UI", 8), fg=self.text_secondary,
                bg=self.bg_secondary, justify=tk.LEFT).pack(anchor=tk.W, pady=(10, 0))
    
    def _save_recipe(self):
        """Save the recipe."""
        try:
            # Validate required fields
            if not self.fields['name'].get().strip():
                messagebox.showerror("Missing", "Recipe name is required")
                return
            
            # Build recipe dict
            recipe = {
                'name': self.fields['name'].get().strip(),
                'type': self.fields['type'].get(),
                'notes': self.fields['notes'].get(1.0, tk.END).strip(),
                'ingredients': {},
                'mixing_time_min': float(self.fields['mixing_time_min'].get()),
                'proof_time_min': float(self.fields['proof_time_min'].get()),
                'oven_temp_c': float(self.fields['oven_temp_c'].get()),
                'cooking_vessel': self.fields['cooking_vessel'].get(),
                'cook_time_min': float(self.fields['cook_time_min'].get()),
            }
            
            # Add ingredients (only if > 0)
            for ingredient, var in self.ingredient_fields.items():
                amount = var.get()
                if amount > 0:
                    recipe['ingredients'][ingredient] = amount
            
            # Add optional fields
            for field in ['room_temp_c', 'room_humidity_pct', 'altitude_m']:
                try:
                    value = float(self.fields[field].get()) if self.fields[field].get() else None
                    if value is not None:
                        recipe[field] = value
                except ValueError:
                    pass
            
            # Call save callback
            if self.on_save(recipe):
                messagebox.showinfo("Success", f"Recipe '{recipe['name']}' saved successfully!")
                self.window.destroy()
            else:
                messagebox.showerror("Error", "Could not save recipe")
        
        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Please check your inputs:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving recipe:\n{str(e)}")
