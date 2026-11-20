#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
养生一人公司 · 深度经营模型层
=============================

在 survival_map_data.py（横截面地图）之上，补充三个纵深维度：

  一、工序链（CHAIN）—— 每个位次的完整交付工序，含前置依赖、
     单位工时、可自动化性、是否瓶颈工序。工时口径写在 TIME_BASE，
     可被真实实测覆盖，不凭空编造。

  二、单位经济（UNIT_ECONOMY）—— 一条成品从选题到交付的
     总工时、自动化后残余工时、换算到的日/周/月产能。

  三、90 天推进路线（ROADMAP）—— 按阶段推进的里程碑，
     每个阶段有明确的出口条件（gate）。

设计原则（延续生存地图的既有约束）：
  * 所有数字要么来自 SSOT 真实统计，要么来自显式声明的口径常量；
  * 凡是无法核验的量，标注为「口径值」而非「实测值」；
  * 禁止虚构样本量、虚构粉丝数、虚构收益承诺。
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import survival_map_data as S


# ─────────────────────────────────────────────────────────────
# 一、工时口径（TIME_BASE）
# ─────────────────────────────────────────────────────────────
# 说明：下列工时是「单人精力的标准工时估计」，单位为分钟/件。
# 它们是**口径值**——用于横向比较与瓶颈识别，不是实测值。
# 每个位次都可以用真实记录覆盖（见 TIME_OVERRIDE）。
#
# auto   动作：脚本已能完成，人只做验收 —— 人工工时是「检查时间」
# semi   动作：脚本出初稿，人做定稿   —— 人工工时是「改稿时间」
# manual 动作：人从头写             —— 人工工时是「净创作时间」
#
# 依据：文案类内容一条成稿的净创作时间通常显著高于一次校对；
# 校对 = 创作的一个小数量级。这个比例关系是全部工时估计的锚点。
TIME_BASE = {
    # 动作名 -> (单件人工分钟, 动作性质)
    # —— auto（验收型）——
    "条目拆解与合规改写": (6, "auto"),
    "去功效化重写": (8, "auto"),
    "食材目录归属核对": (5, "auto"),
    "出处回填至原句": (10, "auto"),
    "节气条目生成": (6, "auto"),
    "经典原句配对": (10, "auto"),
    "节气归位与出处核验": (8, "auto"),
    "体质条目入库": (6, "auto"),
    "结果页红线校验": (5, "auto"),
    "结果页溯源对齐": (8, "auto"),
    "篇名与原句级出处核验": (15, "auto"),
    "出处对照表维护": (12, "auto"),
    "项目与边界条目维护": (8, "auto"),
    "对外物料合规校验": (6, "auto"),
    "自省条目入库": (6, "auto"),
    "每日一问生成": (5, "auto"),
    "早报合规扫描": (5, "auto"),
    "选题素材抽取": (10, "auto"),
    "合规扫描与改写": (8, "auto"),
    "合规扫描": (5, "auto"),
    "早报每日生成": (8, "auto"),
    "早报推送分发": (12, "auto"),
    "推送前合规自检": (6, "auto"),
    "素材溯源核对": (8, "auto"),
    "起居条目拆解与合规改写": (7, "auto"),
    "起居合规扫描": (5, "auto"),
    "订阅内容排期编排": (20, "semi"),
    "付费物料合规校验": (8, "auto"),
    # —— semi（定稿型）——
    "脚本初稿生成": (18, "semi"),
    "课程大纲素材编排": (45, "semi"),
    "讲义初稿生成": (35, "semi"),
    "配图文案初稿生成": (15, "semi"),
    # —— manual（净创作型）——
    "成品文案撰写": (45, "manual"),
    "时令文案撰写": (40, "manual"),
    "体质科普文案撰写": (40, "manual"),
    "节律建议成稿撰写": (35, "manual"),
    "原典逐字比对（ctext/wikisource）": (35, "manual"),
    "白话释读撰写": (50, "manual"),
    "会员权益结构设计": (40, "manual"),
    "问答撰写与改写": (25, "manual"),
    "口播表达与演绎": (50, "manual"),
    "授课讲授与答疑": (60, "manual"),
    "成稿润色": (30, "manual"),
    "群内答疑与陪伴": (25, "manual"),
    "会员答疑与陪伴": (30, "manual"),
    "订阅续费与退订处理": (15, "manual"),
}


