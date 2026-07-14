"""
scene_library.py — reusable scene archetypes for the_math_of_tech.
The generator (pipeline/generate_scripts.py) maps blog `scene` blocks
onto these classes via the `type:` field.

Archetypes:
  concept_title     — hook / section title card
  equation_reveal   — LaTeX equation(s) revealed line by line, with highlights
  equation_annotated— equation from parts, color-coded terms + callout arrow
  transform         — equation A morphs into equation B (TransformMatchingTex)
  graph             — plot a function on axes
  neural_net        — layered network diagram with animated forward pass
  attention_matrix  — token-to-token heatmap; accepts real `weights` + focus_row
  matrix_multiply   — A x B = C with real numbers; walk one row's dot products
  softmax_build     — bar-by-bar softmax: scores -> exponentiate -> normalize
  multi_head        — schematic of h parallel heads -> concat -> W^O projection
  bullet_points     — staged text points (use sparingly — show, don't tell)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from manim import (
    Arrow, Axes, Circle, Create, DecimalMatrix, DOWN, FadeIn, FadeOut,
    FadeTransform, GrowFromCenter, Indicate, IntegerMatrix, LEFT, Line,
    MathTex, ORIGIN, OUT, Rectangle, RIGHT, RoundedRectangle, Square,
    SurroundingRectangle, Text, Transform, TransformMatchingTex, UP, VGroup,
    Write as WriteAnim,
)

from styles import tmot_style as S
from templates.base_scene import TMOTScene

ACCENTS = [S.BLUE, S.YELLOW, S.RED, S.GREEN, S.PURPLE]


class ConceptTitle(TMOTScene):
    """Title card. spec: title, subtitle (optional)."""
    spec = {"title": "Concept", "subtitle": ""}

    def construct(self):
        self.add_watermark()
        title = S.heading(self.spec["title"], font_size=60)
        title.set_color_by_gradient(S.RED, S.PURPLE)   # IG-vivid gradient
        self.fit(title)
        title_g = VGroup(S.shadow(title, 0.05, 0.6), title)  # depth
        group = VGroup(title_g)
        if self.spec.get("subtitle"):
            sub = S.body(self.spec["subtitle"], font_size=28, color=S.MUTED)
            sub.next_to(title_g, DOWN, buff=0.4)
            self.fit(sub)
            group.add(sub)
        group.move_to([0, 0, 0])
        S.ig_safe_shift(group, self.fmt)
        # arrive from depth — perspective does the scaling
        self.play(FadeIn(title_g, shift=OUT * 4), run_time=1.5)
        if len(group) > 1:
            self.play(FadeIn(group[1], shift=OUT * 1.5), run_time=0.7)
        self.wait(float(self.spec.get("duration", 3)) - 2.2)


class EquationReveal(TMOTScene):
    """spec: title, tex (list of latex strings), highlight (optional index)."""
    spec = {"title": "", "tex": [r"e^{i\pi} + 1 = 0"], "highlight": None}

    def construct(self):
        self.add_watermark()
        top = None
        if self.spec.get("title"):
            top = self.title_bar(self.spec["title"])
            self.play(FadeIn(top), run_time=0.6)
        eqs = VGroup(*[
            MathTex(t, color=S.TEXT) for t in self.spec["tex"]
        ]).arrange(DOWN, buff=0.6)
        self.fit(eqs)
        S.ig_safe_shift(eqs, self.fmt)
        for i, eq in enumerate(eqs):
            self.play(WriteAnim(eq), run_time=1.4)
            self.wait(0.6)
        hl = self.spec.get("highlight")
        if hl is not None and 0 <= int(hl) < len(eqs):
            eq = eqs[int(hl)]
            self.play(Indicate(eq, color=S.YELLOW), run_time=1.2)
            eq.set_color(S.YELLOW)
        if self.spec.get("shimmer", S.style_flag("equation_shimmer", True)):
            self.shimmer_in(eqs)
        self.wait(float(self.spec.get("duration", 8)) / 4)


class TransformExplainer(TMOTScene):
    """spec: title, tex_from, tex_to — morphs one equation into another."""
    spec = {"title": "", "tex_from": r"a^2 + b^2", "tex_to": r"c^2"}

    def construct(self):
        self.add_watermark()
        if self.spec.get("title"):
            self.play(FadeIn(self.title_bar(self.spec["title"])), run_time=0.6)
        src = MathTex(self.spec["tex_from"], color=S.TEXT)
        dst = MathTex(self.spec["tex_to"], color=S.YELLOW)
        for m in (src, dst):
            self.fit(m)
            S.ig_safe_shift(m, self.fmt)
        self.play(WriteAnim(src), run_time=1.4)
        self.wait(1)
        self.play(TransformMatchingTex(src, dst), run_time=2)
        if self.spec.get("shimmer", S.style_flag("equation_shimmer", True)):
            self.shimmer_in(dst)
        self.wait(float(self.spec.get("duration", 8)) / 4)


class GraphScene(TMOTScene):
    """spec: title, function (python expr in x, numpy as np),
    x_range [a,b], y_range [a,b], label (latex)."""
    spec = {"title": "", "function": "np.sin(x)",
            "x_range": [-4, 4], "y_range": [-2, 2], "label": ""}

    def construct(self):
        self.add_watermark()
        if self.spec.get("title"):
            self.play(FadeIn(self.title_bar(self.spec["title"])), run_time=0.6)
        xr, yr = self.spec["x_range"], self.spec["y_range"]
        w = 0.85 * self.camera.frame_width
        h = 0.55 * self.camera.frame_height
        axes = Axes(
            x_range=[*xr, (xr[1] - xr[0]) / 4],
            y_range=[*yr, (yr[1] - yr[0]) / 4],
            x_length=w, y_length=h, tips=False,
            # Tufte: axes are reference, not decoration — hairline weight
            axis_config={"color": S.GRID, "stroke_width": 1.5},
        )
        S.ig_safe_shift(axes, self.fmt)
        fn = eval("lambda x: " + self.spec["function"], {"np": np})  # noqa: S307
        curve = axes.plot(fn, stroke_width=5)
        curve.set_color_by_gradient(S.BLUE, S.PURPLE)
        self.play(Create(axes), run_time=1)
        self.play(Create(curve), run_time=2)
        if self.spec.get("label"):
            lab = MathTex(self.spec["label"], color=S.BLUE)
            lab.next_to(curve, UP, buff=0.2)
            self.fit(lab)
            self.play(FadeIn(lab), run_time=0.7)
        self.wait(float(self.spec.get("duration", 8)) / 4)


class NeuralNet(TMOTScene):
    """spec: title, layers (e.g. [3,5,5,2]) — diagram + animated forward pass."""
    spec = {"title": "", "layers": [3, 4, 2]}

    def construct(self):
        self.add_watermark()
        if self.spec.get("title"):
            self.play(FadeIn(self.title_bar(self.spec["title"])), run_time=0.6)
        layers = self.spec["layers"]
        n_l = len(layers)
        w = 0.8 * self.camera.frame_width
        h = 0.5 * self.camera.frame_height
        xs = np.linspace(-w / 2, w / 2, n_l)
        neuron_groups, all_edges = [], VGroup()
        for li, n in enumerate(layers):
            ys = np.linspace(h / 2, -h / 2, n) if n > 1 else [0.0]
            g = VGroup()
            for y in ys:
                c = Circle(radius=min(0.22, h / (2.5 * max(layers))),
                           color=ACCENTS[li % len(ACCENTS)],
                           fill_opacity=0.9, stroke_width=1.5)
                # sheen = cheap sphere shading (pseudo-3D)
                c.set_sheen(0.6, UP + LEFT)
                c.move_to([xs[li], y, 0])
                g.add(c)
            neuron_groups.append(g)
        for li in range(n_l - 1):
            for a in neuron_groups[li]:
                for b in neuron_groups[li + 1]:
                    all_edges.add(Line(a.get_center(), b.get_center(),
                                       color=S.GRID, stroke_width=1.0,
                                       buff=0.22))
        net = VGroup(all_edges, *neuron_groups)
        self.fit(net)
        S.ig_safe_shift(net, self.fmt)
        self.play(Create(all_edges), run_time=1.5)
        self.play(*[GrowFromCenter(g) for g in neuron_groups], run_time=1)
        # forward pass pulse
        for g in neuron_groups:
            self.play(*[Indicate(c, color=S.YELLOW, scale_factor=1.15)
                        for c in g], run_time=0.5)
        self.wait(float(self.spec.get("duration", 10)) / 4)


class AttentionMatrix(TMOTScene):
    """spec: title, tokens (list of strings).
    Optional: weights (n x n row-stochastic list — REAL attention weights;
    if omitted, illustrative random weights are used) and focus_row (int —
    hold on one query row and label its strongest attention)."""
    spec = {"title": "Attention", "tokens": ["the", "cat", "sat"]}

    def construct(self):
        self.add_watermark()
        if self.spec.get("title"):
            self.play(FadeIn(self.title_bar(self.spec["title"])), run_time=0.6)
        toks = self.spec["tokens"]
        n = len(toks)
        given = self.spec.get("weights")
        if given is not None:
            weights = np.array(given, dtype=float)
        else:
            rng = np.random.default_rng(31415)
            weights = rng.dirichlet(np.ones(n) * 1.2, size=n)
        side = min(0.7 * self.camera.frame_width,
                   0.5 * self.camera.frame_height)
        cell = side / n
        cells, labels = VGroup(), VGroup()
        for i in range(n):
            for j in range(n):
                sq = Square(side_length=cell, stroke_color=S.GRID,
                            stroke_width=1, fill_color=S.RED,
                            fill_opacity=float(weights[i][j]))
                sq.set_sheen(0.25, UP + LEFT)   # subtle tile depth
                sq.move_to([(j - (n - 1) / 2) * cell,
                            ((n - 1) / 2 - i) * cell, 0])
                cells.add(sq)
        for k, t in enumerate(toks):
            row = S.body(t, font_size=20, color=S.TEXT)
            row.next_to(cells[k * n], LEFT, buff=0.25)
            col = S.body(t, font_size=20, color=S.TEXT)
            col.next_to(cells[k], UP, buff=0.25)
            labels.add(row, col)
        grid = VGroup(cells, labels)
        self.fit(grid)
        S.ig_safe_shift(grid, self.fmt)
        # backing card + shadow = the heatmap floats above the frame
        card = RoundedRectangle(
            width=cells.width + 0.25, height=cells.height + 0.25,
            corner_radius=0.08, fill_color=S.GRID, fill_opacity=0.35,
            stroke_width=0).move_to(cells.get_center())
        card_g = VGroup(S.shadow(card, offset=0.1, opacity=0.5), card)
        self.play(FadeIn(labels), run_time=0.8)
        self.play(FadeIn(card_g, shift=OUT * 3),
                  FadeIn(cells, shift=OUT * 3, lag_ratio=0.05), run_time=2)
        focus = self.spec.get("focus_row")
        if focus is not None and 0 <= int(focus) < n:
            # hold on one query row: outline it, then flag its strongest key
            i = int(focus)
            row_cells = VGroup(*[cells[i * n + j] for j in range(n)])
            box = SurroundingRectangle(row_cells, color=S.BLUE, buff=0.02)
            self.play(Create(box), run_time=0.6)
            j = int(np.argmax(weights[i]))
            self.play(Indicate(cells[i * n + j], color=S.YELLOW,
                               scale_factor=1.25), run_time=1.0)
        else:
            # highlight strongest attention per row
            for i in range(n):
                j = int(np.argmax(weights[i]))
                self.play(Indicate(cells[i * n + j], color=S.YELLOW),
                          run_time=0.45)
        self.wait(float(self.spec.get("duration", 10)) / 4)


class BulletPoints(TMOTScene):
    """spec: title, points (list of strings). Staged reveal."""
    spec = {"title": "", "points": ["Point one"]}

    def construct(self):
        self.add_watermark()
        if self.spec.get("title"):
            self.play(FadeIn(self.title_bar(self.spec["title"])), run_time=0.6)
        size = 26 if self.is_reel else 30
        # Tufte: no bullet glyphs — spacing and the staged reveal do the work
        pts = VGroup(*[
            S.body(p, font_size=size) for p in self.spec["points"]
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.55)
        self.fit(pts)
        S.ig_safe_shift(pts, self.fmt)
        for p in pts:
            self.play(FadeIn(p, shift=OUT * 1.8), run_time=0.7)
            self.wait(0.5)
        self.wait(float(self.spec.get("duration", 8)) / 4)


class EquationAnnotated(TMOTScene):
    """Reveal one equation built from PARTS, color-code chosen parts, then
    draw a labelled callout arrow to one part. Building from an explicit list
    of latex chunks (MathTex(*parts)) is far more robust than substring
    isolation on nested \\frac / \\left(\\right) equations.
    spec:
      parts        — list of latex chunks; part k is one colorable submobject
      color_idx    — list of part indices to color
      color_names  — parallel list of color names ('blue','yellow','green',
                     'red','purple') for each color_idx entry
      callout_idx  — optional int: part index the arrow points to
      callout_text — plain-english label for the callout"""
    spec = {"title": "", "parts": ["y", "=", "mx", "+", "b"],
            "color_idx": [], "color_names": [],
            "callout_idx": None, "callout_text": ""}

    _CMAP = {"blue": S.BLUE, "yellow": S.YELLOW, "green": S.GREEN,
             "red": S.RED, "purple": S.PURPLE, "text": S.TEXT}

    def construct(self):
        self.add_watermark()
        if self.spec.get("title"):
            self.play(FadeIn(self.title_bar(self.spec["title"])), run_time=0.6)
        parts = list(self.spec.get("parts") or ["?"])
        eq = MathTex(*parts, color=S.TEXT)
        self.fit(eq, margin=0.9)
        S.ig_safe_shift(eq, self.fmt)
        self.play(WriteAnim(eq), run_time=1.8)
        self.wait(0.4)

        idxs = list(self.spec.get("color_idx") or [])
        names = list(self.spec.get("color_names") or [])
        for k, i in enumerate(idxs):
            if 0 <= int(i) < len(eq):
                col = self._CMAP.get(names[k] if k < len(names) else "yellow",
                                     S.YELLOW)
                self.play(eq[int(i)].animate.set_color(col), run_time=0.4)

        ci = self.spec.get("callout_idx")
        if (ci is not None and 0 <= int(ci) < len(eq)
                and self.spec.get("callout_text")):
            part = eq[int(ci)]
            note = S.body(self.spec["callout_text"], font_size=22, color=S.MUTED)
            note.next_to(eq, DOWN, buff=1.2)
            self.fit(note, margin=0.9)
            S.ig_safe_shift(note, self.fmt)
            arrow = Arrow(note.get_top(), part.get_bottom(),
                          color=S.MUTED, buff=0.15, stroke_width=3)
            self.play(Indicate(part, color=S.YELLOW), run_time=0.6)
            self.play(FadeIn(note), Create(arrow), run_time=1.0)
        if self.spec.get("shimmer", S.style_flag("equation_shimmer", True)):
            self.shimmer_in(eq)
        self.wait(float(self.spec.get("duration", 10)) / 4)


class MatrixMultiply(TMOTScene):
    """Show A x B = C with real numbers; optionally walk one row's dot products.
    spec:
      a, b       — 2D lists (the multiplicands); C = A@B is computed
      a_label, b_label, c_label — latex names shown above each matrix
      decimals   — 0 for integers, else decimal places
      highlight_row — int: outline that row of A and sweep B's columns,
                      flashing each resulting entry of C (the dot-product story)"""
    spec = {"title": "", "a": [[1, 0], [0, 1]], "b": [[1], [1]],
            "a_label": "A", "b_label": "B", "c_label": "C",
            "decimals": 0, "highlight_row": None}

    def _mk(self, mat, decimals):
        if decimals == 0:
            return IntegerMatrix(np.round(mat).astype(int).tolist(),
                                 h_buff=1.3)
        return DecimalMatrix(
            mat.tolist(), h_buff=1.6,
            element_to_mobject_config={"num_decimal_places": decimals})

    def construct(self):
        self.add_watermark()
        if self.spec.get("title"):
            self.play(FadeIn(self.title_bar(self.spec["title"])), run_time=0.6)
        A = np.array(self.spec["a"], dtype=float)
        B = np.array(self.spec["b"], dtype=float)
        C = A @ B
        dec = int(self.spec.get("decimals", 0))
        MA, MB, MC = self._mk(A, dec), self._mk(B, dec), self._mk(C, dec)
        for m in (MA, MB, MC):
            m.get_entries().set_color(S.TEXT)
        times, eq = MathTex(r"\times", color=S.MUTED), MathTex("=", color=S.MUTED)
        row = VGroup(MA, times, MB, eq, MC).arrange(RIGHT, buff=0.35)

        def lab(txt, target, color):
            m = MathTex(txt, color=color).scale(0.8)
            m.next_to(target, UP, buff=0.3)
            return m
        labels = VGroup(
            lab(self.spec.get("a_label", "A"), MA, S.BLUE),
            lab(self.spec.get("b_label", "B"), MB, S.YELLOW),
            lab(self.spec.get("c_label", "C"), MC, S.GREEN),
        )
        group = VGroup(row, labels)
        self.fit(group, margin=0.92)
        S.ig_safe_shift(group, self.fmt)

        # shadows after fit() so the offset matches the final scale
        sh = {m: S.shadow(m, offset=0.05, opacity=0.4) for m in (MA, MB, MC)}
        self.play(FadeIn(VGroup(sh[MA], MA), shift=OUT * 3),
                  FadeIn(VGroup(sh[MB], MB), shift=OUT * 3),
                  WriteAnim(times), run_time=1.0)
        self.play(FadeIn(labels[0]), FadeIn(labels[1]), run_time=0.5)
        self.play(WriteAnim(eq), FadeIn(VGroup(sh[MC], MC), shift=OUT * 3),
                  FadeIn(labels[2]), run_time=1.0)

        hr = self.spec.get("highlight_row")
        if hr is not None and 0 <= int(hr) < len(A):
            i = int(hr)
            arow = SurroundingRectangle(MA.get_rows()[i], color=S.BLUE, buff=0.1)
            self.play(Create(arow), run_time=0.6)
            crow = MC.get_rows()[i]
            cols = MB.get_columns()
            for j in range(len(cols)):
                bcol = SurroundingRectangle(cols[j], color=S.YELLOW, buff=0.1)
                self.play(Create(bcol), run_time=0.4)
                self.play(Indicate(crow[j], color=S.GREEN, scale_factor=1.4),
                          run_time=0.5)
                self.play(FadeOut(bcol), run_time=0.25)
            self.play(FadeOut(arow), run_time=0.4)
        self.wait(float(self.spec.get("duration", 12)) / 4)


class SoftmaxBuild(TMOTScene):
    """Mechanically build softmax over one row of scores as growing bars:
    raw score -> exponentiate -> normalize to probabilities that sum to 1.
    spec:
      scores  — list of numbers (a single row, e.g. scaled QK^T for one token)
      labels  — token names under each bar
      decimals — decimals on the probability labels (default 2)"""
    spec = {"title": "", "scores": [2.0, 1.0, 0.0],
            "labels": ["a", "b", "c"], "decimals": 2}

    def construct(self):
        self.add_watermark()
        title = None
        if self.spec.get("title"):
            title = self.title_bar(self.spec["title"])
            self.play(FadeIn(title), run_time=0.6)
        raw = np.array(self.spec["scores"], dtype=float)
        toks = self.spec.get("labels", [str(i) for i in range(len(raw))])
        ex = np.exp(raw - raw.max())
        prob = ex / ex.sum()
        dec = int(self.spec.get("decimals", 2))

        formula = MathTex(
            r"\mathrm{softmax}(x_i)=\frac{e^{x_i}}{\sum_j e^{x_j}}",
            color=S.TEXT).scale(0.8)
        self.fit(formula, margin=0.85)
        if title is not None:
            formula.next_to(title, DOWN, buff=0.45)
            formula.set_x(0)   # title is a top-left running head now
        else:
            formula.to_edge(UP, buff=1.4 if self.is_reel else 0.9)
        self.play(WriteAnim(formula), run_time=1.4)

        n = len(raw)
        span = min(0.8 * self.camera.frame_width, 6.0)
        bw = span / (n * 1.8)
        xs = np.linspace(-span / 2 + bw, span / 2 - bw, n)
        base_y = -1.8
        Hmax = 2.4

        def heights(vals):
            v = np.array(vals, dtype=float)
            return v / v.max() * Hmax

        bars, tlabels = VGroup(), VGroup()
        vlabels = []              # plain list: entries get swapped per stage
        hs = heights(raw)
        for k in range(n):
            bar = Rectangle(width=bw, height=max(hs[k], 0.05),
                            fill_color=S.BLUE, fill_opacity=0.92,
                            stroke_width=0)
            bar.set_sheen(0.45, UP)   # lit-from-above depth
            bar.move_to([xs[k], base_y + hs[k] / 2, 0])
            vlab = MathTex(f"{raw[k]:.2f}", color=S.TEXT).scale(0.55)
            vlab.move_to([xs[k], base_y + hs[k] + 0.3, 0])
            tlab = S.body(toks[k], font_size=22, color=S.MUTED)
            tlab.move_to([xs[k], base_y - 0.35, 0])
            bars.add(bar)
            vlabels.append(vlab)
            tlabels.add(tlab)
        stage_lab = [S.body("scaled scores", font_size=24, color=S.MUTED)]
        stage_lab[0].move_to([0, base_y - 1.1, 0])
        # shift everything into the IG safe band via a throwaway wrapper
        S.ig_safe_shift(VGroup(bars, tlabels, stage_lab[0], *vlabels),
                        self.fmt)
        self.play(FadeIn(bars, shift=OUT * 2.5, lag_ratio=0.1),
                  *[FadeIn(v) for v in vlabels],
                  FadeIn(tlabels), FadeIn(stage_lab[0]),
                  run_time=1.2)
        self.wait(0.6)

        def restage(vals, texts, caption, color):
            # cross-fade label swaps (FadeTransform): a point-morph Transform
            # between unrelated glyphs reads as garbled mid-animation
            hs2 = heights(vals)
            anims = []
            new_labs = []
            for k in range(n):
                new_lab = MathTex(texts[k], color=S.TEXT).scale(0.55)
                new_lab.move_to([xs[k], base_y + hs2[k] + 0.3, 0])
                S.ig_safe_shift(new_lab, self.fmt)
                new_labs.append(new_lab)
                anims.append(FadeTransform(vlabels[k], new_lab))
                anims.append(bars[k].animate.stretch_to_fit_height(
                    max(hs2[k], 0.05)).move_to(
                    [xs[k], bars[k].get_bottom()[1] + hs2[k] / 2, 0])
                    .set_color(color))
            new_stage = S.body(caption, font_size=24, color=S.MUTED)
            new_stage.move_to([0, base_y - 1.1, 0])
            S.ig_safe_shift(new_stage, self.fmt)
            anims.append(FadeTransform(stage_lab[0], new_stage))
            self.play(*anims, run_time=1.5)
            vlabels[:] = new_labs
            stage_lab[0] = new_stage
            self.wait(0.6)

        restage(ex, [f"e^{{{raw[k]:.1f}}}" for k in range(n)],
                "exponentiate", S.YELLOW)
        restage(prob, [f"{prob[k]:.{dec}f}" for k in range(n)],
                "normalize  (sum = 1)", S.GREEN)
        peak = int(np.argmax(prob))
        self.play(Indicate(bars[peak], color=S.GREEN, scale_factor=1.1),
                  Indicate(tlabels[peak], color=S.GREEN), run_time=1.0)
        self.wait(float(self.spec.get("duration", 14)) / 4)


class MultiHead(TMOTScene):
    """Schematic of multi-head attention: h heads run in parallel, their
    outputs concatenate, then a linear projection W^O produces the result.
    spec: n_heads (int)."""
    spec = {"title": "", "n_heads": 3}

    def construct(self):
        self.add_watermark()
        if self.spec.get("title"):
            self.play(FadeIn(self.title_bar(self.spec["title"])), run_time=0.6)
        h = int(self.spec.get("n_heads", 3))
        heads = VGroup()
        for k in range(h):
            box = RoundedRectangle(width=1.4, height=1.0, corner_radius=0.12,
                                   stroke_color=ACCENTS[k % len(ACCENTS)],
                                   fill_color=ACCENTS[k % len(ACCENTS)],
                                   fill_opacity=0.12, stroke_width=2)
            lab = MathTex(rf"\mathrm{{head}}_{{{k+1}}}",
                          color=ACCENTS[k % len(ACCENTS)]).scale(0.5)
            lab.move_to(box.get_center())
            heads.add(VGroup(S.shadow(box, 0.06, 0.5), box, lab))
        heads.arrange(RIGHT, buff=0.5)

        concat = RoundedRectangle(width=heads.width, height=0.7,
                                  corner_radius=0.1, stroke_color=S.TEXT,
                                  fill_color=S.GRID, fill_opacity=0.2,
                                  stroke_width=2)
        concat_lab = S.body("Concat", font_size=22, color=S.TEXT)
        concat_lab.move_to(concat.get_center())
        concat_g = VGroup(S.shadow(concat, 0.06, 0.5), concat, concat_lab)
        concat_g.next_to(heads, DOWN, buff=1.0)

        proj = RoundedRectangle(width=2.2, height=0.7, corner_radius=0.1,
                                stroke_color=S.PURPLE, fill_color=S.PURPLE,
                                fill_opacity=0.15, stroke_width=2)
        proj_lab = MathTex(r"W^{O}", color=S.PURPLE).scale(0.7)
        proj_lab.move_to(proj.get_center())
        proj_g = VGroup(S.shadow(proj, 0.06, 0.5), proj, proj_lab)
        proj_g.next_to(concat_g, DOWN, buff=0.9)

        diagram = VGroup(heads, concat_g, proj_g)
        self.fit(diagram, margin=0.92)
        S.ig_safe_shift(diagram, self.fmt)

        self.play(FadeIn(heads, shift=OUT * 3, lag_ratio=0.0),
                  run_time=1.0)  # parallel arrival from depth
        self.play(*[Indicate(hd, color=S.YELLOW) for hd in heads], run_time=0.8)
        down = VGroup(*[Arrow(hd.get_bottom(), concat.get_top(), buff=0.1,
                              color=S.MUTED, stroke_width=3) for hd in heads])
        self.play(*[Create(a) for a in down], run_time=0.8)
        self.play(FadeIn(concat_g), run_time=0.6)
        a2 = Arrow(concat.get_bottom(), proj.get_top(), buff=0.1,
                   color=S.MUTED, stroke_width=3)
        self.play(Create(a2), FadeIn(proj_g), run_time=0.8)
        self.wait(float(self.spec.get("duration", 12)) / 4)


class TokensToVectors(TMOTScene):
    """The text→numbers abstraction pipeline, SHOWN: a sentence splits into
    tokens, each token becomes a tiny vector pointing a seeded-random
    direction (a "spin", 1 of 360°), and the spins stack into the matrix X.
    Random directions are the honest picture of embeddings at
    initialization — training is what later rotates them into meaning.

    Declutter by design: tokens dim once their spins exist; spins are
    absorbed into the matrix rows. At most one abstraction level is bright
    at a time.

    spec:
      text        — sentence/paragraph (split on spaces)
      max_toks    — tokens visualized; the rest collapse into "… +k" (def 6)
      seed        — rng seed for directions (default 7; keep per-video so
                    re-renders are identical)
      decimals    — decimals for the matrix components (default 1)
      show_matrix — stack spins into X at the end (default true)
    """
    spec = {"title": "", "text": "the river bank held the money",
            "max_toks": 6, "seed": 7, "decimals": 1, "show_matrix": True}

    def construct(self):
        self.add_watermark()
        if self.spec.get("title"):
            self.play(FadeIn(self.title_bar(self.spec["title"])), run_time=0.6)
        words = str(self.spec.get("text", "")).split()
        n_max = max(1, int(self.spec.get("max_toks", 6)))
        shown = words[:n_max]
        extra = len(words) - len(shown)
        rng = np.random.default_rng(int(self.spec.get("seed", 7)))

        # 1) raw text, tokenized
        chips = VGroup(*[S.body(w, font_size=26) for w in shown])
        if extra > 0:
            chips.add(S.body(f"... +{extra}", font_size=26, color=S.MUTED))
        chips.arrange(RIGHT, buff=0.35)
        self.fit(chips, margin=0.9)
        S.ig_safe_shift(chips, self.fmt)
        chips.shift(UP * 1.7)
        self.play(WriteAnim(chips), run_time=1.2)
        self.wait(0.5)

        # 2) each token -> a spin: unit-ish vector, random direction
        angles = rng.uniform(0.0, 2 * np.pi, size=len(shown))
        arrows = VGroup()
        for chip, th in zip(chips, angles):
            v = 0.55 * np.array([np.cos(th), np.sin(th), 0.0])
            a = Arrow(ORIGIN, v, buff=0, stroke_width=4,
                      max_tip_length_to_length_ratio=0.35, color=S.BLUE)
            a.move_to(chip.get_center() + DOWN * 1.5)
            arrows.add(a)
        # spins grow out of their tokens; tokens dim (clutter budget)
        self.play(*[FadeTransform(c.copy(), a)
                    for c, a in zip(chips, arrows)],
                  chips.animate.set_opacity(0.35),
                  run_time=1.4)
        self.wait(0.7)

        if not self.spec.get("show_matrix", True):
            self.wait(float(self.spec.get("duration", 12)) / 4)
            return

        # 3) spins stack into the matrix X (components = the directions)
        dec = int(self.spec.get("decimals", 1))
        rows = [[round(float(np.cos(th)), dec), round(float(np.sin(th)), dec)]
                for th in angles]
        M = DecimalMatrix(
            rows, v_buff=0.7,
            element_to_mobject_config={"num_decimal_places": dec})
        M.get_entries().set_color(S.TEXT)
        lab = MathTex(r"X \in \mathbb{R}^{n \times d}", color=S.BLUE).scale(0.8)
        M.scale(0.8)
        grp = VGroup(M, lab)
        lab.next_to(M, RIGHT, buff=0.5)
        self.fit(grp, margin=0.9)
        S.ig_safe_shift(grp, self.fmt)
        grp.shift(DOWN * 1.2)
        m_rows = M.get_rows()
        self.play(*[FadeTransform(arrows[i], m_rows[i])
                    for i in range(len(shown))],
                  FadeIn(M.get_brackets()),
                  run_time=1.6)
        self.play(FadeIn(lab, shift=OUT * 1.5), run_time=0.7)
        self.wait(float(self.spec.get("duration", 14)) / 4)


class GraphMorph(TMOTScene):
    """Curve evolution on PERSISTENT axes: function morphs into function —
    the plotted counterpart of EquationSteps. The axes are the carry object;
    the curve is one object evolving, never popping. Built for probability
    distribution shifts (prior→posterior, widening Gaussians), activation/
    saturation stories, potentials, and any quant/physics curve that changes
    under a parameter or an operation.

    spec:
      functions — list of python exprs in x (numpy as np), morphed in order
      labels    — optional latex per stage (curve label, cross-faded)
      captions  — optional plain-text move names under the axes
                  ("condition on the data", "increase sigma"); "" skips
      colors    — optional color names per stage ('blue','yellow','green',
                  'red','purple'); default: blue -> purple gradient
      x_range, y_range — axes ranges
      fill      — bool: shade the area under the curve (morphs along;
                  for probability stories the constant area IS the point)
    """
    spec = {"title": "", "functions": ["np.exp(-x**2/2)"],
            "labels": [], "captions": [], "colors": [],
            "x_range": [-4, 4], "y_range": [0, 1], "fill": False}

    _CMAP = {"blue": S.BLUE, "yellow": S.YELLOW, "green": S.GREEN,
             "red": S.RED, "purple": S.PURPLE}

    def construct(self):
        self.add_watermark()
        if self.spec.get("title"):
            self.play(FadeIn(self.title_bar(self.spec["title"])), run_time=0.6)
        xr, yr = self.spec["x_range"], self.spec["y_range"]
        w = 0.85 * self.camera.frame_width
        h = 0.55 * self.camera.frame_height
        axes = Axes(
            x_range=[*xr, (xr[1] - xr[0]) / 4],
            y_range=[*yr, (yr[1] - yr[0]) / 4],
            x_length=w, y_length=h, tips=False,
            axis_config={"color": S.GRID, "stroke_width": 1.5},
        )
        S.ig_safe_shift(axes, self.fmt)   # shift axes ONCE; plots follow

        exprs = list(self.spec.get("functions") or ["x"])
        labels = list(self.spec.get("labels") or [])
        captions = list(self.spec.get("captions") or [])
        colors = list(self.spec.get("colors") or [])
        use_fill = bool(self.spec.get("fill"))

        def stage(k):
            fn = eval("lambda x: " + exprs[k], {"np": np})  # noqa: S307
            c = axes.plot(fn, stroke_width=5)
            if k < len(colors) and colors[k] in self._CMAP:
                c.set_color(self._CMAP[colors[k]])
            else:
                c.set_color_by_gradient(S.BLUE, S.PURPLE)
            area = axes.get_area(c, opacity=0.25) if use_fill else None
            lab = None
            if k < len(labels) and labels[k]:
                lab = MathTex(labels[k], color=c.get_color()).scale(0.8)
                lab.next_to(c, UP, buff=0.2)
                self.fit(lab)
            cap = None
            if k < len(captions) and captions[k]:
                cap = S.body(captions[k], font_size=22, color=S.MUTED)
                cap.next_to(axes, DOWN, buff=0.45)
                self.fit(cap, margin=0.9)
            return c, area, lab, cap

        curve, area, lab, cap = stage(0)
        self.play(Create(axes), run_time=1)
        self.play(Create(curve), run_time=1.6)
        intro = [FadeIn(m) for m in (area, lab, cap) if m is not None]
        if intro:
            self.play(*intro, run_time=0.6)
        self.wait(0.8)

        for k in range(1, len(exprs)):
            new_curve, new_area, new_lab, new_cap = stage(k)
            anims = [Transform(curve, new_curve)]
            if area is not None and new_area is not None:
                anims.append(Transform(area, new_area))
            # L-11: text swaps cross-fade, never point-morph
            for old, new in ((lab, new_lab), (cap, new_cap)):
                if old is not None and new is not None:
                    anims.append(FadeTransform(old, new))
                elif old is not None:
                    anims.append(FadeOut(old))
                elif new is not None:
                    anims.append(FadeIn(new))
            self.play(*anims, run_time=1.8)
            lab, cap = new_lab, new_cap
            self.wait(0.8)

        self.wait(float(self.spec.get("duration", 12)) / 4)


class EquationSteps(TMOTScene):
    """Derivation chain: successive equations MORPH into each other via
    TransformMatchingTex, so one logical chain reads as a single object
    evolving — never popping (visual-storytelling skill: equation
    choreography). Supports the two-track rule (dimmed general form held
    above the working chain) and symbol identity (color_map applied to
    every step, so a symbol keeps its color across the whole chain).

    Authoring rule: shared subexpressions must be BYTE-IDENTICAL between
    consecutive steps — TransformMatchingTex matches isolated tex
    substrings; matching is designed at writing time.

    spec:
      steps     — list of latex strings, in derivation order (>= 1)
      labels    — optional parallel list of short move names shown under the
                  chain ("take the variance"); "" skips that step's label
      anchor    — optional latex kept dimmed at the top throughout
                  (the general form / assumptions — the honest track)
      color_map — optional {tex_substring: color_name} applied to anchor and
                  every step (registry colors; also improves matching, since
                  keys are isolated as submobjects)
      isolate   — optional extra substrings to isolate for better matching
    """
    spec = {"title": "", "steps": [r"a^2+b^2=c^2"], "labels": [],
            "anchor": "", "color_map": {}, "isolate": []}

    _CMAP = {"blue": S.BLUE, "yellow": S.YELLOW, "green": S.GREEN,
             "red": S.RED, "purple": S.PURPLE, "text": S.TEXT}

    def _make(self, tex, iso, cmap):
        m = MathTex(tex, color=S.TEXT,
                    substrings_to_isolate=iso if iso else None)
        for sub, col in cmap.items():
            m.set_color_by_tex(sub, col)
        self.fit(m, margin=0.9)
        S.ig_safe_shift(m, self.fmt)
        return m

    def construct(self):
        self.add_watermark()
        title = None
        if self.spec.get("title"):
            title = self.title_bar(self.spec["title"])
            self.play(FadeIn(title), run_time=0.6)

        cmap = {k: self._CMAP.get(v, S.YELLOW)
                for k, v in (self.spec.get("color_map") or {}).items()}
        iso = list(cmap) + list(self.spec.get("isolate") or [])

        # two-track rule: general form / assumptions dimmed on top
        anchor = None
        if self.spec.get("anchor"):
            anchor = self._make(self.spec["anchor"], iso, cmap).scale(0.7)
            anchor.set_opacity(0.45)
            if title is not None:
                anchor.next_to(title, DOWN, buff=0.4)
                anchor.set_x(0)
            else:
                anchor.to_edge(UP, buff=1.5 if self.is_reel else 1.0)
            self.play(FadeIn(anchor, shift=OUT * 1.5), run_time=0.8)

        steps = [self._make(t, iso, cmap)
                 for t in (self.spec.get("steps") or [r"?"])]
        labels = list(self.spec.get("labels") or [])

        def label_for(k, eq):
            if k >= len(labels) or not labels[k]:
                return None
            lab = S.body(labels[k], font_size=22, color=S.MUTED)
            lab.next_to(eq, DOWN, buff=0.9)
            self.fit(lab, margin=0.9)
            return lab

        eq = steps[0]
        lab = label_for(0, eq)
        self.play(WriteAnim(eq), run_time=1.6)
        if lab is not None:
            self.play(FadeIn(lab), run_time=0.5)
        self.wait(0.8)

        for k in range(1, len(steps)):
            new_eq = steps[k]
            anims = [TransformMatchingTex(eq, new_eq)]
            new_lab = label_for(k, new_eq)
            # L-11: cross-fade text swaps, never point-morph
            if lab is not None and new_lab is not None:
                anims.append(FadeTransform(lab, new_lab))
            elif lab is not None:
                anims.append(FadeOut(lab))
            elif new_lab is not None:
                anims.append(FadeIn(new_lab))
            self.play(*anims, run_time=1.6)
            eq, lab = new_eq, new_lab
            self.wait(0.8)

        self.play(Indicate(eq, color=S.YELLOW, scale_factor=1.06),
                  run_time=1.0)
        self.wait(float(self.spec.get("duration", 12)) / 4)


class BrandedIntro(TMOTScene):
    """Channel intro card (branding from channel.yaml). Rendered
    automatically by pipeline/render.py per branding.segments config —
    never listed in scenes.json."""
    spec = {}

    def construct(self):
        self.add_watermark()
        self.branded_intro()


class BrandedOutro(TMOTScene):
    """Channel outro/CTA card (branding from channel.yaml). Rendered
    automatically by pipeline/render.py per branding.segments config."""
    spec = {}

    def construct(self):
        self.add_watermark()
        self.branded_outro()


class TableReveal(TMOTScene):
    """Tufte-style table: header row + hairline rule, data rows staged in
    one by one — no gridline cage, alignment and spacing carry the eye.
    Cells are plain text (for math tables use matrix_multiply /
    equation_steps instead).
    spec:
      headers    — list of column header strings
      rows       — list of rows (each a list of cell strings, same length)
      highlight  — optional [row, col] (0-indexed into rows) to box after
                   the reveal
      align      — optional 'left' | 'center' (default center)
    """
    spec = {"title": "", "headers": ["A", "B"], "rows": [["1", "2"]],
            "highlight": None, "align": "center"}

    def construct(self):
        self.add_watermark()
        if self.spec.get("title"):
            self.play(FadeIn(self.title_bar(self.spec["title"])), run_time=0.6)
        headers = [str(h) for h in self.spec["headers"]]
        rows = [[str(c) for c in r] for r in self.spec["rows"]]
        n_cols = len(headers)
        size_h = 24 if self.is_reel else 28
        size_c = 22 if self.is_reel else 26

        head = [S.body(h, font_size=size_h, color=S.BLUE) for h in headers]
        body = [[S.body(c, font_size=size_c, color=S.TEXT) for c in r]
                for r in rows]

        # column widths from the widest cell in each column
        pad = 0.55
        col_w = [max([head[j].width]
                     + [body[i][j].width for i in range(len(body))]) + pad
                 for j in range(n_cols)]
        total_w = sum(col_w)
        x_left = -total_w / 2
        col_x = []          # column anchor (center or left edge + pad/2)
        acc = x_left
        for j in range(n_cols):
            col_x.append(acc + col_w[j] / 2)
            acc += col_w[j]
        left_align = self.spec.get("align") == "left"

        row_h = 0.62 if self.is_reel else 0.7
        top_y = 0.5 * (len(rows)) * row_h + 0.6

        def place(mobj, j, y):
            if left_align:
                mobj.move_to([col_x[j] - col_w[j] / 2 + pad / 2
                              + mobj.width / 2, y, 0])
            else:
                mobj.move_to([col_x[j], y, 0])
            return mobj

        header_g = VGroup(*[place(head[j], j, top_y) for j in range(n_cols)])
        rule = S.hairline(total_w)
        rule.move_to([0, top_y - 0.38, 0])
        row_groups = []
        for i, r in enumerate(body):
            y = top_y - 0.85 - i * row_h
            row_groups.append(VGroup(*[place(r[j], j, y)
                                       for j in range(n_cols)]))

        table = VGroup(header_g, rule, *row_groups)
        self.fit(table, margin=0.9)
        S.ig_safe_shift(table, self.fmt)

        self.play(FadeIn(header_g, shift=OUT * 2), Create(rule), run_time=0.9)
        for rg in row_groups:
            self.play(FadeIn(rg, shift=OUT * 1.5), run_time=0.55)
        hl = self.spec.get("highlight")
        if hl is not None:
            i, j = int(hl[0]), int(hl[1])
            if 0 <= i < len(body) and 0 <= j < n_cols:
                box = SurroundingRectangle(row_groups[i][j], color=S.YELLOW,
                                           buff=0.12, stroke_width=2.5)
                self.play(Create(box), run_time=0.7)
                self.play(Indicate(row_groups[i][j], color=S.YELLOW),
                          run_time=0.8)
        self.wait(float(self.spec.get("duration", 10)) / 4)


SCENE_TYPES = {
    "concept_title": ConceptTitle,
    "equation_reveal": EquationReveal,
    "equation_annotated": EquationAnnotated,
    "equation_steps": EquationSteps,
    "transform": TransformExplainer,
    "graph": GraphScene,
    "graph_morph": GraphMorph,
    "tokens_to_vectors": TokensToVectors,
    "neural_net": NeuralNet,
    "attention_matrix": AttentionMatrix,
    "matrix_multiply": MatrixMultiply,
    "softmax_build": SoftmaxBuild,
    "multi_head": MultiHead,
    "table": TableReveal,
    "bullet_points": BulletPoints,
}
