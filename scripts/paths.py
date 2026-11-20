#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
统一路径解析

所有脚本都从这里取路径，避免各自硬编码目录名。
目录约定：

    <repo>/
      data/      单一真相源（SSOT）：知识表、食药清单、出处对照表
      scripts/   构建与校验脚本
      web/       可直接双击打开的成品（生存地图、体质自测）
      output/    生成物输出（早报等）
      docs/      方法论与口径文档

用法：
    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from paths import ROOT, DATA_DIR, WEB_DIR, OUTPUT_DIR, SCRIPTS_DIR
"""
import os

# scripts/ 的上级 = 仓库根
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPTS_DIR)

DATA_DIR = os.path.join(ROOT, "data")
WEB_DIR = os.path.join(ROOT, "web")
OUTPUT_DIR = os.path.join(ROOT, "output")
DOCS_DIR = os.path.join(ROOT, "docs")

# 具体文件
SSOT_CSV = os.path.join(DATA_DIR, "养生知识表.csv")
FOOD_MED_JSON = os.path.join(DATA_DIR, "食药清单.json")
SOURCE_MAP_MD = os.path.join(DATA_DIR, "节气经典_出处对照表.md")

SURVIVAL_MAP_HTML = os.path.join(WEB_DIR, "养生一人公司生存地图.html")
CONSTITUTION_HTML = os.path.join(WEB_DIR, "体质自测.html")
SIM_JS = os.path.join(SCRIPTS_DIR, "sim_engine.js")

BRIEF_OUT_DIR = os.path.join(OUTPUT_DIR, "早报")


def ensure_dir(path):
    """确保目录存在，返回该目录"""
    os.makedirs(path, exist_ok=True)
    return path
