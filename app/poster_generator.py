from __future__ import annotations

from pathlib import Path
from typing import Sequence

from PIL import Image, ImageDraw, ImageFont


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


def _draw_centered(draw: ImageDraw.ImageDraw, x_center: int, y: int, text: str, font, fill=(255, 255, 255), stroke=0, stroke_fill=(0, 0, 0)) -> int:
    w, h = _text_size(draw, text, font)
    draw.text((x_center - w // 2, y), text, font=font, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
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
    """Find a font size and wrapped lines that fit within max_width and max_lines."""
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
    grid_rows: int = 4,
    location: str | None = None,
    hotline: str | None = None,
) -> None:
    W, H = size

    # 鑳屾櫙锛氭煍鍜岀珫鍚戞笎鍙?    img = _v_gradient((W, H), (246, 249, 255), (234, 239, 250)).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # 预解析副标题，预估分类说明行数，动态决定头部高度
    sep_pre = "｜" if "｜" in subtitle else ("|" if "|" in subtitle else None)
    if sep_pre:
        date_txt_pre, cat_txt_pre = [x.strip() for x in subtitle.split(sep_pre, 1)]
    else:
        date_txt_pre, cat_txt_pre = "", subtitle
    cat_max_w_pre = int(W * 0.88)
    _cat_font_pre, _cat_lines_pre = _wrap_fit_lines(
        draw, cat_txt_pre, font_path, max_width=cat_max_w_pre, max_lines=2, start_size=int(H * 0.036)
    )
    base_ratio_pre = 0.24
    per_line_extra_pre = 0.03
    header_h_dyn = int(H * min(0.34, base_ratio_pre + max(0, len(_cat_lines_pre) - 1) * per_line_extra_pre))

    # 澶撮儴妯箙
    header_h = header_h_dyn
    header = _v_gradient((W, header_h), (55, 120, 240), (95, 160, 255))
    img.paste(header, (0, 0))

    # 鏍囬涓庡壇鏍囬
    title_max_width = int(W * 0.9)
    title_font = _shrink_to_fit(draw, title, font_path, title_max_width, int(H * 0.070))
    title_h = _draw_centered(draw, W // 2, int(header_h * 0.22), title, title_font, fill=(255, 255, 255))

    # 鍓爣棰樻媶鍒嗕负锛氭棩鏈?+ 鍒嗙被璇存槑锛堥暱鏂囨湰涓よ鍖呰９+缂╂斁锛?    sep = "锝? if "锝? in subtitle else ("|" if "|" in subtitle else None)
    if sep:
        date_txt, cat_txt = [x.strip() for x in subtitle.split(sep, 1)]
    else:
        date_txt, cat_txt = "", subtitle

    # 鏃ユ湡琛岋紙杈冨皬涓旀敹鏁涘搴︼級
    date_max_w = int(W * 0.9)
    date_font = _shrink_to_fit(draw, date_txt, font_path, date_max_w, int(H * 0.031)) if date_txt else _load_font(font_path, int(H * 0.031))
    sub_y = int(header_h * 0.22) + title_h + int(H * 0.010)
    if date_txt:
        _draw_centered(draw, W // 2, sub_y, date_txt, date_font, fill=(230, 242, 255))
        sub_y += _text_size(draw, date_txt, date_font)[1] + int(H * 0.010)

    # 鍒嗙被璇存槑锛堟渶澶氫袱琛岋紝鑷姩缂╂斁锛?    cat_max_w = int(W * 0.88)
    cat_font, cat_lines = _wrap_fit_lines(draw, cat_txt, font_path, max_width=cat_max_w, max_lines=subtitle_max_lines, start_size=int(H * 0.036))
    for ln in cat_lines:
        _draw_centered(draw, W // 2, sub_y, ln, cat_font, fill=(235, 245, 255))
        sub_y += _text_size(draw, ln, cat_font)[1] + int(H * 0.002)

    # 椤堕儴涓嶅啀鏄剧ず鑳跺泭鏍囪瘑锛涙敼涓哄崱鐗囧簳閮ㄦ按鍗?
    # 涓讳綋瀹瑰櫒
    container_top = header_h - int(H * 0.03)
    container_margin = int(W * 0.05)
    footer_h = int(H * 0.15)
    container_bottom = H - footer_h - int(H * 0.02)
    cont_box = (container_margin, container_top, W - container_margin, container_bottom)
    _rounded_rect(draw, cont_box, radius=28, fill=(255, 255, 255), outline=(225, 230, 240), width=2)

    # 缃戞牸鍖哄煙
    grid_padding_x = int(W * 0.05)
    grid_padding_y = int(H * 0.02)
    grid_left = container_margin + grid_padding_x
    grid_right = W - container_margin - grid_padding_x
    grid_top = container_top + grid_padding_y
    grid_bottom = container_bottom - grid_padding_y
    cols, rows = grid_cols, grid_rows
    cell_w = (grid_right - grid_left) // max(1, cols)
    cell_h = (grid_bottom - grid_top) // max(1, rows)

    base_num_size = int(min(cell_h * 0.50, W * 0.066))
    meta_font = _load_font(font_path, int(min(cell_h * 0.18, W * 0.028)))
    wm_font = _load_font(font_path, int(min(cell_h * 0.16, W * 0.024)))

    for idx, item in enumerate(items[: cols * rows ]):
        c = idx % cols
        r = idx // cols
        x1 = grid_left + c * cell_w + int(cell_w * 0.04)
        y1 = grid_top + r * cell_h + int(cell_h * 0.06)
        x2 = grid_left + (c + 1) * cell_w - int(cell_w * 0.04)
        y2 = grid_top + (r + 1) * cell_h - int(cell_h * 0.06)

        _rounded_rect(draw, (x1, y1, x2, y2), radius=18, fill=(250, 252, 255), outline=(230, 235, 245), width=2)

        number = str(item.get("鍙风爜", "")).strip()
        deposit = item.get("棰勫瓨")
        low = item.get("浣庢秷")
        # 若低消与预存相同，仅显示一个
        try:
            d_val = float(deposit) if deposit is not None else None
        except Exception:
            d_val = None
        try:
            l_val = float(low) if low is not None else None
        except Exception:
            l_val = None
        if d_val is not None and l_val is not None and abs(d_val - l_val) < 1e-6:
            meta = f"棰勫瓨{_fmt_num(d_val)}"
        else:
            meta = f"棰勫瓨{_fmt_num(deposit)} / 浣庢秷{_fmt_num(low)}"

        # 鍙风爜
        cx = (x1 + x2) // 2
        cy = y1 + int((y2 - y1) * 0.15)
        # shrink-to-fit per cell
        max_w = (x2 - x1) - int(cell_w * 0.10)
        num_font = _shrink_to_fit(draw, number, font_path, max_w, base_num_size)
        num_w, num_h = _text_size(draw, number, num_font)
        draw.text((cx - num_w // 2, cy), number, font=num_font, fill=(28, 35, 52))

        # meta
        meta_w, meta_h = _text_size(draw, meta, meta_font)
        _draw_centered_bold(draw, cx, cy + num_h + int((y2 - y1) * 0.10), meta, meta_font, fill=(88, 96, 118))

        # 姘村嵃锛氬湪鏍煎瓙搴曢儴浠ュ崐閫忔槑鏂囧瓧鏍囪瘑
        if branding_label:
            wm_text = branding_label
            wm_w, wm_h = _text_size(draw, wm_text, wm_font)
            wx = cx - wm_w // 2
            wy = y2 - wm_h - int((y2 - y1) * 0.06)
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ld = ImageDraw.Draw(layer)
            ld.text((wx, wy), wm_text, font=wm_font, fill=(55, 120, 240, 72))
            img.paste(layer, (0, 0), layer)

    # 搴曢儴瀹ｄ紶璇潯
    # footer_h 宸蹭簬涓婃柟澹版槑
    footer = _v_gradient((W, footer_h), (55, 120, 240), (95, 160, 255))
    img.paste(footer, (0, H - footer_h))

    # 褰掑睘鍦颁笌鐑嚎锛堝鏋滅粰瀹氾級
    info_line = None
    if location or hotline:
        parts = []
        if location:
            parts.append(f"褰掑睘鍦帮細{location}")
        if hotline:
            parts.append(f"閫夊彿鐑嚎锛歿hotline}")
        info_line = " | ".join(parts)

    info_font = _load_font(font_path, int(H * 0.026))
    tagline_font = _load_font(font_path, int(H * 0.038))
    lines = _wrap_text_by_width(draw, tagline, tagline_font, int(W * 0.92))
    y = H - footer_h + int(footer_h * 0.18)
    if info_line:
        iw, ih = _text_size(draw, info_line, info_font)
        draw.text((W // 2 - iw // 2, y), info_line, font=info_font, fill=(230, 240, 255))
        y += ih + int(H * 0.006)
    for line in lines[:3]:
        w, h = _text_size(draw, line, tagline_font)
        draw.text((W // 2 - w // 2, y), line, font=tagline_font, fill=(255, 255, 255))
        y += h + int(H * 0.008)

    # 淇濆瓨
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(str(output_path), format="JPEG", quality=92, subsampling=0)




