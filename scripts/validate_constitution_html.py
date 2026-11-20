# -*- coding: utf-8 -*-
"""体质自测工具 · 红线校验器

针对用户明确提出的红线做机器校验：
  「结果页无联系方式无链接」

校验分层：
  L1 结果页专属红线：联系方式、URL、二维码、外链、社交账号、电话
  L2 全页合规：病名、疗效断言、问诊诱导、特定人群限定、侵入性项目
  L3 结构完整性：免责声明在位、「不构成诊断」在位、题库与结果文案齐备、
                  结果页文案可溯源到 SSOT 条目

用法：python validate_constitution_html.py
"""
import csv
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import CONSTITUTION_HTML as HTML_PATH, SSOT_CSV as SSOT  # noqa: E402

# ── L1：结果页专属红线 ──────────────────────────────
RESULT_PAGE_FORBIDDEN = [
    # 联系方式形态
    (r"1[3-9]\d{9}", "手机号"),
    (r"\b\d{3,4}-\d{7,8}\b", "固定电话"),
    (r"(?:微信|VX|vx|weixin|WeChat)\s*[:：]?\s*[A-Za-z0-9_-]{4,}", "微信号"),
    (r"(?:QQ|qq)\s*[:：]?\s*[0-9]{5,}", "QQ号"),
    (r"(?:电话|手机|联系方式|联系地址)\s*[:：]", "联系方式字段"),
    (r"(?:扫码|二维码|扫一扫|长按识别)", "扫码引导"),
    (r"(?:微信号|公众号|小程序|抖音号|小红书号|视频号|企业微信)\s*[:：]", "社交账号"),
    # 链接
    (r"https?://", "http(s) 外链"),
    (r"www\.", "www 外链"),
    (r"\b[a-z0-9-]+\.(?:com|cn|net|org|top|xyz|cc)\b", "疑似域名"),
    (r"mailto:", "邮件链接"),
    (r"tel:", "电话链接"),
    (r"<a\s[^>]*href", "超链接标签"),
    (r"二维码", "二维码"),
    # 导流
    (r"(?:加入|联系|添加)\s*(?:我们|微信|群|客服|老师|师)", "私域引流"),
    (r"(?:立即|马上)?\s*(?:购买|下单|充值|报名|优惠|特价|限时)", "购买导流"),
]

