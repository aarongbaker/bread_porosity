"""
Image Preview Component
Reusable component for displaying and interacting with images
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from pathlib import Path
from typing import Optional, Callable, Tuple, Dict
import threading

from gui.theme import get_theme


class ImagePreview(ttk.Frame):
    """Image preview component with zoom and pan capabilities"""

    def __init__(self, parent, controller=None, width=400, height=300):
        """
        Initialize image preview component

        Args:
            parent: Parent widget
            controller: Optional controller for handling events
            width: Default width
            height: Default height
        """
        super().__init__(parent)

        self.theme = get_theme()
        colors = self.theme.colors

        self.controller = controller
        self.width = width
        self.height = height

        # Image state
        self.original_image: Optional[Image.Image] = None
        self.display_image: Optional[ImageTk.PhotoImage] = None
        self.image_path: Optional[str] = None

        # Zoom and pan state
        self.zoom_factor = 1.0
        self.pan_x = 0
        self.pan_y = 0

        # UI elements
        self.canvas: Optional[tk.Canvas] = None
        self.scrollbar_x: Optional[ttk.Scrollbar] = None
        self.scrollbar_y: Optional[ttk.Scrollbar] = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the user interface"""
        colors = self.theme.colors
        
        # Create canvas with scrollbars
        self.canvas = tk.Canvas(
            self,
            bg=colors.bg_secondary,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightcolor=colors.border_color
        )

        self.scrollbar_x = ttk.Scrollbar(self, orient=tk.HORIZONTAL,
                                        command=self.canvas.xview)
        self.scrollbar_y = ttk.Scrollbar(self, orient=tk.VERTICAL,
                                        command=self.canvas.yview)

        self.canvas.config(xscrollcommand=self.scrollbar_x.set,
                          yscrollcommand=self.scrollbar_y.set)

        # Layout
        self.canvas.grid(row=0, column=0, sticky='nsew')
        self.scrollbar_x.grid(row=1, column=0, sticky='ew')
        self.scrollbar_y.grid(row=0, column=1, sticky='ns')

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Bind events
        self.canvas.bind('<ButtonPress-1>', self._on_mouse_press)
        self.canvas.bind('<B1-Motion>', self._on_mouse_drag)
        self.canvas.bind('<MouseWheel>', self._on_mouse_wheel)
        self.canvas.bind('<Button-4>', self._on_mouse_wheel)  # Linux scroll up
        self.canvas.bind('<Button-5>', self._on_mouse_wheel)  # Linux scroll down

        # Default message
        self._show_placeholder("Select an image to preview")

    def load_image(self, image_path: str) -> bool:
        """
        Load an image from file

        Args:
            image_path: Path to the image file

        Returns:
            True if successful, False otherwise
        """
        try:
            path = Path(image_path)
            if not path.exists():
                self._show_error(f"Image not found: {image_path}")
                return False

            # Load image
            self.original_image = Image.open(path)
            self.image_path = str(path)

            # Reset zoom and pan
            self.zoom_factor = 1.0
            self.pan_x = 0
            self.pan_y = 0

            # Display image
            self._update_display()

            return True

        except Exception as e:
            self._show_error(f"Failed to load image: {str(e)}")
            return False

    def load_image_async(self, image_path: str, callback: Optional[Callable] = None) -> None:
        """
        Load an image asynchronously

        Args:
            image_path: Path to the image file
            callback: Optional callback when loading completes
        """
        def load_thread():
            success = self.load_image(image_path)
            if callback:
                self.after(0, lambda: callback(success))

        thread = threading.Thread(target=load_thread, daemon=True)
        thread.start()

    def clear_image(self) -> None:
        """Clear the current image"""
        self.original_image = None
        self.display_image = None
        self.image_path = None
        self.zoom_factor = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self._show_placeholder("No image loaded")

    def _update_display(self) -> None:
        """Update the image display"""
        if not self.original_image or not self.canvas:
            return

        try:
            # Calculate display size
            img_width = int(self.original_image.width * self.zoom_factor)
            img_height = int(self.original_image.height * self.zoom_factor)

            # Resize image
            resized_image = self.original_image.resize((img_width, img_height),
                                                     Image.Resampling.LANCZOS)

            # Create PhotoImage
            self.display_image = ImageTk.PhotoImage(resized_image)

            # Update canvas
            self.canvas.delete('all')
            self.canvas.create_image(self.pan_x, self.pan_y,
                                   anchor=tk.NW, image=self.display_image)

            # Update scroll region
            self.canvas.config(scrollregion=(self.pan_x, self.pan_y,
                                           self.pan_x + img_width,
                                           self.pan_y + img_height))

        except Exception as e:
            self._show_error(f"Failed to update display: {str(e)}")

    def _show_placeholder(self, message: str) -> None:
        """Show placeholder message"""
        if not self.canvas:
            return

        colors = self.theme.colors
        self.canvas.delete('all')
        self.canvas.create_text(
            self.width // 2, self.height // 2,
            text=message,
            fill=colors.text_tertiary,
            font=('Segoe UI', 12),
            anchor=tk.CENTER
        )

    def _show_error(self, message: str) -> None:
        """Show error message"""
        if not self.canvas:
            return

        colors = self.theme.colors
        self.canvas.delete('all')
        self.canvas.create_text(
            self.width // 2, self.height // 2,
            text=message,
            fill=colors.bg_error,
            font=('Segoe UI', 10),
            anchor=tk.CENTER,
            width=self.width - 20
        )

    def _on_mouse_press(self, event) -> None:
        """Handle mouse press for panning"""
        self.canvas.scan_mark(event.x, event.y)

    def _on_mouse_drag(self, event) -> None:
        """Handle mouse drag for panning"""
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        # Update pan coordinates
        self.pan_x = self.canvas.canvasx(0)
        self.pan_y = self.canvas.canvasy(0)

    def _on_mouse_wheel(self, event) -> None:
        """Handle mouse wheel for zooming"""
        if event.delta > 0 or event.num == 4:  # Zoom in
            self.zoom_factor *= 1.1
        elif event.delta < 0 or event.num == 5:  # Zoom out
            self.zoom_factor *= 0.9

        # Limit zoom range
        self.zoom_factor = max(0.1, min(5.0, self.zoom_factor))

        self._update_display()

    def zoom_in(self) -> None:
        """Zoom in"""
        self.zoom_factor *= 1.1
        self.zoom_factor = min(5.0, self.zoom_factor)
        self._update_display()

    def zoom_out(self) -> None:
        """Zoom out"""
        self.zoom_factor *= 0.9
        self.zoom_factor = max(0.1, self.zoom_factor)
        self._update_display()

    def reset_zoom(self) -> None:
        """Reset zoom and pan"""
        self.zoom_factor = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self._update_display()

    def get_image_info(self) -> Optional[Dict]:
        """
        Get information about the current image

        Returns:
            Dictionary with image information or None if no image
        """
        if not self.original_image or not self.image_path:
            return None

        return {
            'path': self.image_path,
            'filename': Path(self.image_path).name,
            'width': self.original_image.width,
            'height': self.original_image.height,
            'mode': self.original_image.mode,
            'zoom_factor': self.zoom_factor,
            'pan_x': self.pan_x,
            'pan_y': self.pan_y
        }

    def set_zoom(self, zoom_factor: float) -> None:
        """
        Set zoom factor

        Args:
            zoom_factor: Zoom factor (0.1 to 5.0)
        """
        self.zoom_factor = max(0.1, min(5.0, zoom_factor))
        self._update_display()

    def center_image(self) -> None:
        """Center the image in the view"""
        if not self.original_image or not self.canvas:
            return

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        img_width = self.original_image.width * self.zoom_factor
        img_height = self.original_image.height * self.zoom_factor

        self.pan_x = (canvas_width - img_width) // 2
        self.pan_y = (canvas_height - img_height) // 2

        self._update_display()
