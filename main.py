#!/usr/bin/env python3
"""
向后兼容启动器 — 委托到 picinvert 包的 CLI 入口。

用法保持不变:
    python main.py                              # 使用默认路径（传统模式）
    python main.py -i ./images -o ./results     # 自定义输入/输出目录
    python main.py -k                           # 保留原文件
    python main.py -s _inverted                 # 自定义输出后缀
    python main.py -r                           # 递归处理子文件夹
    python main.py -f ./my_images               # 文件夹内原地反色（新模式）
"""

from picinvert._cli import main

if __name__ == "__main__":
    main()
