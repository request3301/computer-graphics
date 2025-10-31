from __future__ import annotations

from typing import Dict, Iterable

import tkinter as tk
from tkinter import colorchooser, ttk

from color_models import (
    cmyk_to_rgb,
    hsv_to_rgb,
    normalize_cmyk,
    normalize_hsv,
    normalize_rgb,
    rgb_to_cmyk,
    rgb_to_hsv,
)


def rgb_to_hex(rgb: Iterable[int]) -> str:
    r, g, b = normalize_rgb(*rgb)
    return f"#{r:02X}{g:02X}{b:02X}"


def clamp_value(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    text = (hex_color or "").strip().lstrip("#")
    if len(text) != 6:
        raise ValueError("Expected hex color in format RRGGBB")
    return tuple(int(text[i : i + 2], 16) for i in (0, 2, 4))


class ColorModelsApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Color Models")
        self.root.resizable(False, False)

        self.initial_rgb = (255, 0, 0)
        self.current_rgb = normalize_rgb(*self.initial_rgb)
        self.current_hsv = rgb_to_hsv(*self.current_rgb)
        self.current_cmyk = rgb_to_cmyk(*self.current_rgb)
        self.updating = False

        self.component_configs: Dict[str, Dict[str, Dict[str, float]]] = {
            "RGB": {
                "R": {
                    "min": 0.0,
                    "max": 255.0,
                    "value": float(self.current_rgb[0]),
                    "resolution": 1.0,
                },
                "G": {
                    "min": 0.0,
                    "max": 255.0,
                    "value": float(self.current_rgb[1]),
                    "resolution": 1.0,
                },
                "B": {
                    "min": 0.0,
                    "max": 255.0,
                    "value": float(self.current_rgb[2]),
                    "resolution": 1.0,
                },
            },
            "HSV": {
                "H": {
                    "min": 0.0,
                    "max": 360.0,
                    "value": float(self.current_hsv[0]),
                    "resolution": 1.0,
                },
                "S": {
                    "min": 0.0,
                    "max": 100.0,
                    "value": float(self.current_hsv[1]),
                    "resolution": 0.1,
                },
                "V": {
                    "min": 0.0,
                    "max": 100.0,
                    "value": float(self.current_hsv[2]),
                    "resolution": 0.1,
                },
            },
            "CMYK": {
                "C": {
                    "min": 0.0,
                    "max": 100.0,
                    "value": float(self.current_cmyk[0]),
                    "resolution": 0.1,
                },
                "M": {
                    "min": 0.0,
                    "max": 100.0,
                    "value": float(self.current_cmyk[1]),
                    "resolution": 0.1,
                },
                "Y": {
                    "min": 0.0,
                    "max": 100.0,
                    "value": float(self.current_cmyk[2]),
                    "resolution": 0.1,
                },
                "K": {
                    "min": 0.0,
                    "max": 100.0,
                    "value": float(self.current_cmyk[3]),
                    "resolution": 0.1,
                },
            },
        }

        self.entries: Dict[str, Dict[str, tk.StringVar]] = {
            prefix: {} for prefix in self.component_configs
        }
        self.scales: Dict[str, Dict[str, tk.Scale]] = {
            prefix: {} for prefix in self.component_configs
        }

        self.hex_var = tk.StringVar(value=rgb_to_hex(self.current_rgb))

        self._build_layout()
        self.update_from_rgb(self.current_rgb)

    def _build_layout(self) -> None:
        mainframe = ttk.Frame(self.root, padding=16)
        mainframe.grid(row=0, column=0, sticky="nsew")
        mainframe.columnconfigure(0, weight=1)

        preview_frame = ttk.LabelFrame(mainframe, text="Preview", padding=12)
        preview_frame.grid(row=0, column=0, sticky="ew")
        preview_frame.columnconfigure(0, weight=1)

        self.preview_label = tk.Label(
            preview_frame,
            text=" ",
            width=30,
            height=2,
            relief="sunken",
            background=rgb_to_hex(self.current_rgb),
        )
        self.preview_label.grid(row=0, column=0, columnspan=2, sticky="ew")

        ttk.Label(preview_frame, text="Hex:").grid(
            row=1, column=0, sticky="w", pady=(8, 0)
        )
        ttk.Label(preview_frame, textvariable=self.hex_var).grid(
            row=1, column=1, sticky="e", pady=(8, 0)
        )

        palette_button = ttk.Button(
            preview_frame, text="Palette…", command=self.pick_color
        )
        palette_button.grid(row=2, column=0, columnspan=2, pady=(8, 0))

        row_index = 1
        for prefix in ("RGB", "HSV", "CMYK"):
            frame = ttk.LabelFrame(mainframe, text=prefix, padding=12)
            frame.grid(
                row=row_index,
                column=0,
                sticky="ew",
                pady=(12 if row_index > 1 else 16, 0),
            )
            frame.columnconfigure(2, weight=1)

            for row, (component, config) in enumerate(
                self.component_configs[prefix].items()
            ):
                self._add_component_row(frame, prefix, component, row, config)

            row_index += 1

        button_frame = ttk.Frame(mainframe)
        button_frame.grid(row=row_index, column=0, sticky="ew", pady=(16, 0))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        reset_button = ttk.Button(button_frame, text="Reset", command=self.reset)
        reset_button.grid(row=0, column=0, sticky="w")

        exit_button = ttk.Button(button_frame, text="Exit", command=self.root.destroy)
        exit_button.grid(row=0, column=1, sticky="e")

    def _add_component_row(
        self,
        frame: ttk.LabelFrame,
        prefix: str,
        component: str,
        row: int,
        config: Dict[str, float],
    ) -> None:
        ttk.Label(frame, text=component, width=4).grid(
            row=row, column=0, sticky="w", padx=(0, 8)
        )

        entry_var = tk.StringVar(value=self._format_value(prefix, config["value"]))
        entry = ttk.Entry(frame, width=8, textvariable=entry_var, justify="right")
        entry.grid(row=row, column=1, sticky="w", padx=(0, 8))
        entry.bind(
            "<FocusOut>",
            lambda _event, p=prefix, c=component: self.on_entry_commit(p, c),
        )
        entry.bind(
            "<Return>", lambda _event, p=prefix, c=component: self.on_entry_commit(p, c)
        )
        entry.bind(
            "<KP_Enter>",
            lambda _event, p=prefix, c=component: self.on_entry_commit(p, c),
        )

        scale = tk.Scale(
            frame,
            from_=config["min"],
            to=config["max"],
            orient="horizontal",
            resolution=config.get("resolution", 1.0),
            command=lambda value, p=prefix, c=component: self.on_scale_change(
                p, c, float(value)
            ),
            showvalue=False,
            length=280,
        )
        scale.set(config["value"])
        scale.grid(row=row, column=2, sticky="ew")

        self.entries[prefix][component] = entry_var
        self.scales[prefix][component] = scale

    def on_scale_change(self, prefix: str, component: str, raw_value: float) -> None:
        if self.updating:
            return

        if prefix == "RGB":
            value = int(round(raw_value))
            self.entries[prefix][component].set(str(value))
            rgb_list = list(self.current_rgb)
            rgb_list["RGB".index(component)] = value
            self.update_from_rgb(tuple(rgb_list))
        elif prefix == "HSV":
            value = raw_value
            self.entries[prefix][component].set(f"{value:.2f}")
            hsv_list = list(self.current_hsv)
            index = "HSV".index(component)
            hsv_list[index] = value
            new_hsv = normalize_hsv(*hsv_list)
            self.update_from_rgb(hsv_to_rgb(*new_hsv))
        elif prefix == "CMYK":
            value = raw_value
            self.entries[prefix][component].set(f"{value:.2f}")
            cmyk_list = list(self.current_cmyk)
            index = "CMYK".index(component)
            cmyk_list[index] = value
            new_cmyk = normalize_cmyk(*cmyk_list)
            self.update_from_rgb(cmyk_to_rgb(*new_cmyk))

    def on_entry_commit(self, prefix: str, component: str) -> None:
        if self.updating:
            return

        text = self.entries[prefix][component].get().strip()
        if not text:
            self._refresh_entry(prefix, component)
            return

        try:
            value = float(text)
        except ValueError:
            self._refresh_entry(prefix, component)
            return

        config = self.component_configs[prefix][component]

        if prefix == "RGB":
            value = clamp_value(value, config["min"], config["max"])
            value = int(round(value))
            self.entries[prefix][component].set(str(value))
            self.scales[prefix][component].set(value)
            rgb_list = list(self.current_rgb)
            rgb_list["RGB".index(component)] = value
            self.update_from_rgb(tuple(rgb_list))
        elif prefix == "HSV":
            value = clamp_value(value, config["min"], config["max"])
            hsv_list = list(self.current_hsv)
            index = "HSV".index(component)
            hsv_list[index] = value
            new_hsv = normalize_hsv(*hsv_list)
            self.scales[prefix][component].set(new_hsv[index])
            self.entries[prefix][component].set(f"{new_hsv[index]:.2f}")
            self.update_from_rgb(hsv_to_rgb(*new_hsv))
        elif prefix == "CMYK":
            value = clamp_value(value, config["min"], config["max"])
            cmyk_list = list(self.current_cmyk)
            index = "CMYK".index(component)
            cmyk_list[index] = value
            new_cmyk = normalize_cmyk(*cmyk_list)
            self.scales[prefix][component].set(new_cmyk[index])
            self.entries[prefix][component].set(f"{new_cmyk[index]:.2f}")
            self.update_from_rgb(cmyk_to_rgb(*new_cmyk))

    def pick_color(self) -> None:
        result = colorchooser.askcolor(initialcolor=rgb_to_hex(self.current_rgb))
        if not result or not result[1]:
            return
        try:
            self.update_from_rgb(hex_to_rgb(result[1]))
        except ValueError:
            self._refresh_all()

    def reset(self) -> None:
        self.update_from_rgb(self.initial_rgb)

    def update_from_rgb(self, rgb: Iterable[int]) -> None:
        self.updating = True

        self.current_rgb = normalize_rgb(*rgb)
        self.current_hsv = rgb_to_hsv(*self.current_rgb)
        self.current_cmyk = rgb_to_cmyk(*self.current_rgb)

        for index, component in enumerate("RGB"):
            value = self.current_rgb[index]
            self.scales["RGB"][component].set(value)
            self.entries["RGB"][component].set(str(value))

        for index, component in enumerate("HSV"):
            value = self.current_hsv[index]
            self.scales["HSV"][component].set(value)
            self.entries["HSV"][component].set(f"{value:.2f}")

        for index, component in enumerate("CMYK"):
            value = self.current_cmyk[index]
            self.scales["CMYK"][component].set(value)
            self.entries["CMYK"][component].set(f"{value:.2f}")

        color_hex = rgb_to_hex(self.current_rgb)
        self.preview_label.configure(background=color_hex)
        self.hex_var.set(color_hex)

        self.updating = False

    def _refresh_entry(self, prefix: str, component: str) -> None:
        if prefix == "RGB":
            index = "RGB".index(component)
            self.entries[prefix][component].set(str(self.current_rgb[index]))
        elif prefix == "HSV":
            index = "HSV".index(component)
            self.entries[prefix][component].set(f"{self.current_hsv[index]:.2f}")
        elif prefix == "CMYK":
            index = "CMYK".index(component)
            self.entries[prefix][component].set(f"{self.current_cmyk[index]:.2f}")

    def _refresh_all(self) -> None:
        for prefix in ("RGB", "HSV", "CMYK"):
            for component in self.entries[prefix]:
                self._refresh_entry(prefix, component)

    @staticmethod
    def _format_value(prefix: str, value: float) -> str:
        if prefix == "RGB":
            return str(int(round(value)))
        return f"{value:.2f}"


def main() -> None:
    root = tk.Tk()
    ColorModelsApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