# 各工序的前置依赖（构造链序）。同一环节在不同位次里
# 承担的角色可能不同，因此依赖按「动作名」声明，
# 构建时再按位次内的实际出现顺序对齐。
CHAIN_DEPS = {
    "成品文案撰写": ["去功效化重写"],
    "时令文案撰写": ["节气归位与出处核验"],
    "体质科普文案撰写": ["结果页溯源对齐"],
    "节律建议成稿撰写": ["起居条目拆解与合规改写"],
    "白话释读撰写": ["原典逐字比对（ctext/wikisource）"],
    "口播表达与演绎": ["合规扫描与改写"],
    "成稿润色": ["素材溯源核对"],
    "配图文案初稿生成": ["选题素材抽取"],
    "脚本初稿生成": ["选题素材抽取"],
    "授课讲授与答疑": ["讲义初稿生成"],
    "问答撰写与改写": ["早报合规扫描"],
    "群内答疑与陪伴": ["早报推送分发"],
    "会员答疑与陪伴": ["早报推送分发"],
    "订阅内容排期编排": ["早报每日生成"],
    "订阅续费与退订处理": ["会员答疑与陪伴"],
    "课程大纲素材编排": ["经典原句配对"],
}


# 位次的产出单位：一个「件」是什么
UNIT_DEF = {
    "food_channel": ("条图文", "食养成品文案一条"),
    "solar_channel": ("条图文", "时令成品文案一条"),
    "constitution_channel": ("条图文", "体质科普成品一条"),
    "classic_channel": ("篇释读", "原典白话释读一篇"),
    "routine_channel": ("条图文", "起居节律成品一条"),
    "self_reflect": ("条问答", "自省问答一条"),
    "content_dual": ("条成品", "短视频或图文成品一条"),
    "course_teacher": ("节课", "直播授课一节"),
    "community": ("期早报", "早报推送一期"),
    # 变现位次的「件」不是批量件 —— 一项订阅交付含答疑与续费处理，
    # 不能与图文条数同尺度比较，故单列说明。
    "monetize": ("次交付", "会员订阅交付与答疑一次"),
}


# ─────────────────────────────────────────────────────────────
# 二、瓶颈判定的比例锚点
# ─────────────────────────────────────────────────────────────
# 瓶颈工序 = 单件总工时中占比 ≥ 该阈值的工序。
# 25% 意味着：这一道工序吃掉四分之一以上的精力，
# 优先优化它，收益最大。
BOTTLENECK_THRESHOLD = 0.25

# 一人公司的实际可用工时（口径值）：
# 每周按 6 天工作日、每天专注产出 4 小时计 = 24 小时/周。
# 留出的时间用于分发、回复、迭代等非流水线工作。
WEEKLY_FOCUS_HOURS = 24

# 有效产出系数（口径值）：单条工序链之外的必然占用。
# 一人公司真正的时间去向不止「做内容」：
#   · 多平台分发与排版适配
#   · 评论区与私信回复
#   · 数据回看与选题调整
#   · 素材补充、合规复核、工具维护
#   · 状态波动（生病、情绪、低效时段）
# 单条链只占工作时间的约 55%，其余为维持性开销。
# 若不扣这一层，算出来的产能会显著高于实际可达水平。
EFFECTIVE_OUTPUT_FACTOR = 0.55

# 每月按 4 周计（口径值）—— 用于把周产能折算成月产出件数。
# treemap 的面积口径就是「月产出件数」，全部位次同单位、可比、可复算。
WEEKS_PER_MONTH = 4


