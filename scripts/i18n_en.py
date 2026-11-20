# -*- coding: utf-8 -*-
"""English locale for the survival map data layer.

Why a separate module instead of adding ``_en`` fields inline:
    The Chinese build (``build_survival_map.py``) is already validated and
    battle-tested.  Touching it for i18n risks regressions in a page that
    hundreds of people have already verified.  So the English edition gets
    its own data module and its own generator, and the two share the exact
    same numeric model (roles, areas, tooling ratios, process chains) —
    only the human-readable strings differ.

Translation rules applied here (see docs/en/compliance-handbook.md):
    1. Never imply therapeutic effect.  "wellness habit", "constitution
       tendency" and "daily routine principle" are used instead of
       "treatment", "cure", "therapy" or "remedy".
    2. Never name a disease as an indication.
    3. "companionship, never diagnosis" stays companionship.
    4. The cash outlet is a *subscription*, not a clinical service.
"""

import copy

# ─────────────────────────────────────────────────────────────
# 1. Themes — the SSOT material pools that drive treemap area
# ─────────────────────────────────────────────────────────────

THEME_EN = {
    "食养": "Food Therapy",
    "体质": "Constitution",
    "节气": "Solar Term",
    "经典": "Classical Text",
    "自省": "Self-Reflection",
    "起居": "Daily Routine",
    "边界": "Boundaries",
    "项目": "Programs",
}

# ─────────────────────────────────────────────────────────────
# 2. Tooling states
# ─────────────────────────────────────────────────────────────

TOOL_STATE_EN = {
    "auto": {"label": "Automated", "desc": "scripted end to end, human not involved"},
    "semi": {"label": "Semi-automated", "desc": "script drafts, human finalises"},
    "manual": {"label": "Manual", "desc": "no tooling, written by hand"},
}

# ─────────────────────────────────────────────────────────────
# 3. Tooling evidence — every entry points at a real script
# ─────────────────────────────────────────────────────────────

TOOL_EVIDENCE_EN = {
    "brief_gen": "build_daily_brief.py — six-card daily brief auto-generated (solar-term snapshot / constitution profile / classical quote / today's care / reflection prompt / tomorrow preview)",
    "brief_push": "push_brief_to_docs.py — daily brief MD→MDX→cloud-doc push, 10 self-checks before upload",
    "brief_scan": "build_daily_brief.py — built-in compliance scanner for briefs (claims / medication / consultation-solicitation / program)",
    "constitution_gen": "build_constitution_test.py — 36-question nine-constitution self-assessment, single-file build",
    "constitution_guard": "validate_constitution_html.py — three-layer red-line validation on the result page + 14 injection tests",
    "ssot_guard": "validate_ssot.py — 10 compliance rule families over the whole SSOT table, 0 errors 0 warnings",
    "source_upgrade": "upgrade_sources.py — upgrades every entry's citation to chapter-and-quote level",
    "food_rewrite": "rewrite_food_entries.py — batch rewrite of food entries to remove efficacy wording",
    "batch_build": "build_wellness_batch2/3/4.py — batch generation of constitution segments and solar-term entries",
    "source_map": "data/节气经典_出处对照表.md — quote-level source cross-reference table",
}

# ─────────────────────────────────────────────────────────────
# 4. Role slots — the ten independent business slots of a
#    one-person company, plus their English copy
# ─────────────────────────────────────────────────────────────

