"""
CLI 入口 — 批量图片反色处理。

用法:
    python -m picinvert                              # 使用默认路径（传统模式）
    python -m picinvert -i ./images -o ./results     # 自定义输入/输出目录（传统模式）
    python -m picinvert -k                           # 保留原文件（传统模式）
    picinvert -f ./my_images                         # 文件夹内原地反色（新模式）
    picinvert -f ./my_images -s _converted -r        # 递归 + 自定义后缀
"""

import argparse
import shutil
from datetime import datetime
from pathlib import Path

from PIL import Image
from tqdm import tqdm

from picinvert._core import _invert_image, batch_invert, SUPPORTED_EXT


def _safe_move(src, dst_dir):
    """
    将文件移动到目标目录，如果目标已存在同名文件，则自动重命名（添加时间戳）。
    """
    dst_path = Path(dst_dir) / Path(src).name
    if dst_path.exists():
        stem = dst_path.stem
        suffix = dst_path.suffix
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_name = f"{stem}_{timestamp}{suffix}"
        dst_path = dst_path.parent / new_name
        tqdm.write(f"目标文件已存在，将重命名为: {new_name}")
    shutil.move(str(src), str(dst_path))
    tqdm.write(f"已移动: {src} -> {dst_path}")


def process_batch(input_dir, output_dir, complete_dir, suffix, keep_original,
                  recursive):
    """
    批量处理图片反色。

    参数:
        input_dir:     输入文件夹路径
        output_dir:    输出文件夹路径
        complete_dir:  已完成文件夹路径（keep_original=False 时使用）
        suffix:        输出文件名后缀（默认 "_converted"）
        keep_original: 是否保留原文件（True=不移动）
        recursive:     是否递归处理子文件夹
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    complete_path = Path(complete_dir)

    # 确保文件夹存在
    input_path.mkdir(exist_ok=True)
    output_path.mkdir(exist_ok=True)
    if not keep_original:
        complete_path.mkdir(exist_ok=True)

    # 获取图片文件列表
    if recursive:
        files = [f for f in input_path.rglob("*")
                 if f.is_file() and f.suffix.lower() in SUPPORTED_EXT]
    else:
        files = [f for f in input_path.iterdir()
                 if f.is_file() and f.suffix.lower() in SUPPORTED_EXT]

    if not files:
        print(f"在 {input_path} 中没有找到支持的图片文件。")
        return

    print(f"找到 {len(files)} 个图片文件，开始处理...\n")

    success_count = 0
    fail_count = 0

    for input_file in tqdm(files, desc="处理进度", unit="张"):
        try:
            # 计算输出路径（递归模式下保持相对目录结构）
            if recursive:
                rel_path = input_file.relative_to(input_path)
                out_file = (output_path / rel_path.parent /
                            f"{rel_path.stem}{suffix}{rel_path.suffix}")
            else:
                out_file = output_path / f"{input_file.stem}{suffix}{input_file.suffix}"

            # 确保输出目录的父文件夹存在（递归模式可能需要）
            out_file.parent.mkdir(parents=True, exist_ok=True)

            # 1. 读取原图
            img = Image.open(input_file)

            # 2. 反色
            inverted = _invert_image(img)

            # 3. 保存反色图片
            inverted.save(out_file)

            # 4. 关闭图片（释放资源）
            img.close()
            inverted.close()

            # 5. 移动原文件到 complete 文件夹
            if keep_original:
                tqdm.write(f"[OK] {input_file.name} -> {out_file}")
            else:
                _safe_move(str(input_file), complete_path)
                tqdm.write(f"[OK] {input_file.name} -> {out_file}")

            success_count += 1

        except Exception as e:
            tqdm.write(f"[FAIL] {input_file.name}: {e}")
            fail_count += 1
            continue

    print(f"\n处理完毕。成功: {success_count}, 失败: {fail_count}")


def main():
    parser = argparse.ArgumentParser(
        description="图片反色批处理工具 — 将指定文件夹中的图片反色后输出。",
    )
    parser.add_argument(
        "-f", "--folder",
        default=None,
        help="文件夹路径：扫描文件夹下所有图片并在同目录下生成反色图片（原地模式）",
    )
    parser.add_argument(
        "-s", "--suffix",
        default="_converted",
        help="输出文件名后缀（默认: _converted）",
    )
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="递归处理子文件夹",
    )

    # --folder 模式下不需要的参数（仅传统模式使用）
    parser.add_argument(
        "-i", "--input-dir",
        default="input",
        help="输入文件夹路径（传统模式，默认: input）",
    )
    parser.add_argument(
        "-o", "--output-dir",
        default="output",
        help="输出文件夹路径（传统模式，默认: output）",
    )
    parser.add_argument(
        "-c", "--complete-dir",
        default="complete",
        help="存放已处理原图的文件夹路径（传统模式，默认: complete）",
    )
    parser.add_argument(
        "-k", "--keep-original",
        action="store_true",
        help="保留原文件，不移动到 complete 文件夹（传统模式）",
    )

    args = parser.parse_args()

    # --- 原地模式（--folder）---
    if args.folder is not None:
        folder_path = Path(args.folder).resolve()
        print(f"原地模式: 扫描 {folder_path}")
        print(f"后缀: {args.suffix}, 递归: {args.recursive}\n")

        results = batch_invert(
            folder=folder_path,
            suffix=args.suffix,
            recursive=args.recursive,
        )
        if results:
            print(f"\n处理完毕。成功生成 {len(results)} 个反色图片。")
        else:
            print(f"\n未找到需要处理的图片文件。")
        return

    # --- 传统模式（input → output / complete）---
    base_dir = Path(__file__).parent.parent.resolve()

    input_dir = (base_dir / args.input_dir).resolve()
    output_dir = (base_dir / args.output_dir).resolve()
    complete_dir = (base_dir / args.complete_dir).resolve()

    process_batch(
        input_dir=input_dir,
        output_dir=output_dir,
        complete_dir=complete_dir,
        suffix=args.suffix,
        keep_original=args.keep_original,
        recursive=args.recursive,
    )


if __name__ == "__main__":
    main()
