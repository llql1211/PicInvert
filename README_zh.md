# PicInvert

[English](README.md) | **中文**

一款轻量级的图片反色批处理工具，基于 Pillow 构建。

## 安装

```bash
pip install -e .
```

## 使用

### 原地文件夹模式（推荐）

扫描文件夹中的图片，在原图片同目录下生成反色副本。已处理过的文件会自动跳过。

```bash
picinvert -f ./my_photos
```

选项：

|         参数          |              说明                             |    默认值    |
|-----------------------|-----------------------------------------------|----------------|
| `-f` / `--folder`     | 目标文件夹路径                                |       —      |
| `-s` / `--suffix`     | 输出文件名后缀                                | `_converted` |
| `-r` / `--recursive`  | 递归处理子文件夹                              |     关       |
| `-m` / `--mode`       | 反色模式 (`standard` / `hsv` / `black-white`) | `black-white` |

示例：

```bash
# 自定义后缀
picinvert -f ./photos -s _inverted

# 递归处理
picinvert -f ./photos -r

# 标准 RGB 反色（255 - 各通道像素值）
picinvert -f ./photos -m standard

# HSV 明度反转（保留色相和饱和度）
picinvert -f ./photos -m hsv

# 黑白灰反色（保留彩色区域不变）
picinvert -f ./photos -m black-white

# 组合使用
picinvert -f ./photos -s _done -r
```

### 传统模式（输入 → 输出）

将图片从输入文件夹复制到输出文件夹处理，可选择在处理后将原文件移动到"完成"文件夹。

```bash
picinvert                    # 使用 ./input → ./output，原文件移入 ./complete
picinvert -k                 # 保留原文件
picinvert -i ./src -o ./dst  # 自定义路径
```

### 作为 Python API 使用

```python
from picinvert import invert, batch_invert

# 单张图片（默认 HSV 明度反转）
invert("photo.jpg", suffix="_inverted")

# 标准 RGB 反色
invert("photo.jpg", suffix="_inverted", invert_mode="standard")

# 黑白灰反色（保留彩色区域）
invert("photo.jpg", suffix="_inverted", invert_mode="black-white")

# 批量 — 扫描文件夹，反色，在同目录保存
batch_invert("./photos", suffix="_converted")
```

## 反色模式对比

|              | 标准反色 (`standard`)             | HSV 明度反转 (`hsv`)                        | 黑白灰反色 (`black-white`)                       |
|--------------|-----------------------------------|---------------------------------------------|--------------------------------------------------|
| **算法**     | `255 - 各通道像素值`              | 转为 HSV 色彩空间，只反转 V（明度）通道     | 转为 HSV，仅对饱和度 S 低于阈值的像素反转 V     |
| **色相**     | 反转（红⟷青，蓝⟷黄，绿⟷紫）       | ✅ **保持不变**                             | ✅ **保持不变**                                  |
| **饱和度**   | 连带反转                          | ✅ **保持不变**                             | ✅ **保持不变**                                  |
| **效果**     | 色调完全改变，类似胶片负片效果    | 原始色彩关系保留，仅亮度反转；更柔和        | 只有黑白灰区域被反色，彩色区域完全不变          |
| **适用场景** | 需要完整负片效果时                | 希望保留颜色关系，仅调整明暗分布时          | 图片中有彩色物体，只想反色背景或灰度区域时      |

## 支持的格式

jpg、jpeg、png、bmp、gif、tiff、webp

RGBA 格式的图片只反转 RGB 通道，保留原始 Alpha 通道。其他色彩模式在反色前会自动转为 RGB。
