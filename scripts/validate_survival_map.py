# -*- coding: utf-8 -*-
"""养生一人公司生存地图 · 合规与真实性校验器

三层防线：
    L1  合规红线   —— 全页可见文案不得出现疗效断言、用药名、特定人群、
                      问询诱导、侵入性项目、联系方式与外链
    L2  结构完整性 —— 四页签齐全、treemap 有方块、免责在位且未被削弱、
                      零外部资源依赖
    L3  真实性     —— 页面上的每个数字必须与 SSOT 知识表实际统计一致。
                      这是本图区别于陈磊原图的关键：他的面积口径是自报数字，
                      本图的面积口径必须可回溯。

用法：python validate_survival_map.py
"""

import csv
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import SURVIVAL_MAP_HTML as HTML_PATH, SSOT_CSV as SSOT_PATH  # noqa: E402

# ─────────────────────────────────────────────────────────────
# 词表（与 validate_ssot.py / validate_constitution_html.py 同源）
# ─────────────────────────────────────────────────────────────
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
    "化湿", "生津", "养胃", "清热利胆", "祛湿", "渗湿", "利水消肿", "降压",
    "降脂", "化痰止咳", "温肾助阳", "温阳", "助阳", "滋阴", "壮阳",
    "温经", "通络", "排毒", "增强免疫", "提高免疫", "促进消化", "改善睡眠",
    "缓解疲劳", "抗氧化", "降三高", "软化血管", "开胃消食", "消食化积",
    "止咳化痰", "平喘",
]
SPECIFIC_POPULATION = [
    "产后", "孕期", "孕妇", "妊娠", "哺乳期", "小儿", "婴幼儿", "化疗",
    "放疗", "手术后", "久病", "康复期", "ICU", "透析", "移植后",
    "癌", "症", "征",
]
DIAGNOSTIC_PROBES = [
    "哪里不舒服", "什么症状", "开方", "看下病", "帮我诊", "辨证论治",
    "对症下药", "来看看", "来复查", "带病历", "病情如何", "严重吗", "是不是病",
]
FORBIDDEN_PROJECTS = [
    "针灸", "埋线", "刺血", "放血", "发泡灸", "瘢痕灸", "牵引", "扳法",
]
DISEASE_NAMES = [
    "糖尿病", "高血压", "高血脂", "高尿酸", "痛风", "冠心病", "心脏病",
    "脑梗", "脑卒中", "中风", "脑出血", "动脉硬化", "动脉粥样硬化",
    "脂肪肝", "肝炎", "肝硬化", "胆结石", "胆囊炎", "胰腺炎", "胃溃疡",
    "胃炎", "反流", "肠炎", "阑尾炎", "便秘", "腹泻", "痔疮", "肾结石",
    "肾衰竭", "尿毒症", "肾病", "肾炎", "膀胱炎", "前列腺增生", "尿频",
    "尿急", "水肿", "甲亢", "甲减", "甲状腺", "糖尿病足", "贫血",
    "白血病", "淋巴瘤", "癌症", "肿瘤", "肺癌", "肝癌", "胃癌", "乳腺癌",
    "大肠癌", "食管癌", "宫颈癌", "子宫内膜癌", "子宫肌瘤", "乳腺增生",
    "前列腺癌", "骨关节炎", "类风湿", "痛风性关节炎", "颈椎病", "腰椎间盘",
    "肩周炎", "湿疹", "荨麻疹", "银屑病", "带状疱疹", "痤疮", "失眠症",
    "抑郁症", "焦虑症", "阿尔茨海默", "帕金森", "甲流", "新冠", "肺结核",
    "哮喘", "慢阻肺", "肺心病", "肺炎", "支气管炎", "痛经", "闭经",
    "月经失调", "不孕", "流产", "盆腔炎", "附件炎", "宫外孕",
]
# 引流类（对外页面尤其敏感）
CONTACT_PATTERNS = [
    (r"(?:1[3-9]\d{9})", "手机号"),
    (r"(?:微信|加微|加v|weixin|wx)\s*[:：]?\s*[A-Za-z0-9_-]{4,}", "微信号"),
    (r"(?:二维码|扫码|扫描二维码)", "二维码引导"),
    (r"(?:电话|热线|联系电话|座机)", "电话引导"),
    (r"(?:公众号|小红书号|抖音号|视频号)", "社群账号"),
    (r"(?:邮箱|email)\s*[:：]?\s*\S+@\S+", "邮箱"),
    (r"https?://", "外链"),
    (r"www\.", "外链"),
    (r"(?:下单|购买|立即咨询|加购|购物车|优惠价|下单链接)", "购物导流"),
    (r"(?:咨询我|联系我|私聊我|加我)", "问询引导"),
]

