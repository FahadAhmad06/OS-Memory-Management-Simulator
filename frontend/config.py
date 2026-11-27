"""Central configuration, light-mode blue & white palette, fonts, and layout constants."""

from pathlib import Path

# Application metadata
APP_TITLE = "OS Memory Management Simulator"
APP_SUBTITLE = "Visualize, Analyze, Understand"
UNIVERSITY_NAME = "University of Veterinary and Animal Sciences (UVAS), Lahore"
DEPARTMENT_NAME = "Department of Computer Science — BSCS"
APP_VERSION = "1.0.0"

# Window configuration
WINDOW_WIDTH = 1380
WINDOW_HEIGHT = 860
MIN_WINDOW_WIDTH = 1140
MIN_WINDOW_HEIGHT = 720
SIDEBAR_WIDTH = 245
HEADER_HEIGHT = 74

# Paths
FRONTEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = FRONTEND_DIR.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
ASSETS_DIR = FRONTEND_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
IMAGES_DIR = ASSETS_DIR / "images"
FONTS_DIR = ASSETS_DIR / "fonts"

# Candidate C++ backend executable locations (supports OS-MMS and CMake default binary names)
BACKEND_EXECUTABLE_CANDIDATES = [
    BACKEND_DIR / "build" / "OS-MMS",
    BACKEND_DIR / "OS-MMS",
    PROJECT_ROOT / "OS-MMS",
    BACKEND_DIR / "build" / "os_memory_simulator",
    BACKEND_DIR / "os_memory_simulator",
    PROJECT_ROOT / "os_memory_simulator",
]

# Strictly Light Mode Blue & White Color Palette
COLORS = {
    # Backgrounds
    "app_bg": "#F1F6FC",
    "content_bg": "#F4F8FE",
    "sidebar_bg": "#FFFFFF",
    "header_bg": "#FFFFFF",
    "card_bg": "#FFFFFF",
    "card_alt_bg": "#F8FBFF",
    "input_bg": "#F8FAFC",
    "table_header_bg": "#E6F0FD",
    "table_row_even": "#FFFFFF",
    "table_row_odd": "#F8FBFF",

    # Primary & Accent Blues
    "primary": "#1D4ED8",
    "primary_hover": "#1E40AF",
    "primary_light": "#DBEAFE",
    "primary_soft": "#EFF6FF",
    "secondary": "#0284C7",
    "secondary_hover": "#0369A1",
    "accent_sky": "#38BDF8",
    "accent_indigo": "#4338CA",

    # Typography
    "text_primary": "#0F172A",
    "text_secondary": "#334155",
    "text_muted": "#64748B",
    "text_on_primary": "#FFFFFF",

    # Borders & Dividers
    "border": "#D6E4F7",
    "border_strong": "#93C5FD",
    "divider": "#E2E8F0",

    # Status & Visualization Semantics
    "success": "#15803D",
    "success_bg": "#DCFCE7",
    "success_border": "#86EFAC",

    "danger": "#B91C1C",
    "danger_bg": "#FEE2E2",
    "danger_border": "#FCA5A5",

    "warning": "#B45309",
    "warning_bg": "#FEF3C7",
    "warning_border": "#FCD34D",

    "info": "#0369A1",
    "info_bg": "#E0F2FE",
    "info_border": "#7DD3FC",

    # Memory Block & Frame Palette
    "free_block_bg": "#E2E8F0",
    "free_block_border": "#94A3B8",
    "free_block_text": "#334155",
    "empty_frame_bg": "#F1F5F9",
    "empty_frame_text": "#94A3B8",

    # Neutral Buttons
    "neutral_btn": "#E2E8F0",
    "neutral_btn_hover": "#CBD5E1",
    "neutral_btn_text": "#1E293B",
}

# Distinct high-contrast process colors for memory allocation blocks
PROCESS_PALETTE = [
    "#2563EB",  # Royal Blue
    "#0891B2",  # Cyan Blue
    "#4F46E5",  # Indigo
    "#0D9488",  # Teal
    "#7C3AED",  # Violet
    "#0284C7",  # Sky Blue
    "#1D4ED8",  # Deep Blue
    "#059669",  # Emerald
    "#6366F1",  # Periwinkle
    "#0369A1",  # Ocean
]

# Typography tuples (family, size, weight)
FONTS = {
    "hero_title": ("Segoe UI", 24, "bold"),
    "page_title": ("Segoe UI", 20, "bold"),
    "section_title": ("Segoe UI", 15, "bold"),
    "card_title": ("Segoe UI", 14, "bold"),
    "subtitle": ("Segoe UI", 12, "normal"),
    "body": ("Segoe UI", 12, "normal"),
    "body_bold": ("Segoe UI", 12, "bold"),
    "small": ("Segoe UI", 11, "normal"),
    "small_bold": ("Segoe UI", 11, "bold"),
    "caption": ("Segoe UI", 10, "normal"),
    "metric_value": ("Segoe UI", 22, "bold"),
    "metric_label": ("Segoe UI", 11, "bold"),
    "mono": ("DejaVu Sans Mono", 11, "normal"),
    "mono_bold": ("DejaVu Sans Mono", 11, "bold"),
    "sidebar_item": ("Segoe UI", 13, "bold"),
}

# Shape & Spacing
CORNER_RADIUS_CARD = 14
CORNER_RADIUS_BTN = 10
CORNER_RADIUS_INPUT = 8
PAD_OUTER = 18
PAD_CARD = 16
