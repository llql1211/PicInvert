"""
图片反色核心逻辑（内部实现，不对外暴露）。

公开 API 见同包下的 __init__.py。
"""

from pathlib import Path
from typing import Optional, Union

from PIL import Image, ImageOps


def _invert_image(img: Image.Image) -> Image.Image:
    """
    对 PIL Image 对象进行反色处理，返回反色后的 Image 对象。

    支持 RGB、RGBA、灰度图（L 模式）；其他模式转为 RGB 处理。
    RGBA 图片只反转 RGB 通道，保留原始 Alpha 通道。
    """
    mode = img.mode
    if mode == "RGBA":
        # 只反转 RGB 通道，保留原始 Alpha
        r, g, b, a = img.split()
        rgb = Image.merge("RGB", (r, g, b))
        inverted_rgb = ImageOps.invert(rgb)
        return Image.merge("RGBA", (*inverted_rgb.split(), a))
    elif mode in ("RGB", "L"):
        return ImageOps.invert(img)
    else:
        # 其他模式（P、CMYK 等）转为 RGB 处理
        return ImageOps.invert(img.convert("RGB"))


def invert(
    picture_path: Union[str, Path],
    suffix: str = "_inverted",
    output_dir: Optional[Union[str, Path]] = None,
    invert_mode: str = "standard",
) -> Path:
    """
    读取目标图片，进行反色处理，按新后缀保存为新图片。

    Parameters
    ----------
    picture_path : str or Path
        图片的路径和文件名。
    suffix : str, default "_inverted"
        保存新图片的文件名后缀（添加在扩展名前）。
    output_dir : str or Path or None, default None
        输出目录。为 None 时，输出到源文件所在目录。
    invert_mode : str, default "standard"
        反色模式。当前仅支持 "standard"（255 - 各通道像素值）。
        预留此参数以便后续扩展其他反色算法。

    Returns
    -------
    Path
        输出文件的完整路径。

    Raises
    ------
    FileNotFoundError
        如果 picture_path 不存在。
    ValueError
        如果 invert_mode 不支持。
    """
    picture_path = Path(picture_path)

    if not picture_path.is_file():
        raise FileNotFoundError(f"图片文件不存在: {picture_path}")

    if invert_mode != "standard":
        raise ValueError(
            f"不支持的反色模式: {invert_mode!r}，当前仅支持 'standard'"
        )

    # 确定输出路径
    src_dir = picture_path.parent
    stem = picture_path.stem
    ext = picture_path.suffix

    if output_dir is None:
        out_dir = src_dir
    else:
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / f"{stem}{suffix}{ext}"

    # 读取 → 反色 → 保存
    img = Image.open(picture_path)
    try:
        inverted_img = _invert_image(img)
        inverted_img.save(out_path)
    finally:
        img.close()

    return out_path
