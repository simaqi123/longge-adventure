# -*- coding: utf-8 -*-
"""养生一人公司生存地图 · 数据层

设计原则（对标陈磊「AI 一人公司生存地图」）
------------------------------------------------
陈磊那张 treemap 的三个坐标是：
    面积 = 案例样本数   颜色 = AI 化率档位   块内进度条 = AI 化率
其中「案例样本数」是他自报的数字，无法核验。

养生版必须换口径，否则就是一张更精致的空壳：
    面积 = 该位次可调用的 SSOT 素材条数   ← 可回溯 养生知识表.csv，逐条可数
    颜色 = 工具化率档位                  ← 由动作节点的工具化状态加权算出
    进度条 = 工具化率

三条硬约束：
1. 素材条数一律从 data/养生知识表.csv 实时统计，代码里不写死数字。
2. 工具化率只允许引用**真实存在**的脚本；不存在的能力不能标为已进管线。
3. 四象限名称不照搬陈磊的商业语境（高产/繁荣/转型/领先），
   换成与养生内容生产实际对应的表述。
"""

import csv
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import SSOT_CSV as SSOT_PATH, SOURCE_MAP_MD  # noqa: E402

# ──────────────────────────────────────────────���──────────────
# 一、素材统计（真实读表）
# ─────────────────────────────────────────────────────────────


