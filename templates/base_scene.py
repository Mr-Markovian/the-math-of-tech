"""
base_scene.py — TMOTScene: branded 3D base class for all the_math_of_tech
scenes. Handles the cinematic space stage, watermark, intro/outro, and
YT/IG layout differences.

The stage: a deep-navy 3D space with a receding grid floor and drifting
particle field. The camera holds a slight pitch and drifts slowly during
the scene (parallax). Content plays in the z=0 plane; at scene end,
tear_down() automatically sends it receding back into depth — so every
concept "comes to the front, then goes back" with zero per-scene code.

Format is chosen via environment variable TMOT_FORMAT ("youtube" | "instagram")
so the same scene file renders both without edits.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from manim import (
    DEGREES, DOWN, IN, LEFT, RIGHT, UP,
    FadeIn, FadeOut, ThreeDScene, VGroup, VMobject, Write as WriteAnim,
)

from styles import tmot_style as S

FMT = os.environ.get("TMOT_FORMAT", "youtube")
S.apply_format(FMT)


class TMOTScene(ThreeDScene):
    """3D base scene: pure-black stage with a grey wireframe wavefunction
    drifting endlessly in the lower depth, gentle camera pitch drift, and
    content that auto-recedes into depth at scene end. Provides watermark,
    intro/outro, layout helpers."""

    fmt = FMT
    is_reel = FMT == "instagram"

    #: sideways drift of the wave field (units/s). The wave is x-periodic
    #: with period 2*pi/WAVE_K2, so wrapping at that distance is seamless —
    #: the motion never ends and never jumps.
    WAVE_SPEED = 0.35
    WAVE_K1 = 1.8            # primary spatial frequency
    WAVE_K2 = 0.9            # secondary (sets the wrap period)

    def setup(self):
        self.camera.background_color = S.BG
        self._wm = S.watermark()
        # slight pitch: enough to feel the space, not enough to hurt text
        self.set_camera_orientation(phi=11 * DEGREES, theta=-90 * DEGREES)
        self._bg = []
        img = self._background_image()
        if img is not None:
            self.add_fixed_in_frame_mobjects(img)
            self._bg.append(img)
        else:
            wave = self._wave_bg()
            self.add(wave)
            self._bg.append(wave)
        # slow pitch drift = subtle parallax across the wave field
        self.begin_ambient_camera_rotation(rate=0.008, about="phi")

    # ---- background: optional user artwork ------------------
    def _background_image(self):
        cfg = S.CFG.get("background") or {}
        if cfg.get("mode") != "image":
            return None
        key = "image_instagram" if self.is_reel else "image_youtube"
        rel = cfg.get(key) or ""
        path = (S.ROOT / rel) if rel else None
        if not path or not path.exists():
            return None
        from manim import ImageMobject
        img = ImageMobject(str(path))
        # scale to COVER the frame
        img.scale(max(self.camera.frame_width / img.width,
                      self.camera.frame_height / img.height))
        return img

    # ---- background: wireframe wavefunction ------------------
    def _wave_bg(self):
        """Grey wireframe wavefunction: ~30 depth rows of a superposed wave,
        drifting sideways forever. Each row is x-periodic with period
        2*pi/WAVE_K2, so the wrap is invisible. Rows live in the lower part
        of the frame, receding into depth; amplitude varies smoothly with
        depth for the wave-packet look."""
        k1, k2 = self.WAVE_K1, self.WAVE_K2
        period = 2 * np.pi / k2
        half_frame = self.camera.frame_width / 2
        # far rows need extra width under perspective + one wrap of margin
        half_w = 2.4 * half_frame + period + 1.0
        n_rows = 30
        base_y = -2.9

        rows = VGroup()
        for j in range(n_rows):
            z = -3.0 - 0.7 * j
            amp = 0.55 + 0.45 * np.sin(j * 0.5)      # depth "wave packet"
            phase = 0.6 * j
            depth_fade = 1.0 - 0.75 * (j / n_rows)
            xs = np.linspace(-half_w, half_w, 130)
            ys = (base_y
                  + amp * (0.75 * np.cos(k1 * xs + phase)
                           + 0.35 * np.sin(k2 * xs + 0.4 * phase)))
            row = VMobject(stroke_color=S.GRID, stroke_width=1.3)
            row.set_points_as_corners(
                [[float(x), float(y), z] for x, y in zip(xs, ys)])
            row.make_smooth()
            row.set_stroke(opacity=0.55 * depth_fade)
            rows.add(row)

        # never-ending: drift sideways, wrapping every full x-period
        def drift(m, dt):
            m._offset = getattr(m, "_offset", 0.0) + self.WAVE_SPEED * dt
            if m._offset >= period:
                m.shift(LEFT * period)
                m._offset -= period
            m.shift(RIGHT * self.WAVE_SPEED * dt)
        rows.add_updater(drift)
        return rows

    def add_watermark(self):
        # HUD element: pin to the screen, not the 3D world, or the camera
        # pitch pushes it off-frame
        self.add_fixed_in_frame_mobjects(self._wm)

    # ---- automatic depth exit -------------------------------
    def tear_down(self):
        """Show the scene's curiosity question (if any), then send content
        receding into depth and finish. Any scene spec may carry a
        `question:` field — the on-screen hook that sets up the next scene
        (visual-storytelling skill: questions are content, not narration
        garnish)."""
        q = (getattr(self, "spec", None) or {}).get("question")
        storyboard = bool(os.environ.get("TMOT_STORYBOARD"))
        if q:
            qt = S.body(str(q), font_size=30, color=S.YELLOW)
            self.fit(qt, margin=0.85)
            qt.to_edge(DOWN, buff=1.8 if self.is_reel else 0.9)
            if storyboard:
                self.add(qt)
            else:
                self.play(FadeIn(qt, shift=UP * 0.4), run_time=0.7)
                self.wait(1.3)
        if storyboard:
            # TMOT_STORYBOARD=1 (pipeline/storyboard.py): keep everything ON
            # stage so `manim -s` captures a fully composed audit still —
            # the normal recede is why -s frames are empty (LESSONS L-9).
            super().tear_down()
            return
        try:
            self.stop_ambient_camera_rotation(about="phi")
        except Exception:
            pass
        keep = set(self._bg) | {self._wm}
        content = [m for m in self.mobjects
                   if isinstance(m, VMobject) and m not in keep]
        if content:
            g = VGroup(*content)
            self.play(g.animate.shift(IN * 9).set_opacity(0), run_time=0.8)
        super().tear_down()

    # ---- branding ------------------------------------------
    def branded_intro(self):
        b = S.CFG["branding"]
        name = S.heading(b["intro_text"], font_size=56, color=S.BLUE)
        tag = S.body(b["intro_tagline"], font_size=24, color=S.MUTED)
        tag.next_to(name, DOWN, buff=0.3)
        group = VGroup(name, tag)
        S.ig_safe_shift(group, self.fmt)
        self.play(WriteAnim(name), run_time=1.2)
        self.play(FadeIn(tag), run_time=0.6)
        self.wait(b["intro_duration_s"] - 1.8)
        self.play(FadeOut(group), run_time=0.5)

    def branded_outro(self):
        b = S.CFG["branding"]
        cta_key = "outro_cta_instagram" if self.is_reel else "outro_cta_youtube"
        cta = S.body(b[cta_key], font_size=30, color=S.YELLOW)
        name = S.heading(S.CFG["channel"]["handle"], font_size=44, color=S.BLUE)
        cta.next_to(name, DOWN, buff=0.4)
        group = VGroup(name, cta)
        S.ig_safe_shift(group, self.fmt)
        self.play(FadeIn(group), run_time=0.8)
        self.wait(2)

    # ---- layout helpers ------------------------------------
    def title_bar(self, text: str):
        """Tufte-style running head: small, understated, top-LEFT, with a
        thin hairline rule beneath. Content, not chrome, carries the frame."""
        size = 24 if self.is_reel else 28
        t = S.body(text, font_size=size, color=S.MUTED)
        # cap width so left buff + text never crosses the right edge
        max_w = min(0.9 * self.camera.frame_width,
                    self.camera.frame_width - 1.0)
        if t.width > max_w:
            t.scale_to_fit_width(max_w)
        t.to_corner(UP + LEFT, buff=0.45)
        if self.is_reel:
            t.shift(DOWN * 0.75)   # clear the IG UI band
        rule = S.hairline(min(t.width * 1.4, max_w))
        rule.next_to(t, DOWN, buff=0.14, aligned_edge=LEFT)
        return VGroup(t, rule)

    def fit(self, mobject, margin: float = 0.85):
        """Scale any mobject to fit current frame width — the key trick
        that lets one layout survive both 16:9 and 9:16."""
        max_w = margin * self.camera.frame_width
        if mobject.width > max_w:
            mobject.scale_to_fit_width(max_w)
        return mobject

    def shimmer_in(self, target, buff: float = 0.35, run_time: float = 0.8):
        """Draw a thin shimmer frame around a settled equation: gradient
        stroke + a slow glint traveling the perimeter (dt-updater, so it
        keeps moving through waits). Called AFTER the equation is fully
        revealed — the frame marks the hero, it never competes with it.
        Returns the VGroup(frame, glint) in case the scene wants it."""
        frame = S.shimmer_frame(target, buff)
        glint = VMobject(stroke_width=2.5)
        glint.set_stroke(S.TEXT, opacity=0.85)
        span, speed, samples = 0.10, 0.22, 12

        def drift(m, dt):
            m._ph = getattr(m, "_ph", 0.0) + speed * dt
            a = m._ph % 1.0
            pts = [frame.point_from_proportion((a + span * k / samples) % 1.0)
                   for k in range(samples + 1)]
            m.set_points_as_corners(pts)

        drift(glint, 0.0)          # initial geometry before first frame
        glint.add_updater(drift)
        self.play(FadeIn(frame), run_time=run_time)
        self.add(glint)
        return VGroup(frame, glint)
