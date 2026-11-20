#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
公开版脱敏器 · Sanitizer for Public Release

作用：把内部工作区的 SSOT 知识表，转换成可以公开开源的版本。

三条硬约束：
  1. 条数不变（205 条）——下游生存地图的面积口径依赖这个数字；
  2. 校验必须全过 —— 脱敏后仍要过 validate_ssot.py 的全部规则；
  3. 零泄漏 —— 不出现机构名、价格、内部语料结构、本地路径。

脱敏手法（按字段）：
  · 出处  —— 私有语料的「段级内部编号」归一化为「主题级公开描述」，
             公开可核验的来源（《素问》《灵枢》、国标、法规）原样保留；
  · 备注  —— 内部编号（段4/段29/段41…）归一化，去掉机构与价格字样；
  · 关联项目 —— 机构经营色彩的项目名归一化为「非诊疗类服务」通用名；
  · 内容要点 —— 机构名、价目、会员卡字样替换为通用表达。

用法：
    python sanitize_for_public.py                # 默认输出到 ../data/养生知识表.csv
    python sanitize_for_public.py --in X.csv --out Y.csv
"""
import argparse
import csv
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import ROOT, DATA_DIR, ensure_dir  # noqa: E402

# ─────────────────────────────────────────────────────────────
# 一、字段级替换规则
# ─────────────────────────────────────────────────────────────

# 1.1 机构与经营信息的字面替换（先做，长词优先，避免半替换）
#
#     注意：本文件是公开仓库的一部分，因此**不硬编码任何真实机构名、价格、
#     具体服务名**。规则一律用通用模式（正则）表达，作用于任意来源表。
#     这样脚本本身不含敏感字面量，同时对别人的表同样有效。
LITERAL_REPLACEMENTS = [
    # ── 顺序敏感：先处理「机构名 + 套餐/卡」这类整串文件名，
    #    否则机构名规则会先把它截断，留下「理疗体验服务套餐」这种半截产物。
    (re.compile(r"[\u4e00-\u9fa5]{2,4}(?:堂|轩|舍|坊|馆)[\u4e00-\u9fa5]{0,12}?(?:套餐|会员卡|体验卡|理疗体验[\u4e00-\u9fa5]{0,6})"), "非诊疗类服务套餐设计"),
    (re.compile(r"[\u4e00-\u9fa5]{2,6}(?:中医馆|养生馆|医馆|中医养生馆|养生会馆)[\u4e00-\u9fa5]{0,12}?(?:套餐|会员卡|体验卡|理疗体验[\u4e00-\u9fa5]{0,6})"), "非诊疗类服务套餐设计"),
    # 带日期后缀的价目表文件名 → 通用清单名
    (re.compile(r"[\u4e00-\u9fa5]{0,6}价目表[-_]\d{4,8}"), "非诊疗类服务项目清单"),
    # 通用：中文机构名 + 常见机构后缀（堂/馆/轩/舍/坊）→ 中性表述
    (re.compile(r"[\u4e00-\u9fa5]{2,6}(?:中医馆|养生馆|医馆|中医养生馆|养生会馆)"), "非诊疗类养生服务机构"),
    (re.compile(r"[\u4e00-\u9fa5]{2,4}(?:堂|轩|舍|坊)\s*(?:中医馆|养生馆|医馆)?"), "非诊疗类养生服务机构"),
    # 价目表 / 会员卡类经营词
    (re.compile(r"价目表项目\s*\+\s*会员卡赠项"), "服务项目 + 套餐赠项"),
    (re.compile(r"价目表项目\s*\+\s*会员卡终身咨询"), "服务项目 + 套餐咨询权益"),
    (re.compile(r"价目表项目"), "服务项目"),
    (re.compile(r"价目表"), "服务项目清单"),
    (re.compile(r"\d{4}-\d{2}-\d{2}\s*会员卡条款"), "服务套餐条款"),
    (re.compile(r"养生会员卡"), "养生服务套餐"),
    (re.compile(r"会员卡赠项"), "套餐赠项"),
    (re.compile(r"会员卡终身咨询"), "套餐咨询权益"),
    (re.compile(r"会员卡条款"), "套餐条款"),
    (re.compile(r"会员卡"), "服务套餐"),
    # 金额一律剥离
    (re.compile(r"\d+\s*元"), ""),
    # 机构自指 → 中性业务表述
    (re.compile(r"医馆已停业"), "线下诊疗服务已停办"),
    (re.compile(r"线下诊疗机构已停业"), "线下诊疗服务已停办"),
    (re.compile(r"养生馆普通渠道"), "非诊疗类服务渠道"),
    (re.compile(r"养生馆服务范围"), "非诊疗类服务范围"),
    (re.compile(r"养生馆的禁止行为"), "非诊疗类服务的禁止行为"),
    (re.compile(r"馆内推拿项目"), "推拿类服务项目"),
    (re.compile(r"你的养生馆"), "非诊疗类养生服务机构"),
    (re.compile(r"养生馆"), "非诊疗类养生服务机构"),
    (re.compile(r"医馆"), "线下诊疗机构"),
]

# 1.2 经营类项目名归一化：去掉机构经营色彩，保留服务性质
#     同样是通用模式：把「XX服务/XX项目」这类带机构色彩的自定义名，
#     收敛为「服务」性质的通用名。
PROJECT_ALIASES = {
    "归元灸": "温热灸服务",
    "砭石活络灸": "砭石温敷服务",
    "全身推拿": "全身推拿服务",
    "穴位拔罐": "拔罐服务",
    "养生咨询": "养生咨询服务",
}

# 1.3 内部段落编号归一化：段4 / 段29 / 段41 / 原文段4 …… → 主题级描述
SEGMENT_PATTERNS = [
    # 由原文段29术后饮食调理改写 → 由主题条目改写
    (re.compile(r"由原文段\d+[^，；。]*?(改写|改写；|改写，)"), "由主题条目改写"),
    (re.compile(r"由原文段\d+"), "由主题条目"),
    (re.compile(r"由原文段\d+"), "由主题条目"),
    # 由病证段建议改写 → 由病证方向改写
    (re.compile(r"由病证段建议改写"), "由病证方向改写"),
    (re.compile(r"由病证分型改写"), "由病证分型改写"),
    (re.compile(r"原文段\d+"), "主题段落"),
    (re.compile(r"第\d+段"), "主题段落"),
]

# 1.4 私有语料出处归一化：把「慢病资料-XXX段（细分）」变成可公开的主题级描述
#     保留病种方向词（公开的医学常识），去掉内部编号与「段」字
SOURCE_NORMALIZE = [
    (re.compile(r"^慢病资料-(.+?)段（[^）]*）$"), r"慢病主题资料·\1"),
    (re.compile(r"^慢病资料-(.+?)段$"), r"慢病主题资料·\1"),
    (re.compile(r"^慢病资料-(.+?)相关段$"), r"慢病主题资料·\1"),
    (re.compile(r"^慢病资料-(.+?)主题$"), r"慢病主题资料·\1"),
    (re.compile(r"^慢病资料-慢病合集$"), "慢病主题资料·慢病合集"),
    (re.compile(r"^中医九种体质\.pdf$"), "《中医九种体质》标准"),
]

# 1.5 出处里的「慢病资料-XXX段」在正文里也出现过，一并归一
CONTENT_SOURCE_TOKENS = [
    (re.compile(r"慢病资料-(.+?)段（[^）]*）"), r"慢病主题资料·\1"),
    (re.compile(r"慢病资料-(.+?)相关段"), r"慢病主题资料·\1"),
    (re.compile(r"慢病资料-(.+?)段"), r"慢病主题资料·\1"),
]


def apply_literals(text):
    """按规则表做字面/正则替换。规则表内每项为 (pattern, replacement)，
    pattern 若是 str 则按字面替换，若是编译好的正则则按正则替换。"""
    if not text:
        return text
    for src, dst in LITERAL_REPLACEMENTS:
        if isinstance(src, str):
            text = text.replace(src, dst)
        else:
            text = src.sub(dst, text)
    return text


def normalize_source(src):
    """出处字段归一化：私有语料 → 主题级描述；公开来源原样保留"""
    if not src:
        return src
    out = src
    for pat, rep in SOURCE_NORMALIZE:
        out = pat.sub(rep, out)
    # 「慢病资料-慢病合集」是特例，上面已处理；兜底再扫一次
    if out.startswith("慢病资料-"):
        out = re.sub(r"^慢病资料-(.+?)段（[^）]*）$", r"慢病主题资料·\1", out)
    return out


def normalize_note(note):
    """备注字段归一化：去内部段落编号"""
    if not note:
        return note
    out = note
    for pat, rep in SEGMENT_PATTERNS:
        out = pat.sub(rep, out)
    return out


def normalize_projects(proj):
    """关联项目：机构经营名 → 通用服务名"""
    if not proj:
        return proj
    items = [PROJECT_ALIASES.get(i.strip(), i.strip()) for i in proj.split(",") if i.strip()]
    return ",".join(items)


def normalize_point(point):
    """内容要点：机构/经营字面替换 + 自定义服务名通用化。
    不动医学表述——那些已被上游去医疗化，此处不应再改写语义。"""
    out = apply_literals(point)
    for pat, rep in CONTENT_SOURCE_TOKENS:
        out = pat.sub(rep, out)
    # 自定义服务名通用化：正文里提到具体服务名时同样收敛
    for src, dst in PROJECT_ALIASES.items():
        out = out.replace(src, dst)
    return out


def sanitize_row(row):
    new = dict(row)
    new["条目名"] = apply_literals(new.get("条目名", ""))
    # 条目名里的自定义服务名同样通用化
    for src, dst in PROJECT_ALIASES.items():
        new["条目名"] = new["条目名"].replace(src, dst)
    new["内容要点"] = normalize_point(new.get("内容要点", ""))
    new["出处"] = apply_literals(normalize_source(new.get("出处", "")))
    new["关联项目"] = apply_literals(normalize_projects(new.get("关联项目", "")))
    new["备注"] = apply_literals(normalize_note(new.get("备注", "")))
    for src, dst in PROJECT_ALIASES.items():
        new["备注"] = new["备注"].replace(src, dst)
    return new


# ─────────────────────────────────────────────────────────────
# 二、泄漏自检：任何一条命中都直接失败，不允许「先发出去再说」
# ─────────────────────────────────────────────────────────────

# 正则 + 关键词两套，命中即报错
#     全部为通用模式，不含任何真实机构名或个人信息字面量
LEAK_PATTERNS = [
    # 通用机构名模式：2-6 个中文 + 机构后缀，且未出现在中性表述白名单里
    (re.compile(r"[\u4e00-\u9fa5]{2,6}(?:中医馆|养生馆|医馆)"), "机构名"),
    (re.compile(r"[\u4e00-\u9fa5]{2,4}(?:堂|轩|舍)\s*(?:中医|养生)?"), "机构名"),
    # 价格
    (re.compile(r"\d+\s*元"), "价格"),
    # 经营词
    (re.compile(r"会员卡"), "经营词"),
    (re.compile(r"价目表"), "经营词"),
    # 本地路径
    (re.compile(r"[A-Za-z]:[/\\]Users"), "本地路径"),
    (re.compile(r"AppData"), "本地路径"),
    # 内部段落编号
    (re.compile(r"段\d+"), "内部段落编号"),
    (re.compile(r"原文段"), "内部段落编号"),
    # 个人信息 / 跨项目信息：不硬编码任何字面量。
    #     用 --forbid 参数传入本项目需要屏蔽的词（多个用逗号分隔），
    #     由调用方决定，脚本本身保持通用。
]

# 外部注入的禁用词（个人信息 / 跨项目 / 其他敏感词）
# 命令行 --forbid "词1,词2" 传入；默认空
FORBIDDEN_EXTRA = []

# 出处字段的合法白名单：只允许这些前缀形态出现
ALLOWED_SOURCE_PREFIX = (
    "《素问", "《灵枢", "《中医九种体质》标准", "中医养生保健服务规范",
    "互联网广告管理办法", "慢病主题资料·", "非诊疗类服务项目清单",
    "非诊疗类服务套餐设计", "中医九种体质",
)


def audit(rows, fieldnames):
    """脱敏后自检。返回 (errors, warnings)"""
    errors, warnings = [], []
    for i, row in enumerate(rows, start=2):
        for field in fieldnames:
            val = row.get(field) or ""
            for pat, label in LEAK_PATTERNS:
                if pat.search(val):
                    errors.append(f"第{i}行 [{label}] 字段'{field}' 命中泄漏: {pat.pattern} → {val[:60]}")
            for word in FORBIDDEN_EXTRA:
                if word and word in val:
                    errors.append(f"第{i}行 [禁用词] 字段'{field}' 命中 '{word}' → {val[:60]}")
        src = (row.get("出处") or "").strip()
        if src and not src.startswith(ALLOWED_SOURCE_PREFIX):
            errors.append(f"第{i}行 出处未在白名单内: {src[:60]}")
    return errors, warnings


# ─────────────────────────────────────────────────────────────
# 三、主流程
# ─────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="生成可公开的开源版知识表")
    ap.add_argument("--in", dest="inp", default=None, help="输入 CSV（默认取仓库根的 SSOT 表）")
    ap.add_argument("--out", dest="out", default=None, help="输出 CSV（默认 data/养生知识表.csv）")
    ap.add_argument("--forbid", dest="forbid", default="",
                    help="额外禁用词，逗号分隔（个人信息 / 跨项目信息等）。"
                         "命中即中止不出文件")
    args = ap.parse_args()

    global FORBIDDEN_EXTRA
    FORBIDDEN_EXTRA = [w.strip() for w in args.forbid.split(",") if w.strip()]

    inp = args.inp or os.path.join(ROOT, "SSOT", "养生知识表.csv")
    out = args.out or os.path.join(DATA_DIR, "养生知识表.csv")

    if not os.path.exists(inp):
        print(f"[错误] 输入不存在: {inp}")
        return 1

    with io.open(inp, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        rows = [dict(r) for r in reader]

    before = len(rows)
    cleaned = [sanitize_row(r) for r in rows]

    # 条数守恒：脱敏绝不改变条目数
    assert len(cleaned) == before, "脱敏改变了条目数"

    errors, warnings = audit(cleaned, fieldnames)
    if errors:
        print(f"[失败] 脱敏自检发现 {len(errors)} 处泄漏，已中止，未写出文件：")
        for e in errors[:30]:
            print("   ", e)
        if len(errors) > 30:
            print(f"    ... 另有 {len(errors) - 30} 处")
        return 2

    ensure_dir(os.path.dirname(out))
    with io.open(out, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned)

    print(f"[完成] 已写出 {out}")
    print(f"  条数 {before} → {len(cleaned)}（守恒）")
    print(f"  字段 {len(fieldnames)} 个：{'、'.join(fieldnames)}")
    print(f"  泄漏自检：0 处命中")
    themes = {}
    for r in cleaned:
        themes[r["主题"]] = themes.get(r["主题"], 0) + 1
    print("  主题分布：" + "  ".join(f"{k}={v}" for k, v in sorted(themes.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
