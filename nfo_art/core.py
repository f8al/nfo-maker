"""
nfo_art.core - Library for generating retro NFO/keygen-style banners.
"""
from __future__ import annotations
import sys, os, shutil, datetime, textwrap, re
from dataclasses import dataclass
from typing import List, Optional

# ---------- ANSI utils ----------
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

def strip_ansi(s: str) -> str:
    return ANSI_RE.sub("", s)

def visible_len(s: str) -> int:
    return len(strip_ansi(s))

def pad_to_width(s: str, width: int) -> str:
    pad = max(0, width - visible_len(s))
    return s + (" " * pad)

def wrap_ansi_line(s: str, maxw: int) -> List[str]:
    """Wrap a colored string by visible width without breaking ANSI sequences."""
    if maxw <= 0:
        return [s]
    out = []
    cur = ""
    v = 0
    i = 0
    n = len(s)
    while i < n:
        if s[i] == "\x1b":
            m = ANSI_RE.match(s, i)
            if m:
                cur += m.group(0)
                i = m.end()
                continue
        ch = s[i]
        cur += ch
        if ch != "\n":
            v += 1
        if ch == "\n" or v >= maxw:
            out.append(cur.rstrip("\n"))
            cur = ""
            v = 0
        i += 1
    if cur or not out:
        out.append(cur)
    return out

def center_visible(s: str, total: int) -> str:
    w = visible_len(s)
    if w >= total:
        return s
    left = (total - w) // 2
    return (" " * left) + s

# ---------- Optional FIGlet ----------
try:
    from pyfiglet import Figlet
    HAVE_PYFIGLET = True
except Exception:
    HAVE_PYFIGLET = False

