from __future__ import annotations

from pathlib import Path
from typing import Sequence

from PIL import Image, ImageDraw, ImageFont

from .theme_system import ThemeColors


def _fmt_num(val) -> str:
    if val is None:
        return "--"
    try:
        f = float(val)
    except Exception:
        return str(val)
    if abs(f - int(f)) < 1e-6:
        return str(int(f))
    s = f"{f:.1f}"
    return s.rstrip("0").rstrip(".")


def _load_font(font_path: str | None, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if font_path:
        try:
            return ImageFont.truetype(font_path, size=size)
        except Exception:
            pass
    try:
        return ImageFont.truetype("arial.ttf", size=size)
    except Exception:
        return ImageFont.load_default()


def _text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=0)
    return (bbox[2] - bbox[0], bbox[3] - bbox[1])


def _draw_centered(draw: ImageDraw.ImageDraw, x_center: int, y: int, text: str, font, fill=(255, 255, 255)) -> int:
    w, h = _text_size(draw, text, font)
    draw.text((x_center - w // 2, y), text, font=font, fill=fill)
    return h


def _draw_centered_bold(draw: ImageDraw.ImageDraw, x_center: int, y: int, text: str, font, fill=(0, 0, 0)) -> int:
    w, h = _text_size(draw, text, font)
    x = x_center - w // 2
    draw.text((x, y), text, font=font, fill=fill)
    draw.text((x + 1, y), text, font=font, fill=fill)
    return h


def _shrink_to_fit(draw, text, font_path: str | None, max_width: int, start_size: int) -> ImageFont.ImageFont:
    size = start_size
    while size >= 14:
        font = _load_font(font_path, size)
        w, _ = _text_size(draw, text, font)
        if w <= max_width:
            return font
        size -= 2
    return _load_font(font_path, 14)


def _wrap_text_by_width(draw, text: str, font, max_width: int) -> list[str]:
    lines: list[str] = []
    buf = ""
    for ch in text:
        test = buf + ch
        w, _ = _text_size(draw, test, font)
        if w <= max_width:
            buf = test
        else:
            if buf:
                lines.append(buf)
            buf = ch
    if buf:
        lines.append(buf)
    return lines


def _wrap_fit_lines(draw, text: str, font_path: str | None, *, max_width: int, max_lines: int, start_size: int, min_size: int = 16):
    size = start_size
    chosen_font = _load_font(font_path, size)
    lines = _wrap_text_by_width(draw, text, chosen_font, max_width)
    while (len(lines) > max_lines or any(_text_size(draw, ln, chosen_font)[0] > max_width for ln in lines)) and size > min_size:
        size -= 2
        chosen_font = _load_font(font_path, size)
        lines = _wrap_text_by_width(draw, text, chosen_font, max_width)
    return chosen_font, lines


def _v_gradient(size: tuple[int, int], top_rgb: tuple[int, int, int], bottom_rgb: tuple[int, int, int]) -> Image.Image:
    w, h = size
    base = Image.new("RGB", (w, h), top_rgb)
    top = Image.new("RGB", (w, h), bottom_rgb)
    mask = Image.new("L", (w, h))
    md = ImageDraw.Draw(mask)
    for y in range(h):
        md.line([(0, y), (w, y)], fill=int(255 * y / (h - 1)))
    base.paste(top, (0, 0), mask)
    return base


def _rounded_rect(draw: ImageDraw.ImageDraw, box, radius: int, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def render_poster(
    *,
    output_path: Path,
    font_path: str | None,
    title: str,
    subtitle: str,
    tagline: str,
    items: Sequence[dict],
    size: tuple[int, int] = (1080, 1440),
    branding_label: str | None = None,
    grid_cols: int = 3,
    grid_rows: int = 3,
    location: str | None = None,
    hotline: str | None = None,
    subtitle_max_lines: int = 2,
    theme: ThemeColors | None = None,
) -> None:
    W, H = size

    # 使用主题配色或默认配色
    if theme is None:
        from .theme_system import THEMES
        theme = THEMES["默认蓝调"]

    # Background
    img = _v_gradient((W, H), theme.bg_top, theme.bg_bottom).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # Subtitle parsing and header height
    sep = "｜" if "｜" in subtitle else ("|" if "|" in subtitle else None)
    if sep:
        date_txt, cat_txt = [x.strip() for x in subtitle.split(sep, 1)]
    else:
        date_txt, cat_txt = "", subtitle

    cat_font_probe, cat_lines_probe = _wrap_fit_lines(draw, cat_txt, font_path, max_width=int(W * 0.88), max_lines=subtitle_max_lines, start_size=int(H * 0.036))
    header_ratio = 0.26 + max(0, len(cat_lines_probe) - 1) * 0.03
    header_h = int(H * min(0.34, header_ratio))
    header = _v_gradient((W, header_h), theme.header_top, theme.header_bottom)
    img.paste(header, (0, 0))

    # Title
    title_font = _shrink_to_fit(draw, title, font_path, int(W * 0.9), int(H * 0.070))
    t_h = _draw_centered(draw, W // 2, int(header_h * 0.20), title, title_font, fill=theme.title_color)

    # Date and category with extra spacing
    y = int(header_h * 0.20) + t_h + int(H * 0.020)  # 增加间隔
    if date_txt:
        date_font = _shrink_to_fit(draw, date_txt, font_path, int(W * 0.9), int(H * 0.031))
        _draw_centered(draw, W // 2, y, date_txt, date_font, fill=theme.subtitle_color)
        y += _text_size(draw, date_txt, date_font)[1] + int(H * 0.018)  # 增加间隔

    cat_font, cat_lines = _wrap_fit_lines(draw, cat_txt, font_path, max_width=int(W * 0.88), max_lines=subtitle_max_lines, start_size=int(H * 0.036))
    for ln in cat_lines:
        _draw_centered(draw, W // 2, y, ln, cat_font, fill=theme.subtitle_color)
        y += _text_size(draw, ln, cat_font)[1] + int(H * 0.008)  # 增加间隔

    # Container
    footer_h = int(H * 0.15)
    container_top = header_h - int(H * 0.03)
    container_margin = int(W * 0.05)
    container_bottom = H - footer_h - int(H * 0.02)
    cont_box = (container_margin, container_top, W - container_margin, container_bottom)
    _rounded_rect(draw, cont_box, radius=28, fill=(255, 255, 255), outline=theme.card_border, width=2)

    # Grid (3x3 by default)
    grid_padding_x = int(W * 0.05)
    grid_padding_y = int(H * 0.02)
    grid_left = container_margin + grid_padding_x
    grid_right = W - container_margin - grid_padding_x
    grid_top = container_top + grid_padding_y
    grid_bottom = container_bottom - grid_padding_y
    cell_w = (grid_right - grid_left) // max(1, grid_cols)
    cell_h = (grid_bottom - grid_top) // max(1, grid_rows)

    num_font_base = int(min(cell_h * 0.50, W * 0.066))
    meta_font = _load_font(font_path, int(min(cell_h * 0.18, W * 0.028)))
    wm_font = _load_font(font_path, int(min(cell_h * 0.16, W * 0.024)))

    for idx, item in enumerate(items[: grid_cols * grid_rows]):
        c = idx % grid_cols
        r = idx // grid_cols
        x1 = grid_left + c * cell_w + int(cell_w * 0.04)
        y1 = grid_top + r * cell_h + int(cell_h * 0.06)
        x2 = grid_left + (c + 1) * cell_w - int(cell_w * 0.04)
        y2 = grid_top + (r + 1) * cell_h - int(cell_h * 0.06)

        _rounded_rect(draw, (x1, y1, x2, y2), radius=18, fill=theme.card_fill, outline=theme.card_border, width=2)

        number = str(item.get("号码", "")).strip()
        deposit = item.get("预存")
        low = item.get("低消")

        cx = (x1 + x2) // 2
        cy = y1 + int((y2 - y1) * 0.14)
        max_w = (x2 - x1) - int(cell_w * 0.10)
        num_font = _shrink_to_fit(draw, number, font_path, max_w, num_font_base)
        n_w, n_h = _text_size(draw, number, num_font)
        draw.text((cx - n_w // 2, cy), number, font=num_font, fill=(28, 35, 52))

        dep_text = f"预存{_fmt_num(deposit)}"
        low_text = f"低消{_fmt_num(low)}"

        # 预存和低消分两行显示
        y_meta = cy + n_h + int((y2 - y1) * 0.08)
        _draw_centered_bold(draw, cx, y_meta, dep_text, meta_font, fill=(88, 96, 118))
        y_meta += _text_size(draw, dep_text, meta_font)[1] + int((y2 - y1) * 0.02)
        _draw_centered_bold(draw, cx, y_meta, low_text, meta_font, fill=(88, 96, 118))

        if branding_label:
            wm_w, wm_h = _text_size(draw, branding_label, wm_font)
            wx = cx - wm_w // 2
            wy = y2 - wm_h - int((y2 - y1) * 0.06)
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ld = ImageDraw.Draw(layer)
            ld.text((wx, wy), branding_label, font=wm_font, fill=(55, 120, 240, 72))
            img.paste(layer, (0, 0), layer)

    # Footer
    footer = _v_gradient((W, footer_h), theme.footer_top, theme.footer_bottom)
    img.paste(footer, (0, H - footer_h))

    info_line = None
    if location or hotline:
        parts = []
        if location:
            parts.append(f"归属地：{location}")
        if hotline:
            parts.append(f"选号热线：{hotline}")
        info_line = " | ".join(parts)

    info_font = _load_font(font_path, int(H * 0.026))
    tagline_font = _load_font(font_path, int(H * 0.038))
    y = H - footer_h + int(footer_h * 0.18)
    if info_line:
        iw, ih = _text_size(draw, info_line, info_font)
        draw.text((W // 2 - iw // 2, y), info_line, font=info_font, fill=theme.subtitle_color)
        y += ih + int(H * 0.006)
    for ln in _wrap_text_by_width(draw, tagline, tagline_font, int(W * 0.92))[:3]:
        tw, th = _text_size(draw, ln, tagline_font)
        draw.text((W // 2 - tw // 2, y), ln, font=tagline_font, fill=theme.tagline_color)
        y += th + int(H * 0.008)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(str(output_path), format="JPEG", quality=92, subsampling=0)

