"""
picinvert — 图片反色处理工具。

提供 invert() 函数用于单张图片反色，以及 picinvert CLI 命令用于批量处理。
"""

from picinvert._core import invert

__all__ = ["invert"]
