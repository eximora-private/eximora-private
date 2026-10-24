#!/usr/bin/env python3
"""Generates the animated Material 3 Expressive SVGs for the profile README.

Edit CONFIG below, then run:  python3 generate.py
Writes assets/light/*.svg and assets/dark/*.svg. Pure SVG (CSS + SMIL) — animates directly on GitHub.
"""
import math
from html import escape
from pathlib import Path

CONFIG = {
    "greeting": "hi, i'm",
    "name": "eximora",
    "tagline": "developer · linux enthusiast · detail obsessed",
    "verb": "I build",
    "words": ["tools", "systems", "interfaces", "automations"],
    "cards": [
        ("build", "Software and tools that", "feel fast and stay simple."),
        ("tinker", "Linux, reproducible setups", "and everything under the hood."),
        ("learn", "Always exploring something", "new — one commit at a time."),
    ],
    "outro": "thanks for stopping by",
}

# Material 3 baseline tonal palettes
THEMES = {
    "light": dict(surface="#FEF7FF", container="#F3EDF7", container_high="#ECE6F0", on_surface="#1D1B20",
                  on_variant="#49454F", outline="#CAC4D0", primary="#6750A4", on_primary="#FFFFFF",
                  primary_c="#EADDFF", on_primary_c="#4F378B", secondary_c="#E8DEF8", on_secondary_c="#4A4458",
                  tertiary="#7D5260", tertiary_c="#FFD8E4"),
    "dark": dict(surface="#141218", container="#211F26", container_high="#2B2930", on_surface="#E6E0E9",
                 on_variant="#CAC4D0", outline="#49454F", primary="#D0BCFF", on_primary="#381E72",
                 primary_c="#4F378B", on_primary_c="#EADDFF", secondary_c="#4A4458", on_secondary_c="#E8DEF8",
                 tertiary="#EFB8C8", tertiary_c="#633B48"),
}

OUT = Path(__file__).parent / "assets"
SANS = "'Google Sans Flex', 'Google Sans', 'Roboto Flex', Roboto, Inter, system-ui, sans-serif"
SPRING = "cubic-bezier(.34, 1.56, .64, 1)"  # overshooting spatial spring
EMPH = ".2 0 0 1"  # emphasized easing (SMIL keySplines can't overshoot)


# ---------- shapes: every shape uses the same point count, so any two can morph into each other ----------
N = 180


def radius(kind, t):
    if kind == "circle":
        return 1.0
    if kind == "cookie":
        return 1 + .07 * math.cos(9 * t)
    if kind == "flower":
        return .92 + .14 * math.cos(6 * t)
    if kind == "clover":
        return .9 + .16 * math.cos(4 * t)
    if kind == "burst":
        return 1 + .05 * math.cos(12 * t)
    if kind == "pentagon":
        return .96 + .08 * math.cos(5 * t)
    if kind == "squircle":
        c, s = abs(math.cos(t)), abs(math.sin(t))
        return .9 * (c ** 4 + s ** 4) ** -.25
    raise ValueError(kind)


def shape(kind, cx, cy, r):
    pts = []
    for i in range(N):
        t = 2 * math.pi * i / N
        k = r * radius(kind, t)
        pts.append(f"{cx + k * math.cos(t):.1f} {cy + k * math.sin(t):.1f}")
    return "M" + " L".join(pts) + "Z"


def morph(kinds, cx, cy, r, hold, move):
    """SMIL animate cycling through shapes, holding each one, with emphasized easing between."""
    seq = kinds + kinds[:1]
    step = hold + move
    total = step * len(kinds)
    values, times, splines = [], [], []
    for i, k in enumerate(seq):
        d = shape(k, cx, cy, r)
        if i == 0:
            values += [d]; times += [0]
        else:
            values += [d]; times += [(i * step) / total]; splines += [EMPH]
        if i < len(kinds):
            values += [d]; times += [(i * step + hold) / total]; splines += ["0 0 1 1"]
    return (f'<animate attributeName="d" dur="{total}s" repeatCount="indefinite" calcMode="spline" '
            f'values="{";".join(values)}" keyTimes="{";".join(f"{t:.4f}" for t in times)}" keySplines="{";".join(splines)}"/>')


def spin(cx, cy, dur, reverse=False):
    a, b = (360, 0) if reverse else (0, 360)
    return (f'<animateTransform attributeName="transform" type="rotate" from="{a} {cx} {cy}" to="{b} {cx} {cy}" '
            f'dur="{dur}s" repeatCount="indefinite"/>')