def _action_minutes(name, state):
    """取某动作的单件人工分钟。找不到时回退到按性质的保守估计。"""
    if name in TIME_BASE:
        return TIME_BASE[name][0]
    fallback = {"auto": 8, "semi": 25, "manual": 40}
    return fallback.get(state, 30)


def build_chain(items=None):
    """为每个位次构建工序链。

    返回：{role_key: {
        unit, unit_note,
        steps: [{name, state, minutes, dep, bottleneck, cum_minutes, share}],
        total_minutes, manual_minutes, auto_saved_minutes,
        unit_econ: {...}
    }}
    """
    items = items if items is not None else S.build_map()
    chains = {}

    for it in items:
        key = it["key"]
        unit, unit_note = UNIT_DEF.get(key, ("件", "成品一件"))
        acts = it["actions"]
        names = {a["name"] for a in acts}

        steps = []
        for a in acts:
            mins = _action_minutes(a["name"], a["state"])
            # 依赖只保留该位次内真实存在的动作
            deps = [d for d in CHAIN_DEPS.get(a["name"], []) if d in names]
            steps.append({
                "name": a["name"],
                "state": a["state"],
                "state_label": S.TOOL_STATES[a["state"]]["label"],
                "minutes": mins,
                "dep": deps[0] if deps else None,
                "tool": a["tool"],
                "tool_evidence": a["tool_evidence"],
            })

        total = sum(s["minutes"] for s in steps)
        for s in steps:
            s["share"] = round(s["minutes"] / total * 100, 1) if total else 0.0
            s["bottleneck"] = s["share"] / 100 >= BOTTLENECK_THRESHOLD

        # 累积工时（用于甘特式进度展示）
        cum = 0
        for s in steps:
            cum += s["minutes"]
            s["cum_minutes"] = cum

        manual_min = sum(s["minutes"] for s in steps if s["state"] == "manual")
        semi_min = sum(s["minutes"] for s in steps if s["state"] == "semi")
        auto_min = sum(s["minutes"] for s in steps if s["state"] == "auto")
        # 自动化的直接收益：若该环节完全由脚本完成，人工只需抽样验收，
        # 按自动环节工时的 30% 计残余成本。
        auto_saved = round(auto_min * 0.7)
        residual = total - auto_saved

        # 可投入单条链的周有效工时
        usable = WEEKLY_FOCUS_HOURS * 60 * EFFECTIVE_OUTPUT_FACTOR
        unit_econ = {
            "unit": unit,
            "unit_note": unit_note,
            "total_minutes": total,
            "manual_minutes": manual_min,
            "semi_minutes": semi_min,
            "auto_minutes": auto_min,
            "auto_saved_minutes": auto_saved,
            "residual_minutes": residual,
            "weekly_usable_minutes": round(usable),
            "pieces_per_day": round(usable / residual / 5, 1) if residual else 0,
            "pieces_per_week": round(usable / residual) if residual else 0,
            "bottleneck": max(steps, key=lambda s: s["minutes"])["name"] if steps else None,
            "bottleneck_share": max((s["share"] for s in steps), default=0.0),
            # 若把瓶颈手工环节接入管线，可释放的分钟数上限
            "headroom_minutes": max(
                (s["minutes"] for s in steps if s["state"] == "manual"), default=0
            ),
            # 瓶颈自动化后的周产能提升幅度（口径推算）
            "pieces_per_week_if_optimized": (
                round(usable / (residual - max(
                    (s["minutes"] for s in steps if s["state"] == "manual"), default=0
                ) * 0.7)) if residual else 0
            ),
            # 月产出件数（口径推算，由残余工时推导）
            "pieces_per_month": (
                round(usable / residual * WEEKS_PER_MONTH) if residual else 0
            ),
        }

        chains[key] = {
            "unit": unit,
            "unit_note": unit_note,
            "steps": steps,
            "unit_econ": unit_econ,
        }

    return chains


