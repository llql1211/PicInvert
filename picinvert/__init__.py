"""
picinvert — 图片反色处理工具。

提供 invert() 函数用于单张图片反色，以及 picinvert CLI 命令用于批量处理。
"""

from picinvert._core import (
    batch_invert, invert,
    _invert_image, _invert_rgb, _invert_hsv_lightness, _invert_black_white,
)

__all__ = [
    "batch_invert", "invert",
    "_invert_image", "_invert_rgb", "_invert_hsv_lightness", "_invert_black_white",
]