# ---------- assets ----------
def header(c):
    W, H = 1200, 440
    cfg = CONFIG
    x = 88
    fs_word, line_h = 28, 64
    words = cfg["words"]
    verb_w = len(cfg["verb"]) * 15.5
    pill_x = x + verb_w + 14
    widths = [len(w) * 16.5 + 56 for w in words]

    # rotating words: hold, then spring to the next one
    n = len(words)
    seg = 100 / n
    frames = []
    for i in range(n):
        frames.append(f"{i * seg:.2f}% {{ transform: translateY({-i * line_h}px); animation-timing-function: linear; }}")
        frames.append(f"{(i + 1) * seg - 9:.2f}% {{ transform: translateY({-i * line_h}px); animation-timing-function: {SPRING}; }}")
    frames.append(f"100% {{ transform: translateY({-n * line_h}px); }}")
    cycle = n * 2.4
    w_values, w_times, w_splines = [], [], []
    for i in range(n + 1):
        w = widths[i % n]
        if i == 0:
            w_values += [w]; w_times += [0]
        else:
            w_values += [w]; w_times += [i / n]; w_splines += [EMPH]
        if i < n:
            w_values += [w]; w_times += [((i + 1) * seg - 9) / 100]; w_splines += ["0 0 1 1"]
    stack = "".join(
        f'<text x="{pill_x + 28}" y="{352 + i * line_h}" class="word">{escape(w)}</text>'
        for i, w in enumerate(words + words[:1])
    )
    chip_w = len(cfg["greeting"]) * 9.5 + 40
    sx, sy = 920, 220

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>
  text {{ font-family: {SANS}; }}
  .in {{ opacity: 0; animation: enter .9s {SPRING} forwards; }}
  @keyframes enter {{ from {{ opacity: 0; transform: translateY(24px); }} to {{ opacity: 1; transform: none; }} }}
  .pop {{ transform-box: fill-box; transform-origin: center; animation: pop 1.1s {SPRING} both; }}
  @keyframes pop {{ from {{ transform: scale(.2); opacity: 0; }} to {{ transform: scale(1); opacity: 1; }} }}
  .d1 {{ animation-delay: .1s; }} .d2 {{ animation-delay: .22s; }} .d3 {{ animation-delay: .34s; }} .d4 {{ animation-delay: .46s; }} .d5 {{ animation-delay: .6s; }}
  .name {{ font-size: 112px; font-weight: 700; letter-spacing: -3px; fill: {c['on_surface']}; }}
  .tag {{ font-size: 24px; fill: {c['on_variant']}; }}
  .verb {{ font-size: {fs_word}px; font-weight: 500; fill: {c['on_surface']}; }}
  .chip {{ font-size: 18px; font-weight: 500; fill: {c['on_secondary_c']}; }}
  .word {{ font-size: {fs_word}px; font-weight: 600; fill: {c['on_primary']}; }}
  .stack {{ animation: words {cycle}s infinite; }}
  @keyframes words {{ {' '.join(frames)} }}
  .float {{ animation: float 6s ease-in-out infinite alternate; }}
  @keyframes float {{ to {{ transform: translateY(-14px); }} }}
</style>
<defs>
  <clipPath id="pill"><rect x="{pill_x}" y="{352 - 36}" height="{fs_word + 22}" rx="25" width="{widths[0]}">
    <animate attributeName="width" dur="{cycle}s" repeatCount="indefinite" calcMode="spline"
      values="{';'.join(f'{w:.0f}' for w in w_values)}" keyTimes="{';'.join(f'{t:.4f}' for t in w_times)}" keySplines="{';'.join(w_splines)}"/></rect></clipPath>
  <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="2" fill="{c['outline']}"/></pattern>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="56"/></clipPath>
</defs>

<g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="{c['container']}"/>
  <rect x="700" y="0" width="500" height="{H}" fill="url(#dots)" opacity=".55"/>

  <g class="pop d2"><path fill="{c['primary_c']}">{morph(['cookie', 'flower', 'squircle', 'clover', 'burst', 'pentagon'], sx, sy, 150, 2.2, .9)}{spin(sx, sy, 40)}</path></g>
  <g class="pop d4"><g class="float"><path fill="{c['tertiary_c']}" d="{shape('cookie', 1095, 92, 52)}">{spin(1095, 92, 18, True)}</path></g></g>
  <g class="pop d5"><g class="float" style="animation-delay:-3s"><path fill="{c['secondary_c']}" d="{shape('clover', 760, 360, 38)}">{spin(760, 360, 24)}</path></g></g>
  <g class="pop d3"><circle cx="{sx}" cy="{sy}" r="26" fill="{c['primary']}"/></g>

  <g class="in d1">
    <rect x="{x}" y="78" width="{chip_w}" height="38" rx="19" fill="{c['secondary_c']}"/>
    <text x="{x + 20}" y="103" class="chip">{escape(cfg['greeting'])}</text>
  </g>
  <text x="{x - 6}" y="222" class="name in d2">{escape(cfg['name'])}<tspan fill="{c['primary']}">.</tspan></text>
  <text x="{x}" y="270" class="tag in d3">{escape(cfg['tagline'])}</text>
  <g class="in d4">
    <text x="{x}" y="352" class="verb" textLength="{verb_w:.0f}" lengthAdjust="spacingAndGlyphs">{escape(cfg['verb'])}</text>
    <g clip-path="url(#pill)">
      <rect x="{pill_x}" y="300" width="{max(widths) + 20}" height="80" fill="{c['primary']}"/>
      <g class="stack">{stack}</g>
    </g>
  </g>