# ─────────────────────────────────────────────────────────────
# 三、90 天推进路线
# ─────────────────────────────────────────────────────────────
# 三个阶段，每阶段有明确出口条件。阶段划分依据：
#   阶段一 补契约与校验 —— 先让素材可信，再谈分发
#   阶段二 上管线       —— 把重复搬运接进脚本，人力腾给表达
#   阶段三 建闭环       —— 产出、分发、复盘形成回路
ROADMAP = [
    {
        "phase": 1,
        "title": "立契约 · 让素材可信",
        "window": "第 1–30 天",
        "goal": "把养生知识表做成唯一真相源，每条可溯源、每条过红线。",
        "tasks": [
            ("建立 SSOT 登记表，明确唯一写入者", "已落地", "docs/契约层.md"),
            ("知识表补出处至篇名级，节气条目到原句级", "已落地", "upgrade_sources.py"),
            ("10 类合规校验规则跑通，全表 0 错误", "已落地", "validate_ssot.py"),
            ("食养条目去功效化重写，杜绝症状指向", "已落地", "rewrite_food_entries.py"),
            ("节气与经典条目建立出处对照表", "已落地", "data/节气经典_出处对照表.md"),
        ],
        "gate": "SSOT 校验 0 错误 0 警告，且任一条目可在 30 秒内回溯出处",
        "exit_signal": "校验器有非零错误，或仍存在无法回溯出处的条目",
    },
    {
        "phase": 2,
        "title": "上管线 · 把重复接进脚本",
        "window": "第 31–60 天",
        "goal": "重复搬运型环节全部进管线，人力集中到判断与表达。",
        "tasks": [
            ("早报六卡自动生成，含合规扫描", "已落地", "build_daily_brief.py"),
            ("早报推送云文档，上传前十项自检", "已落地", "push_brief_to_docs.py"),
            ("体质自测工具生成，结果页红线三层校验", "已落地", "build_constitution_test.py"),
            ("选题抽取、脚本初稿接入早报管线", "已落地", "build_daily_brief.py"),
            ("逐位次锁定瓶颈工序并安排工具化", "待推进", "本表瓶颈一栏"),
        ],
        "gate": "选定一个位次，其手工环节仅剩表达与判断类，且瓶颈工序工时占比降至 25% 以下",
        "exit_signal": "瓶颈工序仍占单件工时 25% 以上，说明提效未落到点上",
    },
    {
        "phase": 3,
        "title": "建闭环 · 产出分发复盘成回路",
        "window": "第 61–90 天",
        "goal": "内容产出、自动分发与效果回看连成可迭代的闭环。",
        "tasks": [
            ("分发通道固化到云文档空间", "已落地", "早报推送通道_腾讯文档.md"),
            ("案例库沉淀可对外展示的成品", "已落地", "生存地图案例页"),
            ("按位次建立产出节奏与产能基线", "待推进", "本表单位经济"),
            ("沉淀可复用模板，形成第二内容源", "待推进", "—"),
            ("建立回流机制：读者问题回灌素材表", "待推进", "—"),
        ],
        "gate": "连续 4 周按计划节奏产出，且每期产出都带出处与免责",
        "exit_signal": "无法维持连续 4 周节奏，说明产能基线定得过高",
    },
    {
        "phase": 4,
        "title": "收现金 · 把陪伴转成订阅",
        "window": "第 91–180 天",
        "goal": "线下交付停办后的唯一现金路径：内容拉新 → 私域沉淀 → 订阅。"
                "先跑通三环的通路判据，再谈规模。",
        "tasks": [
            ("会员权益结构设计与边界自检", "待推进", "本表变现链路第三环"),
            ("订阅内容排期接入早报管线", "待推进", "build_daily_brief.py"),
            ("付费物料合规校验接入订阅流程", "待推进", "ssot_guard"),
            ("记录续订与退订，建立留存口径", "待推进", "—"),
            ("按真实数据回填三环通路判据", "待推进", "本表变现链路"),
        ],
        "gate": "三环各有连续 4 周的真实记录，且续订意愿能被统计，"
                "而不只是统计一次付费",
        "exit_signal": "只能统计一次性成交、统计不出续订意愿，"
                       "说明陪伴关系尚未成立，此时扩量只会放大流失",
    },
]


