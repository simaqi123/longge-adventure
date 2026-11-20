#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Validator for the English survival map.

The English page is generated from the same numeric model as the Chinese one,
so the two must agree on every number that matters.  This validator checks
that agreement, plus the structural invariants, plus the English-specific
compliance requirements.

What it checks:
    1. The three structural invariants (material conservation, one cash
       outlet, one area metric).
    2. The English page's numbers match the Chinese model's numbers exactly.
    3. The disclaimer is present, in English, and says the right things.
    4. No contact details, external links or QR codes leaked into the page.
    5. No Chinese prose (except real file names, which a reader must type).

Usage:
    python scripts/validate_en_map.py
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import WEB_DIR  # noqa: E402

HTML_PATH = os.path.join(WEB_DIR, "solo-wellness-map.en.html")

# Contact details / outbound links — never allowed on a knowledge page.
CONTACT_PATTERNS = [
    (re.compile(r"\b1[3-9]\d{9}\b"), "phone number"),
    (re.compile(r"\b\d{3,4}-\d{7,8}\b"), "phone number"),
    (re.compile(r"weixin|wechat|微信|qq\s*[:：]\s*\d{5,}"), "contact handle"),
    (re.compile(r"https?://(?!github\.com|www\.workbuddy\.cn)[^\s\"'<>]+"), "external link"),
    (re.compile(r"wxp://|weixin://"), "wechat scheme link"),
    (re.compile(r"二维码|扫码|scan.{0,10}code"), "QR / scan prompt"),
    # social handle — but not a CSS at-rule (@media, @keyframes, ...)
    (re.compile(r"(?<![\w@])@(?!media|keyframes|supports|font-face|import|charset|"
                r"namespace|layer|container|property|viewport|counter-style|"
                r"font-feature-values|starting-style)[A-Za-z][A-Za-z0-9_.]{3,24}"), "social handle"),
]

DISCLAIMER_MARKERS = [
    "no medical advice",
    "not a diagnosis",
    "qualified healthcare professional",
]

# Real file names that are Chinese and must stay verbatim.
ALLOWED_CJK_FILES = [
    "节气经典_出处对照表.md",
    "早报推送通道_腾讯文档.md",
    "契约层.md",
]


def main():
    if not os.path.exists(HTML_PATH):
        print(f"[跳过] {HTML_PATH} 不存在")
        return

    with open(HTML_PATH, encoding="utf-8") as f:
        html = f.read()

    errors, warns = [], []

    # ---- extract the embedded payload -------------------------------------
    m = re.search(r"const DATA = (\{.*?\});\n", html, re.S)
    if not m:
        print("❌ 未能从页面中提取 DATA 载荷")
        sys.exit(1)
    data = json.loads(m.group(1))

    items = data["items"]
    order = data["order"]
    deep = data["deep"]

    # ---- 1. structural invariants ----------------------------------------
    if len(items) != 10:
        errors.append(f"位次数量应为 10，实际 {len(items)}")
    if len(order) != len(set(order)):
        errors.append("位次 key 存在重复")

    total_material = sum(i["material"] for i in items)
    if total_material != 205:
        errors.append(f"独占素材合计应为 205，实际 {total_material}")

    cash = [i for i in items if i.get("is_cash")]
    if len(cash) != 1:
        errors.append(f"现金出口应恰好 1 个，实际 {len(cash)}")

    channels = [i for i in items if i.get("is_channel")]
    if len(channels) != 3:
        errors.append(f"成品出口应恰好 3 个，实际 {len(channels)}")

    # ---- 2. the English numbers match the model ---------------------------
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import survival_deep_model as M  # noqa: E402

    model = M.build_deep_model()
    for key in order:
        if key not in model["roles"]:
            errors.append(f"位次 '{key}' 不在深度模型中")
            continue
        want = model["roles"][key]["area"]
        got = next((i["area"] for i in items if i["key"] == key), None)
        if want != got:
            errors.append(f"位次 '{key}' 面积不一致：模型 {want} vs 页面 {got}")

    total_area_model = sum(model["roles"][k]["area"] for k in model["order"])
    total_area_page = sum(i["area"] for i in items)
    if total_area_model != total_area_page:
        errors.append(f"面积合计不一致：模型 {total_area_model} vs 页面 {total_area_page}")

    # ---- 3. disclaimer ----------------------------------------------------
    body = re.sub(r"<script[\s\S]*?</script>", " ", html)
    body = re.sub(r"<style[\s\S]*?</style>", " ", body)
    visible = re.sub(r"<[^>]+>", " ", body).lower()
    for marker in DISCLAIMER_MARKERS:
        if marker.lower() not in visible:
            errors.append(f"免责声明缺少关键表述: '{marker}'")

    # ---- 4. no contact details or outbound links ---------------------------
    # CSS is the main source of false positives (@media, url(...)), so scan
    # the document with <style> blocks removed.
    contact_probe = re.sub(r"<style[\s\S]*?</style>", " ", html)
    for pat, label in CONTACT_PATTERNS:
        hit = pat.search(contact_probe)
        if hit:
            ctx = contact_probe[max(0, hit.start() - 50):hit.end() + 50].replace("\n", " ")
            errors.append(f"页面含{label}: …{ctx}…")

    # ---- 5. no Chinese prose ---------------------------------------------
    probe = html
    for name in ALLOWED_CJK_FILES:
        probe = probe.replace(name, "")
    leftover = sorted(set(re.findall(r"[一-鿿]+", probe)))
    if leftover:
        for w in leftover:
            hit = re.search(re.escape(w), probe)
            ctx = probe[max(0, hit.start() - 60):hit.end() + 40].replace("\n", " ")
            errors.append(f"英文页面出现中文 '{w}': …{ctx}…")

    # ---- 6. the page must not promise revenue ----------------------------
    revenue_markers = re.findall(
        r"(projected monthly income|guaranteed (?:revenue|income|earnings)|"
        r"expected revenue|revenue forecast)", html, re.I)
    if revenue_markers:
        errors.append(f"页面出现收入承诺表述: {sorted(set(revenue_markers))}")

    # ---- report -----------------------------------------------------------
    print("=== English survival map ===")
    print(f"  role slots        : {len(items)}")
    print(f"  exclusive material: {total_material}")
    print(f"  total monthly area: {total_area_page} pieces")
    print(f"  cash outlets      : {len(cash)}")
    print(f"  output slots      : {len(channels)}")
    print(f"  roadmap phases    : {len(data['roadmap'])}")
    print(f"  risk criteria     : {len(data['risks'])}")
    print(f"  monetization links: {len(data['funnel'])}")

    if warns:
        print(f"\n  警告 {len(warns)} 条：")
        for w in warns[:10]:
            print(f"    {w}")

    if errors:
        print(f"\n❌ 错误 {len(errors)} 条：")
        for e in errors[:25]:
            print(f"    {e}")
        sys.exit(1)

    print("\n✅ 全部通过。")


if __name__ == "__main__":
    main()
