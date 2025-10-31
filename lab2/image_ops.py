from __future__ import annotations

import math
from typing import List, Sequence, Tuple

import tkinter as tk

RGBPixel = Tuple[int, int, int]
RGBImage = List[List[RGBPixel]]
GrayImage = List[List[int]]


def _parse_pixel(pixel: object) -> RGBPixel:
    if isinstance(pixel, tuple) and len(pixel) == 3:
        r, g, b = pixel
        return int(r), int(g), int(b)

    text = str(pixel).strip()
    if text.startswith("#") and len(text) == 7:
        return tuple(int(text[i : i + 2], 16) for i in (1, 3, 5))  # type: ignore[arg-type]

    if text.startswith("rgb"):
        components = text[text.find("(") + 1 : text.find(")")]  # rgb(r,g,b)
        parts = [part.strip() for part in components.split(",")]
        return tuple(int(part) for part in parts[:3])  # type: ignore[arg-type]

    raise ValueError(f"Unsupported pixel format: {pixel!r}")


def clamp(value: float, lower: int = 0, upper: int = 255) -> int:
    return int(max(lower, min(upper, round(value))))


def photoimage_to_rgb(image: tk.PhotoImage) -> RGBImage:
    width = image.width()
    height = image.height()
    data: RGBImage = []
    for y in range(height):
        row: List[RGBPixel] = []
        for x in range(width):
            row.append(_parse_pixel(image.get(x, y)))
        data.append(row)
    return data


def rgb_to_photoimage(data: RGBImage) -> tk.PhotoImage:
    height = len(data)
    width = len(data[0]) if height else 0
    photo = tk.PhotoImage(width=width, height=height)
    for y, row in enumerate(data):
        buffer = "{" + " ".join(f"#{r:02x}{g:02x}{b:02x}" for r, g, b in row) + "}"
        photo.put(buffer, to=(0, y))
    return photo


def rgb_to_grayscale(data: RGBImage) -> GrayImage:
    grayscale: GrayImage = []
    for row in data:
        gray_row = [clamp(0.299 * r + 0.587 * g + 0.114 * b) for r, g, b in row]
        grayscale.append(gray_row)
    return grayscale


def grayscale_to_rgb(data: GrayImage) -> RGBImage:
    return [[(value, value, value) for value in row] for row in data]


def compute_histogram(data: GrayImage) -> List[int]:
    histogram = [0] * 256
    for row in data:
        for value in row:
            histogram[value] += 1
    return histogram


def otsu_threshold(histogram: Sequence[int]) -> int:
    total = sum(histogram)
    if total == 0:
        return 0

    sum_total = sum(index * count for index, count in enumerate(histogram))
    sum_background = 0.0
    weight_background = 0.0
    max_variance = -1.0
    threshold = 0

    for index, count in enumerate(histogram):
        weight_background += count
        if weight_background == 0:
            continue

        weight_foreground = total - weight_background
        if weight_foreground == 0:
            break

        sum_background += index * count

        mean_background = sum_background / weight_background
        mean_foreground = (sum_total - sum_background) / weight_foreground

        between_variance = (
            weight_background
            * weight_foreground
            * (mean_background - mean_foreground) ** 2
        )

        if between_variance > max_variance:
            max_variance = between_variance
            threshold = index

    return threshold


def triangle_threshold(histogram: Sequence[int]) -> int:
    non_zero_indices = [index for index, count in enumerate(histogram) if count > 0]
    if not non_zero_indices:
        return 0

    first = non_zero_indices[0]
    last = non_zero_indices[-1]
    if first == last:
        return first

    peak = max(range(first, last + 1), key=lambda idx: histogram[idx])

    if (last - peak) >= (peak - first):
        start = peak
        end = last
        step = 1
    else:
        start = peak
        end = first
        step = -1

    vec_x = end - start
    vec_y = histogram[end] - histogram[start]
    length = math.hypot(vec_x, vec_y)
    if length == 0:
        return start

    max_distance = -1.0
    threshold = start

    current = start
    while True:
        rel_x = current - start
        rel_y = histogram[current] - histogram[start]
        distance = abs(vec_x * rel_y - vec_y * rel_x) / length
        if distance > max_distance:
            max_distance = distance
            threshold = current

        if current == end:
            break

        current += step

    return threshold


def apply_threshold(data: GrayImage, threshold: int) -> GrayImage:
    return [[0 if value <= threshold else 255 for value in row] for row in data]


LAPLACIAN_KERNEL: Tuple[Tuple[int, int, int], ...] = (
    (0, -1, 0),
    (-1, 4, -1),
    (0, -1, 0),
)


def laplacian_sharpen(data: RGBImage, amount: float = 1.0) -> RGBImage:
    height = len(data)
    width = len(data[0]) if height else 0
    result: RGBImage = []

    for y in range(height):
        row: List[RGBPixel] = []
        for x in range(width):
            laplacian = [0.0, 0.0, 0.0]
            for ky, kernel_row in enumerate(LAPLACIAN_KERNEL):
                for kx, weight in enumerate(kernel_row):
                    if weight == 0:
                        continue
                    yy = min(max(y + ky - 1, 0), height - 1)
                    xx = min(max(x + kx - 1, 0), width - 1)
                    pr, pg, pb = data[yy][xx]
                    laplacian[0] += weight * pr
                    laplacian[1] += weight * pg
                    laplacian[2] += weight * pb

            original = data[y][x]
            sharpened = tuple(
                clamp(original[channel] + amount * laplacian[channel])
                for channel in range(3)
            )
            row.append(sharpened)
        result.append(row)

    return result


def threshold_photoimage(
    image: tk.PhotoImage, method: str
) -> Tuple[int, tk.PhotoImage]:
    rgb_data = photoimage_to_rgb(image)
    grayscale = rgb_to_grayscale(rgb_data)
    histogram = compute_histogram(grayscale)

    if method.lower() == "otsu":
        threshold = otsu_threshold(histogram)
    elif method.lower() == "triangle":
        threshold = triangle_threshold(histogram)
    else:
        raise ValueError("Unsupported thresholding method")

    binary = apply_threshold(grayscale, threshold)
    photo = rgb_to_photoimage(grayscale_to_rgb(binary))
    return threshold, photo


def sharpen_photoimage(image: tk.PhotoImage, amount: float = 1.0) -> tk.PhotoImage:
    rgb_data = photoimage_to_rgb(image)
    sharpened = laplacian_sharpen(rgb_data, amount=amount)
    return rgb_to_photoimage(sharpened)