# 免责必须在位，且不得被削弱
DISCLAIMER_REQUIRED = "不构成诊断或治疗建议"
DISCLAIMER_WEAKENERS = ["无需就医", "不必就医", "不用就医", "无需就诊", "不必就诊"]

# 否定语境豁免：合规声明句本身必然出现「诊断」「治疗」等字样。
# 只有当该词出现在下列受控短语中时，才不判为违规。
NEGATION_PHRASES = [
    "不构成诊断或治疗建议",
    "不构成诊断建议",
    "不构成治疗建议",
    "不作为诊断依据",
    "不作为治疗依据",
    "不是诊断",
    "非诊断",
    "不作诊断",
    "不替代医疗",
    "不能替代医疗",
    "与诊断无关",
    "与治疗无关",
    "非医疗行为",
    "非诊疗行为",
    # 防护性表述：描述「已做的防护动作」而非描述症状本身
    "杜绝症状指向",
    "杜绝疗效指向",
    "去除症状指向",
    "不含症状指向",
    "无症状指向",
    # v3 新增：变现链路页的合规说明句。
    # 这些句子是**声明本表不做什么**，含有被禁词只是因为在列举红线，
    # 不能因此判违规——否则只会逼着人把合规声明删掉。
    "不写病名、不承诺效果、不限定特定人群",
    "只写体质倾向与生活原则",
    "杜绝功效断言",
]


def strip_negated(text, terms):
    """从 text 中剔除受控否定短语后，再检查 terms 是否仍存在。

    做法：把每条否定短语所在位置整段挖空，再扫描。
    这样只豁免确切的合规声明，不会误放过真正的违规表述。
    """
    if not terms:
        return []
    masked = text
    for ph in NEGATION_PHRASES:
        masked = masked.replace(ph, " " * len(ph))
    return sorted({t for t in terms if t in masked})


def strip_tags(html_text):
    """去标签 + 去 script/style 块，得到页面可见文案。"""
    t = re.sub(r"<script[\s\S]*?</script>", " ", html_text)
    t = re.sub(r"<style[\s\S]*?</style>", " ", t)
    t = re.sub(r"<!--[\s\S]*?-->", " ", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"&[a-zA-Z]+;|&#\d+;", " ", t)
    return t


