# PicInvert

**English** | [中文](README_zh.md)

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

|         Flag         |             Description                           |    Default   |
|----------------------|---------------------------------------------------|--------------|
| `-f` / `--folder`    | Target folder path                                |       —      |
| `-s` / `--suffix`    | Output filename suffix                            | `_converted` |
| `-r` / `--recursive` | Process subdirectories recursively                |      off     |
| `-m` / `--mode`      | Invert mode (`standard` / `hsv` / `black-white`)  | `hsv`        |

Examples:

```bash
# Custom suffix
picinvert -f ./photos -s _inverted

# Recursive
picinvert -f ./photos -r

# Standard RGB invert (255 - pixel value)
picinvert -f ./photos -m standard

# HSV lightness invert (preserves hue & saturation)
picinvert -f ./photos -m hsv

# Black & white only invert (preserves colored areas)
picinvert -f ./photos -m black-white

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

# Single image (HSV lightness invert by default)
invert("photo.jpg", suffix="_inverted")

# Standard RGB invert
invert("photo.jpg", suffix="_inverted", invert_mode="standard")

# Black & white only (preserves colored areas)
invert("photo.jpg", suffix="_inverted", invert_mode="black-white")

# Batch — scan folder, invert, save alongside
batch_invert("./photos", suffix="_converted")
```

## Invert mode comparison

| Method              | Standard invert (`standard`)                              | HSV lightness invert (`hsv`)                                        | Black & white only (`black-white`)                                |
|---------------------|-----------------------------------------------------------|----------------------------------------------------------------------|--------------------------------------------------------------------|
| **Algorithm**       | `255 - pixel value` per channel                           | Convert to HSV, invert only V (lightness/value) channel              | Convert to HSV, invert V only where S < threshold                 |
| **Hue**             | Inverted (red ⟷ cyan, blue ⟷ yellow, etc.)                | ✅ **Preserved**                                                      | ✅ **Preserved**                                                  |
| **Saturation**      | Inverted along with hue                                   | ✅ **Preserved**                                                      | ✅ **Preserved**                                                  |
| **Effect**          | Full tonal reversal, like photographic negative           | Original color relationships retained; only brightness flips         | Only grayscale areas inverted; colored areas unchanged            |
| **Use case**        | When a complete negative effect is desired                | When you want to preserve color identity, adjusting lightness        | When image has colored objects; invert only background / grayscale |

## Supported formats

jpg, jpeg, png, bmp, gif, tiff, webp

RGBA images have only the RGB channels inverted; the alpha channel is preserved. Other color modes are converted to RGB before inverting.
