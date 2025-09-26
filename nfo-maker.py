#!/usr/bin/env python3
import sys, os, math, argparse, shutil, textwrap, datetime, re

# --- ANSI helpers (strip + visible width) ---
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

def strip_ansi(s: str) -> str:
    return ANSI_RE.sub("", s)

def visible_len(s: str) -> int:
    return len(strip_ansi(s))

def pad_to_width(s: str, width: int) -> str:
    """Right-pad with spaces so that *visible* width equals `width` even if s has ANSI codes."""
    pad = max(0, width - visible_len(s))
    return s + (" " * pad)

# Optional: use pyfiglet when available for nicer FIGlet fonts
try:
    from pyfiglet import Figlet
    HAVE_PYFIGLET = True
except Exception:
    HAVE_PYFIGLET = False

# -------- 5x7 fallback font (subset) --------
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
    '-': [0b00000,0b00000,0b00000,0b11111,0b00000,0b00000,0b00000],
    '_': [0b00000,0b00000,0b00000,0b00000,0b00000,0b00000,0b11111],
    '.': [0b00000,0b00000,0b00000,0b00000,0b00000,0b00110,0b00110],
    ',': [0b00000,0b00000,0b00000,0b00000,0b00110,0b00100,0b01000],
    '!': [0b00100,0b00100,0b00100,0b00100,0b00100,0b00000,0b00100],
    '?': [0b01110,0b10001,0b00001,0b00010,0b00100,0b00000,0b00100],
    ':': [0b00000,0b00110,0b00110,0b00000,0b00110,0b00110,0b00000],
    '/': [0b00001,0b00010,0b00100,0b01000,0b10000,0b00000,0b00000],
}

BOX = {
    "single": {"tl":"┌","tr":"┐","bl":"└","br":"┘","h":"─","v":"│","t":"├","u":"┴","n":"┬","x":"┼"},
    "double": {"tl":"╔","tr":"╗","bl":"╚","br":"╝","h":"═","v":"║","t":"╠","u":"╩","n":"╦","x":"╬"},
    "ascii":  {"tl":"+","tr":"+","bl":"+","br":"+","h":"-","v":"|","t":"+","u":"+","n":"+","x":"+"},
    "none":   {"tl":"","tr":"","bl":"","br":"","h":"","v":"","t":"","u":"","n":"","x":""},
}

ANSI = {"reset":"\x1b[0m","bold":"\x1b[1m"}

def _gradient_256(start, end, width):
    if width <= 1: return [start]
    step = (end - start) / (width - 1)
    return [int(round(start + i*step)) for i in range(width)]

PALETTES = {
    "none": lambda w: ["" for _ in range(w)],
    "mono": lambda w: [ANSI["bold"] for _ in range(w)],
    "cyan": lambda w: [f"\x1b[36m" for _ in range(w)],
    "magenta": lambda w: [f"\x1b[35m" for _ in range(w)],
    "grey": lambda w: [f"\x1b[90m" for _ in range(w)],
    "gradient": lambda w: [f"\x1b[38;5;{c}m" for c in _gradient_256(27, 201, w)], # cyan→pink
    "sunset": lambda w: [f"\x1b[38;5;{c}m" for c in _gradient_256(202, 226, w)],  # orange→yellow
}

def render_figlet(text, width, font="slant"):
    f = Figlet(font=font, width=1000)
    art = f.renderText(text)
    return [line.rstrip("\n") for line in art.splitlines()]

def render_5x7_line(ln, on="█", off=" "):
    rows = [""] * 7
    for ch in ln:
        g = FONT_5x7.get(ch.upper(), FONT_5x7.get('?'))
        for r in range(7):
            row_bits = g[r]
            for bit in range(5):
                mask = 1 << (4-bit)
                rows[r] += (on if (row_bits & mask) else off)
            rows[r] += " "
    return rows

def render_5x7(text, on="█", off=" "):
    parts = []
    for ln in text.splitlines():
        parts += render_5x7_line(ln, on=on, off=off)
        parts.append("")
    return parts[:-1] if parts else []

def _resolve_palette(palette_name, width, vt_safe=False):
    if vt_safe:
        # Map non-VT palettes to safe equivalents
        safe = {
            'none': lambda w: ['']*w,
            'mono': lambda w: ['\x1b[1m']*w,  # bold only
            'cyan': lambda w: ['\x1b[36m']*w, # 3X color
            'magenta': lambda w: ['\x1b[35m']*w,
            'grey': lambda w: ['\x1b[37m']*w, # white as grey fallback
        }
        fn = safe.get(palette_name)
        if fn is None:
            fn = safe['mono']
        return fn(width)
    # non-VT: use full palette table
    fn = PALETTES.get(palette_name, PALETTES['none'])
    return fn(width)

def colorize(lines, palette_name, vt_safe=False):
    # compute width from raw (no ANSI)
    width = max((len(l) for l in lines), default=0)
    colors = _resolve_palette(palette_name, width, vt_safe=vt_safe)
    out = []
    for line in lines:
        padded = line + " " * (width - len(line))
        segs = [colors[i] + ch for i, ch in enumerate(padded)]
        out.append("".join(segs) + ANSI["reset"])
    return out, width

