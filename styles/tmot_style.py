"""
tmot_style.py — style layer for the_math_of_tech.
Loads config/channel.yaml and exposes colors, fonts, and helpers
so every scene stays visually consistent.
"""
from pathlib import Path

import yaml
from manim import (
    DOWN, RIGHT, UP, LEFT,
    Line, RoundedRectangle, Text, VGroup, config as manim_config,
)

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "channel.yaml"

with open(CONFIG_PATH, encoding="utf-8") as f:
    CFG = yaml.safe_load(f)

# ---- palette ------------------------------------------------
C = CFG["colors"]
BG = C["background"]
TEXT = C["text"]
BLUE = C["accent_blue"]
YELLOW = C["accent_yellow"]
RED = C["accent_red"]
GREEN = C["accent_green"]
PURPLE = C["accent_purple"]
GRID = C["grid"]
MUTED = C["muted"]

FONT_HEADING = CFG["fonts"]["heading"]
FONT_BODY = CFG["fonts"]["body"]
FONT_CODE = CFG["fonts"]["code"]

CHANNEL = CFG["channel"]["name"]


def style_flag(name: str, default: bool = False) -> bool:
    """Brand-wide style toggle from channel.yaml's `style:` section."""
    return bool((CFG.get("style") or {}).get(name, default))


def shimmer_frame(mobject, buff: float = 0.35) -> RoundedRectangle:
    """Thin neon frame for hero equations: rounded rect, gradient stroke
    (blue -> white -> blue reads as a static shimmer), NO fill so the
    stage stays black behind the math. Clamped so it never leaves the
    frame even when the equation was fitted to full width."""
    fw = manim_config.frame_width
    buff_x = min(buff, max(0.08, (0.98 * fw - mobject.width) / 2))
    frame = RoundedRectangle(
        width=mobject.width + 2 * buff_x,
        height=mobject.height + 2 * buff,
        corner_radius=0.15,
        stroke_width=1.5, fill_opacity=0.0,
    )
    frame.set_stroke(color=[BLUE, TEXT, BLUE], opacity=0.5)
    frame.move_to(mobject)
    return frame


def apply_format(fmt: str = "youtube") -> dict:
    """Set manim global config for 'youtube' (16:9) or 'instagram' (9:16).
    Call BEFORE scene construction (e.g. in generated script header).
    Returns the format dict for layout decisions."""
    f = CFG["formats"][fmt]
    manim_config.pixel_width = f["pixel_width"]
    manim_config.pixel_height = f["pixel_height"]
    manim_config.frame_rate = f["frame_rate"]
    if fmt == "instagram":
        # keep frame_height = 8.0 (manim default) and shrink width
        manim_config.frame_height = 8.0
        manim_config.frame_width = 8.0 * 9 / 16
    else:
        manim_config.frame_height = 8.0
        manim_config.frame_width = 8.0 * 16 / 9
    manim_config.background_color = BG
    return f


def watermark() -> Text:
    """Small channel watermark, bottom-right."""
    wm = Text(
        CFG["channel"]["watermark_text"],
        font=FONT_BODY, font_size=18, color=MUTED,
    )
    wm.set_opacity(CFG["channel"]["watermark_opacity"])
    wm.to_corner(DOWN + RIGHT, buff=0.25)
    return wm


def heading(text: str, font_size: int = 48, color: str = TEXT) -> Text:
    return Text(text, font=FONT_HEADING, font_size=font_size, color=color)


def body(text: str, font_size: int = 28, color: str = TEXT) -> Text:
    return Text(text, font=FONT_BODY, font_size=font_size, color=color)


def shadow(mobject, offset: float = 0.07, opacity: float = 0.5):
    """Pseudo-3D drop shadow: dark offset copy to layer BEHIND `mobject`.
    Usage: group = VGroup(S.shadow(m), m)."""
    sh = mobject.copy()
    sh.set_fill("#000000", opacity=opacity)
    sh.set_stroke("#000000", width=1, opacity=opacity * 0.6)
    sh.shift(DOWN * offset + RIGHT * offset)
    return sh


def with_depth(mobject, offset: float = 0.07, opacity: float = 0.5):
    """Return VGroup(shadow, mobject) — the one-call 3D-ish card look."""
    return VGroup(shadow(mobject, offset, opacity), mobject)


def hairline(width: float, color: str = None):
    """Tufte-style thin rule for separating title from content."""
    return Line([0, 0, 0], [width, 0, 0],
                stroke_color=color or GRID, stroke_width=1.5)


def ig_safe_shift(mobject, fmt: str):
    """Shift content into the IG-safe vertical band when rendering reels."""
    if fmt != "instagram":
        return mobject
    f = CFG["formats"]["instagram"]
    top = f["safe_top_frac"]
    bottom = f["safe_bottom_frac"]
    # net shift upward if bottom margin dominates
    net = (bottom - top) / 2 * manim_config.frame_height
    return mobject.shift(UP * net)
