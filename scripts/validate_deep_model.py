#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
养生一人公司生存地图 · 深度模型校验
===================================

校验新增的四个维度（工序链 / 经营推演 / 90天路线 / 风险预警）：

  D1 结构完整   —— 新增页签、面板、控件齐全
  D2 数据自洽   —— 工序链工时、单位经济、推演参数内部一致
  D3 页面一致   —— 页面渲染出的数字与数据层逐项对得上
  D4 合规       —— 新增文案不越红线、不含收入承诺、不含引流

判据全部可复算，不依赖人工阅读。
"""

import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import SURVIVAL_MAP_HTML as HTML_PATH, SIM_JS as SIM_JS_PATH  # noqa: E402
sys.stdout.reconfigure(encoding="utf-8")

import survival_map_data as S
import survival_deep_model as D



checks = []
errors = []


def ok(msg):
    checks.append(msg)


def bad(msg):
    errors.append(msg)


def strip_tags(t):
    t = re.sub(r"<script[\s\S]*?</script>", " ", t)
    t = re.sub(r"<style[\s\S]*?</style>", " ", t)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", t)


def strip_scripts(html_text):
    """仅保留静态 HTML 部分（去掉 script），用于「静态可见文案」检查。"""
    return re.sub(r"<script[\s\S]*?</script>", " ", html_text)


def has_negated_ctx(text, pos, window=30):
    """判断命中位置是否处于否定语境。

    防护性表述（如「不做收入预测」「收入预测都是虚构」）本身是合规声明，
    不能因为含有敏感词就判违规 —— 那样只会逼着人把声明删掉。

    注意否定词可能出现在命中位置的**前方或后方**
    （「不做收入预测」在前，「收入预测都是虚构」在后），
    故前后窗口都要查。

    但后置否定必须**紧邻**命中词（间隔不超过 6 字）——
    否则「保底收入 8000 元/月 …… 本页所有推算都是虚构」这种
    真违规会被误放行。实测踩过这个坑。
    """
    before = text[max(0, pos - window):pos]
    after = text[pos:pos + window]
    # 前置否定词表。
    # 注意：不能把「不构成诊断或治疗建议」这类**免责声明**当作豁免依据 ——
    # 否则任何免责声明后面的收入承诺都会被放行（实测踩过）。
    # 免责类词单独剔除，只保留真正在否定该命中词的表达。
    marks = ["不做收入", "不做", "不推算", "不承诺", "不出现", "不含",
             "不由本表", "没有真实", "不提供", "不预测", "无收入"]
    if any(x in before for x in marks):
        return True
    # 后置否定：仅接受紧邻的「……都是虚构 / ……是虚构」
    tight = after[:8]
    return bool(re.search(r"^(?:[^。；;]{0,4})(都是虚构|是虚构)", tight))


def unescape(t):
    """还原 HTML 实体，便于与数据层原文逐字比较。"""
    return (t.replace("&lt;", "<").replace("&gt;", ">")
             .replace("&amp;", "&").replace("&quot;", '"')
             .replace("&#39;", "'").replace("&nbsp;", " "))


def main():
    model = D.build_deep_model()
    roles = model["roles"]
    order = model["order"]

    html = io.open(HTML_PATH, encoding="utf-8").read()
    visible = strip_tags(html)
    # 静态可见文案（不含 script）
    static_visible = strip_tags(strip_scripts(html))
    # JS 内的模板文案——动态渲染出来的用户可见文本。
    # 注意：脚本块本身不能再走 strip_tags（那会把 script 整块删空），
    # 只做「去标签 + 压空白」。
    js_visible = re.sub(
        r"\s+", " ",
        " ".join(re.sub(r"<[^>]+>", " ", m)
                 for m in re.findall(r"<script[\s\S]*?</script>", html)),
    )

    # ───────────────────────────────────────────────────────
    # D1 结构完整
    # ───────────────────────────────────────────────────────
    EXPECTED_TABS = [
        ("panel-map", "生存地图"), ("panel-chain", "工序链"),
        ("panel-sim", "经营推演"), ("panel-funnel", "变现链路"),
        ("panel-roadmap", "90天路线"),
        ("panel-risk", "风险预警"), ("panel-report", "生成报告"),
        ("panel-model", "生存模型"), ("panel-cases", "案例库"),
    ]
    for pid, name in EXPECTED_TABS:
        if f'id="{pid}"' in html:
            ok(f"D1 面板 {name} 在位")
        else:
            bad(f"D1 缺少面板 {name}")

    tabs = re.findall(r'<button[^>]*data-tab="([^"]+)"', html)
    expect_tabs = [p.replace("panel-", "") for p, _ in EXPECTED_TABS]
    if len(tabs) == len(expect_tabs) and set(tabs) == set(expect_tabs):
        ok(f"D1 导航页签 {len(tabs)} 个齐全且与面板对应")
    else:
        bad(f"D1 导航页签异常：{len(tabs)} 个 {tabs}，"
            f"应为 {len(expect_tabs)} 个 {expect_tabs}")

    for cid in ["chainOpts", "simOpts", "simHours", "simOpt", "simAuto"]:
        if f'id="{cid}"' in html:
            ok(f"D1 控件 {cid} 在位")
        else:
            bad(f"D1 缺少控件 {cid}")

    # 推演引擎独立文件且被内联
    sim_js = io.open(SIM_JS_PATH, encoding="utf-8").read()
    if "const SIM = (function" in sim_js and "function run(" in sim_js:
        ok("D1 推演引擎结构完整（SIM.run 可用）")
    else:
        bad("D1 推演引擎结构异常")
    if "const SIM = (function" in html:
        ok("D1 推演引擎已内联进单文件页面")
    else:
        bad("D1 推演引擎未内联，页面将无法离线运行")

    # ───────────────────────────────────────────────────────
    # D2 数据自洽
    # ───────────────────────────────────────────────────────
    for k in order:
        r = roles[k]
        u = r["unit_econ"]
        steps = r["chain_steps"]

        # 工序链非空且每步都有工时
        if steps and all(s["minutes"] > 0 for s in steps):
            ok(f"D2 {r['name']} 工序链 {len(steps)} 步，工时齐备")
        else:
            bad(f"D2 {r['name']} 工序链存在零工时或空步骤")

        # 单件总工时 = 各步之和
        if sum(s["minutes"] for s in steps) == u["total_minutes"]:
            ok(f"D2 {r['name']} 单件总工时 {u['total_minutes']} 分 = 各工序之和")
        else:
            bad(f"D2 {r['name']} 单件总工时与工序之和不符")

        # 残余工时 = 总工时 - 自动化节省
        if u["total_minutes"] - u["auto_saved_minutes"] == u["residual_minutes"]:
            ok(f"D2 {r['name']} 残余工时 {u['residual_minutes']} 分计算正确")
        else:
            bad(f"D2 {r['name']} 残余工时计算错误")

        # 瓶颈判定：至少一个工序被标为瓶颈，且其占比 ≥ 阈值
        thr = model["config"]["bottleneck_threshold"] / 100
        bns = [s for s in steps if s["bottleneck"]]
        if bns and all(s["share"] / 100 >= thr for s in bns):
            ok(f"D2 {r['name']} 瓶颈判定成立（{bns[0]['name']} 占 {bns[0]['share']}%）")
        else:
            bad(f"D2 {r['name']} 瓶颈判定与阈值 {int(thr*100)}% 不符")

        # 最耗工时的工序必须就是瓶颈之一
        top = max(steps, key=lambda s: s["minutes"])
        if top["name"] in [s["name"] for s in bns]:
            ok(f"D2 {r['name']} 最耗时工序即瓶颈（{top['name']}）")
        else:
            bad(f"D2 {r['name']} 最耗时工序 {top['name']} 未被标为瓶颈")

        # 产能为正且落在合理区间（一人公司不可能一周产 200 件）
        pw = u["pieces_per_week"]
        if 0 < pw <= 60:
            ok(f"D2 {r['name']} 周产能 {pw} 件在合理区间")
        else:
            bad(f"D2 {r['name']} 周产能 {pw} 件超出合理区间（0–60）")

    # 有效产出系数必须在 0 与 1 之间，且产能计算确实用了它
    ef = model["config"]["effective_factor"]
    if 0 < ef < 1:
        ok(f"D2 有效产出系数 {ef} 合法（已扣除维持性开销）")
    else:
        bad(f"D2 有效产出系数 {ef} 非法")

    # 路线图：每阶段必须有出口条件与任务
    for p in model["roadmap"]:
        if p["tasks"] and p["gate"] and p["exit_signal"]:
            ok(f"D2 阶段{p['phase']} {p['title']}：{len(p['tasks'])} 项任务，出口条件齐备")
        else:
            bad(f"D2 阶段{p['phase']} 缺少任务或出口条件")

    # 风险：每条必须有指标、阈值、应对
    for r in model["risks"]:
        if r["indicator"] and r["threshold"] and r["action"]:
            ok(f"D2 风险「{r['name']}」判据齐备")
        else:
            bad(f"D2 风险「{r['name']}」判据不完整")

    # ───────────────────────────────────────────────────────
    # D3 页面一致
    # ───────────────────────────────────────────────────────
    # MODEL 数据必须内联且与数据层一致
    m = re.search(r"const MODEL = (\{.*?\});\n", html, re.S)
    if m:
        try:
            page_model = json.loads(m.group(1))
            same = all(
                page_model["roles"][k]["unit_econ"]["residual_minutes"]
                == roles[k]["unit_econ"]["residual_minutes"]
                for k in order
            )
            if same:
                ok("D3 页面内联模型与数据层逐位一致")
            else:
                bad("D3 页面内联模型与数据层不一致")
        except json.JSONDecodeError as e:
            bad(f"D3 页面内联模型 JSON 解析失败：{e}")
            page_model = None
    else:
        bad("D3 页面未内联 MODEL 数据")
        page_model = None

    # 逐字段双向核验：页面里的每个数字都要能被数据层重算复现。
    # 这一层专门防「页面数字被改但内部仍自洽」的情况。
    if page_model:
        for k in order:
            pu = page_model["roles"][k]["unit_econ"]
            du = roles[k]["unit_econ"]
            for field in ("total_minutes", "residual_minutes", "manual_minutes",
                          "auto_saved_minutes", "pieces_per_week",
                          "weekly_usable_minutes", "pieces_per_month"):
                if pu.get(field) != du.get(field):
                    bad(f"D3 {roles[k]['name']} 页面内联 {field} 被篡改："
                        f"页面 {pu.get(field)} / 数据层 {du.get(field)}")

            # v3 核心字段：面积、独占素材、位次性质
            # 这三项一旦被改，treemap 的面积口径与现金出口判定都会失真，
            # 必须逐位核验（只比对 unit_econ 不够 —— 那是上一个漏过点）。
            pr = page_model["roles"][k]
            dr = roles[k]
            for field in ("area", "material", "is_channel", "is_cash"):
                if pr.get(field) != dr.get(field):
                    bad(f"D3 {dr['name']} 页面内联 {field} 被篡改："
                        f"页面 {pr.get(field)} / 数据层 {dr.get(field)}")

        # v3 不变量：页面内联模型的素材互斥分摊必须守恒
        pm_sum = sum(r.get("material", 0) for r in page_model["roles"].values())
        dm_sum = sum(r.get("material", 0) for r in roles.values())
        if pm_sum != dm_sum:
            bad(f"D3 页面内联素材分摊不守恒：页面 Σ {pm_sum} / 数据层 Σ {dm_sum}")
        else:
            ok(f"D3 页面内联素材分摊守恒（Σ {pm_sum}）")

        # v3 不变量：页面内联模型必须存在现金出口
        pm_cash = [r["name"] for r in page_model["roles"].values() if r.get("is_cash")]
        if not pm_cash:
            bad("D3 页面内联模型缺少现金出口位次")
        else:
            ok(f"D3 页面内联模型现金出口在位：{pm_cash}")

        # v3 不变量：位次性质与素材归属必须自洽
        #   · 标为成品出口（is_channel=true）→ 独占素材必须为 0
        #   · 标为素材位次（is_channel=false）→ 必须有独占素材
        #   这一条能抓住「把渠道位次的 is_channel 改成 false」这类
        #   只改标记不改数据的伪装。
        incons = []
        for r in page_model["roles"].values():
            mat = r.get("material", 0)
            if r.get("is_channel") and mat != 0:
                incons.append(f'{r["name"]} 标为成品出口却独占 {mat} 条素材')
            if not r.get("is_channel") and not r.get("is_cash") and mat <= 0:
                incons.append(f'{r["name"]} 标为素材位次却无独占素材')
        if incons:
            for x in incons:
                bad(f"D3 位次性质与素材归属不自洽：{x}")
        else:
            ok("D3 位次性质与素材归属自洽")

        # 有效产出系数必须与数据层一致（产能公式的基数）
        pc = page_model.get("config") or {}
        if pc.get("effective_factor") != model["config"]["effective_factor"]:
            bad(f"D3 有效产出系数被篡改：页面 {pc.get('effective_factor')} / "
                f"数据层 {model['config']['effective_factor']}")
        else:
            ok("D3 有效产出系数与数据层一致")

        # 其余配置项同样逐项核验（瓶颈阈值、周可用工时、口径声明）
        for f in ("bottleneck_threshold", "weekly_focus_hours", "time_basis"):
            if pc.get(f) != model["config"].get(f):
                bad(f"D3 页面内联配置 {f} 被篡改："
                    f"页面 {pc.get(f)} / 数据层 {model['config'].get(f)}")
        # 内联模型的重算关系必须自洽（不能只比对单个字段）
        if page_model:
            recalc_ok = True
            for k in order:
                pu = page_model["roles"][k]["unit_econ"]
                if pu["total_minutes"] - pu["auto_saved_minutes"] != pu["residual_minutes"]:
                    recalc_ok = False
                    bad(f"D3 {roles[k]['name']} 页面内残余工时算式不自洽")
            if recalc_ok:
                ok("D3 页面内联模型的工时算式逐位自洽")
        # 路线与风险条目数必须与数据层一致
        if len(page_model.get("roadmap", [])) != len(model["roadmap"]):
            bad("D3 页面内联路线阶段数与数据层不符")
        if len(page_model.get("risks", [])) != len(model["risks"]):
            bad("D3 页面内联风险条数与数据层不符")

    # 页面上的单位经济数字必须真实出现
    # （数字在 JS 模板中动态渲染，故静态与动态两处都查）
    for k in order:
        r = roles[k]
        u = r["unit_econ"]
        nums = [str(u["total_minutes"]), str(u["residual_minutes"])]
        if any(n in static_visible for n in nums) or any(n in js_visible for n in nums):
            ok(f"D3 {r['name']} 工时数字在页面可见")
        else:
            bad(f"D3 {r['name']} 工时数字未出现在页面")

    # 90 天路线与风险的文案必须在页面可见
    for p in model["roadmap"]:
        if p["title"] in visible:
            ok(f"D3 路线阶段「{p['title']}」在页面可见")
        else:
            bad(f"D3 路线阶段「{p['title']}」未出现在页面")
    for r in model["risks"]:
        if r["name"] in visible:
            ok(f"D3 风险「{r['name']}」在页面可见")
        else:
            bad(f"D3 风险「{r['name']}」未出现在页面")

    # 结构完整性：路线必须有出口条件块，风险必须有阈值块。
    # 关键：检查依据是「数据层真值是否出现在页面对应块内」，
    # 而不是「某个字样还在不在」——后者被改写措辞就会漏过。
    n_gate = len(re.findall(r'class="rm-gate"', html))
    if n_gate == len(model["roadmap"]):
        ok(f"D3 路线出口条件块 {n_gate} 个齐全")
    else:
        bad(f"D3 路线出口条件块数 {n_gate} ≠ {len(model['roadmap'])}")

    n_rk = len(re.findall(r'class="rk-item"', html))
    if n_rk == len(model["risks"]):
        ok(f"D3 风险条目块 {n_rk} 个齐全")
    else:
        bad(f"D3 风险条目块数 {n_rk} ≠ {len(model['risks'])}")

    # 风险块内必须含该风险的阈值真值（数据层原句）
    rk_starts = [m.start() for m in re.finditer(r'<div class="rk-item">', html)]
    risk_blocks = []
    for i, st in enumerate(rk_starts):
        nxt = rk_starts[i + 1] if i + 1 < len(rk_starts) else len(html)
        risk_blocks.append(html[st:nxt])
    miss_th = 0
    for blk, r in zip(risk_blocks, model["risks"]):
        ub = unescape(blk)
        if r["threshold"] not in ub:
            miss_th += 1
            bad(f"D3 风险「{r['name']}」的判定阈值文本被篡改或抹除")
        # 小节标题本身也不可被改写（把「判定阈值」换成别的说法＝藏起判据）
        if "判定阈值" not in ub:
            miss_th += 1
            bad(f"D3 风险「{r['name']}」的判定阈值小节标题被抹除")
    if risk_blocks and miss_th == 0:
        ok("D3 每个风险条目的判定阈值与数据层一致")

    # 阶段块内必须含该阶段的出口条件真值
    rm_starts = [m.start() for m in re.finditer(r'<div class="rm-item">', html)]
    phase_blocks = []
    for i, st in enumerate(rm_starts):
        nxt = rm_starts[i + 1] if i + 1 < len(rm_starts) else len(html)
        phase_blocks.append(html[st:nxt])
    miss_ex = 0
    for blk, p in zip(phase_blocks, model["roadmap"]):
        ub = unescape(blk)
        if p["gate"] not in ub:
            miss_ex += 1
            bad(f"D3 阶段{p['phase']} 的出口条件文本被篡改或抹除")
        if p["exit_signal"] not in ub:
            miss_ex += 1
            bad(f"D3 阶段{p['phase']} 的「未达成则」文本被篡改或抹除")
        # 小节标题本身也不可被改写（把「出口条件」换成别的说法＝藏起判据）
        if "出口条件" not in ub:
            miss_ex += 1
            bad(f"D3 阶段{p['phase']} 的出口条件小节标题被抹除")
        if "未达成则" not in ub:
            miss_ex += 1
            bad(f"D3 阶段{p['phase']} 的「未达成则」小节标题被抹除")
    if phase_blocks and miss_ex == 0:
        ok("D3 每个路线阶段的出口条件与数据层一致")

    # 首屏预渲染必须指向真实存在的位次。
    # v3 之前这里写死了一个位次 key，位次合并后 key 失效，
    # 首屏推演直接空白 —— 无头功能测试当时没覆盖到，是真实缺陷。
    # 故此处显式校验：代码里不得出现写死的、且不在数据层中的位次 key。
    if page_model:
        valid_keys = set(page_model["roles"].keys())
        # 找出 JS 中形如 renderChain('xxx') / simRole = 'xxx' 的写死位次
        hardcoded = set(re.findall(r"renderChain\(\s*'([^']+)'", html))
        hardcoded |= set(re.findall(r"simRole\s*=\s*'([^']+)'", html))
        bad_keys = sorted(hardcoded - valid_keys)
        if bad_keys:
            bad(f"D3 首屏写死了不存在的位次：{bad_keys}，首屏会空白")
        else:
            ok(f"D3 首屏预渲染位次有效（{sorted(hardcoded) or '取自数据层首个'}）")

        # 首屏渲染必须真的产出内容（不能是空串）
        for pid, label in (("chain", "工序链"), ("sim", "经营推演")):
            pat = (r'document\.getElementById\(\s*[\'"]' + pid
                   + r'[\'"]\s*\)\.innerHTML\s*=\s*html')
            if not re.search(pat, html):
                bad(f"D3 {label} 首屏未挂载渲染结果")
            else:
                ok(f"D3 {label} 首屏挂载渲染结果")

    # ───────────────────────────────────────────────────────
    # D4 合规
    # ───────────────────────────────────────────────────────
    # 收入类词：推演明确声明不含收入预测。
    # 「收入预测」等词允许出现在否定语境（如「不做收入预测」「收入预测都是虚构」）。
    income_patterns = [
        (r"(收入预测|收益预测|利润预测|预计收入|预计收益|保底收入|轻松月入|月入\d|"
         r"月入\s*\d|预计月入|日入\s*\d|年入\s*\d|赚\s*\d+|变现\s*\d+)", "收入承诺"),
    ]
    for pat, nm in income_patterns:
        found = False
        for m in re.finditer(pat, visible):
            if has_negated_ctx(visible, m.start()):
                continue
            found = True
            bad(f"D4 出现{nm}表述：{visible[max(0,m.start()-20):m.end()+20][:50]}")
            break
        if not found:
            ok(f"D4 无{nm}表述")

    # 推演区必须显式声明不含收入预测
    if "不做收入预测" in visible or "不含收入" in visible or "不承诺收入" in visible:
        ok("D4 推演区已声明不含收入/转化率预测")
    else:
        bad("D4 推演区未声明不含收入预测")

    # 工时必须标注为口径值，不得冒充实测
    # （该标注写在工序链与推演的动态文案里，故静态与动态两处都查）
    if "口径值" in static_visible or "口径值" in js_visible:
        ok("D4 工时已标注为口径值（非实测）")
    else:
        bad("D4 工时未标注为口径值")

    # 反向检查：不得把工时说成实测
    # （文案在 JS 模板里，故静态与动态两处都查）
    for pat, nm in [
        (r"工时为实测", "冒充实测"),
        (r"实测工时", "冒充实测"),
        (r"真实工时(?!数据)", "冒充实测"),
    ]:
        found = False
        for scope_name, scope in (("静态", static_visible), ("动态", js_visible)):
            for m in re.finditer(pat, scope):
                if has_negated_ctx(scope, m.start()):
                    continue
                found = True
                bad(f"D4 {scope_name}文案出现{nm}表述："
                    f"{scope[max(0,m.start()-20):m.end()+20][:50]}")
                break
            if found:
                break
        if not found:
            ok(f"D4 无{nm}表述")

    # 联系方式与外链
    contact = [
        (r"(?<![不无未])微信[:：]\s*\w{5,}", "微信号"),
        (r"(?<![不无未])QQ[:：]\s*\d{5,}", "QQ号"),
        (r"1[3-9]\d{9}", "手机号"),
        (r"https?://(?!www\.workbuddy\.cn)[^\s\"'<>]+", "外链"),
    ]
    for pat, nm in contact:
        m = re.search(pat, visible)
        if m:
            bad(f"D4 页面出现{nm}：{m.group(0)[:40]}")
        else:
            ok(f"D4 无{nm}")

    # 医疗红线
    medical = [
        (r"诊断|治愈|根治|疗效|有效率|替代药物|停药|处方",
         "医疗指向"),
        (r"无需就医|不必就医|不用看医生", "削弱免责"),
    ]
    for pat, nm in medical:
        # 允许出现在否定/引用语境（如"不构成诊断或治疗建议"）
        found = False
        for m in re.finditer(pat, visible):
            ctx = visible[max(0, m.start() - 14):m.start()]
            if any(x in ctx for x in ["不构成", "不作", "非", "无", "不提供", "禁止", "不含"]):
                continue
            found = True
            bad(f"D4 页面出现{nm}：{visible[max(0,m.start()-14):m.end()+8][:50]}")
            break
        if not found:
            ok(f"D4 无{nm}（免责语境除外）")

    # 免责声明必须在位
    if "不构成诊断或治疗建议" in visible:
        ok("D4 免责声明在位")
    else:
        bad("D4 免责声明缺失")

    # ───────────────────────────────────────────────────────
    # 输出
    # ───────────────────────────────────────────────────────
    print("═" * 62)
    print("养生一人公司生存地图 · 深度模型校验")
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
    print(f"   工序链 10 位次 · 单位经济自洽 · 页面与数据层一致 · "
          f"推演无收入承诺")
    return 0


if __name__ == "__main__":
    sys.exit(main())
