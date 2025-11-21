from __future__ import annotations

from typing import Callable

Point = tuple[int, int]
LineAlgorithm = Callable[[int, int, int, int], list[Point]]
CircleAlgorithm = Callable[[int, int, int], list[Point]]


def step_line_points(x1: int, y1: int, x2: int, y2: int) -> list[Point]:
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return [(x1, y1)]

    points: list[Point] = []
    if abs(dx) >= abs(dy):
        slope = dy / dx if dx != 0 else 0.0
        step = 1 if dx >= 0 else -1
        x = x1
        while True:
            raw_y = y1 + slope * (x - x1)
            point = (x, int(round(raw_y)))
            if not points or point != points[-1]:
                points.append(point)
            if x == x2:
                break
            x += step
    else:
        inv_slope = dx / dy if dy != 0 else 0.0
        step = 1 if dy >= 0 else -1
        y = y1
        while True:
            raw_x = x1 + inv_slope * (y - y1)
            point = (int(round(raw_x)), y)
            if not points or point != points[-1]:
                points.append(point)
            if y == y2:
                break
            y += step
    return points


def dda_line_points(x1: int, y1: int, x2: int, y2: int) -> list[Point]:
    dx = x2 - x1
    dy = y2 - y1
    steps = max(abs(dx), abs(dy))
    if steps == 0:
        return [(x1, y1)]

    points: list[Point] = []
    x = float(x1)
    y = float(y1)
    x_inc = dx / steps
    y_inc = dy / steps

    for _ in range(steps + 1):
        point = (int(round(x)), int(round(y)))
        if not points or point != points[-1]:
            points.append(point)
        x += x_inc
        y += y_inc

    return points


def bresenham_line_points(x1: int, y1: int, x2: int, y2: int) -> list[Point]:
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x2 >= x1 else -1
    sy = 1 if y2 >= y1 else -1

    x = x1
    y = y1
    points: list[Point] = [(x, y)]

    if dx >= dy:
        err = 2 * dy - dx
        for _ in range(dx):
            if err >= 0:
                y += sy
                err -= 2 * dx
            x += sx
            err += 2 * dy
            point = (x, y)
            if point != points[-1]:
                points.append(point)
    else:
        err = 2 * dx - dy
        for _ in range(dy):
            if err >= 0:
                x += sx
                err -= 2 * dy
            y += sy
            err += 2 * dx
            point = (x, y)
            if point != points[-1]:
                points.append(point)

    return points


def bresenham_circle_points(xc: int, yc: int, radius: int) -> list[Point]:
    if radius < 0:
        raise ValueError("Radius must be non-negative.")

    points: list[Point] = []
    seen: set[Point] = set()
    x = 0
    y = radius
    d = 3 - 2 * radius

    while y >= x:
        for px, py in _circle_symmetry_points(xc, yc, x, y):
            point = (px, py)
            if point not in seen:
                seen.add(point)
                points.append(point)
        x += 1
        if d > 0:
            y -= 1
            d += 4 * (x - y) + 10
        else:
            d += 4 * x + 6

    return points


def _circle_symmetry_points(xc: int, yc: int, x: int, y: int) -> list[Point]:
    return [
        (xc + x, yc + y),
        (xc - x, yc + y),
        (xc + x, yc - y),
        (xc - x, yc - y),
        (xc + y, yc + x),
        (xc - y, yc + x),
        (xc + y, yc - x),
        (xc - y, yc - x),
    ]


LINE_ALGORITHMS: dict[str, dict[str, object]] = {
    "step_line": {
        "label": "Step-by-step line",
        "color": "#7c3aed",
        "func": step_line_points,
    },
    "dda_line": {
        "label": "DDA line",
        "color": "#2563eb",
        "func": dda_line_points,
    },
    "bresenham_line": {
        "label": "Bresenham line",
        "color": "#059669",
        "func": bresenham_line_points,
    },
}

CIRCLE_ALGORITHMS: dict[str, dict[str, object]] = {
    "bresenham_circle": {
        "label": "Bresenham circle",
        "color": "#ea580c",
        "func": bresenham_circle_points,
    }
}