ROLE_EN = {
    "food_channel": {
        "name": "Food-Wellness Channel Lead",
        "sub": "One Food, One Lesson · The Daily Table",
        "desc": "Builds content around everyday meals. This slot consumes the largest volume of material, so it is also the one that runs out first if nothing replenishes it.",
        "actions": {
            "条目拆解与合规改写": "Entry breakdown and compliance rewrite",
            "去功效化重写": "Efficacy-wording removal",
            "食材目录归属核对": "Ingredient catalogue classification check",
            "出处回填至原句": "Citation backfill to quote level",
            "成品文案撰写": "Final copy writing",
        },
    },
    "solar_channel": {
        "name": "Solar-Term Wellness Lead",
        "sub": "24 Solar Terms · Seasonal Living",
        "desc": "A calendar-driven slot: material rotates with the solar terms, which makes the content rhythm self-evident rather than something you have to invent.",
        "actions": {
            "节气条目生成": "Solar-term entry generation",
            "经典原句配对": "Classical quote pairing",
            "节气归位与出处核验": "Term assignment and citation verification",
            "时令文案撰写": "Seasonal copy writing",
        },
    },
    "constitution_channel": {
        "name": "Constitution Insight Lead",
        "sub": "Nine Constitutions · Tendency Science",
        "desc": "Explains constitution tendencies and drives the self-assessment interaction. The output is a tendency profile, never a diagnosis.",
        "actions": {
            "体质条目入库": "Constitution entry intake",
            "自测题库与工具生成": "Question bank and assessment build",
            "结果页红线校验": "Result-page red-line validation",
            "结果页溯源对齐": "Result-page citation alignment",
            "体质科普文案撰写": "Constitution explainer copy writing",
        },
    },
    "classic_channel": {
        "name": "Classical Text Scholar",
        "sub": "Huangdi Neijing · Quote-Level Citations",
        "desc": "Does source tracing and plain-language reading of the classics. Small material volume, but the highest citation precision bar in the whole system.",
        "actions": {
            "篇名与原句级出处核验": "Chapter-and-quote citation verification",
            "出处对照表维护": "Citation cross-reference maintenance",
            "原典逐字比对（ctext/wikisource）": "Verbatim collation against ctext / wikisource",
            "白话释读撰写": "Plain-language reading writing",
        },
    },
    "routine_channel": {
        "name": "Daily Routine Lead",
        "sub": "Sleep, Rhythm, Everyday Habits",
        "desc": "Covers the mechanics of a day: sleep, waking, pace. The advice stays at the level of general routine principles, never condition-specific.",
        "actions": {
            "起居条目拆解与合规改写": "Routine entry breakdown and compliance rewrite",
            "节律建议成稿撰写": "Rhythm recommendation drafting",
            "起居合规扫描": "Routine compliance scan",
        },
    },
    "self_reflect": {
        "name": "Self-Reflection Lead",
        "sub": "One Question a Day · Emotional Living",
        "desc": "A daily question rather than a daily lecture. This slot carries the companionship tone of the whole system.",
        "actions": {
            "自省条目入库": "Reflection entry intake",
    "自测题库与工具生成": "Question bank and assessment build",
            "每日一问生成": "Daily question generation",
            "早报合规扫描": "Brief compliance scan",
            "问答撰写与改写": "Question answering and rewriting",
        },
    },
    "content_dual": {
        "name": "Short-Video & Carousel Producer",
        "sub": "Spoken Video · Illustrated Notes",
        "desc": "Transfers finished material into two output shapes. The scripted steps stay deliberately shallow — the judgment in delivery is what you keep by hand.",
        "actions": {
            "选题素材抽取": "Topic material extraction",
            "脚本初稿生成": "Script first-draft generation",
            "配图文案初稿生成": "Caption first-draft generation",
            "合规扫描与改写": "Compliance scan and rewrite",
            "素材溯源核对": "Material citation check",
            "口播表达与演绎": "Spoken delivery and interpretation",
            "成稿润色": "Final polish",
        },
    },
    "course_teacher": {
        "name": "Online Course Instructor",
        "sub": "Structured Course · Live Teaching",
        "desc": "Packages the material into a sequence. Live teaching is where the questions actually arrive, so it stays fully manual on purpose.",
        "actions": {
            "课程大纲素材编排": "Course outline material sequencing",
            "讲义初稿生成": "Handout first-draft generation",
            "合规扫描": "Compliance scan",
            "授课讲授与答疑": "Teaching and Q&A",
        },
    },
    "community": {
        "name": "Community & Private-Channel Lead",
        "sub": "Daily Briefs · Long-term Companionship",
        "desc": "The slot that turns scattered attention into a relationship you can reach again tomorrow. It is the first layer where people opt in.",
        "actions": {
            "早报每日生成": "Daily brief generation",
            "早报推送分发": "Daily brief push and delivery",
            "推送前合规自检": "Pre-push compliance self-check",
            "群内答疑与陪伴": "In-group Q&A and companionship",
        },
    },
    "monetize": {
        "name": "Monetization Lead",
        "sub": "Membership Subscription · Paid Community",
        "desc": "The single cash outlet of the whole system. It converts a long companionship into a paid subscription. Off-premise delivery was discontinued, so this is the only path to revenue.",
        "actions": {
            "会员权益结构设计": "Membership benefit structure design",
            "订阅内容排期编排": "Subscription content scheduling",
            "付费物料合规校验": "Paid-material compliance validation",
            "会员答疑与陪伴": "Member Q&A and companionship",
            "订阅续费与退订处理": "Subscription renewal and cancellation handling",
        },
    },
}