# ── L2：全页合规（与 SSOT 校验器同源词表） ──────────
FORBIDDEN_TERMS = [
    "治疗", "根治", "治愈", "防治", "专治", "疗效", "有效率", "治愈率",
    "消炎", "杀菌", "排毒", "祛湿", "活血化瘀", "滋阴补阳", "疏通经络",
    "包治", "一次见效", "保证见效", "无副作用", "祖传秘方", "诊断",
    "辨证结果", "医嘱", "处方",
]
EFFICACY_CLAIMS = [
    "养心安神", "安神", "养心安", "清润养阴", "养阴", "健脾养胃", "健脾",
    "理气化痰", "化痰软坚", "化痰", "散结", "清肝明目", "清肝", "润肺止咳",
    "润肺", "活血化瘀", "活血", "调经", "行气", "平补气血", "温补气血",
    "益气养血", "补气", "疏肝理气", "理气和胃", "清利湿热", "化湿消滞",
    "化湿", "生津", "养胃", "清热利胆", "祛湿", "渗湿", "利水消肿",
    "降压", "降脂", "化痰止咳", "温肾助阳", "温阳", "助阳", "滋阴",
    "壮阳", "温经", "通络", "排毒", "增强免疫", "提高免疫", "促进消化",
    "改善睡眠", "缓解疲劳", "抗氧化", "降三高", "软化血管", "开胃消食",
    "消食化积", "止咳化痰", "平喘",
]
# 病名（结果页/题库均不得出现）——独立于 FORBIDDEN_TERMS
DISEASE_NAMES = [
    "糖尿病", "高血压", "高血脂", "高尿酸", "痛风", "冠心病", "心脏病",
    "脑梗", "脑卒中", "中风", "脑出血", "动脉硬化", "动脉粥样硬化",
    "脂肪肝", "肝炎", "肝硬化", "脂肪肝", "胆结石", "胆囊炎", "胰腺炎",
    "胃溃疡", "胃炎", "反流", "肠炎", "阑尾炎", "便秘", "腹泻",
    "痔疮", "肾结石", "肾衰竭", "尿毒症", "肾病", "肾炎", "膀胱炎",
    "前列腺增生", "尿频", "尿急", "水肿", "甲亢", "甲减", "甲状腺",
    "甲亢", "糖尿病足", "贫血", "白血病", "淋巴瘤", "癌症", "肿瘤",
    "肺癌", "肝癌", "胃癌", "乳腺癌", "大肠癌", "食管癌", "宫颈癌",
    "子宫内膜癌", "子宫肌瘤", "乳腺增生", "前列腺癌", "骨关节炎",
    "类风湿", "痛风性关节炎", "颈椎病", "腰椎间盘", "肩周炎", "湿疹",
    "荨麻疹", "银屑病", "带状疱疹", "痤疮", "失眠症", "抑郁症",
    "焦虑症", "阿尔茨海默", "帕金森", "甲流", "新冠", "肺结核",
    "哮喘", "慢阻肺", "肺心病", "肺炎", "支气管炎", "脂肪肝", "痛经",
    "闭经", "月经失调", "不孕", "流产", "盆腔炎", "附件炎", "宫外孕",
]
SPECIFIC_POPULATION = [
    "产后", "孕期", "孕妇", "妊娠", "哺乳期", "小儿", "婴幼儿", "化疗",
    "放疗", "手术后", "久病", "康复期", "ICU", "透析", "移植后", "癌", "症", "征",
]
DIAGNOSTIC_PROBES = [
    "哪里不舒服", "什么症状", "开方", "看下病", "帮我诊", "辨证论治",
    "对症下药", "来看看", "来复查", "带病历", "病情如何", "严重吗", "是不是病",
]
FORBIDDEN_PROJECTS = ["针灸", "埋线", "刺血", "放血", "发泡灸", "瘢痕灸", "牵引", "扳法"]

# 允许出现的"否定语境"白名单：这些短语出现在免责声明里，属于必要免责表述
NEGATION_CONTEXT = [
    "不构成诊断", "不替代医疗诊断", "不是疾病判断", "请至医疗机构就诊",
    "由医师面诊", "不是诊断", "不构成医疗诊断", "若需要了解具体健康状况",
]


def strip_negation_context(text):
    """剔除否定语境免责段落后再检测，避免把免责声明误判为违规。"""
    for phrase in NEGATION_CONTEXT:
        # 把含该短语的整句替换掉
        text = re.sub(r"[^。\n]*" + re.escape(phrase) + r"[^。\n]*", "", text)
    return text


def split_result_page(html_text):
    """切出结果页文本。

    覆盖三个范围，缺一不可：
      1. HTML 中 <div id="result-page"> 容器内的全部内容
      2. JS 的 RESULTS 结果文案对象
      3. JS 里 showResult() 的渲染逻辑（含动态拼出的免责文案）
    另外，注入内容常被塞在 </body> 前——那属于页面级文本，
    由 L2 全页可见文案扫描兜底；此处额外把 result-page 容器之后到
    </body> 之间的静态 HTML 也纳入 L1，避免绕过。
    """
    # 1. HTML 结果页容器：取到容器结束为止（用 div 配平计数）
    html_part = ""
    m = re.search(r'<div id="result-page"[^>]*>', html_text)
    if m:
        start = m.start()
        depth = 0
        i = m.start()
        for mm in re.finditer(r'<div\b[^>]*>|</div>', html_text[m.start():]):
            if mm.group(0).startswith("</div"):
                depth -= 1
                if depth == 0:
                    html_part = html_text[start:start + mm.end()]
                    break
            else:
                depth += 1
        else:
            html_part = html_text[start:]
    # 2. RESULTS 对象
    m2 = re.search(r"const RESULTS = (\{.*?\});\n", html_text, re.S)
    js_part = m2.group(1) if m2 else ""
    # 3. showResult 渲染逻辑
    m3 = re.search(r"function showResult\(\)\{(.*?)\n\}", html_text, re.S)
    js_show = m3.group(1) if m3 else ""
    # 4. 结果页容器之后到 </body> 之前的静态内容（注入测试常落此处）
    tail = ""
    if m:
        end_marker = html_text.find("</body>")
        if end_marker > m.end():
            tail = html_text[m.end():end_marker]
    return "\n".join([html_part, js_part, js_show, tail])