</g>
</svg>
"""


def cards(c):
    W, H, gap = 1200, 250, 24
    cw = (W - 2 * gap) / 3
    icons = [("cookie", c["primary_c"], c["primary"]), ("clover", c["tertiary_c"], c["tertiary"]),
             ("squircle", c["secondary_c"], c["on_secondary_c"])]
    out = []
    for i, ((title, l1, l2), (kind, fill, accent)) in enumerate(zip(CONFIG["cards"], icons)):
        x0 = i * (cw + gap)
        ix, iy = x0 + 70, 74
        out.append(f"""
<g class="card" style="animation-delay:{.12 * i:.2f}s">
  <rect x="{x0:.1f}" y="0" width="{cw:.1f}" height="{H}" rx="40" fill="{c['container']}"/>
  <path fill="{fill}" d="{shape(kind, ix, iy, 38)}">{spin(ix, iy, 16 + 6 * i, i % 2 == 1)}</path>
  <circle cx="{ix}" cy="{iy}" r="9" fill="{accent}"/>
  <text x="{x0 + 36:.1f}" y="164" class="title">{escape(title)}</text>
  <text x="{x0 + 36:.1f}" y="198" class="body">{escape(l1)}</text>
  <text x="{x0 + 36:.1f}" y="224" class="body">{escape(l2)}</text>
</g>""")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>
  text {{ font-family: {SANS}; }}
  .title {{ font-size: 30px; font-weight: 700; fill: {c['on_surface']}; letter-spacing: -.5px; }}
  .body {{ font-size: 19px; fill: {c['on_variant']}; }}
  .card {{ opacity: 0; animation: up 1s {SPRING} forwards; }}
  @keyframes up {{ from {{ opacity: 0; transform: translateY(40px); }} to {{ opacity: 1; transform: none; }} }}
</style>
{''.join(out)}
</svg>
"""


def divider(c):
    """M3 Expressive wavy progress indicator."""
    W, H, cy = 1200, 32, 16
    amp, wl, end = 5, 44, 860
    pts = [f"M{-wl} {cy}"]
    x = -wl
    while x < end + wl:
        pts.append(f"q{wl / 4} {-amp * 2} {wl / 2} 0 t{wl / 2} 0")
        x += wl
    wave = " ".join(pts)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs><clipPath id="a"><rect x="0" y="0" width="{end}" height="{H}"/></clipPath></defs>
<g clip-path="url(#a)">
  <path d="{wave}" fill="none" stroke="{c['primary']}" stroke-width="6" stroke-linecap="round">
    <animateTransform attributeName="transform" type="translate" from="0 0" to="{wl} 0" dur="1.4s" repeatCount="indefinite"/>
  </path>
</g>
<line x1="{end + 22}" y1="{cy}" x2="{W - 22}" y2="{cy}" stroke="{c['secondary_c']}" stroke-width="6" stroke-linecap="round"/>
<circle cx="{W - 6}" cy="{cy}" r="4" fill="{c['primary']}"/>
</svg>
"""


def footer(c):
    W, H, cx, cy = 1200, 190, 600, 72
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<circle cx="{cx}" cy="{cy}" r="52" fill="{c['primary_c']}"/>
<path fill="{c['primary']}">{morph(['burst', 'cookie', 'pentagon', 'flower', 'clover', 'squircle', 'circle'], cx, cy, 30, .35, .45)}{spin(cx, cy, 2.8)}</path>
<text x="{cx}" y="166" text-anchor="middle" style="font-family: {SANS}; font-size: 20px; font-weight: 500" fill="{c['on_variant']}">{escape(CONFIG['outro'])}</text>
</svg>
"""


if __name__ == "__main__":
    for theme, colors in THEMES.items():
        d = OUT / theme
        d.mkdir(parents=True, exist_ok=True)
        for name, fn in [("header", header), ("cards", cards), ("divider", divider), ("footer", footer)]:
            (d / f"{name}.svg").write_text(fn(colors), encoding="utf-8")
            print(f"wrote assets/{theme}/{name}.svg")