# ---------- 5x7 fallback font ----------
FONT_5x7 = {
    'A': [0b01110,0b10001,0b10001,0b11111,0b10001,0b10001,0b10001],
    'B': [0b11110,0b10001,0b10001,0b11110,0b10001,0b10001,0b11110],
    'C': [0b01111,0b10000,0b10000,0b10000,0b10000,0b10000,0b01111],
    'D': [0b11110,0b10001,0b10001,0b10001,0b10001,0b10001,0b11110],
    'E': [0b11111,0b10000,0b10000,0b11110,0b10000,0b10000,0b11111],
    'F': [0b11111,0b10000,0b10000,0b11110,0b10000,0b10000,0b10000],
    'G': [0b01111,0b10000,0b10000,0b10111,0b10001,0b10001,0b01111],
    'H': [0b10001,0b10001,0b10001,0b11111,0b10001,0b10001,0b10001],
    'I': [0b11111,0b00100,0b00100,0b00100,0b00100,0b00100,0b11111],
    'J': [0b00111,0b00010,0b00010,0b00010,0b10010,0b10010,0b01100],
    'K': [0b10001,0b10010,0b10100,0b11000,0b10100,0b10010,0b10001],
    'L': [0b10000,0b10000,0b10000,0b10000,0b10000,0b10000,0b11111],
    'M': [0b10001,0b11011,0b10101,0b10101,0b10001,0b10001,0b10001],
    'N': [0b10001,0b11001,0b10101,0b10011,0b10001,0b10001,0b10001],
    'O': [0b01110,0b10001,0b10001,0b10001,0b10001,0b10001,0b01110],
    'P': [0b11110,0b10001,0b10001,0b11110,0b10000,0b10000,0b10000],
    'Q': [0b01110,0b10001,0b10001,0b10001,0b10101,0b10010,0b01101],
    'R': [0b11110,0b10001,0b10001,0b11110,0b10100,0b10010,0b10001],
    'S': [0b01111,0b10000,0b10000,0b01110,0b00001,0b00001,0b11110],
    'T': [0b11111,0b00100,0b00100,0b00100,0b00100,0b00100,0b00100],
    'U': [0b10001,0b10001,0b10001,0b10001,0b10001,0b10001,0b01110],
    'V': [0b10001,0b10001,0b10001,0b10001,0b01010,0b01010,0b00100],
    'W': [0b10001,0b10001,0b10001,0b10101,0b10101,0b11011,0b10001],
    'X': [0b10001,0b01010,0b00100,0b00100,0b00100,0b01010,0b10001],
    'Y': [0b10001,0b01010,0b00100,0b00100,0b00100,0b00100,0b00100],
    'Z': [0b11111,0b00001,0b00010,0b00100,0b01000,0b10000,0b11111],
    '0': [0b01110,0b10011,0b10101,0b10101,0b11001,0b10001,0b01110],
    '1': [0b00100,0b01100,0b00100,0b00100,0b00100,0b00100,0b01110],
    '2': [0b01110,0b10001,0b00001,0b00010,0b00100,0b01000,0b11111],
    '3': [0b11110,0b00001,0b00001,0b01110,0b00001,0b00001,0b11110],
    '4': [0b00010,0b00110,0b01010,0b10010,0b11111,0b00010,0b00010],
    '5': [0b11111,0b10000,0b11110,0b00001,0b00001,0b10001,0b01110],
    '6': [0b00110,0b01000,0b10000,0b11110,0b10001,0b10001,0b01110],
    '7': [0b11111,0b00001,0b00010,0b00100,0b01000,0b01000,0b01000],
    '8': [0b01110,0b10001,0b10001,0b01110,0b10001,0b10001,0b01110],
    '9': [0b01110,0b10001,0b10001,0b01111,0b00001,0b00010,0b01100],
    ' ': [0,0,0,0,0,0,0],
    '-': [0,0,0,0b11111,0,0,0],
    '_': [0,0,0,0,0,0,0b11111],
    '.': [0,0,0,0,0,0b00110,0b00110],
    ',': [0,0,0,0,0b00110,0b00100,0b01000],
    '!': [0b00100,0b00100,0b00100,0b00100,0b00100,0,0b00100],
    '?': [0b01110,0b10001,0b00001,0b00010,0b00100,0,0b00100],
    ':': [0,0b00110,0b00110,0,0b00110,0b00110,0],
    '/': [0b00001,0b00010,0b00100,0b01000,0b10000,0,0],
}

def render_5x7(text: str, on="█", off=" ") -> List[str]:
    rows: List[str] = []
    for ln in text.splitlines():
        line_rows = [""]*7
        for ch in ln:
            g = FONT_5x7.get(ch.upper(), FONT_5x7.get('?'))
            for r in range(7):
                row_bits = g[r]
                for bit in range(5):
                    mask = 1 << (4-bit)
                    line_rows[r] += (on if (row_bits & mask) else off)
                line_rows[r] += " "
        rows.extend(line_rows)
        rows.append("")
    return rows[:-1] if rows else []

def render_figlet(text: str, font="slant") -> List[str]:
    f = Figlet(font=font, width=1000)
    art = f.renderText(text)
    return [ln.rstrip("\n") for ln in art.splitlines()]

# ---------- Boxes ----------
BOX = {
    "single": {"tl":"┌","tr":"┐","bl":"└","br":"┘","h":"─","v":"│"},
    "double": {"tl":"╔","tr":"╗","bl":"╚","br":"╝","h":"═","v":"║"},
    "ascii":  {"tl":"+","tr":"+","bl":"+","br":"+","h":"-","v":"|"},
    "none":   {"tl":"","tr":"","bl":"","br":"","h":"","v":""},
}

# ---------- Palettes ----------
ANSI = {"reset":"\x1b[0m","bold":"\x1b[1m"}

def _gradient_256(start, end, width):
    if width <= 1: return [start]
    step = (end - start) / (width - 1)
    return [int(round(start + i*step)) for i in range(width)]

