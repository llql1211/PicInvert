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


def batch_invert(
    folder: Union[str, Path],
    suffix: str = "_converted",
    recursive: bool = False,
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
                inverted_img = _invert_image(img)
                inverted_img.save(out_path)
            finally:
                img.close()

            output_paths.append(out_path)
            tqdm.write(f"[OK] {input_file.name} -> {out_path.name}")

        except Exception as e:
            tqdm.write(f"[FAIL] {input_file.name}: {e}")
            continue

    return output_paths
