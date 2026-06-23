"""
图片反色核心逻辑（内部实现，不对外暴露）。

公开 API 见同包下的 __init__.py。
"""

from pathlib import Path
from typing import Optional, Union

from PIL import Image, ImageOps
from tqdm import tqdm

# 支持的图片扩展名（不区分大小写）
SUPPORTED_EXT = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}


def _invert_rgb(img: Image.Image) -> Image.Image:
    """
    标准 RGB 反色（255 - 各通道像素值）。
    支持 RGB、RGBA、灰度图（L 模式）；其他模式转为 RGB 处理。
    RGBA 图片只反转 RGB 通道，保留原始 Alpha 通道。
    """
    mode = img.mode
    if mode == "RGBA":
        r, g, b, a = img.split()
        rgb = Image.merge("RGB", (r, g, b))
        inverted_rgb = ImageOps.invert(rgb)
        return Image.merge("RGBA", (*inverted_rgb.split(), a))
    elif mode in ("RGB", "L"):
        return ImageOps.invert(img)
    else:
        return ImageOps.invert(img.convert("RGB"))


def _invert_hsv_lightness(img: Image.Image) -> Image.Image:
    """
    HSV 反转明度：将图像转为 HSV 色彩空间，只反转 V（明度）通道，
    保持 H（色相）和 S（饱和度）不变，再转回 RGB/RGBA。
    适用于需要保留原始色彩关系的场景。
    """
    # 先处理 RGBA：拆出 Alpha，只对 RGB 部分做 HSV 处理
    alpha = None
    if img.mode == "RGBA":
        rgb, alpha = img.split()[:3], img.split()[3]
        img_rgb = Image.merge("RGB", rgb)
    elif img.mode in ("RGB", "L"):
        img_rgb = img.convert("RGB")
    else:
        img_rgb = img.convert("RGB")

    hsv = img_rgb.convert("HSV")
    h, s, v = hsv.split()
    v = v.point(lambda x: 255 - x)  # 反转明度

    inverted_rgb = Image.merge("HSV", (h, s, v)).convert("RGB")

    if alpha is not None:
        return Image.merge("RGBA", (*inverted_rgb.split(), alpha))
    return inverted_rgb


def _invert_black_white(img: Image.Image, threshold: int = 30) -> Image.Image:
    """
    仅反色黑白灰色（低饱和度区域），保留彩色区域不变。

    原理：将图像转为 HSV，对饱和度（S）低于阈值的像素反转明度（V），
    达到「黑白灰反色、彩色保留」的效果。

    Parameters
    ----------
    img : Image.Image
        要处理的 PIL Image 对象。
    threshold : int, default 30
        饱和度阈值（0-255）。饱和度低于此值的像素被视为"黑白灰"进行反色。
    """
    # 处理 RGBA
    alpha = None
    if img.mode == "RGBA":
        rgb_parts, alpha = img.split()[:3], img.split()[3]
        img_rgb = Image.merge("RGB", rgb_parts)
    elif img.mode in ("RGB", "L"):
        img_rgb = img.convert("RGB")
    else:
        img_rgb = img.convert("RGB")

    hsv = img_rgb.convert("HSV")
    h, s, v = hsv.split()

    # 创建掩码：饱和度 < threshold 的像素为 True（黑白灰）
    mask = s.point(lambda x: 255 if x < threshold else 0).convert("1")

    # 反转 V 通道
    v_inverted = v.point(lambda x: 255 - x)

    # 根据掩码混合：有颜色的像素保留原 V，黑白灰像素用反转后的 V
    v_blended = Image.composite(v_inverted, v, mask)

    inverted_rgb = Image.merge("HSV", (h, s, v_blended)).convert("RGB")

    if alpha is not None:
        return Image.merge("RGBA", (*inverted_rgb.split(), alpha))
    return inverted_rgb