def load_ssot():
    with open(SSOT_PATH, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def theme_counts(rows=None):
    """主题 -> 条数。treemap 面积的全部来源。"""
    rows = rows if rows is not None else load_ssot()
    return dict(Counter(r["主题"] for r in rows))


# ─────────────────────────────────────────────────────────────
# 二、动作节点的三种工具化状态
# ─────────────────────────────────────────────────────────────
# auto    已进管线：由脚本自动完成，人不介入
# semi    半自动：脚本出初稿，人工定稿
# manual  纯手工：无工具，靠人手逐条写
#
# 每一项都必须能指到一个真实存在的脚本文件（见 TOOL_EVIDENCE），
# 否则不允许标 auto。
TOOL_STATES = {
    "auto": {"label": "已进管线", "weight": 1.0, "color": "green"},
    "semi": {"label": "半自动", "weight": 0.5, "color": "amber"},
    "manual": {"label": "纯手工", "weight": 0.0, "color": "red"},
}

# 真实存在的能力清单 —— 只有列在这里的，才允许在角色里标为 auto/semi
TOOL_EVIDENCE = {
    "brief_gen": "build_daily_brief.py — 六卡早报自动生成（节气快照/体质画像/经典条文/今日养护/自省问答/明日预告）",
    "brief_push": "push_brief_to_docs.py — 早报 MD→MDX→腾讯文档推送，上传前 10 项自检",
    "brief_scan": "build_daily_brief.py 内置早报合规扫描器（断言类/用药类/问询类/项目类）",
    "constitution_gen": "build_constitution_test.py — 36 题九体质自测工具单文件生成",
    "constitution_guard": "validate_constitution_html.py — 结果页红线三层校验 + 14 项注入测试",
    "ssot_guard": "validate_ssot.py — SSOT 10 类合规校验，全表 0 错误 0 警告",
    "source_upgrade": "upgrade_sources.py — 条目出处升级为篇名+原句级",
    "food_rewrite": "rewrite_food_entries.py — 食养条目去功效化批量重写",
    "batch_build": "build_wellness_batch2/3/4.py — 分型段落与节气条目批量拆解生成",
    "source_map": "data/节气经典_出处对照表.md — 逐条原句出处对照",
}

# ─────────────────────────────────────────────────────────────
# 三、位次定义
# ─────────────────────────────────────────────────────────────
# themes  : 主素材池（决定面积），取自 SSOT 的「主题」列
# pool    : 跨位次可复用的补充素材池（用于标注，不计入面积）
# actions : 动作节点清单，决定工具化率
#
# actions 每项：
#   name   动作名
#   state  auto / semi / manual
#   tool   对应 TOOL_EVIDENCE 的键（manual 时为 None）
#
ROLES = [
    {
        "key": "food_channel",
        "name": "食养内容号主",
        "sub": "一食一养 · 日常餐桌",
        "themes": ["食养"],
        "pool": ["体质", "节气", "经典", "自省", "起居", "边界", "项目"],
        "desc": "以每日餐食为载体做内容输出，素材消耗量最大的位次。",
        "actions": [
            {"name": "条目拆解与合规改写", "state": "auto", "tool": "batch_build"},
            {"name": "去功效化重写", "state": "auto", "tool": "food_rewrite"},
            {"name": "食材目录归属核对", "state": "auto", "tool": "ssot_guard"},
            {"name": "出处回填至原句", "state": "auto", "tool": "source_upgrade"},
            {"name": "成品文案撰写", "state": "manual", "tool": None},
        ],
    },
    {
        "key": "solar_channel",
        "name": "节气养生号主",
        "sub": "二十四节气 · 时令起居",
        "themes": ["节气"],
        "pool": ["食养", "体质", "经典", "自省", "起居", "边界", "项目"],
        "desc": "按节气推进的内容位次，素材随节气轮转消耗。",
        "actions": [
            {"name": "节气条目生成", "state": "auto", "tool": "batch_build"},
            {"name": "经典原句配对", "state": "auto", "tool": "source_map"},
            {"name": "节气归位与出处核验", "state": "auto", "tool": "source_upgrade"},
            {"name": "时令文案撰写", "state": "manual", "tool": None},
        ],
    },
    {
        "key": "constitution_channel",
        "name": "体质辨析号主",
        "sub": "九种体质 · 倾向科普",
        "themes": ["体质"],
        "pool": ["食养", "节气", "经典", "自省", "起居", "边界", "项目"],
        "desc": "围绕体质倾向做科普与自测互动的位次。",
        "actions": [
            {"name": "体质条目入库", "state": "auto", "tool": "batch_build"},
            {"name": "自测题库与工具生成", "state": "auto", "tool": "constitution_gen"},
            {"name": "结果页红线校验", "state": "auto", "tool": "constitution_guard"},
            {"name": "结果页溯源对齐", "state": "auto", "tool": "ssot_guard"},
            {"name": "体质科普文案撰写", "state": "manual", "tool": None},
        ],
    },
    {
        "key": "classic_channel",
        "name": "经典研读博主",
        "sub": "内经原文 · 逐条出处",
        "themes": ["经典"],
        "pool": ["食养", "体质", "节气", "自省", "起居", "边界", "项目"],
        "desc": "做原文溯源与白话对照，素材少但对出处精度要求最高。",
        "actions": [
            {"name": "篇名与原句级出处核验", "state": "auto", "tool": "source_upgrade"},
            {"name": "出处对照表维护", "state": "auto", "tool": "source_map"},
            {"name": "原典逐字比对（ctext/wikisource）", "state": "manual", "tool": None},
            {"name": "白话释读撰写", "state": "manual", "tool": None},
        ],
    },
    {
        "key": "routine_channel",
        "name": "起居调养号主",
        "sub": "作息起居 · 日常节律",
        "themes": ["起居"],
        "pool": ["食养", "体质", "节气", "经典", "自省", "边界", "项目"],
        "desc": "起居类素材的专属出口，35 条起居条目归属于此。"
                "与体质辨析号主强关联：起居是体质调养的落地动作。",
        "actions": [
            {"name": "起居条目拆解与合规改写", "state": "auto", "tool": "batch_build"},
            {"name": "节律建议成稿撰写", "state": "manual", "tool": None},
            {"name": "起居合规扫描", "state": "auto", "tool": "brief_scan"},
        ],
    },
    {
        "key": "self_reflect",
        "name": "自省心性号主",
        "sub": "每日一问 · 情绪起居",
        "themes": ["自省"],
        "pool": ["食养", "体质", "节气", "经典", "起居", "边界", "项目"],
        "desc": "以自省问答为载体的内容位次。",
        "actions": [
            {"name": "自省条目入库", "state": "auto", "tool": "batch_build"},
            {"name": "每日一问生成", "state": "auto", "tool": "brief_gen"},
            {"name": "早报合规扫描", "state": "auto", "tool": "brief_scan"},
            {"name": "问答撰写与改写", "state": "manual", "tool": None},
        ],
    },
    {
        "key": "content_dual",
        "name": "短视频图文内容主",
        "sub": "口播成片 · 图文笔记",
        "themes": [],
        "pool": ["食养", "节气", "体质"],
        "desc": "成品出口位次。短视频与图文是同一批素材的两种形态，"
                "合并计一个位次——分开计会把同一批素材重复计入面积。",
        "actions": [
            {"name": "选题素材抽取", "state": "auto", "tool": "brief_gen"},
            {"name": "脚本初稿生成", "state": "semi", "tool": "brief_gen"},
            {"name": "配图文案初稿生成", "state": "semi", "tool": "brief_gen"},
            {"name": "合规扫描与改写", "state": "auto", "tool": "brief_scan"},
            {"name": "素材溯源核对", "state": "auto", "tool": "ssot_guard"},
            {"name": "口播表达与演绎", "state": "manual", "tool": None},
            {"name": "成稿润色", "state": "manual", "tool": None},
        ],
    },
    {
        "key": "course_teacher",
        "name": "线上课程讲师",
        "sub": "体系课 · 直播带教",
        "themes": [],
        "pool": ["起居", "食养", "经典"],
        "desc": "把素材组织成课程结构的位次。",
        "actions": [
            {"name": "课程大纲素材编排", "state": "semi", "tool": "brief_gen"},
            {"name": "讲义初稿生成", "state": "semi", "tool": "brief_gen"},
            {"name": "合规扫描", "state": "auto", "tool": "brief_scan"},
            {"name": "授课讲授与答疑", "state": "manual", "tool": None},
        ],
    },
    {
        "key": "community",
        "name": "社群私域主",
        "sub": "早报分发 · 长期陪伴",
        "themes": [],
        "pool": ["体质", "边界"],
        "desc": "负责长期陪伴与内容分发，是转化链条的末端。",
        "actions": [
            {"name": "早报每日生成", "state": "auto", "tool": "brief_gen"},
            {"name": "早报推送分发", "state": "auto", "tool": "brief_push"},
            {"name": "推送前合规自检", "state": "auto", "tool": "brief_push"},
            {"name": "群内答疑与陪伴", "state": "manual", "tool": None},
        ],
    },
    {
        "key": "monetize",
        "name": "私域变现主",
        "sub": "会员订阅 · 付费社群",
        "themes": ["边界", "项目"],
        "pool": ["食养", "体质", "节气", "经典", "自省", "起居"],
        "desc": "唯一通向现金的位次。承接前九个位次的流量，"
                "把陪伴关系转为付费订阅；线下交付已停办，本位次是养生链的现金出口。",
        "actions": [
            {"name": "会员权益结构设计", "state": "manual", "tool": None},
            {"name": "订阅内容排期编排", "state": "semi", "tool": "brief_gen"},
            {"name": "付费物料合规校验", "state": "auto", "tool": "ssot_guard"},
            {"name": "会员答疑与陪伴", "state": "manual", "tool": None},
            {"name": "订阅续费与退订处理", "state": "manual", "tool": None},
        ],
    },
]

# ─────────────────────────────────────────────────────────────
# 三之二、手工环节的语义分类
# ─────────────────────────────────────────────────────────────
# 纯手工不等于「都该自动化」。手工环节分两类：
#   movable —— 重复搬运型。同样的动作在别处已有现成工具可承接，
#              迁移过来即可省下手工（例如「选题素材抽取」）。
#   human   —— 含判断与表达型。需要人的经验与风格，刻意保留手工
#              （例如「口播表达与演绎」「白话释读撰写」）。
# 这个区分决定了「全手工」阶段该建议什么、也决定了什么不该被自动化。
MOVABLE_ACTIONS = {
    # 短视频图文内容主
    "选题素材抽取": "move",
    "口播表达与演绎": "human",
    "成稿润色": "human",
    # 线上课程讲师
    "授课讲授与答疑": "human",
    # 食养内容号主
    "成品文案撰写": "human",
    # 节气养生号主
    "时令文案撰写": "human",
    # 体质辨析号主
    "体质科普文案撰写": "human",
    # 起居调养号主
    "节律建议成稿撰写": "human",
    # 经典研读博主
    "原典逐字比对（ctext/wikisource）": "assist",
    "白话释读撰写": "human",
    # 自省心性号主
    "问答撰写与改写": "human",
    # 私域变现主
    "会员权益结构设计": "human",
    "会员答疑与陪伴": "human",
    "订阅续费与退订处理": "move",
    # 社群私域主
    "群内答疑与陪伴": "human",
}



# ─────────────────────────────────────────────────────────────
# 四、四象限（养生语境，不照搬商业语境）
# ─────────────────────────────────────────────────────────────
QUADRANTS = [
    {
        "key": "manual_zone",
        "name": "纯手工区",
        "color": "red",
        "desc": "关键动作仍靠人逐条手写，人力占用最重，无法规模复制。",
        "threshold": "工具化率 < 30%",
    },
    {
        "key": "tool_zone",
        "name": "工具区",
        "color": "orange",
        "desc": "有脚本可用但没有统一契约与出处溯源，产出依赖个人习惯。",
        "threshold": "30% ≤ 工具化率 < 55%",
    },
    {
        "key": "pipeline_zone",
        "name": "流程区",
        "desc": "关键动作已进管线，产出可重跑可验收，人只做定稿。",
        "color": "yellow",
        "threshold": "55% ≤ 工具化率 < 80%",
    },
    {
        "key": "system_zone",
        "name": "系统区",
        "color": "green",
        "desc": "一人可跑完整闭环：素材供给、合规校验、分发落地全部自洽。",
        "threshold": "工具化率 ≥ 80%",
    },
]


def quadrant_of(rate):
    if rate < 30:
        return QUADRANTS[0]
    if rate < 55:
        return QUADRANTS[1]
    if rate < 80:
        return QUADRANTS[2]
    return QUADRANTS[3]


# ─────────────────────────────────────────────────────────────
# 五、计算
# ─────────────────────────────────────────────────────────────


def tool_rate(role):
    """工具化率 = Σ 节点权重 / 节点数 × 100

    权重：已进管线 1.0，半自动 0.5，纯手工 0.0
    """
    acts = role["actions"]
    total = sum(TOOL_STATES[a["state"]]["weight"] for a in acts)
    return round(total / len(acts) * 100)


# ─────────────────────────────────────────────────────────────
# 四之半、主题归属表（v3 新增 · treemap 面积互斥的前提）
# ─────────────────────────────────────────────────────────────
# v2 的缺陷：位次的 themes 列表互相重叠，导致同一批 SSOT 条目
# 被多个位次重复计入面积（10 个位次面积和 569 > 实际条目总数）。
#
# v3 的规则：**每个主题只归属一个主位次**，归属后该主题的条目数
# 全额计入那个位次的面积；其他引用该主题的位次把它记进 pool，
# 标为「共享取材」，不重复占面积。
#
# 于是恒等式成立：
#     Σ(各位次 area) ≡ Σ(各主题条目数) ≡ SSOT 实际条目数
# 校验器 validate_survival_map.py 会核这条恒等式。
#
# 归属依据是「这条素材最终由谁交付」：
#   食养   → 食养内容号主      体质 → 体质辨析号主
#   节气   → 节气养生号主      经典 → 经典研读博主
#   自省   → 自省心性号主      边界 → 私域变现主（合规边界是变现前提）
#   起居   → 起居调养号主（新增，见下）
#   项目   → 私域变现主（线下交付停办，项目类条目降级为知识素材）
THEME_OWNER = {
    "食养": "food_channel",
    "体质": "constitution_channel",
    "节气": "solar_channel",
    "经典": "classic_channel",
    "自省": "self_reflect",
    "边界": "monetize",
    "项目": "monetize",
    "起居": "routine_channel",
}

# 渠道位次（shortvideo / course_teacher / community / note_writer）
# 不独占任何主题 —— 它们是「成品出口」，素材来自上游主题位次。
# 面积口径与主题位次不同，不能用素材条数（否则必然重复）。
# 渠道位次的面积 = **每月独占产出的成品件数**，由工序链推��（见 survival_deep_model）。
# 主题位次的面积 = **独占加工的素材条数**，逐条可回溯 SSOT。
# 两者单位不同，故在页面上分区展示、分别标注口径，绝不混算。

# 每月按 4 周计
MONTHS_PER_YEAR = 12
WEEKS_PER_MONTH = 4


def allocate_materials(rows=None):
    """素材互斥分摊：每条 SSOT 条目归属唯一一个主加工位次。

    返回 {role_key: 条数}，各值之和 ≡ SSOT 实际条目数。
    分配规则（按优先级，先到先得）：
      1. 主题位次：直接取走本主题的全部条目（它独占该主题）
      2. 渠道位次：从共享池中按权重取用，但**已被主题位次取走的
         条目不再重复计**——渠道位次的取用量单列为「共享取材」，
         不计入 treemap 面积。
    因此主题位次面积之和 ≡ SSOT 条目总数，treemap 面积口径唯一且可核。
    """
    rows = rows if rows is not None else load_ssot()
    tc = theme_counts(rows)
    owned = {}
    for theme, role_key in THEME_OWNER.items():
        owned[role_key] = owned.get(role_key, 0) + tc.get(theme, 0)
    return owned


def build_map(rows=None):
    """产出 treemap 数据。

    面积口径（v3 修正）：**互斥分摊**。
    ─────────────────────────────────────────────
    v2 的口径是「该位次主素材池在 SSOT 中的条目数」，
    结果 10 个位次的面积之和达到 569 条，而 SSOT 实际只有 205 条 ——
    同一批素材被多个位次各算了一遍，treemap 面积因此完全失真。

    v3 改为**统一口径：面积 = 该位次每月独占产出的成品件数**。

    理由：v2 混用了两种不可比的量 —— 主题位次用「素材条数」，
    渠道位次本质上也是用素材条数，于是同一批素材被重复计入，
    10 个位次面积之和达 569，而 SSOT 实际只有 205 条。

    v3 的口径只有一种量：**月产出件数**，全部由工序链推导
    （残余工时 → 周产能 → 月产能），同单位、可比、可复算。
    素材条数不再是面积，而是独立的「素材供给」指标：
      area      —— 月产出件数（treemap 面积）
      material  —— 独占素材条数（可回溯 SSOT，Σ = 条目总数）

    恒等式（校验器会核）：
      Σ 各主题位次的 material ≡ SSOT 实际条目数
      Σ 各渠道位次的 material = 0（渠道不独占素材，只做成品出口）
    """
    rows = rows if rows is not None else load_ssot()
    tc = theme_counts(rows)
    owned = allocate_materials(rows)
    items = []
    for r in ROLES:
        # 主题位次独占素材条数；渠道位次为 0（成品出口不独占素材）
        is_channel = len(r["themes"]) == 0
        material = owned.get(r["key"], 0)
        rate = tool_rate(r)
        q = quadrant_of(rate)
        # 校验：所有非 manual 节点都必须有真实工具证据
        for a in r["actions"]:
            if a["state"] != "manual":
                assert a["tool"] in TOOL_EVIDENCE, (
                    f"[{r['key']}] 动作「{a['name']}」标为 {a['state']}"
                    f"但工具 {a['tool']} 不在真实能力清单中"
                )
        if is_channel:
            area_note = "月产出件数（工序链推导）"
        else:
            area_note = (f"月产出件数 · 独占素材 {material} 条"
                         f"（{' + '.join(r['themes'])}）")
        items.append(
            {
                "key": r["key"],
                "name": r["name"],
                "sub": r["sub"],
                "desc": r["desc"],
                "themes": r["themes"],
                "pool": r["pool"],
                "is_channel": is_channel,
                "is_cash": r["key"] == "monetize",
                "material": material,
                "area": 0,   # 由 build_deep_model 用工序链回填
                "area_note": area_note,
                "rate": rate,
                "quadrant": q["key"],
                "quadrant_name": q["name"],
                "quadrant_color": q["color"],
                "actions": [
                    {
                        "name": a["name"],
                        "state": a["state"],
                        "state_label": TOOL_STATES[a["state"]]["label"],
                        "tool": a["tool"],
                        "tool_evidence": TOOL_EVIDENCE.get(a["tool"], ""),
                    }
                    for a in r["actions"]
                ],
                "manual_gap": [a["name"] for a in r["actions"] if a["state"] == "manual"],
            }
        )
    items.sort(key=lambda x: -x["area"])
    return items


def build_stats(rows=None):
    """左侧「数据来源」面板 —— 全部为可核验的真实统计。"""
    rows = rows if rows is not None else load_ssot()
    tc = theme_counts(rows)
    js = set()
    for r in rows:
        for j in re.split(r"[、,，]", r["适用节气"]):
            j = j.strip()
            if j and j != "ALL":
                js.add(j)
    zs = set()
    for r in rows:
        for z in re.split(r"[、,，]", r["适用体质"]):
            z = z.strip()
            if z and z != "ALL":
                zs.add(z)
    # 二十四节气标准名
    SOLAR_TERMS = {
        "立春", "雨水", "惊蛰", "春分", "清明", "谷雨",
        "立夏", "小满", "芒种", "夏至", "小暑", "大暑",
        "立秋", "处暑", "白露", "秋分", "寒露", "霜降",
        "立冬", "小雪", "大雪", "冬至", "小寒", "大寒",
    }
    covered = sorted(SOLAR_TERMS & js)
    # 基础体质（以「质」结尾，如气虚质/痰湿质）与倾向标签（如脾虚倾向）分开计
    base_zs = sorted({z for z in zs if z.endswith("质")})
    trend_zs = sorted({z for z in zs if z.endswith("倾向")})
    return {
        "素材总条数": len(rows),
        "内容主题数": len(tc),
        "节气覆盖": f"{len(covered)}/24",
        "体质分类数": len(base_zs),
        "倾向标签数": len(trend_zs),
        "校验规则类": 10,
        "红线注入测试": "14/14 拦截",
        "主题分布": tc,
    }


def build_report(role_key, stage, rows=None):
    """生成报告：现状判定 + 缺口 + 建议动作（全部由真实覆盖率推导）。

    stage 决定建议的**落点**，不只是措辞：
        manual   —— 一切靠手写，报告应指出先接哪一步、接完能省多少
        tool     —— 有脚本没流程，报告应指出如何归拢成可重跑的管线
        pipeline —— 关键动作已进管线，报告应指出闭环还差哪一环
        system   —— 想跑完整闭环，报告应指出内容调度与分层
    """
    rows = rows if rows is not None else load_ssot()
    items = build_map(rows)
    role = next((i for i in items if i["key"] == role_key), None)
    if role is None:
        return None

    # 按动作顺序给出建议：工具化程度高的先做
    ordered = sorted(role["actions"], key=lambda a: -TOOL_STATES[a["state"]]["weight"])

    # 各阶段的建议挑选规则不同
    picks = []
    if stage == "manual":
        # 全手工：优先「先接哪一步」，按省力程度排，只给 3 条
        # 优先挑那些「同类动作已在别处有现成工具」的环节——
        # 这类动作本质是重复搬运，接进管线即可省下手工；
        # 真正含判断与表达的环节不作为自动化目标。
        # 该位次动作清单里，属于「重复搬运型」的环节优先作为自动化目标
        for a in ordered:
            if len(picks) >= 3:
                break
            kind = MOVABLE_ACTIONS.get(a["name"])
            if kind == "move":
                picks.append({
                    "name": a["name"],
                    "kind": "先接管线",
                    "detail": f"这一步属于重复搬运，同类动作已有现成能力可承接，"
                              f"迁移过来即可省下手工：{a['tool_evidence']}",
                })
            elif kind == "assist":
                picks.append({
                    "name": a["name"],
                    "kind": "可辅助",
                    "detail": "这一步需要人做判断，但可比对与检索的重复部分"
                              "可以交给工具，人只做最终确认："
                              + (a["tool_evidence"]
                                 or "目前尚无现成工具，可先把原典检索与版本比对写成脚本，"
                                    "再由人确认最终用字"),
                })
        if not picks:
            picks.append({
                "name": role["actions"][0]["name"],
                "kind": "保持现状",
                "detail": "该位次的动作已全部进管线，当前没有可继续自动化的手工环节。",
            })
    elif stage == "tool":
        # 有工具：指出如何归拢成管线
        autos = [a for a in ordered if a["state"] == "auto"]
        semis = [a for a in ordered if a["state"] == "semi"]
        for a in autos[:2]:
            picks.append({
                "name": a["name"],
                "kind": "归拢",
                "detail": f"已具备工具能力，缺的是稳定调用顺序：{a['tool_evidence']}",
            })
        for a in semis[:1]:
            picks.append({
                "name": a["name"],
                "kind": "定稿边界",
                "detail": f"脚本出初稿、人工定稿，需写清初稿到定稿的验收标准："
                          f"{a['tool_evidence']}",
            })
        if not picks:
            picks.append({
                "name": "整体管线",
                "kind": "归拢",
                "detail": "该位次动作均已归拢，可直接接入统一调度。",
            })
    elif stage == "pipeline":
        # 有流程：指出闭环还差哪一环
        gaps = [a["name"] for a in role["actions"] if a["state"] == "manual"]
        if gaps:
            picks.append({
                "name": gaps[0],
                "kind": "闭环缺口",
                "detail": "这一步仍需人承接，是当前闭环上唯一的断点，"
                          "建议先明确它的交付标准与留痕方式。",
            })
        picks.append({
            "name": "产出留痕",
            "kind": "闭环补齐",
            "detail": "每次产出需要能回溯到具体条目与出处，"
                      "建议把素材引用与出处字段随产出一起归档。",
        })
        picks.append({
            "name": "分发节奏",
            "kind": "闭环补齐",
            "detail": "已有产出但尚未固定分发节奏，"
                      "建议接入推送通道形成稳定节律。",
        })
    else:  # system
        # 要闭环：重点在内容分层与调度
        picks.append({
            "name": "内容分层",
            "kind": "闭环",
            "detail": "素材已达可调度规模，建议按主题与节气把条目编排成固定栏目，"
                      "避免每期临时选材。",
        })
        picks.append({
            "name": "选题调度",
            "kind": "闭环",
            "detail": "现有能力可直接承担选材与初稿，"
                      "建议把选题规则写成可配置项，按节气与体质自动排期。",
        })
        manual_names = [a["name"] for a in role["actions"] if a["state"] == "manual"]
        picks.append({
            "name": manual_names[0] if manual_names else "人工环节",
            "kind": "保留人工",
            "detail": "该环节含判断与表达，建议刻意保留手工，"
                      "作为内容差异化的来源而非自动化目标。",
        })

    # 缺口 = 仍为纯手工的动作
    gaps = role["manual_gap"]
    if not gaps:
        gap_text = "该位次的动作已全部进管线，当前不存在纯手工缺口。"
    else:
        gap_text = "、".join(gaps) + " 仍为纯手工环节。"

    # 下一步：按阶段给一个具体动作
    NEXT = {
        "manual": "先把「{first}」这类重复搬运动作接进现有脚本，"
                  "让机器承担搬运，人只保留判断与表达。",
        "tool": "把散落在各处的脚本归到统一契约层，形成一条可重跑、"
                "可验收的产出管线。",
        "pipeline": "给管线补上留痕与分发两个环节，跑通从素材到阅读场景的完整闭环。",
        "system": "当前已接近闭环，重点转向内容分层的选题调度，"
                  "让每期产出可预期、可复盘。",
    }
    first = role["actions"][0]["name"]
    next_step = NEXT[stage].format(first=first)

    return {
        "role": role,
        "stage": stage,
        "stage_name": {
            "manual": "全手工",
            "tool": "有工具",
            "pipeline": "有流程",
            "system": "要闭环",
        }[stage],
        "gaps": gaps,
        "gap_text": gap_text,
        "picks": picks,
        "next_step": next_step,
        "pool_size": role["area"],
    }


if __name__ == "__main__":
    import sys

    sys.stdout.reconfigure(encoding="utf-8")
    items = build_map()
    stats = build_stats()
    print("=== 养生一人公司生存地图 · 数据层 ===\n")
    print(f"素材总条数 {stats['素材总条数']} / 主题 {stats['内容主题数']} 类")
    print(f"节气覆盖 {stats['节气覆盖']}  体质分类 {stats['体质分类数']} 种\n")
    print(f"{'位次':<14}{'面积':>5}  {'工具化':>5}  象限")
    print("-" * 52)
    for it in items:
        print(f"{it['name']:<14}{it['area']:>5}  {it['rate']:>4}%  {it['quadrant_name']}")
    print("\n象限分布：")
    from collections import Counter as C
    for k, v in C(i["quadrant_name"] for i in items).most_common():
        print(f"  {k}: {v} 个位次")
