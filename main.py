#!/usr/bin/env python3
"""
图片反色批处理工具
- 读取 input 文件夹中的所有图片
- 生成反色图片到 output 文件夹（文件名添加 _converted 后缀）
- 将原图片移动到 complete 文件夹
"""

import os
import shutil
from pathlib import Path
from PIL import Image, ImageOps

# 支持的图片扩展名（不区分大小写）
SUPPORTED_EXT = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}


def invert_image(img):
    """
    对 PIL Image 对象进行反色处理，返回反色后的 Image 对象。
    支持 RGB、RGBA、灰度图，其他模式转换为 RGB 处理。
    """
    mode = img.mode
    if mode == 'RGBA':
        # 只反转 RGB 通道，保留原始 Alpha
        r, g, b, a = img.split()
        rgb = Image.merge('RGB', (r, g, b))
        inverted_rgb = ImageOps.invert(rgb)
        return Image.merge('RGBA', (*inverted_rgb.split(), a))
    elif mode in ('RGB', 'L'):
        return ImageOps.invert(img)
    else:
        # 其他模式（P、CMYK等）转为 RGB 处理
        return ImageOps.invert(img.convert('RGB'))


def safe_move(src, dst_dir):
    """
    将文件移动到目标目录，如果目标已存在同名文件，则自动重命名（添加时间戳）。
    """
    dst_path = Path(dst_dir) / Path(src).name
    if dst_path.exists():
        # 生成带时间戳的新文件名
        stem = dst_path.stem
        suffix = dst_path.suffix
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_name = f"{stem}_{timestamp}{suffix}"
        dst_path = dst_path.parent / new_name
        print(f"目标文件已存在，将重命名为: {new_name}")
    shutil.move(str(src), str(dst_path))
    print(f"已移动: {src} -> {dst_path}")


def process_batch():
    # 定义文件夹路径（相对于脚本所在目录）
    base_dir = Path(__file__).parent
    input_dir = base_dir / "input"
    output_dir = base_dir / "output"
    complete_dir = base_dir / "complete"

    # 确保文件夹存在
    input_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)
    complete_dir.mkdir(exist_ok=True)

    # 获取 input 文件夹中的所有文件
    files = [f for f in input_dir.iterdir() if f.is_file() and f.suffix.lower() in SUPPORTED_EXT]

    if not files:
        print("input 文件夹中没有找到支持的图片文件。")
        return

    print(f"找到 {len(files)} 个图片文件，开始处理...")

    for input_path in files:
        try:
            # 1. 读取原图
            img = Image.open(input_path)
            print(f"正在处理: {input_path.name}")

            # 2. 反色
            inverted = invert_image(img)

            # 3. 构造输出文件名（添加 _converted 后缀）
            stem = input_path.stem
            suffix = input_path.suffix
            output_name = f"{stem}_converted{suffix}"
            output_path = output_dir / output_name

            # 4. 保存反色图片
            inverted.save(output_path)
            print(f"  反色保存: {output_path}")

            # 5. 关闭图片（释放资源）
            img.close()
            inverted.close()

            # 6. 移动原文件到 complete 文件夹
            safe_move(input_path, complete_dir)

        except Exception as e:
            print(f"处理文件 {input_path.name} 时出错: {e}")
            continue

    print("所有任务处理完毕。")


if __name__ == "__main__":
    from datetime import datetime
    process_batch()