def boxify(lines, style="double", pad=1, title=None):
    b = BOX.get(style, BOX["double"])
    if style == "none": return lines
    content_w = max((visible_len(l) for l in lines), default=0)
    inner = []
    for l in lines:
        body = " " * pad + pad_to_width(l, content_w) + " " * pad
        inner.append(body)
    w = content_w + pad*2
    # title (caption) atop
    if title:
        cap = f" {title} "
        cap_len = len(cap)
        left = max(0, (w - cap_len)//2)
        right = max(0, w - cap_len - left)
        top = b["tl"] + (b["h"] * left) + cap + (b["h"] * right) + b["tr"]
    else:
        top = b["tl"] + (b["h"] * w) + b["tr"]
    bot = b["bl"] + (b["h"] * w) + b["br"]
    # add vertical bars
    framed = [top] + [b["v"] + s + b["v"] for s in inner] + [bot]
    return framed

def wrap_kv(label, value, width, label_w=14):
    wrap_w = max(1, width - label_w - 2)
    if not value:
        return [f"{label:<{label_w}}: "]
    chunks = textwrap.wrap(str(value), width=wrap_w) or [""]
    lines = []
    for idx, ch in enumerate(chunks):
        if idx == 0:
            lines.append(f"{label:<{label_w}}: {ch}")
        else:
            lines.append(" " * (label_w + 2) + ch)
    return lines

def build_nfo_block(args, content_width):
    env = os.environ
    def get(name, default=""):
        return getattr(args, name.replace("-","_")) or env.get(name.upper(), default)
    fields = [
        ("Release", get("release")),
        ("Date", get("date") or datetime.date.today().isoformat()),
        ("Supplier", get("supplier")),
        ("Cracked by", get("cracked_by")),
        ("Group", get("group")),
        ("URL", get("url")),
        ("Greets", get("greets")),
        ("Notes", get("notes")),
    ]
    out = []
    for k, v in fields:
        out += wrap_kv(k, v, content_width)
    return out

def parse_args():
    ap = argparse.ArgumentParser(description="Make ANSI/Unicode NFO-style art from stdin.")
    ap.add_argument("--preset", choices=["unicode","ansi","ascii"], default="unicode", help="Character set style.")
    ap.add_argument("--border", choices=["double","single","ascii","none"], default="double", help="Add a box frame.")
    ap.add_argument("--align", choices=["left","center"], default="left")
    ap.add_argument("--gradient", choices=["none","mono","cyan","magenta","grey","gradient","sunset"], default="gradient")
    ap.add_argument("--figlet-font", default="slant", help="If pyfiglet is installed, use this FIGlet font.")
    ap.add_argument("--wrap", type=int, default=0, help="Wrap long inputs before rendering.")
    ap.add_argument("--vt-safe", dest="vt_safe", action="store_true", help="Use VT-compatible SGR only (no 256-color).")
    # NFO block
    ap.add_argument("--nfo", action="store_true", help="Append a classic NFO metadata block under the title art.")
    ap.add_argument("--group", default="")
    ap.add_argument("--release", default="")
    ap.add_argument("--supplier", default="")
    ap.add_argument("--cracked-by", dest="cracked_by", default="")
    ap.add_argument("--date", default="")
    ap.add_argument("--url", default="")
    ap.add_argument("--greets", default="")
    ap.add_argument("--notes", default="")
    ap.add_argument("--title", default="", help="Frame title caption (top border).")
    ap.add_argument("--charset", choices=["unicode","ascii"], default="unicode", help="Use ASCII borders for strict VT terminals.")
    ap.add_argument("--network-safe", action="store_true", help="Cisco/Fortinet-safe: ASCII only, no color, VT-safe.")
    return ap.parse_args()

def main():
    args = parse_args()
    raw = sys.stdin.read()
    text = raw.strip("\n\r ")

    if not text:
        print("No input. Pipe or type some text into stdin.", file=sys.stderr)
        sys.exit(1)

    if args.wrap and args.wrap > 0:
        text = "\n".join(textwrap.wrap(text.replace("\n"," "), width=args.wrap))

    # Enforce network-safe defaults for Cisco/Fortinet style terminals
    if args.network_safe:
        args.charset = 'ascii'
        args.vt_safe = True
        args.gradient = 'none'
        args.preset = 'ascii'

    if args.preset == "unicode":
        on, off = "█", " "
    elif args.preset == "ansi":
        on, off = "▓", " "
    else:
        on, off = "#", " "

    # Render title art
    if HAVE_PYFIGLET and "\n" not in text:
        lines = render_figlet(text, width=1000, font=args.figlet_font)
    else:
        lines = render_5x7(text, on=on, off=off)

    # Optional NFO section
    if args.nfo:
        # preview width before color
        width_preview = max((len(l) for l in lines), default=0)
        info_lines = build_nfo_block(args, content_width=width_preview)
        lines = lines + [""] + info_lines

    # Colorize
    colored, raw_width = colorize(lines, args.gradient, vt_safe=args.vt_safe)

    # Center alignment (only when not boxed to avoid nesting)
    if args.align == "center" and args.border == "none":
        term_w = shutil.get_terminal_size((80,25)).columns
        colored = [line.center(term_w) for line in colored]

    # Caption: prefer --title, else group when --nfo
    caption = args.title or (args.group if args.nfo and args.group else None)

    # Charset handling: force ASCII borders under --charset ascii
    border_style = args.border
    if args.charset == 'ascii' and args.border in ('double','single'):
        border_style = 'ascii'

    # Box with ANSI-aware sizing
    framed = boxify(colored, style=border_style, pad=1, title=caption)

    for ln in framed:
        print(ln)

if __name__ == "__main__":
    main()
