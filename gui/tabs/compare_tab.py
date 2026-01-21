"""
Compare Tab
Compare multiple recipes side-by-side
"""

import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import List

from gui.controllers.recipe_controller import RecipeController
from gui.theme import get_theme
from models.recipe import Recipe


class CompareTab(ttk.Frame):
    """Tab for comparing recipes."""

    def __init__(self, parent, recipe_controller: RecipeController):
        super().__init__(parent)

        self.recipe_controller = recipe_controller
        self.recipe_service = recipe_controller.recipe_service
        self.recipes: List[Recipe] = []
        self.theme = get_theme()
        self.colors = self.theme.colors

        self.listbox: tk.Listbox
        self.output_text: scrolledtext.ScrolledText

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
        ttk.Button(controls, text="Compare", command=self._compare_selected).pack(side=tk.LEFT, padx=5)

        self.listbox = tk.Listbox(
            left_frame,
            selectmode=tk.MULTIPLE,
            height=12,
            bg=self.colors.bg_tertiary,
            fg=self.colors.text_primary,
            selectbackground=self.colors.bg_accent,
            highlightcolor=self.colors.border_color
        )
        self.listbox.pack(fill=tk.BOTH, expand=True)

        self.output_text = scrolledtext.ScrolledText(
            right_frame,
            wrap=tk.WORD,
            font=('Consolas', 9),
            bg=self.colors.bg_secondary,
            fg=self.colors.text_primary,
            insertbackground=self.colors.bg_accent
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.output_text.insert(tk.END, "Select multiple recipes to compare.")

    def refresh_recipes(self) -> None:
        self.recipes = self.recipe_controller.get_all_recipes()
        self.listbox.delete(0, tk.END)

        for recipe in self.recipes:
            label = f"{recipe.id}: {recipe.name}"
            self.listbox.insert(tk.END, label)

    def _compare_selected(self) -> None:
        selection = self.listbox.curselection()
        if len(selection) < 2:
            messagebox.showinfo("Select Recipes", "Select at least two recipes to compare.")
            return

        recipe_ids = [self.recipes[i].id for i in selection]
        comparison = self.recipe_service.compare_recipes(recipe_ids)

        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, json.dumps(comparison, indent=2))
