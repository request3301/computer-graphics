from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

try:
    from .algorithms import (
        CIRCLE_ALGORITHMS,
        LINE_ALGORITHMS,
        CircleAlgorithm,
        LineAlgorithm,
        Point,
    )
except ImportError:  # pragma: no cover - allows running as script
    from algorithms import (
        CIRCLE_ALGORITHMS,
        LINE_ALGORITHMS,
        CircleAlgorithm,
        LineAlgorithm,
        Point,
    )


class RasterApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Lab 3 — Raster (scan conversion) algorithms")

        self.scale_var = tk.IntVar(value=20)
        self.status_var = tk.StringVar(
            value="Ready. Provide line or circle parameters."
        )

        self.line_vars = {
            "x1": tk.StringVar(value="-8"),
            "y1": tk.StringVar(value="-4"),
            "x2": tk.StringVar(value="9"),
            "y2": tk.StringVar(value="5"),
        }
        self.circle_vars = {
            "xc": tk.StringVar(value="2"),
            "yc": tk.StringVar(value="-1"),
            "r": tk.StringVar(value="6"),
        }

        self.algorithm_flags: dict[str, tk.BooleanVar] = {}
        for key in LINE_ALGORITHMS:
            self.algorithm_flags[key] = tk.BooleanVar(value=True)
        for key in CIRCLE_ALGORITHMS:
            self.algorithm_flags[key] = tk.BooleanVar(value=True)

        self.current_line: tuple[int, int, int, int] | None = None
        self.current_circle: tuple[int, int, int] | None = None

        self.canvas: tk.Canvas

        self._build_ui()
        self.render_scene()

    def _build_ui(self) -> None:
        mainframe = ttk.Frame(self.root, padding=12)
        mainframe.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        mainframe.columnconfigure(1, weight=1)
        mainframe.rowconfigure(0, weight=1)

        controls = ttk.Frame(mainframe)
        controls.grid(row=0, column=0, sticky="nsw", padx=(0, 16))
        controls.columnconfigure(0, weight=1)

        self._build_line_inputs(controls)
        self._build_circle_inputs(controls)
        self._build_options_panel(controls)

        status_label = ttk.Label(
            controls, textvariable=self.status_var, wraplength=220, anchor="w"
        )
        status_label.grid(row=4, column=0, sticky="ew", pady=(8, 0))

        display = ttk.Frame(mainframe)
        display.grid(row=0, column=1, sticky="nsew")
        display.columnconfigure(0, weight=1)
        display.rowconfigure(0, weight=1)

        canvas_frame = ttk.LabelFrame(display, text="Raster playground", padding=8)
        canvas_frame.grid(row=0, column=0, sticky="nsew")
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            canvas_frame,
            width=820,
            height=580,
            background="#ffffff",
            highlightthickness=0,
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind("<Configure>", lambda _event: self.render_scene())

    def _build_line_inputs(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Line parameters", padding=12)
        frame.grid(row=0, column=0, sticky="ew")
        for idx, coord in enumerate(("x1", "y1", "x2", "y2")):
            ttk.Label(frame, text=f"{coord}:", width=3).grid(
                row=idx // 2,
                column=(idx % 2) * 2,
                sticky="w",
                padx=(0, 4),
                pady=2,
            )
            entry = ttk.Entry(frame, width=6, textvariable=self.line_vars[coord])
            entry.grid(row=idx // 2, column=(idx % 2) * 2 + 1, pady=2, sticky="w")

        ttk.Button(frame, text="Draw line", command=self.draw_line).grid(
            row=2, column=0, columnspan=4, pady=(8, 0), sticky="ew"
        )

    def _build_circle_inputs(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Circle parameters", padding=12)
        frame.grid(row=1, column=0, sticky="ew", pady=(12, 0))
        labels = ("xc", "yc", "r")
        for idx, coord in enumerate(labels):
            ttk.Label(frame, text=f"{coord}:").grid(
                row=0, column=idx * 2, sticky="w", padx=(0, 4)
            )
            entry = ttk.Entry(frame, width=6, textvariable=self.circle_vars[coord])
            entry.grid(row=0, column=idx * 2 + 1, sticky="w")

        ttk.Button(frame, text="Draw circle", command=self.draw_circle).grid(
            row=1, column=0, columnspan=6, pady=(8, 0), sticky="ew"
        )

    def _build_options_panel(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Display options", padding=12)
        frame.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Algorithms:").grid(
            row=0, column=0, columnspan=2, sticky="w"
        )

        row_index = 1
        for key in LINE_ALGORITHMS:
            meta = LINE_ALGORITHMS[key]
            color_box = tk.Label(frame, background=meta["color"], width=2)
            color_box.grid(row=row_index, column=0, sticky="w", padx=(0, 6))
            ttk.Checkbutton(
                frame,
                text=meta["label"],
                variable=self.algorithm_flags[key],
                command=self.render_scene,
            ).grid(row=row_index, column=1, sticky="w")
            row_index += 1

        for key in CIRCLE_ALGORITHMS:
            meta = CIRCLE_ALGORITHMS[key]
            color_box = tk.Label(frame, background=meta["color"], width=2)
            color_box.grid(row=row_index, column=0, sticky="w", padx=(0, 6))
            ttk.Checkbutton(
                frame,
                text=meta["label"],
                variable=self.algorithm_flags[key],
                command=self.render_scene,
            ).grid(row=row_index, column=1, sticky="w")
            row_index += 1

        ttk.Label(frame, text="Scale (pixels per unit):").grid(
            row=row_index, column=0, columnspan=2, sticky="w", pady=(8, 0)
        )
        row_index += 1
        scale_slider = tk.Scale(
            frame,
            from_=8,
            to=40,
            orient="horizontal",
            resolution=1,
            variable=self.scale_var,
            command=lambda _value: self.render_scene(),
        )
        scale_slider.grid(row=row_index, column=0, columnspan=2, sticky="ew")
        row_index += 1

        ttk.Button(frame, text="Clear drawing", command=self.clear_scene).grid(
            row=row_index, column=0, columnspan=2, pady=(8, 0), sticky="ew"
        )
        row_index += 1

        mapping_text = (
            "Origin at canvas center. Each integer (x, y) is placed at the "
            "center of a raster cell of the selected scale."
        )
        ttk.Label(frame, text=mapping_text, wraplength=220, justify="left").grid(
            row=row_index, column=0, columnspan=2, sticky="w", pady=(8, 0)
        )

    def draw_line(self) -> None:
        try:
            x1 = int(self.line_vars["x1"].get())
            y1 = int(self.line_vars["y1"].get())
            x2 = int(self.line_vars["x2"].get())
            y2 = int(self.line_vars["y2"].get())
        except ValueError:
            messagebox.showerror("Invalid input", "Line coordinates must be integers.")
            return

        self.current_line = (x1, y1, x2, y2)
        self.status_var.set(f"Line set from ({x1}, {y1}) to ({x2}, {y2}).")
        self.render_scene()

    def draw_circle(self) -> None:
        try:
            xc = int(self.circle_vars["xc"].get())
            yc = int(self.circle_vars["yc"].get())
            radius = int(self.circle_vars["r"].get())
        except ValueError:
            messagebox.showerror(
                "Invalid input", "Circle parameters must be integers (radius ≥ 0)."
            )
            return

        if radius < 0:
            messagebox.showerror("Invalid radius", "Radius must be non-negative.")
            return

        self.current_circle = (xc, yc, radius)
        self.status_var.set(f"Circle set at ({xc}, {yc}) with radius {radius}.")
        self.render_scene()

    def clear_scene(self) -> None:
        self.current_line = None
        self.current_circle = None
        self.status_var.set("Drawing cleared.")
        self.render_scene()

    def render_scene(self) -> None:
        self.canvas.delete("all")
        self.canvas.update_idletasks()

        width = max(int(self.canvas.winfo_width()), 200)
        height = max(int(self.canvas.winfo_height()), 200)
        origin_x = round(width / 2) + 0.5
        origin_y = round(height / 2) + 0.5

        scale = max(self.scale_var.get(), 1)

        self._draw_grid(width, height, origin_x, origin_y, scale)
        self._draw_axes(width, height, origin_x, origin_y)

        if self.current_line:
            for key, meta in LINE_ALGORITHMS.items():
                if not self.algorithm_flags[key].get():
                    continue
                func: LineAlgorithm = meta["func"]  # type: ignore[assignment]
                points = func(*self.current_line)
                self._draw_points(points, origin_x, origin_y, scale, meta["color"])

        if self.current_circle:
            for key, meta in CIRCLE_ALGORITHMS.items():
                if not self.algorithm_flags[key].get():
                    continue
                func: CircleAlgorithm = meta["func"]  # type: ignore[assignment]
                points = func(*self.current_circle)
                self._draw_points(points, origin_x, origin_y, scale, meta["color"])

        self.canvas.create_text(
            8,
            height - 8,
            anchor="sw",
            text=f"Scale: 1 unit = {scale} px",
            fill="#4b5563",
            font=("Helvetica", 10),
        )

    def _draw_grid(
        self, width: int, height: int, origin_x: float, origin_y: float, scale: int
    ) -> None:
        max_x = int(width / (2 * scale)) + 2
        max_y = int(height / (2 * scale)) + 2
        grid_color = "#e5e7eb"

        for step in range(-max_x, max_x + 1):
            x = origin_x + step * scale
            self.canvas.create_line(x, 0, x, height, fill=grid_color)

        for step in range(-max_y, max_y + 1):
            y = origin_y + step * scale
            self.canvas.create_line(0, y, width, y, fill=grid_color)

        label_color = "#9ca3af"
        for step in range(-max_x, max_x + 1):
            if step == 0:
                continue
            x = origin_x + step * scale
            self.canvas.create_text(
                x,
                origin_y + 4,
                text=str(step),
                fill=label_color,
                font=("Helvetica", 9),
                anchor="n",
            )

        for step in range(-max_y, max_y + 1):
            if step == 0:
                continue
            y = origin_y - step * scale
            self.canvas.create_text(
                origin_x + 4,
                y,
                text=str(step),
                fill=label_color,
                font=("Helvetica", 9),
                anchor="w",
            )

    def _draw_axes(
        self, width: int, height: int, origin_x: float, origin_y: float
    ) -> None:
        axis_color = "#6b7280"
        self.canvas.create_line(0, origin_y, width, origin_y, fill=axis_color, width=2)
        self.canvas.create_line(origin_x, 0, origin_x, height, fill=axis_color, width=2)
        self.canvas.create_text(
            width - 8, origin_y - 12, text="x", fill=axis_color, font=("Helvetica", 11)
        )
        self.canvas.create_text(
            origin_x + 12, 12, text="y", fill=axis_color, font=("Helvetica", 11)
        )

    def _draw_points(
        self,
        points: list[Point],
        origin_x: float,
        origin_y: float,
        scale: int,
        color: str,
    ) -> None:
        for x, y in points:
            left = origin_x + x * scale
            right = origin_x + (x + 1) * scale
            top = origin_y - y * scale
            bottom = origin_y - (y + 1) * scale
            self.canvas.create_rectangle(
                left,
                top,
                right,
                bottom,
                fill=color,
                outline="",
            )


def main() -> None:
    root = tk.Tk()
    RasterApp(root)
    root.minsize(1024, 720)
    root.mainloop()


if __name__ == "__main__":
    main()
