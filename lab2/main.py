from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import image_ops


class ImageProcessingApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Lab 2 — Global Thresholding & Sharpening")

        self.original_image: tk.PhotoImage | None = None
        self.processed_image: tk.PhotoImage | None = None

        self.threshold_var = tk.StringVar(value="—")
        self.status_var = tk.StringVar(value="Load an image to begin.")

        self._placeholder_image = self._create_placeholder_image(320, 240)

        self._build_layout()

    def _build_layout(self) -> None:
        mainframe = ttk.Frame(self.root, padding=16)
        mainframe.grid(row=0, column=0, sticky="nsew")
        mainframe.columnconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        previews = ttk.Frame(mainframe)
        previews.grid(row=0, column=0, columnspan=3, sticky="nsew")
        previews.columnconfigure(0, weight=1)
        previews.columnconfigure(1, weight=1)
        previews.rowconfigure(0, weight=1)

        self.original_label = ttk.LabelFrame(previews, text="Original", padding=12)
        self.original_label.grid(row=0, column=0, padx=(0, 12), sticky="nsew")

        self.original_preview = tk.Label(
            self.original_label,
            relief="sunken",
            background="#f0f0f0",
        )
        self.original_preview.pack(fill="both", expand=True)
        self._show_image(self._placeholder_image, self.original_preview)

        self.result_label = ttk.LabelFrame(previews, text="Processed", padding=12)
        self.result_label.grid(row=0, column=1, sticky="nsew")

        self.processed_preview = tk.Label(
            self.result_label,
            relief="sunken",
            background="#f0f0f0",
        )
        self.processed_preview.pack(fill="both", expand=True)
        self._show_image(self._placeholder_image, self.processed_preview)

        button_frame = ttk.Frame(mainframe, padding=(0, 16, 0, 0))
        button_frame.grid(row=1, column=0, sticky="ew")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        button_frame.columnconfigure(3, weight=1)

        ttk.Button(button_frame, text="Load Image…", command=self.load_image).grid(
            row=0, column=0, padx=4, ipady=4, sticky="ew"
        )
        ttk.Button(
            button_frame,
            text="Otsu Threshold",
            command=lambda: self.apply_threshold("otsu"),
        ).grid(row=0, column=1, padx=4, ipady=4, sticky="ew")
        ttk.Button(
            button_frame,
            text="Triangle Threshold",
            command=lambda: self.apply_threshold("triangle"),
        ).grid(row=0, column=2, padx=4, ipady=4, sticky="ew")
        ttk.Button(button_frame, text="Sharpen", command=self.sharpen).grid(
            row=0, column=3, padx=4, ipady=4, sticky="ew"
        )

        info_frame = ttk.Frame(mainframe, padding=(0, 12, 0, 0))
        info_frame.grid(row=2, column=0, sticky="ew")
        info_frame.columnconfigure(1, weight=1)

        ttk.Label(info_frame, text="Threshold:").grid(row=0, column=0, sticky="w")
        ttk.Label(info_frame, textvariable=self.threshold_var).grid(
            row=0, column=1, sticky="w"
        )

        status_bar = ttk.Label(mainframe, textvariable=self.status_var, anchor="w")
        status_bar.grid(row=3, column=0, sticky="ew")

    def load_image(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=(
                ("Supported", "*.png *.gif *.ppm *.pgm"),
                ("PNG", "*.png"),
                ("GIF", "*.gif"),
                ("PPM/PGM", "*.ppm *.pgm"),
                ("All files", "*.*"),
            ),
        )

        if not file_path:
            return

        try:
            image = tk.PhotoImage(file=file_path)
        except tk.TclError as exc:
            messagebox.showerror("Load failed", f"Could not open image:\n{exc}")
            return

        self.original_image = image
        self.processed_image = None

        self._show_image(image, self.original_preview)
        self._clear_processed()

        self.threshold_var.set("—")
        self.status_var.set(f"Loaded: {file_path}")

    def apply_threshold(self, method: str) -> None:
        if not self.original_image:
            messagebox.showinfo(
                "No image", "Load an image before applying thresholding."
            )
            return

        try:
            threshold, result = image_ops.threshold_photoimage(
                self.original_image, method
            )
        except ValueError as exc:
            messagebox.showerror("Thresholding error", str(exc))
            return

        self.processed_image = result
        self._show_image(result, self.processed_preview)
        method_name = "Otsu" if method.lower() == "otsu" else "Triangle"
        self.threshold_var.set(f"{method_name}: {threshold}")
        self.status_var.set(f"Applied {method_name} threshold.")

    def sharpen(self) -> None:
        if not self.original_image:
            messagebox.showinfo("No image", "Load an image before sharpening.")
            return

        result = image_ops.sharpen_photoimage(self.original_image)
        self.processed_image = result
        self._show_image(result, self.processed_preview)
        self.threshold_var.set("—")
        self.status_var.set("Applied Laplacian sharpening.")

    def _show_image(self, image: tk.PhotoImage, display: tk.Label) -> None:
        display.configure(image=image)
        display.image = image

    def _clear_processed(self) -> None:
        self.processed_image = None
        self._show_image(self._placeholder_image, self.processed_preview)
        self.processed_preview.configure(background="#f0f0f0")

    def _create_placeholder_image(self, width: int, height: int) -> tk.PhotoImage:
        image = tk.PhotoImage(width=width, height=height)
        image.put("#d9d9d9", to=(0, 0, width, height))
        return image


def main() -> None:
    root = tk.Tk()
    ImageProcessingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