def load_ssot_rows():
    with open(SSOT_PATH, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    errors, checks = [], []

    if not os.path.exists(HTML_PATH):
        print(f"✗ 文件不存在：{HTML_PATH}")
        return 1
    html_text = open(HTML_PATH, encoding="utf-8").read()
    visible = strip_tags(html_text)

    # ══════════════════════════════════════════════════
    # L1 合规红线
    # ══════════════════════════════════════════════════
    for name, terms in [
        ("医疗化表述", FORBIDDEN_TERMS),
        ("功效断言", EFFICACY_CLAIMS),
        ("特定人群限定", SPECIFIC_POPULATION),
        ("问询诱导", DIAGNOSTIC_PROBES),
        ("侵入性项目", FORBIDDEN_PROJECTS),
        ("病名", DISEASE_NAMES),
    ]:
        hits = strip_negated(visible, terms)
        if hits:
            errors.append(f"L1 页面可见文案含{name}：{hits}")
    checks.append(f"L1 合规红线 6 类词表（病名 {len(DISEASE_NAMES)} 条）")

    for pat, name in CONTACT_PATTERNS:
        m = re.search(pat, visible, re.I)
        if m:
            errors.append(f"L1 页面可见文案含{name}：{m.group(0)[:40]}")
    checks.append(f"L1 引流类 {len(CONTACT_PATTERNS)} 类模式")

    # 免责在位 + 未被削弱
    if DISCLAIMER_REQUIRED not in visible:
        errors.append(f"L1 缺少免责声明：应含「{DISCLAIMER_REQUIRED}」")
    else:
        checks.append("L1 免责声明在位")
    for w in DISCLAIMER_WEAKENERS:
        if w in visible:
            errors.append(f"L1 免责声明被削弱：出现「{w}」")

    # ══════════════════════════════════════════════════
    # L2 结构完整性
    # ══════════════════════════════════════════════════
    for tab in ["map", "report", "model", "cases"]:
        if f'panel-{tab}' not in html_text:
            errors.append(f"L2 缺少页签面板：{tab}")
    checks.append("L2 四页签齐全（生存地图/生成报告/生存模型/案例库）")

    cells = re.findall(r'class="tm-cell"', html_text)
    if len(cells) < 8:
        errors.append(f"L2 treemap 方块仅 {len(cells)} 个，少于 8")
    else:
        checks.append(f"L2 treemap 方块 {len(cells)} 个")

    for pid in ["treemap", "detail", "report", "roleOpts", "stageOpts"]:
        if f'id="{pid}"' not in html_text:
            errors.append(f"L2 缺少必要元素 id={pid}")
    checks.append("L2 关键 DOM 元素齐全")

    # 零外部资源
    ext = re.findall(r'(?:src|href)\s*=\s*"(https?://[^"]+)"', html_text)
    if ext:
        errors.append(f"L2 存在外部资源依赖：{ext[:3]}")
    else:
        checks.append("L2 零外部资源依赖（离线可开）")

    # ══════════════════════════════════════════════════
    # L3 真实性：页面数字必须与 SSOT 实际一致
    # ══════════════════════════════════════════════════
    rows = load_ssot_rows()
    total = len(rows)
    themes = sorted({r["主题"] for r in rows})

    # 3.1 素材总条数
    m = re.search(r'<div class="n">(\d+)<small>条</small></div>', html_text)
    if not m:
        errors.append("L3 未找到素材总条数")
    elif int(m.group(1)) != total:
        errors.append(f"L3 素材总条数不符：页面 {m.group(1)} / 实际 {total}")
    else:
        checks.append(f"L3 素材总条数与 SSOT 一致（{total} 条）")

    # 3.2 内容主题数
    m = re.search(r'<div class="n">(\d+)<small>类</small></div>', html_text)
    if not m:
        errors.append("L3 未找到内容主题数")
    elif int(m.group(1)) != len(themes):
        errors.append(f"L3 内容主题数不符：页面 {m.group(1)} / 实际 {len(themes)}")
    else:
        checks.append(f"L3 内容主题数与 SSOT 一致（{len(themes)} 类）")

    # 3.3 treemap 内每个位次的面积（v3：月产出件数）与素材供给（独占条数）
    #     面积口径由工序链推导，不能再与主题条数直接比；
    #     但「独占素材」必须与互斥分摊结果一致。
    from collections import Counter
    tc = Counter(r["主题"] for r in rows)
    area_notes = re.findall(r'class="tm-area">([^<]+)</text>', html_text)
    # 也从 DATA JSON 里取全部位次（大小方块都会渲染 tm-area）
    m_json = re.search(r"const DATA = (\{.*?\});\n", html_text, re.S)
    if not m_json:
        errors.append("L3 未解析到 DATA 数据块")
    else:
        data = json.loads(m_json.group(1))
        # 3.3.1 v3 核心不变量：素材互斥分摊守恒
        #   Σ 各位次独占素材 ≡ SSOT 实际条目数
        #   这条恒等式是 v3 修复「面积重复计入」的根本保障，
        #   一旦有人把同一主题挂到多个位次上，此处立刻报错。
        owned_sum = sum(r.get("material", 0) for r in data["roles"].values())
        if owned_sum != total:
            errors.append(
                f"L3 素材互斥分摊不守恒：Σ 各位次独占素材 {owned_sum} "
                f"≠ SSOT 实际 {total} 条"
            )
        else:
            checks.append(f"L3 素材互斥分摊守恒（Σ {owned_sum} ≡ {total} 条）")

        # 3.3.2 渠道位次（成品出口）不得独占素材
        bad_ch = [r["name"] for r in data["roles"].values()
                  if r.get("is_channel") and r.get("material", 0) != 0]
        if bad_ch:
            errors.append(f"L3 成品出口位次不应独占素材：{bad_ch}")
        else:
            checks.append("L3 成品出口位次独占素材均为 0")

        # 3.3.3 面积必须为正且等于工序链推导的月产出件数
        bad_area = []
        for key, role in data["roles"].items():
            ue = role.get("unit_econ") or {}
            expect = ue.get("pieces_per_month")
            if expect is None:
                bad_area.append(f"{role['name']} 缺 unit_econ")
            elif role["area"] != expect:
                bad_area.append(
                    f"{role['name']} 页面 {role['area']} / 推导 {expect}")
        if bad_area:
            errors.append("L3 面积与工序链推导的月产出件数不符：" + "；".join(bad_area))
        else:
            checks.append(
                f"L3 {len(data['roles'])} 个位次面积与工序链推导的月产出件数一致")

        # 3.3.4 现金出口必须存在（医馆停业后，私域变现是唯一现金出口）
        cash = [r["name"] for r in data["roles"].values() if r.get("is_cash")]
        if not cash:
            errors.append("L3 地图缺少现金出口位次，全图无通向现金的路径")
        else:
            checks.append(f"L3 现金出口位次在位：{cash}")

        checks.append(f"L3 {len(data['roles'])} 个位次面积口径已核对")

        # 3.4 工具化率必须与动作节点状态一致
        W = {"auto": 1.0, "semi": 0.5, "manual": 0.0}
        for key, role in data["roles"].items():
            acts = role["actions"]
            calc = round(sum(W[a["state"]] for a in acts) / len(acts) * 100)
            if calc != role["rate"]:
                errors.append(
                    f"L3 位次「{role['name']}」工具化率与动作状态不符："
                    f"页面 {role['rate']}% / 重算 {calc}%"
                )
        checks.append("L3 工具化率与动作节点状态加权一致")

        # 3.5 页面可见的"工具化 X%"必须等于数据中的 rate
        shown = {int(x) for x in re.findall(r"工具化 (\d+)%", visible)}
        for key, role in data["roles"].items():
            if role["rate"] not in shown:
                errors.append(
                    f"L3 位次「{role['name']}」工具化率 {role['rate']}% 未在页面出现"
                )
        checks.append(f"L3 页面可见工具化率覆盖全部 {len(data['roles'])} 个位次")

        # 3.6 非手工动作必须有工具证据
        for key, role in data["roles"].items():
            for a in role["actions"]:
                if a["state"] != "manual" and not a["tool_evidence"]:
                    errors.append(
                        f"L3 位次「{role['name']}」动作「{a['name']}」"
                        f"标为 {a['state']} 但无工具证据"
                    )
        checks.append("L3 所有非手工动作均有工具证据")

        # 3.7 象限归属必须与门槛一致
        TH = {"manual_zone": (0, 30), "tool_zone": (30, 55),
              "pipeline_zone": (55, 80), "system_zone": (80, 101)}
        for key, role in data["roles"].items():
            lo, hi = TH[role["quadrant"]]
            if not (lo <= role["rate"] < hi):
                errors.append(
                    f"L3 位次「{role['name']}」象限归属错误："
                    f"工具化 {role['rate']}% 落在 {role['quadrant']}"
                )
        checks.append("L3 象限归属与门槛一致")

    # 3.8 免责不得只出现一次（页脚与报告页都要有）
    n_disc = visible.count("不构成诊断或治疗建议")
    if n_disc < 1:
        errors.append("L3 免责缺失")
    else:
        checks.append(f"L3 免责在位（可见文案中出现 {n_disc} 次）")

    # 3.9 页面渲染出的工具化率文字，必须与 DATA 中的 rate 集合完全一致
    #     （防止有人手改 HTML 填入一个不存在于数据层的数字）
    if m_json:
        data = json.loads(m_json.group(1))
        legal_rates = {r["rate"] for r in data["roles"].values()}
        shown_rates = {int(x) for x in re.findall(r"工具化 (\d+)%", visible)}
        illegal = shown_rates - legal_rates
        if illegal:
            errors.append(
                f"L3 页面出现数据层不存在的工具化率：{sorted(illegal)}"
                f"（合法值 {sorted(legal_rates)}）"
            )
        else:
            checks.append(
                f"L3 页面工具化率文字全部可回溯到数据层（{len(shown_rates)} 个取值）"
            )

        # 3.10 页面渲染出的面积标注，必须与数据层的 area_note 一致
        #      v3：标注格式为「月产 N 件 · 独占素材 M 条」，
        #      故按 area_note 集合比对，防止手改 HTML 填入不存在的数据。
        legal_notes = {r["area_note"] for r in data["roles"].values()}
        shown_notes = set(
            m.group(1).strip()
            for m in re.finditer(r'class="tm-area"[^>]*>([^<]+)', html_text)
        )
        # 页面实际渲染的 tm-area 文本是「月产 N 件 · 独占素材 M 条」，
        # 与 area_note（较长，含口径说明）不同构，故单独校验其数值。
        bad_num = []
        for key, role in data["roles"].items():
            want = f'月产 {role["area"]} 件 · 独占素材 {role.get("material", 0)} 条'
            if want not in shown_notes:
                bad_num.append(f'{role["name"]} 缺「{want}」')
        if bad_num:
            errors.append("L3 页面面积标注与数据层不符：" + "；".join(bad_num))
        else:
            checks.append(
                f"L3 页面面积标注全部可回溯到数据层（{len(shown_notes)} 个取值）")

        # 3.10.1 反向检查：页面上不得出现数据层之外的面积标注
        #      只查「每个应有的是否都在」会漏掉「多出来的一条」——
        #      例如手工塞进一条「月产 9999 件」的假标注。
        legal_area_texts = {
            f'月产 {r["area"]} 件 · 独占素材 {r.get("material", 0)} 条'
            for r in data["roles"].values()
        }
        extra = {n for n in shown_notes if n not in legal_area_texts}
        if extra:
            errors.append(f"L3 页面出现数据层不存在的面积标注：{sorted(extra)}")
        else:
            checks.append("L3 页面无多余面积标注")

        # 3.11 免责必须同时出现在页脚与报告提示中
        #      （防止有人把其中一处删掉，或用其它表述替换）
        n_src = html_text.count(DISCLAIMER_REQUIRED)
        if DISCLAIMER_REQUIRED not in html_text:
            errors.append("L3 免责在 HTML 源码中缺失")
        elif n_src < 2:
            errors.append(
                f"L3 免责仅出现 {n_src} 次，页脚与报告提示各需一次"
            )
        else:
            checks.append("L3 免责在页脚与报告提示中同时在位")

        # 3.13 页面上出现的象限名必须全部来自数据层的合法集合
        #      锚定在 pill 徽章元素与图例项上，不做泛匹配（否则「工作区」这类
        #      普通词会被误判）。静态 HTML 与 JS 模板分别扫。
        import survival_map_data as _SMD
        legal_quads = {q["name"] for q in _SMD.QUADRANTS}
        static_html = re.sub(r"<script[\s\S]*?</script>", " ", html_text)
        # 静态区：pill 徽章内的文字
        pill_texts = [
            m.group(1).strip()
            for m in re.finditer(r'class="pill[^"]*"[^>]*>([^<]+)</', static_html)
        ]
        # JS 区：拼进模板的象限名（含引号包裹）
        js_html = html_text[html_text.find("<script>"):] if "<script>" in html_text else ""
        pill_texts += [
            m.group(1).strip()
            for m in re.finditer(r"['\"]([^'\"]{2,8})['\"]", js_html)
            if m.group(1).strip() in legal_quads or m.group(1).strip().endswith("区")
        ]
        illegal_quads = {
            t for t in pill_texts
            if t not in legal_quads and t not in {"地区", "校区", "园区", "小区", "社区", "景区"}
        }
        if illegal_quads:
            errors.append(f"L3 页面出现非法象限名：{sorted(illegal_quads)}")
        else:
            checks.append(f"L3 页面象限徽章名全部合法（合法 {len(legal_quads)} 个）")

        # 3.12 免责之外的替代性表述不能削弱免责
        weaken_ctx = [
            (r"仅供参考[，,]?\s*不需(?:要)?(?:就医|就诊|看医生)", "削弱免责"),
            (r"仅供参考[，,]?\s*自行判断", "削弱免责"),
            (r"仅供参考[，,]?\s*无风险", "削弱免责"),
        ]
        for pat, nm in weaken_ctx:
            m = re.search(pat, visible)
            if m:
                errors.append(f"L3 出现{nm}表述：{m.group(0)[:40]}")

    # ══════════════════════════════════════════════════
    # 输出
    # ══════════════════════════════════════════════════
    print("═" * 62)
    print("养生一人公司生存地图 · 合规与真实性校验")
    print("═" * 62)
    for c in checks:
        print(f"  ✓ {c}")
    print()
    if errors:
        print(f"✗ 发现 {len(errors)} 处问题：")
        for e in errors:
            print(f"    ✗ {e}")
        return 1
    print("✅ 全部通过")
    print(f"   合规红线 6 类 + 引流 {len(CONTACT_PATTERNS)} 类 · 结构完整 · "
          f"数字与 SSOT 逐项一致")
    return 0


if __name__ == "__main__":
    sys.exit(main())
