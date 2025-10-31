from __future__ import annotations


RGB = tuple[int, int, int]
CMYK = tuple[float, float, float, float]
HSV = tuple[float, float, float]


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def rgb_to_cmyk(r: int, g: int, b: int) -> CMYK:
    r_norm = clamp(r, 0, 255) / 255.0
    g_norm = clamp(g, 0, 255) / 255.0
    b_norm = clamp(b, 0, 255) / 255.0

    k = 1.0 - max(r_norm, g_norm, b_norm)
    if k >= 0.999999:
        return 0.0, 0.0, 0.0, 100.0

    c = (1.0 - r_norm - k) / (1.0 - k)
    m = (1.0 - g_norm - k) / (1.0 - k)
    y = (1.0 - b_norm - k) / (1.0 - k)

    return tuple(round(component * 100.0, 2) for component in (c, m, y, k))


def cmyk_to_rgb(c: float, m: float, y: float, k: float) -> RGB:
    c_norm = clamp(c, 0.0, 100.0) / 100.0
    m_norm = clamp(m, 0.0, 100.0) / 100.0
    y_norm = clamp(y, 0.0, 100.0) / 100.0
    k_norm = clamp(k, 0.0, 100.0) / 100.0

    r = 255.0 * (1.0 - c_norm) * (1.0 - k_norm)
    g = 255.0 * (1.0 - m_norm) * (1.0 - k_norm)
    b = 255.0 * (1.0 - y_norm) * (1.0 - k_norm)

    return tuple(int(round(channel)) for channel in (r, g, b))


def rgb_to_hsv(r: int, g: int, b: int) -> HSV:
    r_norm = clamp(r, 0, 255) / 255.0
    g_norm = clamp(g, 0, 255) / 255.0
    b_norm = clamp(b, 0, 255) / 255.0

    max_val = max(r_norm, g_norm, b_norm)
    min_val = min(r_norm, g_norm, b_norm)
    delta = max_val - min_val

    # Hue calculation
    if delta == 0:
        hue = 0.0
    elif max_val == r_norm:
        hue = (60 * ((g_norm - b_norm) / delta) + 360) % 360
    elif max_val == g_norm:
        hue = (60 * ((b_norm - r_norm) / delta) + 120) % 360
    else:  # max_val == b_norm
        hue = (60 * ((r_norm - g_norm) / delta) + 240) % 360

    saturation = 0.0 if max_val == 0 else delta / max_val
    value = max_val

    return round(hue, 2), round(saturation * 100.0, 2), round(value * 100.0, 2)


def hsv_to_rgb(h: float, s: float, v: float) -> RGB:
    h_norm = clamp(h, 0.0, 360.0) % 360.0
    s_norm = clamp(s, 0.0, 100.0) / 100.0
    v_norm = clamp(v, 0.0, 100.0) / 100.0

    if s_norm == 0.0:
        value = int(round(v_norm * 255.0))
        return value, value, value

    h_sector = h_norm / 60.0
    sector_index = int(h_sector)
    fraction = h_sector - sector_index

    p = v_norm * (1.0 - s_norm)
    q = v_norm * (1.0 - s_norm * fraction)
    t = v_norm * (1.0 - s_norm * (1.0 - fraction))

    sector_map = {
        0: (v_norm, t, p),
        1: (q, v_norm, p),
        2: (p, v_norm, t),
        3: (p, q, v_norm),
        4: (t, p, v_norm),
    }

    r_norm, g_norm, b_norm = sector_map.get(sector_index % 6, (v_norm, p, q))

    return tuple(int(round(channel * 255.0)) for channel in (r_norm, g_norm, b_norm))


def cmyk_to_hsv(c: float, m: float, y: float, k: float) -> HSV:
    return rgb_to_hsv(*cmyk_to_rgb(c, m, y, k))


def hsv_to_cmyk(h: float, s: float, v: float) -> CMYK:
    return rgb_to_cmyk(*hsv_to_rgb(h, s, v))


def normalize_rgb(r: int, g: int, b: int) -> RGB:
    return tuple(int(clamp(component, 0, 255)) for component in (r, g, b))


def normalize_cmyk(c: float, m: float, y: float, k: float) -> CMYK:
    return tuple(round(clamp(component, 0.0, 100.0), 2) for component in (c, m, y, k))


def normalize_hsv(h: float, s: float, v: float) -> HSV:
    h_wrapped = clamp(h, 0.0, 360.0) % 360.0
    s_clamped = clamp(s, 0.0, 100.0)
    v_clamped = clamp(v, 0.0, 100.0)
    return round(h_wrapped, 2), round(s_clamped, 2), round(v_clamped, 2)