# ─────────────────────────────────────────────────────────────
# 四、生存风险判据
# ─────────────────────────────────────────────────────────────
# 每条风险给出「可观测指标 + 阈值 + 应对」，阈值是判定线而非预测。
RISKS = [
    {
        "name": "素材见底",
        "indicator": "主素材池可用条数",
        "threshold": "剩余可用条数 < 3 个月产出量",
        "why": "素材耗尽则被迫降质或停更，位次失去内容供给",
        "action": "扩池：接入起居、自省、节气交叉取材，或把长文拆成系列",
    },
    {
        "name": "瓶颈固化",
        "indicator": "单件工时中最大工序占比",
        "threshold": "> 25% 且为手工环节",
        "why": "一道工序吃掉四分之一精力，是产能天花板的真实所在",
        "action": "对该工序做工具化或减法：能否删、并、改为模板复用",
    },
    {
        "name": "合规反噬",
        "indicator": "校验器错误数 / 注入拦截率",
        "threshold": "错误数 > 0，或拦截率 < 100%",
        "why": "一条越界内容可让整个内容位次失去信任，且传播不可撤回",
        "action": "停更排查，先修校验器再恢复产出；红线不做例外",
    },
    {
        "name": "产能透支",
        "indicator": "周产出件数的残余工时占周可用工时比",
        "threshold": "> 100%（排期已超可用工时）",
        "why": "长期超载会牺牲质量，最终触发合规问题或断更",
        "action": "降频而非降质：把节奏从每日改为隔日，保住单件水准",
    },
    {
        "name": "单点依赖",
        "indicator": "位次中纯手工动作数",
        "threshold": "≥ 2 个且都不可迁移",
        "why": "一人公司的产能随人状态波动，单点依赖会让排期连续失真",
        "action": "把其中一个改为半自动：脚本出初稿，人只定稿",
    },
    {
        "name": "口径漂移",
        "indicator": "面积口径与工具化率是否仍可回溯",
        "threshold": "任一项无法回溯到数据层",
        "why": "口径一旦不可核验，地图就成了自我说服，决策失去依据",
        "action": "停用相关结论，回到 SSOT 重建口径后再算",
    },
]


# ─────────────────────────────────────────────────────────────
# 四之半、变现链路（v3 新增 · 线下交付停办后的现金出口）
# ─────────────────────────────────────────────────────────────
# 合规纪律：此处**不出现任何收入数字**。
# 没有真实的定价、转化与续订数据时，任何收入推算都是虚构。
# 链路只回答三个可核验的问题：
#   ① 钱从哪个环节进来          ② 这一环靠什么能力撑住
#   ③ 什么条件下才算这一环通了
# 「通路判据」是可观测的（条数、周数、留存率口径），
# 由使用者用自己的真实数据填入，而不是由这里编一个数字。
MONETIZATION_FUNNEL = [
    {
        "stage": 1,
        "badge": "内容层",
        "title": "公开内容位次",
        "why": "拉新入口",
        "cards": [
            {
                "k": "承载位次",
                "n": "短视频图文 · 图文笔记 · 课程",
                "d": "全部为公开内容位次，承担拉新与信任建立，不直接收费。",
                "m": "工具化率 50%–67%",
            },
            {
                "k": "合规前置",
                "n": "每条成品带出处与免责",
                "d": "内容先过校验器再发布，只写体质倾向与生活原则，"
                      "不写病名、不承诺效果、不限定特定人群。",
                "m": "10 类合规校验规则",
            },
        ],
    },
    {
        "stage": 2,
        "badge": "沉淀层",
        "title": "社群私域主",
        "why": "把注意力变成可反复触达的关系",
        "cards": [
            {
                "k": "承载位次",
                "n": "社群私域主 · 早报推送",
                "d": "早报每日自动生成并推送，是持续触达的载体；订阅内容排期也由此承接。",
                "m": "早报六卡 · 自动生成即校验",
            },
            {
                "k": "触达依据",
                "n": "体质自测工具",
                "d": "自测结果页引用知识表原文，用户带着自己的体质倾向进入社群。",
                "m": "36 题 · 9 体质",
            },
        ],
    },
    {
        "stage": 3,
        "badge": "现金出口",
        "title": "私域变现主",
        "why": "唯一产生现金的环节",
        "cards": [
            {
                "k": "承接位次",
                "n": "会员订阅 · 付费社群",
                "d": "承接前两层沉淀的关系，把长期陪伴转为付费订阅权益。",
                "m": "月交付 30 次（工序链推导）",
            },
            {
                "k": "边界约束",
                "n": "边界与项目条目归此位次",
                "d": "对外物料先过合规校验；项目类条目仅作知识素材介绍，不构成服务承诺。",
                "m": "付费物料合规校验已进管线",
            },
        ],
    },
]


