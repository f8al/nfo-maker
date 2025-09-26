"""
nfo_art.cli - command line interface
"""
import sys, argparse
from .core import (
    NFOArtOptions, make_art, make_py_snippet,
    save_py_snippet, save_nfo_file, strip_ansi
)

def parse_args():
    ap = argparse.ArgumentParser(description="Make ANSI/Unicode NFO-style art from stdin.")
    ap.add_argument("--preset", choices=["unicode","ansi","ascii"], default="unicode")
    ap.add_argument("--border", choices=["double","single","ascii","none"], default="double")
    ap.add_argument("--align", choices=["left","center"], default="left")
    ap.add_argument("--gradient", choices=["none","mono","cyan","magenta","grey","gradient","sunset"], default="gradient")
    ap.add_argument("--figlet-font", default="slant")
    ap.add_argument("--wrap", type=int, default=0, help="Wrap title text before rendering.")
    # NFO
    ap.add_argument("--nfo", action="store_true")
    ap.add_argument("--group", default="")
    ap.add_argument("--release", default="")
    ap.add_argument("--supplier", default="")
    ap.add_argument("--cracked-by", dest="cracked_by", default="")
    ap.add_argument("--date", default="")
    ap.add_argument("--url", default="")
    ap.add_argument("--greets", default="")
    ap.add_argument("--notes", default="")
    ap.add_argument("--title", default="", help="Frame title caption (top border).")
    # Compatibility
    ap.add_argument("--vt-safe", dest="vt_safe", action="store_true", help="Use VT-compatible SGR only (no 256-color).")
    ap.add_argument("--charset", choices=["unicode","ascii"], default="unicode", help="Use ASCII borders for strict VT terminals.")
    ap.add_argument("--network-safe", action="store_true", help="Cisco/Fortinet-safe: ASCII only, no color, VT-safe.")
    # Layout / Output
    ap.add_argument("--max-width", type=int, default=0, help="Hard wrap output to this column width (ANSI-aware).")
    ap.add_argument("--no-color", action="store_true", help="Strip all ANSI (no color, no bold).")
    ap.add_argument("--python", action="store_true", help="Output as Python print() statements instead of raw text.")
    ap.add_argument("--save-py", metavar="FILE", help="Additionally save Python print() snippet to a file.")
    ap.add_argument("--save-nfo", metavar="FILE", help="Save plain .nfo (CP437-encoded) without ANSI codes.")
    return ap.parse_args()

def main():
    args = parse_args()
    raw = sys.stdin.read()
    text = raw.strip("\n\r ")
    if not text:
        print("No input. Pipe or type some text into stdin.", file=sys.stderr)
        sys.exit(1)

    opt = NFOArtOptions(
        preset=args.preset, border=args.border, align=args.align, gradient=args.gradient,
        figlet_font=args.figlet_font, wrap=args.wrap,
        nfo=args.nfo, group=args.group, release=args.release, supplier=args.supplier,
        cracked_by=args.cracked_by, date=args.date, url=args.url, greets=args.greets,
        notes=args.notes, title=args.title,
        vt_safe=args.vt_safe, charset=args.charset, network_safe=args.network_safe,
        max_width=args.max_width, no_color=args.no_color,
    )

    framed = make_art(text, opt)

    # Save to files (doesn't alter stdout behavior)
    if args.save_py:
        save_py_snippet(args.save_py, framed)
    if args.save_nfo:
        save_nfo_file(args.save_nfo, framed)

    if args.python:
        sys.stdout.write(make_py_snippet(framed))
    else:
        sys.stdout.write("\n".join(framed) + "\n")

if __name__ == "__main__":
    main()
