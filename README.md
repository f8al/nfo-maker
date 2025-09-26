![](https://github.com/f8al/media/blob/main/nfo-banner.png?raw=true)
# 🎨 NFO Art Maker

[![PyPI](https://img.shields.io/pypi/v/nfo-maker.svg)](https://pypi.org/project/nfo-art/)
[![Python Versions](https://img.shields.io/pypi/pyversions/nfo-maker.svg)](https://pypi.org/project/nfo-art/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**NFO Art** is a retro-inspired Python library + CLI that generates banners styled like classic `.NFO` and keygen cracktro art from the 80s/90s warez scene.

It supports Unicode/ANSI/ASCII art, optional color gradients, and `.nfo` file output in CP437 encoding for true nostalgia.

---

## 🚀 Installation

```bash
# Basic install
pip install nfo-maker

# With FIGlet support (fancier fonts)
pip install nfo-maker pyfiglet
```

---

## 🖥️ CLI Usage

Pipe text in via stdin and style it:

```bash
echo "securityshrimp" | nfo-maker --border double --gradient cyan
```

### Options

- `--preset` : unicode | ansi | ascii
- `--border` : double | single | ascii | none
- `--gradient` : none | mono | cyan | magenta | grey | gradient | sunset
- `--figlet-font` : Use any FIGlet font (requires `pyfiglet`)
- `--save-nfo file.nfo` : Save CP437 `.nfo` file (ANSI stripped, ASCII fallback)
- `--python` : Output Python `print()` snippet
- `--save-py file.py` : Save snippet directly to file
- `--max-width` : ANSI-aware wrapping
- `--no-color` : Strip all color/bold codes
- `--network-safe` : Cisco/Fortinet compatible (ASCII only, no color)
#### --nfo Options
- `--title` : Title to place in top of banner
- `--release` : Text to place in Release
- `--supplier` : Text to place in Supplier
- `--cracked-by` : Text to place in Cracked By
- `--group` : Text to place in Group
- `--url` : Text to place in URL
- `--greets` : Text to place in Greets
- `--notes` : Text to place in notes
### Example

```bash
echo "NFO Art Maker" | nfo-maker --figlet-font speed --nfo --release "NFO Art Maker 1.0.1" --cracked-by "f8al" --group "w00w00" --url "https://www.securityshrimp.com" --greets "Batoure, Bobby the Phish" --notes "hack the planet" --supplier "SecurityShtimp" --title "NFO Art Maker"
```
![](https://github.com/f8al/media/blob/main/nfo-full.png?raw=true)
---

## 🐍 Library Usage

```python
from nfo_art import NFOArtOptions, make_art, make_art_string, save_py_snippet, save_nfo_file

# Simple banner
opts = NFOArtOptions(border="double", gradient="cyan")
print(make_art_string("SECURITYSHRIMP", opts))

# With NFO metadata
opts = NFOArtOptions(
    preset="unicode", border="double", gradient="gradient",
    nfo=True, group="w00w00",
    release="Ghost Shrimp Keygen Deluxe",
    cracked_by="f8al",
    notes="For educational demos only."
)
print(make_art_string("NFO-MAKER", opts))

# Save outputs
lines = make_art("securityshrimp", opts)
save_py_snippet("banner.py", lines)   # Python snippet with ANSI \x1b escapes
save_nfo_file("banner.nfo", lines)    # Pure CP437 .nfo file
```

---

## 🛠️ Development

Clone and install in editable mode:

```bash
git clone https://github.com/f8al/nfo-maker.git
cd nfo-maker
pip install -e .[pyfiglet]
```

Run CLI locally:

```bash
echo "HELLO" | python -m nfo_art.cli --gradient magenta
```

---

## 📜 License

MIT © 2025 Security Shrimp LTD, LLC ([@securityshrimp](https://securityshrimp.com))