# ─────────────────────────────────────────────────────────────
# 5. Output units
# ─────────────────────────────────────────────────────────────

UNIT_EN = {
    "food_channel": ("post", "one finished food-wellness post"),
    "solar_channel": ("post", "one finished seasonal post"),
    "constitution_channel": ("post", "one finished constitution explainer"),
    "classic_channel": ("reading", "one plain-language classical reading"),
    "routine_channel": ("post", "one finished daily-routine post"),
    "self_reflect": ("Q&A", "one reflection Q&A"),
    "content_dual": ("finished piece", "one finished short video or carousel"),
    "course_teacher": ("lesson", "one live teaching session"),
    "community": ("brief", "one daily brief pushed"),
    "monetize": ("delivery", "one subscription delivery and Q&A"),
}

# ─────────────────────────────────────────────────────────────
# 6. Process-chain step names (TIME_BASE / CHAIN_DEPS keys)
# ─────────────────────────────────────────────────────────────

ACTION_EN = {
    "付费物料合规校验": "Paid-material compliance check",
    "会员权益结构设计": "Membership benefit design",
    "会员答疑与陪伴": "Member Q&A and companionship",
    "体质条目入库": "Constitution entry intake",
    "体质科普文案撰写": "Constitution explainer writing",
    "出处回填至原句": "Citation backfill to quote level",
    "出处对照表维护": "Citation cross-reference upkeep",
    "原典逐字比对（ctext/wikisource）": "Verbatim collation (ctext / wikisource)",
    "去功效化重写": "Efficacy-wording removal",
    "口播表达与演绎": "Spoken delivery and interpretation",
    "合规扫描": "Compliance scan",
    "合规扫描与改写": "Compliance scan and rewrite",
    "对外物料合规校验": "Outbound-material compliance check",
    "成品文案撰写": "Final copy writing",
    "成稿润色": "Final polish",
    "授课讲授与答疑": "Teaching and Q&A",
    "推送前合规自检": "Pre-push compliance self-check",
    "早报合规扫描": "Brief compliance scan",
    "早报推送分发": "Daily brief push and delivery",
    "早报每日生成": "Daily brief generation",
    "时令文案撰写": "Seasonal copy writing",
    "条目拆解与合规改写": "Entry breakdown and compliance rewrite",
    "每日一问生成": "Daily question generation",
    "白话释读撰写": "Plain-language reading writing",
    "篇名与原句级出处核验": "Chapter-and-quote citation verification",
    "素材溯源核对": "Material citation check",
    "经典原句配对": "Classical quote pairing",
    "结果页溯源对齐": "Result-page citation alignment",
    "结果页红线校验": "Result-page red-line check",
    "群内答疑与陪伴": "In-group Q&A and companionship",
    "脚本初稿生成": "Script first-draft generation",
    "自省条目入库": "Reflection entry intake",
    "自测题库与工具生成": "Question bank and assessment build",
    "节律建议成稿撰写": "Rhythm recommendation drafting",
    "节气归位与出处核验": "Term assignment and citation check",
    "节气条目生成": "Solar-term entry generation",
    "订阅内容排期编排": "Subscription content scheduling",
    "订阅续费与退订处理": "Renewal and cancellation handling",
    "讲义初稿生成": "Handout first-draft generation",
    "课程大纲素材编排": "Course outline sequencing",
    "起居合规扫描": "Routine compliance scan",
    "起居条目拆解与合规改写": "Routine entry breakdown and rewrite",
    "选题素材抽取": "Topic material extraction",
    "配图文案初稿生成": "Caption first-draft generation",
    "问答撰写与改写": "Q&A writing and rewriting",
    "项目与边界条目维护": "Program and boundary entry upkeep",
    "食材目录归属核对": "Ingredient catalogue classification check",
}

# ─────────────────────────────────────────────────────────────
# 7. 90-day roadmap
# ─────────────────────────────────────────────────────────────

