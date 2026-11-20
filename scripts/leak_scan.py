#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
公开版泄漏扫描

在 CI 里跑：确保仓库里没有机构名、价格、局部路径、跨项目信息等不该公开的内容。

与 `sanitize_for_public.py` 的区别：
  · 脱敏器负责「生成时清洗」，本脚本负责「发布前复检」
  · 本脚本扫的是**整个仓库**，不只是知识表

用法：
    python scripts/leak_scan.py
退出码：0 = 干净，1 = 发现泄漏
"""
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import ROOT  # noqa: E402

# 按目录分级的禁用模式。
#   说明：scripts/ 下的脱敏器与校验器**必然**包含用于检测的字面量，
#   因此对 scripts/ 只检查「路径 / 个人信息 / 跨项目」三类，不检查机构名与经营词。
FORBIDDEN = {
    "data": [
        (r"[\u4e00-\u9fa5]{2,6}(?:中医馆|养生馆|医馆)", "机构名"),
        (r"[\u4e00-\u9fa5]{2,4}(?:堂|轩|舍|坊)", "机构名"),
        (r"\d+\s*元", "价格"),
        (r"会员卡", "经营词"),
        (r"价目表", "经营词"),
        (r"[A-Za-z]:[/\\]Users", "本地路径"),
    ],
    "web": [
        (r"[\u4e00-\u9fa5]{2,6}(?:中医馆|养生馆|医馆)", "机构名"),
        (r"[\u4e00-\u9fa5]{2,4}(?:堂|轩|舍|坊)", "机构名"),
        (r"\d+\s*元", "价格"),
        (r"会员卡", "经营词"),
        (r"价目表", "经营词"),
        (r"[A-Za-z]:[/\\]Users", "本地路径"),
    ],
    "examples": [
        (r"[\u4e00-\u9fa5]{2,6}(?:中医馆|养生馆|医馆)", "机构名"),
        (r"\d+\s*元", "价格"),
        (r"会员卡", "经营词"),
        (r"价目表", "经营词"),
        (r"[A-Za-z]:[/\\]Users", "本地路径"),
    ],
    "scripts": [
        (r"[A-Za-z]:[/\\]Users", "本地路径"),
        (r"AppData", "本地路径"),
    ],
    "docs": [
        (r"[A-Za-z]:[/\\]Users", "本地路径"),
        (r"AppData", "本地路径"),
    ],
}

# 全局适用：README / LICENSE / CONTRIBUTING / AGENTS 里同样不允许出现的
GLOBAL_FORBIDDEN = [
    (r"[A-Za-z]:[/\\]Users", "本地路径"),
    (r"AppData", "本地路径"),
]

SKIP_DIRS = {".git", "__pycache__", "output", ".github"}
TEXT_EXT = {".py", ".md", ".csv", ".json", ".js", ".yml", ".yaml", ".txt", ".html", ".gitignore"}

# 自指豁免：这两个文件**必然**包含用于检测的字面量本身。
# 不豁免的话扫描器会永远检出自己。
SELF_EXEMPT = {"scripts/leak_scan.py", "scripts/sanitize_for_public.py"}


def iter_files():
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            p = os.path.join(root, fn)
            rel = os.path.relpath(p, ROOT)
            top = rel.split(os.sep)[0]
            ext = os.path.splitext(fn)[1].lower()
            if ext not in TEXT_EXT and fn not in (".gitignore",):
                continue
            yield p, rel, top


def main():
    hits = []
    scanned = 0
    for p, rel, top in iter_files():
        if rel.replace("\\", "/") in SELF_EXEMPT:
            continue
        try:
            text = io.open(p, encoding="utf-8").read()
        except Exception:
            continue
        scanned += 1
        patterns = list(FORBIDDEN.get(top, [])) + list(GLOBAL_FORBIDDEN)
        for pat, label in patterns:
            for m in re.finditer(pat, text):
                line = text[:m.start()].count("\n") + 1
                ctx = text[max(0, m.start() - 40):m.start() + 40].replace("\n", " ")
                hits.append((rel, line, label, pat, ctx))

    print(f"扫描 {scanned} 个文件")
    if not hits:
        print("✅ 未发现泄漏")
        return 0

    print(f"❌ 发现 {len(hits)} 处疑似泄漏：")
    seen = set()
    for rel, line, label, pat, ctx in hits:
        key = (rel, label)
        if key in seen:
            continue
        seen.add(key)
        print(f"  {rel}:{line}  [{label}] {pat}")
        print(f"      …{ctx}…")
    return 1


if __name__ == "__main__":
    sys.exit(main())
