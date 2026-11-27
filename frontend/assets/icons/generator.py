"""Programmatic high-DPI Pillow icon and illustration generator in the blue & white palette."""

from __future__ import annotations

from typing import Tuple
import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont


def _hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    cleaned = hex_color.lstrip("#")
    return (
        int(cleaned[0:2], 16),
        int(cleaned[2:4], 16),
        int(cleaned[4:6], 16),
    )


def create_nav_icon(name: str, color: str = "#1D4ED8", size: int = 20) -> ctk.CTkImage:
    """Render crisp anti-aliased navigation icons via 4x supersampling."""
    scale = 4
    px = size * scale
    img = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    rgb = _hex_to_rgb(color)
    stroke = max(2, int(2.2 * scale))

    if name == "home":
        # Roof
        draw.line(
            [(px * 0.14, px * 0.50), (px * 0.50, px * 0.18), (px * 0.86, px * 0.50)],
            fill=rgb,
            width=stroke,
            joint="curve",
        )
        # Body
        draw.rounded_rectangle(
            [px * 0.24, px * 0.44, px * 0.76, px * 0.84],
            radius=4 * scale,
            outline=rgb,
            width=stroke,
        )
        # Door
        draw.rectangle(
            [px * 0.43, px * 0.60, px * 0.57, px * 0.84],
            fill=rgb,
        )
    elif name == "allocation":
        # Segmented memory bar
        draw.rounded_rectangle(
            [px * 0.14, px * 0.20, px * 0.86, px * 0.80],
            radius=4 * scale,
            outline=rgb,
            width=stroke,
        )
        draw.rectangle([px * 0.18, px * 0.25, px * 0.42, px * 0.75], fill=rgb)
        draw.line([(px * 0.62, px * 0.20), (px * 0.62, px * 0.80)], fill=rgb, width=stroke)
    elif name == "paging":
        # Two linked tables with translation arrow
        draw.rounded_rectangle(
            [px * 0.12, px * 0.20, px * 0.44, px * 0.80],
            radius=3 * scale,
            outline=rgb,
            width=stroke,
        )
        draw.rounded_rectangle(
            [px * 0.56, px * 0.20, px * 0.88, px * 0.80],
            radius=3 * scale,
            outline=rgb,
            width=stroke,
        )
        draw.line([(px * 0.12, px * 0.42), (px * 0.44, px * 0.42)], fill=rgb, width=stroke)
        draw.line([(px * 0.12, px * 0.62), (px * 0.44, px * 0.62)], fill=rgb, width=stroke)
        draw.line([(px * 0.56, px * 0.42), (px * 0.88, px * 0.42)], fill=rgb, width=stroke)
        draw.line([(px * 0.56, px * 0.62), (px * 0.88, px * 0.62)], fill=rgb, width=stroke)
        draw.line([(px * 0.44, px * 0.50), (px * 0.56, px * 0.50)], fill=rgb, width=stroke)
    elif name == "replacement":
        # Circular refresh / frame swap
        draw.arc(
            [px * 0.16, px * 0.16, px * 0.84, px * 0.84],
            start=35,
            end=315,
            fill=rgb,
            width=stroke,
        )
        draw.polygon(
            [
                (px * 0.84, px * 0.26),
                (px * 0.66, px * 0.28),
                (px * 0.80, px * 0.44),
            ],
            fill=rgb,
        )
    elif name == "comparison":
        # Three comparison bars
        draw.rounded_rectangle([px * 0.16, px * 0.48, px * 0.34, px * 0.82], radius=2 * scale, fill=rgb)
        draw.rounded_rectangle([px * 0.41, px * 0.24, px * 0.59, px * 0.82], radius=2 * scale, fill=rgb)
        draw.rounded_rectangle([px * 0.66, px * 0.36, px * 0.84, px * 0.82], radius=2 * scale, fill=rgb)
    elif name == "about":
        # Info circle
        draw.ellipse([px * 0.14, px * 0.14, px * 0.86, px * 0.86], outline=rgb, width=stroke)
        draw.ellipse([px * 0.45, px * 0.30, px * 0.55, px * 0.40], fill=rgb)
        draw.line([(px * 0.50, px * 0.47), (px * 0.50, px * 0.70)], fill=rgb, width=stroke)
    elif name == "exit":
        # Door + exit arrow
        draw.line(
            [
                (px * 0.52, px * 0.18),
                (px * 0.20, px * 0.18),
                (px * 0.20, px * 0.82),
                (px * 0.52, px * 0.82),
            ],
            fill=rgb,
            width=stroke,
        )
        draw.line([(px * 0.42, px * 0.50), (px * 0.84, px * 0.50)], fill=rgb, width=stroke)
        draw.polygon(
            [
                (px * 0.86, px * 0.50),
                (px * 0.70, px * 0.36),
                (px * 0.70, px * 0.64),
            ],
            fill=rgb,
        )
    else:
        draw.ellipse([px * 0.2, px * 0.2, px * 0.8, px * 0.8], fill=rgb)

    resized = img.resize((size, size), Image.Resampling.LANCZOS)
    return ctk.CTkImage(light_image=resized, dark_image=resized, size=(size, size))


