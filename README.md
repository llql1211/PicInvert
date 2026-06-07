# PicInvert

A lightweight Python tool for batch inverting (negating) image colors. Built on Pillow.

## Installation

```bash
pip install -e .
```

## Usage

### In-place folder mode (recommended)

Scan a folder for images and save inverted copies alongside the originals. Already processed files are automatically skipped.

```bash
picinvert -f ./my_photos
```

Options:

|         Flag         |             Description            |    Default   |
|----------------------|------------------------------------|--------------|
| `-f` / `--folder`    | Target folder path                 |       —      |
| `-s` / `--suffix`    | Output filename suffix             | `_converted` |
| `-r` / `--recursive` | Process subdirectories recursively |      off     |

Examples:

```bash
# Custom suffix
picinvert -f ./photos -s _inverted

# Recursive
picinvert -f ./photos -r

# Combine
picinvert -f ./photos -s _done -r
```

### Traditional mode (input → output)

Copy images from an input folder to an output folder, optionally moving originals to a "complete" folder after processing.

```bash
picinvert                    # uses ./input → ./output, moves originals to ./complete
picinvert -k                 # keep originals in place
picinvert -i ./src -o ./dst  # custom paths
```

### As a Python API

```python
from picinvert import invert, batch_invert

# Single image
invert("photo.jpg", suffix="_inverted")

# Batch — scan folder, invert, save alongside
batch_invert("./photos", suffix="_converted")
```

## Supported formats

jpg, jpeg, png, bmp, gif, tiff, webp

RGBA images have only the RGB channels inverted; the alpha channel is preserved. Other color modes are converted to RGB before inverting.