ROADMAP_EN = {
    1: {
        "title": "Establish the contract · Make the material trustworthy",
        "window": "Days 1–30",
        "goal": "Make the knowledge table the single source of truth: every entry traceable, every entry past the red lines.",
        "tasks": {
            "建立 SSOT 登记表，明确唯一写入者": "Register the SSOT and name the single writer",
            "知识表补出处至篇名级，节气条目到原句级": "Backfill citations to chapter level, solar-term entries to quote level",
            "10 类合规校验规则跑通，全表 0 错误": "Get all 10 compliance rule families passing, 0 errors table-wide",
            "食养条目去功效化重写，杜绝症状指向": "Rewrite food entries to remove efficacy wording and symptom targeting",
            "节气与经典条目建立出处对照表": "Build the quote-level source cross-reference table",
        },
        "gate": "SSOT validation returns 0 errors and 0 warnings, and any single entry can be traced to its source in 30 seconds",
        "exit_signal": "The validator returns a non-zero error count, or entries remain whose source cannot be traced",
    },
    2: {
        "title": "Pipe it · Move repetition into scripts",
        "window": "Days 31–60",
        "goal": "Every repetitive handling step moves into the pipeline, so human effort concentrates on judgment and expression.",
        "tasks": {
            "早报六卡自动生成，含合规扫描": "Auto-generate the six-card daily brief, compliance scan included",
            "早报推送云文档，上传前十项自检": "Push the brief to a cloud doc, 10 self-checks before upload",
            "体质自测工具生成，结果页红线三层校验": "Build the self-assessment tool, three-layer red-line check on the result page",
            "选题抽取、脚本初稿接入早报管线": "Wire topic extraction and script drafting into the brief pipeline",
            "逐位次锁定瓶颈工序并安排工具化": "Lock the bottleneck step per role slot and schedule its tooling",
        },
        "gate": "For one chosen slot, only expression and judgment remain manual, and the bottleneck step falls below 25% of per-piece minutes",
        "exit_signal": "The bottleneck step still takes more than 25% of per-piece minutes — the efficiency gain missed its target",
    },
    3: {
        "title": "Close the loop · Output, distribution and review become a circuit",
        "window": "Days 61–90",
        "goal": "Connect content output, automated distribution and effect review into a loop that can be iterated.",
        "tasks": {
            "分发通道固化到云文档空间": "Lock the distribution channel to a cloud doc space",
            "案例库沉淀可对外展示的成品": "Accumulate finished, externally presentable work in the case library",
            "按位次建立产出节奏与产能基线": "Set an output rhythm and a capacity baseline per role slot",
            "沉淀可复用模板，形成第二内容源": "Distil reusable templates into a second content source",
            "建立回流机制：读者问题回灌素材表": "Build the feedback loop: reader questions feed back into the material table",
        },
        "gate": "Four consecutive weeks at the planned rhythm, with every output carrying a citation and a disclaimer",
        "exit_signal": "The rhythm cannot be held for four consecutive weeks — the capacity baseline was set too high",
    },
    4: {
        "title": "Collect cash · Turn companionship into a subscription",
        "window": "Days 91–180",
        "goal": "The only cash path after off-premise delivery was discontinued: content brings people in, the private channel retains them, subscription converts them. Prove the three links work before worrying about scale.",
        "tasks": {
            "会员权益结构设计与边界自检": "Design the membership benefit structure and self-check its boundaries",
            "订阅内容排期接入早报管线": "Wire subscription content scheduling into the brief pipeline",
            "付费物料合规校验接入订阅流程": "Wire paid-material compliance validation into the subscription flow",
            "记录续订与退订，建立留存口径": "Record renewals and cancellations, establish a retention metric",
            "按真实数据回填三环通路判据": "Backfill the three-link gate criteria with real data",
        },
        "gate": "All three links have four consecutive weeks of real records, and renewal intent is measurable — not just one-off purchases",
        "exit_signal": "Only one-off transactions can be counted, and renewal intent cannot — which means the companionship is not real",
    },
}

# ─────────────────────────────────────────────────────────────
# 8. Risk register — six observable criteria
# ─────────────────────────────────────────────────────────────