def create_module_illustration(module_type: str, width: int = 260, height: int = 84) -> ctk.CTkImage:
    """Create crisp technical vector-style illustrations for the Home module cards."""
    scale = 2
    w, h = width * scale, height * scale
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Soft blue backdrop
    draw.rounded_rectangle([0, 0, w - 1, h - 1], radius=12 * scale, fill=(239, 246, 255, 255), outline=(191, 219, 254, 255), width=2)

    if module_type == "allocation":
        # Contiguous partition blocks P1 | Free | P2 | P3 | Free
        segments = [
            (0.06, 0.26, (37, 99, 235, 255), "P1"),
            (0.27, 0.42, (203, 213, 225, 255), "FREE"),
            (0.43, 0.67, (2, 132, 199, 255), "P2"),
            (0.68, 0.84, (79, 70, 229, 255), "P3"),
            (0.85, 0.94, (203, 213, 225, 255), ""),
        ]
        y1, y2 = int(h * 0.24), int(h * 0.76)
        for x1_r, x2_r, color, label in segments:
            x1, x2 = int(w * x1_r), int(w * x2_r)
            draw.rounded_rectangle([x1, y1, x2, y2], radius=6 * scale, fill=color)
            if label:
                text_fill = (15, 23, 42, 255) if label == "FREE" else (255, 255, 255, 255)
                draw.text((x1 + 8 * scale, y1 + 12 * scale), label, fill=text_fill)

    elif module_type == "paging":
        # Logical [Page | Offset] -> Page Table -> Physical [Frame | Offset]
        y1, y2 = int(h * 0.26), int(h * 0.74)
        # Logical box
        draw.rounded_rectangle([int(w * 0.05), y1, int(w * 0.31), y2], radius=6 * scale, fill=(29, 78, 216, 255))
        draw.line([(int(w * 0.19), y1), (int(w * 0.19), y2)], fill=(255, 255, 255, 255), width=2)
        draw.text((int(w * 0.07), y1 + 12 * scale), "P#", fill=(255, 255, 255, 255))
        draw.text((int(w * 0.21), y1 + 12 * scale), "OFF", fill=(255, 255, 255, 255))

        # Arrow 1
        draw.line([(int(w * 0.33), h // 2), (int(w * 0.41), h // 2)], fill=(2, 132, 199, 255), width=3 * scale)
        draw.polygon([(int(w * 0.42), h // 2), (int(w * 0.39), h // 2 - 5 * scale), (int(w * 0.39), h // 2 + 5 * scale)], fill=(2, 132, 199, 255))

        # Page Table box
        draw.rounded_rectangle([int(w * 0.43), int(h * 0.18), int(w * 0.59), int(h * 0.82)], radius=6 * scale, fill=(255, 255, 255, 255), outline=(29, 78, 216, 255), width=2 * scale)
        draw.text((int(w * 0.46), int(h * 0.40)), "PT", fill=(29, 78, 216, 255))

        # Arrow 2
        draw.line([(int(w * 0.61), h // 2), (int(w * 0.68), h // 2)], fill=(2, 132, 199, 255), width=3 * scale)
        draw.polygon([(int(w * 0.69), h // 2), (int(w * 0.66), h // 2 - 5 * scale), (int(w * 0.66), h // 2 + 5 * scale)], fill=(2, 132, 199, 255))

        # Physical box
        draw.rounded_rectangle([int(w * 0.70), y1, int(w * 0.95), y2], radius=6 * scale, fill=(13, 148, 136, 255))
        draw.line([(int(w * 0.83), y1), (int(w * 0.83), y2)], fill=(255, 255, 255, 255), width=2)
        draw.text((int(w * 0.72), y1 + 12 * scale), "F#", fill=(255, 255, 255, 255))
        draw.text((int(w * 0.85), y1 + 12 * scale), "OFF", fill=(255, 255, 255, 255))

    elif module_type == "replacement":
        # 4 frame columns showing page slots and hit/fault indicators
        cols = [
            (["7", "-", "-"], (220, 38, 38, 255)),
            (["7", "0", "-"], (220, 38, 38, 255)),
            (["7", "0", "1"], (220, 38, 38, 255)),
            (["7", "0", "1"], (22, 163, 74, 255)),
        ]
        col_w = int(w * 0.17)
        gap = int(w * 0.05)
        start_x = int(w * 0.08)
        slot_h = int(h * 0.21)
        for idx, (slots, badge_color) in enumerate(cols):
            cx = start_x + idx * (col_w + gap)
            for s_idx, val in enumerate(slots):
                sy = int(h * 0.12) + s_idx * (slot_h + 2 * scale)
                fill = (255, 255, 255, 255) if val != "-" else (226, 232, 240, 255)
                draw.rounded_rectangle([cx, sy, cx + col_w, sy + slot_h], radius=3 * scale, fill=fill, outline=(147, 197, 253, 255), width=2)
                draw.text((cx + col_w // 3, sy + 2 * scale), val, fill=(15, 23, 42, 255))
            # Bottom status bar
            by = int(h * 0.82)
            draw.rounded_rectangle([cx, by, cx + col_w, by + 8 * scale], radius=3 * scale, fill=badge_color)

    resized = img.resize((width, height), Image.Resampling.LANCZOS)
    return ctk.CTkImage(light_image=resized, dark_image=resized, size=(width, height))


def create_developer_avatar(
    initials: str,
    accent_color: str = "#1D4ED8",
    is_leader: bool = False,
    size: int = 96,
) -> ctk.CTkImage:
    """
    Generate a clean vector-style portrait avatar wearing glasses for each team member.
    All three team members wear glasses as required.
    """
    scale = 4
    px = size * scale
    img = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    accent = _hex_to_rgb(accent_color)

    # Outer circular badge
    ring_color = (29, 78, 216, 255) if is_leader else (147, 197, 253, 255)
    ring_w = 5 * scale if is_leader else 3 * scale
    draw.ellipse([2 * scale, 2 * scale, px - 2 * scale, px - 2 * scale], fill=(239, 246, 255, 255), outline=ring_color, width=ring_w)

    # Shoulders / Shirt
    draw.pieslice(
        [int(px * 0.18), int(px * 0.62), int(px * 0.82), int(px * 1.12)],
        start=180,
        end=360,
        fill=accent,
    )
    # White collar V
    draw.polygon(
        [
            (int(px * 0.43), int(px * 0.63)),
            (int(px * 0.57), int(px * 0.63)),
            (int(px * 0.50), int(px * 0.76)),
        ],
        fill=(255, 255, 255, 255),
    )

    # Neck
    draw.rectangle(
        [int(px * 0.44), int(px * 0.54), int(px * 0.56), int(px * 0.66)],
        fill=(241, 194, 155, 255),
    )

    # Head
    draw.ellipse(
        [int(px * 0.32), int(px * 0.22), int(px * 0.68), int(px * 0.58)],
        fill=(248, 206, 170, 255),
        outline=(217, 168, 130, 255),
        width=2 * scale,
    )

    # Hair
    draw.pieslice(
        [int(px * 0.31), int(px * 0.19), int(px * 0.69), int(px * 0.44)],
        start=180,
        end=360,
        fill=(30, 41, 59, 255),
    )

    # Eyes behind glasses
    eye_y = int(px * 0.40)
    draw.ellipse([int(px * 0.39), eye_y - 2 * scale, int(px * 0.43), eye_y + 2 * scale], fill=(15, 23, 42, 255))
    draw.ellipse([int(px * 0.57), eye_y - 2 * scale, int(px * 0.61), eye_y + 2 * scale], fill=(15, 23, 42, 255))

    # Eyeglasses (frames + bridge + temple arms)
    glass_stroke = max(2, int(2.4 * scale))
    frame_color = (15, 23, 42, 255)
    lens_tint = (255, 255, 255, 85)
    # Left lens
    draw.rounded_rectangle(
        [int(px * 0.34), int(px * 0.35), int(px * 0.48), int(px * 0.45)],
        radius=3 * scale,
        fill=lens_tint,
        outline=frame_color,
        width=glass_stroke,
    )
    # Right lens
    draw.rounded_rectangle(
        [int(px * 0.52), int(px * 0.35), int(px * 0.66), int(px * 0.45)],
        radius=3 * scale,
        fill=lens_tint,
        outline=frame_color,
        width=glass_stroke,
    )
    # Bridge
    draw.line([(int(px * 0.48), int(px * 0.39)), (int(px * 0.52), int(px * 0.39))], fill=frame_color, width=glass_stroke)
    # Temple arms
    draw.line([(int(px * 0.31), int(px * 0.38)), (int(px * 0.34), int(px * 0.39))], fill=frame_color, width=glass_stroke)
    draw.line([(int(px * 0.66), int(px * 0.39)), (int(px * 0.69), int(px * 0.38))], fill=frame_color, width=glass_stroke)

    # Smile
    draw.arc(
        [int(px * 0.44), int(px * 0.45), int(px * 0.56), int(px * 0.52)],
        start=15,
        end=165,
        fill=(120, 53, 15, 255),
        width=2 * scale,
    )

    # Leader crown/star badge at top-right if Team Leader
    if is_leader:
        bx, by = int(px * 0.78), int(px * 0.22)
        r = int(px * 0.11)
        draw.ellipse([bx - r, by - r, bx + r, by + r], fill=(29, 78, 216, 255), outline=(255, 255, 255, 255), width=2 * scale)
        draw.text((bx - int(r * 0.45), by - int(r * 0.55)), "★", fill=(255, 255, 255, 255))

    resized = img.resize((size, size), Image.Resampling.LANCZOS)
    return ctk.CTkImage(light_image=resized, dark_image=resized, size=(size, size))