def main():
    if not os.path.exists(HTML_PATH):
        print(f"❌ 未找到：{HTML_PATH}")
        return 1
    html_text = open(HTML_PATH, encoding="utf-8").read()

    errors, warns, checks = [], [], []

    # ── L1 结果页专属红线 ──
    result_page = split_result_page(html_text)
    if not result_page.strip():
        errors.append("L1：未能切出结果页内容，解析失败")
    scan_result = strip_negation_context(result_page)
    for pat, name in RESULT_PAGE_FORBIDDEN:
        hit = re.search(pat, scan_result)
        if hit:
            errors.append(f"L1 结果页出现{name}：{hit.group(0)!r}")
    checks.append(f"L1 结果页红线扫描（{len(RESULT_PAGE_FORBIDDEN)} 类）")

    # ── L2 全页合规 ──
    # 2.1 页面可见文案（去掉 CSS/JS 代码块，只看渲染出来的文字）
    visible = re.sub(r"<style[^>]*>.*?</style>", " ", html_text, flags=re.S)
    visible = re.sub(r"<script[^>]*>.*?</script>", " ", visible, flags=re.S)
    visible = re.sub(r"<[^>]+>", " ", visible)
    visible = strip_negation_context(visible)
    for name, terms in [
        ("医疗化表述", FORBIDDEN_TERMS),
        ("疗效断言", EFFICACY_CLAIMS),
        ("特定人群限定", SPECIFIC_POPULATION),
        ("问诊诱导", DIAGNOSTIC_PROBES),
        ("侵入性项目", FORBIDDEN_PROJECTS),
        ("病名", DISEASE_NAMES),
    ]:
        hits = [t for t in terms if t in visible]
        if hits:
            errors.append(f"L2 页面可见文案含{name}：{hits}")
    checks.append(f"L2 全页合规扫描（6 类词表，病名词表 {len(DISEASE_NAMES)} 条）")

    # 2.2 题目文本本身也扫一遍（含 JS 里的题库）
    m_q = re.search(r"const QUESTIONS = (\[.*?\]);\n", html_text, re.S)
    if not m_q:
        errors.append("L2：未能解析 QUESTIONS 题库")
    else:
        qtext = strip_negation_context(m_q.group(1))
        for name, terms in [
            ("医疗化表述", FORBIDDEN_TERMS),
            ("疗效断言", EFFICACY_CLAIMS),
            ("特定人群限定", SPECIFIC_POPULATION),
            ("问诊诱导", DIAGNOSTIC_PROBES),
            ("病名", DISEASE_NAMES),
        ]:
            hits = [t for t in terms if t in qtext]
            if hits:
                errors.append(f"L2 题库含{name}：{hits}")
        # 题目不得含联系方式/链接
        for pat, nm in [(r"https?://", "外链"), (r"1[3-9]\d{9}", "手机号"),
                        (r"(?:微信|QQ)\s*[:：]", "社交账号")]:
            hit = re.search(pat, qtext)
            if hit:
                errors.append(f"L2 题库出现{nm}：{hit.group(0)!r}")
    checks.append("L2 题库合规扫描")

    # ── L3 结构完整性 ──
    # 3.1 免责声明在位
    if "不构成诊断" not in html_text and "不替代医疗诊断" not in html_text:
        errors.append("L3：缺少免责声明「不构成诊断 / 不替代医疗诊断」")
    checks.append("L3 免责声明在位")

    # 3.2 免责声明必须完整（含就医指引）
    if "医疗机构就诊" not in html_text and "医师面诊" not in html_text:
        errors.append("L3：缺少就医指引「医疗机构就诊 / 医师面诊」")
    checks.append("L3 就医指引在位")

    # 3.3 免责白名单不得被削弱——负向检查
    for bad in ["仅供参考，无需就医", "无需就医", "不必看医生", "可以代替医生"]:
        if bad in html_text:
            errors.append(f"L3：出现削弱免责的表述 {bad!r}")
    checks.append("L3 免责未被削弱")

    # 3.4 题库规模与九种体质覆盖
    if m_q:
        qlist = re.findall(r"""['"]stem['"]:\s*['"](.*?)['"]""", m_q.group(1))
        if len(qlist) < 30:
            errors.append(f"L3：题库仅 {len(qlist)} 题，少于 30")
        cons = set(re.findall(r"""['"]cons['"]:\s*['"]([^'"]+)['"]""", m_q.group(1)))
        need = {"气虚质", "阳虚质", "阴虚质", "痰湿质", "湿热质",
                "血瘀质", "气郁质", "气滞质", "肺燥质"}
        miss = need - cons
        if miss:
            errors.append(f"L3：体质覆盖不全，缺 {sorted(miss)}")
        checks.append(f"L3 题库 {len(qlist)} 题 · 覆盖 {len(cons)} 种体质")

    # 3.5 结果页文案必须可溯源到 SSOT 条目
    with open(SSOT, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    ssot_con = {r["内容要点"] for r in rows if r["主题"] == "体质"}
    ssot_ids = {r["ID"] for r in rows}
    ssot_point = {r["ID"]: r["内容要点"] for r in rows}
    m_r = re.search(r"const RESULTS = (\{.*?\});\n", html_text, re.S)
    if m_r:
        # 每条建议是 {'id': 'W-xxx', 'text': '...'}，逐条核对 id 存在且 text 与 SSOT 原文逐字一致
        pairs = re.findall(
            r"""['"]id['"]:\s*['"]([^'"]+)['"],\s*['"]text['"]:\s*['"](.*?)['"]\}""",
            m_r.group(1), re.S)
        if not pairs:
            errors.append("L3：结果页建议未按 SSOT ID 引用结构生成")
        for sid, text in pairs:
            if sid not in ssot_ids:
                errors.append(f"L3：结果页引用了不存在的 SSOT 条目 {sid}")
            elif text != ssot_point[sid]:
                errors.append(f"L3：结果页 {sid} 文案与 SSOT 原文不一致")
        if pairs:
            checks.append(f"L3 结果页 {len(pairs)} 条建议逐字溯源到 SSOT 条目")
    else:
        errors.append("L3：未能解析 RESULTS 结果文案")

    # 3.6 无外链资源（离线可开）
    ext = re.findall(r'(?:src|href)\s*=\s*["\'](https?://[^"\']+)', html_text)
    if ext:
        errors.append(f"L3：引用了外部资源（离线打不开）：{ext[:3]}")
    else:
        checks.append("L3 零外部资源依赖（离线可开）")

    # ── 输出 ──
    print("=" * 62)
    print("体质自测工具 · 红线校验")
    print("=" * 62)
    for c in checks:
        print(f"  ✓ {c}")
    if warns:
        print("\n警告：")
        for w in warns:
            print(f"  ⚠ {w}")
    if errors:
        print("\n错误：")
        for e in errors:
            print(f"  ✗ {e}")
        print(f"\n总计错误 {len(errors)} 条。")
        return 1
    print("\n✅ 全部通过。结果页无联系方式、无链接、无二维码、无外链。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