RISK_EN = {
    "素材见底": {
        "name": "Material running dry",
        "indicator": "Usable entries remaining in the primary material pool",
        "threshold": "Remaining usable entries < 3 months of output",
        "why": "When material runs out you are pushed to cut quality or stop publishing, and the slot loses its supply.",
        "action": "Widen the pool: cross-source from daily-routine, reflection and solar-term material, or split long pieces into series",
    },
    "瓶颈固化": {
        "name": "Bottleneck hardening",
        "indicator": "Share of per-piece minutes taken by the single largest step",
        "threshold": "> 25% and the step is manual",
        "why": "One step eating a quarter of your attention is where the real capacity ceiling sits.",
        "action": "Tool it or subtract from it: can the step be deleted, merged, or turned into a reusable template?",
    },
    "合规反噬": {
        "name": "Compliance backlash",
        "indicator": "Validator error count / injection interception rate",
        "threshold": "Error count > 0, or interception rate < 100%",
        "why": "One out-of-bounds item can cost an entire channel its trust, and distribution cannot be taken back.",
        "action": "Pause publishing, fix the validator first, then resume. Red lines get no exceptions",
    },
    "产能透支": {
        "name": "Capacity overdraft",
        "indicator": "Residual minutes of weekly output as a share of available weekly hours",
        "threshold": "> 100% (the schedule already exceeds available hours)",
        "why": "Running overloaded for long costs quality and eventually trips either a compliance problem or a silent stop.",
        "action": "Lower the frequency, not the quality: move from daily to every other day and protect per-piece standards",
    },
    "单点依赖": {
        "name": "Single-point dependency",
        "indicator": "Number of purely manual steps in a role slot",
        "threshold": "≥ 2 and neither is transferable",
        "why": "A one-person company's capacity swings with their own state, and a single point of dependency makes the schedule wrong in a streak.",
        "action": "Turn one of them semi-automated: the script drafts, the human only finalises",
    },
    "口径漂移": {
        "name": "Metric drift",
        "indicator": "Whether the area metric and tooling ratio are still traceable",
        "threshold": "Either one can no longer be traced back to the data layer",
        "why": "Once the metric stops being verifiable, the map becomes self-persuasion and decisions lose their basis.",
        "action": "Stop using the affected conclusions, go back to the SSOT, rebuild the metric, then recompute",
    },
}

# ─────────────────────────────────────────────────────────────
# 9. Monetization path — three links, one cash outlet
# ─────────────────────────────────────────────────────────────

FUNNEL_EN = [
    {
        "stage": 1,
        "badge": "Content layer",
        "title": "Public content slots",
        "why": "The acquisition front door",
        "cards": {
            "承载位次": {
                "k": "Carrying slot",
                "n": "Short video & carousel · illustrated notes · course",
                "d": "All public content slots. They carry acquisition and trust-building, and charge nothing directly.",
                "m": "Tooling ratio 50%–67%",
            },
            "合规前置": {
                "k": "Compliance first",
                "n": "Every finished piece carries a citation and a disclaimer",
                "d": "Content passes the validator before publication. It states constitution tendencies and living principles only — never a disease name, never an outcome promise, never a restricted audience.",
                "m": "22 red-line checks",
            },
        },
    },
    {
        "stage": 2,
        "badge": "Retention layer",
        "title": "Community & private channel",
        "why": "Turn attention into a relationship you can reach again",
        "cards": {
            "承载位次": {
                "k": "Carrying slot",
                "n": "Community lead · daily brief push",
                "d": "The daily brief is generated and pushed automatically — the carrier of continuous contact. Subscription scheduling is picked up from here.",
                "m": "Six-card brief · generated and validated together",
            },
            "触达依据": {
                "k": "Reason to engage",
                "n": "The constitution self-assessment",
                "d": "The result page quotes the knowledge table, so readers arrive in the community already holding a constitution tendency profile.",
                "m": "36 questions · 9 constitutions",
            },
        },
    },
    {
        "stage": 3,
        "badge": "Cash outlet",
        "title": "Monetization lead",
        "why": "The only step that produces cash",
        "cards": {
            "承接位次": {
                "k": "Receiving slot",
                "n": "Membership subscription · paid community",
                "d": "Receives the relationships retained by the two layers above and turns long companionship into paid subscription benefits.",
                "m": "30 deliveries per month (derived from the process chain)",
            },
            "边界约束": {
                "k": "Boundary constraint",
                "n": "Boundary and program entries belong to this slot",
                "d": "Outbound material passes compliance validation first. Program entries are introduced as knowledge material only, and constitute no service promise.",
                "m": "Paid-material compliance check is in the pipeline",
            },
        },
    },
]

FUNNEL_GATES_EN = [
    {
        "layer": "Public content layer",
        "gate": "Four consecutive weeks at the planned rhythm, every piece carrying a citation and a disclaimer",
        "why": "If the content supply wobbles, the two layers above it have no raw material",
    },
    {
        "layer": "Private retention layer",
        "gate": "A measurable share of self-assessment users enter the brief subscription and leave a constitution record",
        "why": "A reader who leaves no profile behind cannot be served when they pay",
    },
    {
        "layer": "Cash outlet layer",
        "gate": "Subscribers' renewal intent is recorded, not just one-off purchases",
        "why": "Counting only one-off transactions cannot tell you whether the relationship holds",
    },
]