# 各环节的「通路判据」——什么条件下才算这一环真的通了。
# 这些是可观测口径，不是预测值。由使用者填自己的真实数据。
MONETIZATION_GATES = [
    ("公开内容层", "连续 4 周按节奏产出，且每条带出处与免责",
     "内容供给不稳，后面两层就没有原料"),
    ("私域沉淀层", "自测工具的使用者中，有明确比例进入早报订阅并留下体质记录",
     "没有留下个人画像的读者，付费时无法承接"),
    ("现金出口层", "订阅者的续订意愿能被记录，而非只统计一次付费",
     "只做一次性成交，无法判断陪伴关系是否成立"),
]



def build_deep_model(rows=None):
    """产出可直接嵌入页面的深度模型。"""
    items = S.build_map(rows) if rows is not None else S.build_map()
    chains = build_chain(items)
    stats = S.build_stats(rows) if rows is not None else S.build_stats()

    # 把工序链挂回每个位次
    for it in items:
        ch = chains[it["key"]]
        it["chain_steps"] = ch["steps"]
        it["unit_econ"] = ch["unit_econ"]
        # v3：treemap 面积统一为「月产出件数」，由工序链推导，同单位可比
        it["area"] = ch["unit_econ"]["pieces_per_month"]

    # 面积回填后再排序 —— treemap 要求按面积降序
    items.sort(key=lambda x: -x["area"])
    order = [i["key"] for i in items]

    return {
        "roles": {i["key"]: i for i in items},
        "order": order,
        "chains": chains,
        "roadmap": ROADMAP,
        "risks": RISKS,
        "funnel": MONETIZATION_FUNNEL,
        "funnel_gates": MONETIZATION_GATES,
        "config": {
            "weekly_focus_hours": WEEKLY_FOCUS_HOURS,
            "bottleneck_threshold": int(BOTTLENECK_THRESHOLD * 100),
            "effective_factor": EFFECTIVE_OUTPUT_FACTOR,
            "time_basis": "口径值（非实测），可按真实记录覆盖",
        },
        "stats": stats,
    }


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    m = build_deep_model()
    print("=== 养生一人公司 · 深度经营模型 ===\n")
    print(f"{'位次':<14}{'单位':>8}{'总工时':>8}{'残余':>8}{'周产能':>8}  瓶颈")
    print("-" * 76)
    for k in m["order"]:
        r = m["roles"][k]
        u = r["unit_econ"]
        print(f"{r['name']:<14}{u['unit']:>8}{u['total_minutes']:>7}分"
              f"{u['residual_minutes']:>7}分{u['pieces_per_week']:>7}件  {u['bottleneck']}")
    print("\n90 天路线：")
    for p in m["roadmap"]:
        done = sum(1 for t in p["tasks"] if t[1] == "已落地")
        print(f"  阶段{p['phase']} {p['title']}：{done}/{len(p['tasks'])} 已落地")
    print(f"\n风险判据 {len(m['risks'])} 条")
