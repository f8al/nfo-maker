# 🎨 NFO Art Maker

A retro-inspired **command-line tool** that generates ASCII/ANSI/Unicode
art banners like the old-school **.NFO / keygen cracktro** files of the
80s and 90s.\
Works great on macOS (Apple Silicon), Linux, and anywhere Python 3 runs.

------------------------------------------------------------------------

## ✨ Features

-   Render text as **block art** using:
    -   Built-in 5×7 ASCII font
    -   Any [pyfiglet](https://pypi.org/project/pyfiglet/) font
        (`--figlet-font`)
-   Add **borders** (double, single, ASCII, or none)
-   Add **color gradients** with ANSI escape codes
-   Include an **NFO metadata block**:
    -   Release, Supplier, Cracked by, Group, Greets, Notes...
-   Compatible modes:
    -   `--vt-safe` → only safe SGR sequences (no 256-color)
    -   `--charset ascii` → ASCII-only borders
    -   `--network-safe` → Cisco/Fortinet CLI safe (ASCII-only, no
        color, plain `#` fill)

------------------------------------------------------------------------

## 🚀 Quick Start

``` bash
chmod +x nfo_art.py

# Basic usage
echo "SecurityShrimp" | ./nfo_art.py

# Unicode blocks + double border + gradient
echo "SECURITYSHRIMP" | ./nfo_art.py --preset unicode --border double --gradient gradient

# With NFO metadata
echo "SecurityShrimp" | ./nfo_art.py --nfo \
  --group SHR1MP \
  --release "Ghost Shrimp Keygen Deluxe" \
  --cracked-by f8al \
  --greets "w00w00, DC402" \
  --notes "For educational demos only."
```

------------------------------------------------------------------------

## 🔧 Options

### Rendering

-   `--preset {unicode,ansi,ascii}`\
    Choose block characters (`█`, `▓`, or `#`).
-   `--border {double,single,ascii,none}`\
    Frame style.
-   `--align {left,center}`\
    Align output (center works best with `--border none`).
-   `--gradient {none,mono,cyan,magenta,grey,gradient,sunset}`\
    Color palette (if not `--vt-safe` or `--network-safe`).
-   `--figlet-font <name>`\
    Use a FIGlet font if [pyfiglet](https://pypi.org/project/pyfiglet/)
    is installed.

### Metadata

-   `--nfo` → Append classic NFO fields
-   `--group`, `--release`, `--supplier`, `--cracked-by`, `--date`,
    `--url`, `--greets`, `--notes`

### Compatibility

-   `--vt-safe` → strip 256-color, keep only 8/16 SGR safe for
    VT100/VT220
-   `--charset ascii` → force ASCII borders (`+-|`)
-   `--network-safe` → Cisco/Fortinet compatible:
    -   ASCII borders
    -   No color
    -   Plain ASCII fills (`#`)

------------------------------------------------------------------------

## 📚 Examples

### FIGlet font (requires `pyfiglet`)

``` bash
echo "SecurityShrimp" | ./nfo_art.py --figlet-font slant --gradient cyan
```

### VT-safe output

``` bash
echo "SecurityShrimp" | ./nfo_art.py --figlet-font standard --gradient cyan --vt-safe
```

### Cisco/Fortinet safe

``` bash
echo "SECURITYSHRIMP" | ./nfo_art.py --network-safe
```

------------------------------------------------------------------------

## 🖼️ Preview Fonts

See available fonts:

``` bash
pyfiglet -l | less
```

Top picks: 
Classio / Readable
`slant`, `standard`, `big`, `block`, `doom`, `starwars`, `smshadow`, `smslant`.

Retro / Demo-Scene Flavor
`doom`, `starwars`, `smshadow`, `bubble`, `digital`, `rectangles`, `speed`, `universe`, `pagga`.

------------------------------------------------------------------------

## 📝 License

MIT -- do whatever you want, just don't blame me if your banner bricks a
Cisco box 😉