# ─────────────────────────────────────────────────────────────
# 10. Roadmap task status and internal evidence pointers
# ─────────────────────────────────────────────────────────────

STATUS_EN = {
    "已落地": "Shipped",
    "待推进": "Next",
}

# Internal pointers are translated for readability.  Real file paths stay
# untouched — they are what a reader has to type.
EVIDENCE_EN = {
    "本表瓶颈一栏": "bottleneck column in this table",
    "本表单位经济": "unit economics in this table",
    "本表变现链路": "monetization path in this table",
    "本表变现链路第三环": "third link of the monetization path in this table",
    "生存地图案例页": "survival map case page",
    "早报推送通道_腾讯文档.md": "早报推送通道_腾讯文档.md (daily-brief push channel doc)",
}


# ─────────────────────────────────────────────────────────────
# 11. Localisation helpers
# ─────────────────────────────────────────────────────────────


def localize_roles(roles):
    """Return a deep copy of ROLES with English copy attached.

    The numeric model (themes, action states, tooling tools) is untouched —
    only the human-readable strings are replaced.
    """
    out = copy.deepcopy(roles)
    for role in out:
        en = ROLE_EN.get(role["key"], {})
        role["name_en"] = role["name"] = en.get("name", role["name"])
        role["sub_en"] = role["sub"] = en.get("sub", role["sub"])
        role["desc_en"] = role["desc"] = en.get("desc", role["desc"])
        amap = en.get("actions", {})
        for act in role["actions"]:
            act["name_en"] = act["name"] = amap.get(act["name"], act["name"])
    return out


def localize_roadmap(roadmap):
    out = copy.deepcopy(roadmap)
    for phase in out:
        en = ROADMAP_EN.get(phase["phase"], {})
        phase["title_en"] = phase["title"] = en.get("title", phase["title"])
        phase["window_en"] = phase["window"] = en.get("window", phase["window"])
        phase["goal_en"] = phase["goal"] = en.get("goal", phase["goal"])
        phase["gate_en"] = phase["gate"] = en.get("gate", phase["gate"])
        phase["exit_signal_en"] = phase["exit_signal"] = en.get(
            "exit_signal", phase["exit_signal"])
        tmap = en.get("tasks", {})
        # tasks are (title, status, evidence) tuples -> widen to list and append EN title
        phase["tasks"] = [
            [tmap.get(t[0], t[0])] + list(t[1:])
            for t in phase["tasks"]
        ]
        for t in phase["tasks"]:
            t[1] = STATUS_EN.get(t[1], t[1])
            t[2] = EVIDENCE_EN.get(t[2], t[2])
    return out


def localize_risks(risks):
    out = copy.deepcopy(risks)
    for risk in out:
        en = RISK_EN.get(risk["name"], {})
        risk["name_en"] = risk["name"] = en.get("name", risk["name"])
        risk["indicator_en"] = risk["indicator"] = en.get("indicator", risk["indicator"])
        risk["threshold_en"] = risk["threshold"] = en.get("threshold", risk["threshold"])
        risk["why_en"] = risk["why"] = en.get("why", risk["why"])
        risk["action_en"] = risk["action"] = en.get("action", risk["action"])
    return out


def localize_funnel(funnel, gates):
    out = copy.deepcopy(funnel)
    for stage in out:
        en = next((s for s in FUNNEL_EN if s["stage"] == stage["stage"]), {})
        stage["badge_en"] = stage["badge"] = en.get("badge", stage["badge"])
        stage["title_en"] = stage["title"] = en.get("title", stage["title"])
        stage["why_en"] = stage["why"] = en.get("why", stage["why"])
        cmap = en.get("cards", {})
        for card in stage["cards"]:
            c = cmap.get(card["k"], {})
            card["k_en"] = card["k"] = c.get("k", card["k"])
            card["n_en"] = card["n"] = c.get("n", card["n"])
            card["d_en"] = card["d"] = c.get("d", card["d"])
            card["m_en"] = card["m"] = c.get("m", card["m"])
    g_out = []
    for g, en in zip(gates, FUNNEL_GATES_EN):
        g_out.append([en["layer"], en["gate"], en["why"]])
    return out, g_out