PALETTES = {
    "none": lambda w: ["" for _ in range(w)],
    "mono": lambda w: [ANSI["bold"] for _ in range(w)],
    "cyan": lambda w: ["\x1b[36m" for _ in range(w)],
    "magenta": lambda w: ["\x1b[35m" for _ in range(w)],
    "grey": lambda w: ["\x1b[90m" for _ in range(w)],
    "gradient": lambda w: [f"\x1b[38;5;{c}m" for c in _gradient_256(27, 201, w)],
    "sunset": lambda w: [f"\x1b[38;5;{c}m" for c in _gradient_256(202, 226, w)],
}

def resolve_palette(name: str, width: int, vt_safe: bool=False) -> List[str]:
    if vt_safe:
        safe = {
            "none": lambda w: ["" for _ in range(w)],
            "mono": lambda w: [ANSI["bold"] for _ in range(w)],
            "cyan": lambda w: ["\x1b[36m" for _ in range(w)],
            "magenta": lambda w: ["\x1b[35m" for _ in range(w)],
            "grey": lambda w: ["\x1b[37m" for _ in range(w)],
        }
        fn = safe.get(name, safe["mono"])
        return fn(width)
    return PALETTES.get(name, PALETTES["none"])(width)

def colorize(lines: List[str], palette_name: str, vt_safe: bool=False) -> List[str]:
    width = max((len(l) for l in lines), default=0)
    colors = resolve_palette(palette_name, width, vt_safe=vt_safe)
    out: List[str] = []
    for line in lines:
        padded = line + " " * (width - len(line))
        segs = [colors[i] + ch for i, ch in enumerate(padded)]
        out.append("".join(segs) + ANSI["reset"])
    return out