def _invert_image(img: Image.Image, invert_mode: str = "black-white") -> Image.Image:
    """
    对 PIL Image 对象进行反色处理，返回反色后的 Image 对象。

    Parameters
    ----------
    img : Image.Image
        要处理的 PIL Image 对象。
    invert_mode : str, default "black-white"
        反色模式。
        - "standard"：标准 RGB 反色（255 - 各通道像素值）
        - "hsv"：HSV 色彩空间下只反转明度（V）通道，保持色相和饱和度不变
        - "black-white"：仅反转黑白灰色（低饱和度区域），保留彩色区域不变

    Raises
    ------
    ValueError
        如果 invert_mode 不支持。
    """
    if invert_mode == "standard":
        return _invert_rgb(img)
    elif invert_mode == "hsv":
        return _invert_hsv_lightness(img)
    elif invert_mode == "black-white":
        return _invert_black_white(img)
    else:
        raise ValueError(
            f"不支持的反色模式: {invert_mode!r}，支持 'standard'、'hsv' 和 'black-white'"
        )


def invert(
    picture_path: Union[str, Path],
    suffix: str = "_inverted",
    output_dir: Optional[Union[str, Path]] = None,
    invert_mode: str = "black-white",
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
    invert_mode : str, default "black-white"
        反色模式。
        - "standard"：标准 RGB 反色（255 - 各通道像素值）
        - "hsv"：HSV 色彩空间下只反转明度（V）通道；保留色相和饱和度
        - "black-white"：仅反转黑白灰色（低饱和度区域），保留彩色区域不变

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
        inverted_img = _invert_image(img, invert_mode=invert_mode)
        inverted_img.save(out_path)
    finally:
        img.close()

    return out_path


def batch_invert(
    folder: Union[str, Path],
    suffix: str = "_converted",
    recursive: bool = False,
    invert_mode: str = "black-white",
) -> list[Path]:
    """
    扫描文件夹下所有图片文件，跳过文件名以 suffix 结尾的文件，
    将图片反色后以新文件名保存到同目录下。

    流程：
    1. 扫描文件夹下所有支持的图片文件
    2. 过滤掉文件名（不含扩展名）以 suffix 结尾的文件（如已转换过的）
    3. 过滤掉输出文件已存在的文件（避免重复处理）
    4. 对每个符合条件的图片执行反色，添加后缀保存到同目录

    Parameters
    ----------
    folder : str or Path
        要扫描的文件夹路径。
    suffix : str, default "_converted"
        输出文件名后缀（添加在扩展名前），同时用于过滤已转换的文件。
    recursive : bool, default False
        是否递归处理子文件夹。
    invert_mode : str, default "black-white"
        反色模式，透传给 _invert_image()。

    Returns
    -------
    list[Path]
        成功生成的输出文件路径列表。

    Raises
    ------
    NotADirectoryError
        如果 folder 不是文件夹。
    """
    folder = Path(folder)

    if not folder.is_dir():
        raise NotADirectoryError(f"路径不是文件夹: {folder}")

    # 扫描图片文件
    if recursive:
        all_files = [
            f for f in folder.rglob("*")
            if f.is_file() and f.suffix.lower() in SUPPORTED_EXT
        ]
    else:
        all_files = [
            f for f in folder.iterdir()
            if f.is_file() and f.suffix.lower() in SUPPORTED_EXT
        ]

    # 过滤：排除文件名（去除扩展名）以 suffix 结尾的文件，
    # 以及输出文件已存在的文件（避免重复处理）
    files_to_process = [
        f for f in all_files
        if not f.stem.endswith(suffix)
        and not (f.parent / f"{f.stem}{suffix}{f.suffix}").exists()
    ]

    if not files_to_process:
        return []

    output_paths = []

    for input_file in tqdm(files_to_process, desc="处理进度", unit="张"):
        try:
            # 递归模式下，输出到源文件所在的子目录
            out_path = input_file.parent / f"{input_file.stem}{suffix}{input_file.suffix}"

            img = Image.open(input_file)
            try:
                inverted_img = _invert_image(img, invert_mode=invert_mode)
                inverted_img.save(out_path)
            finally:
                img.close()

            output_paths.append(out_path)
            tqdm.write(f"[OK] {input_file.name} -> {out_path.name}")

        except Exception as e:
            tqdm.write(f"[FAIL] {input_file.name}: {e}")
            continue

    return output_paths
