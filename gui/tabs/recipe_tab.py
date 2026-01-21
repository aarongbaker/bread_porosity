"""
Recipe Tab
Browse recipes and view details or predictions
"""

import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import List, Optional

from gui.controllers.recipe_controller import RecipeController
from gui.theme import get_theme
from models.recipe import Recipe


class RecipeTab(ttk.Frame):
    """Tab for browsing recipes."""

    def __init__(self, parent, recipe_controller: RecipeController):
        super().__init__(parent)

        self.recipe_controller = recipe_controller
        self.recipes: List[Recipe] = []
        self.theme = get_theme()
        self.colors = self.theme.colors

        self.listbox: tk.Listbox
        self.details_text: scrolledtext.ScrolledText
        self.porosity_var = tk.StringVar()
        self.scale_var = tk.StringVar(value="1.0")

        self._build_ui()
        self.refresh_recipes()

    def _build_ui(self) -> None:
        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_frame = ttk.Frame(main_pane)
        right_frame = ttk.Frame(main_pane)
        main_pane.add(left_frame, weight=1)
        main_pane.add(right_frame, weight=3)

        controls = ttk.Frame(left_frame)
        controls.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(controls, text="Refresh", command=self.refresh_recipes).pack(side=tk.LEFT)
        ttk.Button(controls, text="View", command=self._view_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls, text="Predict", command=self._predict_selected).pack(side=tk.LEFT)

        action_frame = ttk.Frame(right_frame)
        action_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(action_frame, text="Porosity").pack(side=tk.LEFT)
        ttk.Entry(action_frame, textvariable=self.porosity_var, width=8).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Update Porosity", command=self._update_porosity).pack(
            side=tk.LEFT
        )

        ttk.Label(action_frame, text="Scale").pack(side=tk.LEFT, padx=(10, 0))
        ttk.Entry(action_frame, textvariable=self.scale_var, width=6).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Scale", command=self._scale_recipe).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(action_frame, text="Delete", command=self._delete_recipe).pack(side=tk.LEFT)
        ttk.Button(action_frame, text="Create From JSON", command=self._create_from_json).pack(
            side=tk.RIGHT
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

        self.details_text = scrolledtext.ScrolledText(
            right_frame,
            wrap=tk.WORD,
            font=('Consolas', 9),
            bg=self.colors.bg_secondary,
            fg=self.colors.text_primary,
            insertbackground=self.colors.bg_accent
        )
        self.details_text.pack(fill=tk.BOTH, expand=True)
        self.details_text.insert(tk.END, "Select a recipe to view details.")

    def refresh_recipes(self) -> None:
        """Reload recipes."""
        self.recipes = self.recipe_controller.get_all_recipes()
        self.listbox.delete(0, tk.END)

        for recipe in self.recipes:
            label = f"{recipe.id}: {recipe.name}"
            self.listbox.insert(tk.END, label)

    def _get_selected_recipe(self) -> Optional[Recipe]:
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showinfo("No Selection", "Select a recipe first.")
            return None
        return self.recipes[selection[0]]

    def _view_selected(self) -> None:
        recipe = self._get_selected_recipe()
        if not recipe:
            return

        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(tk.END, json.dumps(recipe.to_dict(), indent=2))

    def _predict_selected(self) -> None:
        recipe = self._get_selected_recipe()
        if not recipe:
            return

        prediction = self.recipe_controller.predict_porosity(str(recipe.id))
        if not prediction:
            messagebox.showwarning("Prediction Failed", "No prediction available.")
            return

        payload = {
            "recipe": recipe.to_dict(),
            "prediction": prediction
        }
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(tk.END, json.dumps(payload, indent=2))

    def _update_porosity(self) -> None:
        recipe = self._get_selected_recipe()
        if not recipe:
            return

        try:
            porosity = float(self.porosity_var.get())
        except ValueError:
            messagebox.showwarning("Invalid Porosity", "Enter a numeric porosity value.")
            return

        success = self.recipe_controller.update_recipe_porosity(str(recipe.id), porosity)
        if success:
            messagebox.showinfo("Updated", "Porosity updated.")
            self.refresh_recipes()

    def _scale_recipe(self) -> None:
        recipe = self._get_selected_recipe()
        if not recipe:
            return

        try:
            scale_factor = float(self.scale_var.get())
        except ValueError:
            messagebox.showwarning("Invalid Scale", "Enter a numeric scale factor.")
            return

        scaled = self.recipe_controller.scale_recipe(str(recipe.id), scale_factor)
        if not scaled:
            messagebox.showwarning("Scale Failed", "Unable to scale recipe.")
            return

        self.refresh_recipes()

    def _delete_recipe(self) -> None:
        recipe = self._get_selected_recipe()
        if not recipe:
            return

        deleted = self.recipe_controller.delete_recipe(str(recipe.id))
        if deleted:
            self.refresh_recipes()

    def _create_from_json(self) -> None:
        try:
            data = json.loads(self.details_text.get(1.0, tk.END))
        except json.JSONDecodeError:
            messagebox.showwarning("Invalid JSON", "Fix JSON before creating recipe.")
            return

        recipe = self.recipe_controller.create_recipe(data)
        if recipe:
            self.refresh_recipes()