def boxify(lines: List[str], style="double", pad=1, title: Optional[str]=None) -> List[str]:
    b = BOX.get(style, BOX["double"])
    if style == "none":
        return lines
    content_w = max((visible_len(l) for l in lines), default=0)
    inner: List[str] = []
    for l in lines:
        inner.append(" " * pad + pad_to_width(l, content_w) + " " * pad)
    w = content_w + pad*2
    if title:
        cap = f" {title} "
        left = max(0, (w - len(cap))//2)
        right = max(0, w - len(cap) - left)
        top = b["tl"] + (b["h"]*left) + cap + (b["h"]*right) + b["tr"]
    else:
        top = b["tl"] + (b["h"]*w) + b["tr"]
    bot = b["bl"] + (b["h"]*w) + b["br"]
    return [top] + [b["v"] + s + b["v"] for s in inner] + [bot]

# ---------- NFO helpers ----------
def wrap_kv(label: str, value: str, width: int, label_w=14) -> List[str]:
    wrap_w = max(1, width - label_w - 2)
    if not value:
        return [f"{label:<{label_w}}: "]
    chunks = textwrap.wrap(str(value), width=wrap_w) or [""]
    out: List[str] = []
    for i, ch in enumerate(chunks):
        if i == 0:
            out.append(f"{label:<{label_w}}: {ch}")
        else:
            out.append(" " * (label_w + 2) + ch)
    return out

def build_nfo_block(group: str="", release: str="", supplier: str="", cracked_by: str="",
                    date: str="", url: str="", greets: str="", notes: str="",
                    content_width: int=80) -> List[str]:
    if not date:
        date = datetime.date.today().isoformat()
    fields = [
        ("Release", release),
        ("Date", date),
        ("Supplier", supplier),
        ("Cracked by", cracked_by),
        ("Group", group),
        ("URL", url),
        ("Greets", greets),
        ("Notes", notes),
    ]
    out: List[str] = []
    for k, v in fields:
        out += wrap_kv(k, v, content_width)
    return out

# ---------- Public API ----------
@dataclass
class NFOArtOptions:
    preset: str = "unicode"
    border: str = "double"
    align: str = "left"
    gradient: str = "gradient"
    figlet_font: str = "slant"
    wrap: int = 0
    # NFO
    nfo: bool = False
    group: str = ""
    release: str = ""
    supplier: str = ""
    cracked_by: str = ""
    date: str = ""
    url: str = ""
    greets: str = ""
    notes: str = ""
    title: str = ""
    # Compatibility
    vt_safe: bool = False
    charset: str = "unicode"
    network_safe: bool = False
    # Layout
    max_width: int = 0
    no_color: bool = False

def make_art(text: str, opt: Optional[NFOArtOptions]=None) -> List[str]:
    if opt is None:
        opt = NFOArtOptions()
    text = (text or "").strip("\n\r ")
    if not text:
        return []

    if opt.wrap and opt.wrap > 0:
        text = "\n".join(textwrap.wrap(text.replace("\n"," "), width=opt.wrap))

    if opt.network_safe:
        opt.charset = "ascii"
        opt.vt_safe = True
        opt.gradient = "none"
        opt.preset = "ascii"

    if opt.preset == "unicode":
        on, off = "█", " "
    elif opt.preset == "ansi":
        on, off = "▓", " "
    else:
        on, off = "#", " "

    if HAVE_PYFIGLET and "\n" not in text:
        lines = render_figlet(text, font=opt.figlet_font)
    else:
        lines = render_5x7(text, on=on, off=off)

    if opt.nfo:
        width_preview = max((len(l) for l in lines), default=0)
        info_lines = build_nfo_block(
            group=opt.group, release=opt.release, supplier=opt.supplier, cracked_by=opt.cracked_by,
            date=opt.date, url=opt.url, greets=opt.greets, notes=opt.notes, content_width=width_preview
        )
        lines = lines + [""] + info_lines

    colored = colorize(lines, opt.gradient, vt_safe=opt.vt_safe)

    if opt.no_color:
        colored = [strip_ansi(l) for l in colored]

    if opt.align == "center" and opt.border == "none":
        term_w = shutil.get_terminal_size((80,25)).columns
        colored = [center_visible(ln, term_w) for ln in colored]

    if opt.max_width and opt.max_width > 0:
        wrapped: List[str] = []
        for ln in colored:
            wrapped.extend(wrap_ansi_line(ln, opt.max_width))
        colored = wrapped

    border_style = opt.border
    if opt.charset == "ascii" and opt.border in ("double","single"):
        border_style = "ascii"

    caption = opt.title or (opt.group if opt.nfo and opt.group else None)
    framed = boxify(colored, style=border_style, pad=1, title=caption)
    return framed

def make_art_string(text: str, opt: Optional[NFOArtOptions]=None) -> str:
    return "\n".join(make_art(text, opt))

def make_py_snippet(lines: List[str]) -> str:
    out: List[str] = []
    for ln in lines:
        safe = ln.replace("\\", "\\\\").replace("\x1b", "\\x1b").replace('"', '\\"')
        out.append(f'print("{safe}")')
    return "\n".join(out) + "\n"

def save_py_snippet(file_path: str, lines: List[str]) -> None:
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(make_py_snippet(lines))

def save_nfo_file(file_path: str, lines: List[str]) -> None:
    plain_lines = [strip_ansi(l) for l in lines]
    try:
        with open(file_path, "wb") as nf:
            nf.write(("\r\n".join(plain_lines) + "\r\n").encode("cp437"))
    except UnicodeEncodeError:
        trans_table = str.maketrans({
            '┌': '+','┐': '+','└': '+','┘': '+','─': '-', '│': '|',
            '╔': '+','╗': '+','╚': '+','╝': '+','═': '-', '║': '|',
            '█': '#','▓': '#','▒': '#','░': '#',
        })
        ascii_lines = [s.translate(trans_table) for s in plain_lines]
        with open(file_path, "wb") as nf:
            nf.write(("\r\n".join(ascii_lines) + "\r\n").encode("cp437", errors="ignore"))
