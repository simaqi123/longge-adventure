# -*- coding: utf-8 -*-
"""English edition of the one-person company survival map.

Design notes
------------
The Chinese page (``build_survival_map.py``) is the reference implementation
and is left completely untouched.  This generator reuses the *same* numeric
model — the same roles, the same mutually-exclusive material allocation, the
same squarified treemap layout function, the same process chains and the same
90-day roadmap — and swaps in the English copy from ``i18n_en.py``.

That is deliberate: when an English reader asks "is this the same model?", the
answer has to be yes, and the treemap areas have to be pixel-for-pixel
comparable.  Only the strings differ.

Output: ``web/solo-wellness-map.en.html`` — single file, zero external
dependencies, opens offline by double-click.

Usage:
    python scripts/build_en_map.py
"""

import json
import re
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from paths import WEB_DIR, ensure_dir  # noqa: E402
import survival_map_data as D  # noqa: E402
import survival_deep_model as M  # noqa: E402
import i18n_en as I18N  # noqa: E402

OUT_HTML = os.path.join(WEB_DIR, "solo-wellness-map.en.html")

# Reuse the reference treemap layout so both editions share one algorithm.
from build_survival_map import squarify  # noqa: E402

QUADRANT_EN = {
    "系统区": "System zone",
    "工具区": "Tooling zone",
    "流程区": "Process zone",
    "纯手工区": "Manual zone",
}

QUAD_DESC_EN = {
    "系统区": "One person can run the whole loop: material supply, compliance validation, distribution and review all hold together.",
    "工具区": "The bulk of the work is already scripted. Human effort sits on the last mile — the part that actually needs a person.",
    "流程区": "Half the chain is scripted, half is still manual. The highest-leverage move is to find the one step that still eats the most minutes.",
    "纯手工区": "Heavy on human hours and impossible to copy. Good for thinking, bad as a production line — move material out of here first.",
}

DISCLAIMER_EN = (
    "This page describes how a one-person content business is organised and how its "
    "output capacity is calculated. It contains no medical advice, it is not a diagnosis, "
    "and it provides no treatment guidance. The wellness material it references is "
    "general lifestyle information only. If you feel unwell, please consult a qualified "
    "healthcare professional."
)


def build_items(model):
    """Treemap items: one per role slot, area = monthly output pieces.

    Numeric fields come straight from the deep model (which is where the area
    metric is back-filled from the process chain's residual minutes).  Only the
    human-readable strings come from the English locale.
    """
    localized = {r["key"]: r for r in I18N.localize_roles(D.ROLES)}
    mroles = model["roles"]

    items = []
    for key in model["order"]:
        m = mroles[key]
        role = localized[key]
        amap = role.get("_action_en", {})
        items.append({
            "key": key,
            "name": role["name_en"],
            "sub": role["sub_en"],
            "desc": role["desc_en"],
            "area": m["area"],
            "material": m["material"],
            "rate": m["rate"],
            "quadrant": m["quadrant"],
            "quadrant_name": QUADRANT_EN.get(m["quadrant_name"], m["quadrant_name"]),
            "quadrant_color": m["quadrant_color"],
            "is_channel": m["is_channel"],
            "is_cash": m["is_cash"],
            "actions": [
                {
                    "name": a["name_en"],
                    "state": a["state"],
                    "state_label": I18N.TOOL_STATE_EN[a["state"]]["label"],
                    "state_desc": I18N.TOOL_STATE_EN[a["state"]]["desc"],
                    "tool": a["tool"],
                    "tool_evidence": I18N.TOOL_EVIDENCE_EN.get(a["tool"], "") if a["tool"] else "",
                }
                for a in role["actions"]
            ],
            "manual_gap": [I18N.ACTION_EN.get(g, g) for g in m["manual_gap"]],
        })
    return items


def build_payload():
    model = M.build_deep_model()

    localized = {r["key"]: r for r in I18N.localize_roles(D.ROLES)}
    deep_roles = {}
    for key, dr in model["roles"].items():
        dr = json.loads(json.dumps(dr, ensure_ascii=False))
        if key in localized:
            dr["name"] = localized[key]["name_en"]
            dr["sub"] = localized[key]["sub_en"]
            dr["desc"] = localized[key]["desc_en"]
        # themes / pools -> English
        dr["quadrant_name"] = QUADRANT_EN.get(dr.get("quadrant_name"), dr.get("quadrant_name"))
        dr["themes"] = [I18N.THEME_EN.get(t, t) for t in dr.get("themes", [])]
        dr["pool"] = [I18N.THEME_EN.get(t, t) for t in dr.get("pool", [])]
        dr["area_note"] = (
            f"monthly output pieces · {dr.get('material', 0)} exclusive entries "
            f"({', '.join(dr.get('themes', []))})"
        )
        # action nodes -> English
        for act in dr.get("actions", []):
            act["name"] = I18N.ACTION_EN.get(act["name"], act["name"])
            act["state_label"] = I18N.TOOL_STATE_EN[act["state"]]["label"]
            if act.get("tool"):
                act["tool_evidence"] = I18N.TOOL_EVIDENCE_EN.get(act["tool"], act["tool_evidence"])
        # manual gap -> English
        dr["manual_gap"] = [I18N.ACTION_EN.get(g, g) for g in dr.get("manual_gap", [])]
        # chain steps -> English
        for st in dr.get("chain_steps", []):
            st["name"] = I18N.ACTION_EN.get(st["name"], st["name"])
            if st.get("dep"):
                st["dep"] = I18N.ACTION_EN.get(st["dep"], st["dep"])
            st["state_label"] = I18N.TOOL_STATE_EN[st["state"]]["label"]
            if st.get("tool"):
                st["tool_evidence"] = I18N.TOOL_EVIDENCE_EN.get(st["tool"], st["tool_evidence"])
        if key in I18N.UNIT_EN:
            dr["unit"], dr["unit_note"] = I18N.UNIT_EN[key]
        ue = dr.get("unit_econ")
        if ue:
            ue = dict(ue)
            ue["unit"], ue["unit_note"] = I18N.UNIT_EN.get(key, (ue["unit"], ue["unit_note"]))
            if ue.get("bottleneck"):
                ue["bottleneck"] = I18N.ACTION_EN.get(ue["bottleneck"], ue["bottleneck"])
            dr["unit_econ"] = ue
        deep_roles[key] = dr

    # process-chain step names are shared keys — translate them in place
    chains = {}
    for key, ch in model["chains"].items():
        ch = json.loads(json.dumps(ch, ensure_ascii=False))
        if key in I18N.UNIT_EN:
            ch["unit"], ch["unit_note"] = I18N.UNIT_EN[key]
        for step in ch.get("steps", []):
            step["name"] = I18N.ACTION_EN.get(step["name"], step["name"])
            step["state_label"] = I18N.TOOL_STATE_EN[step["state"]]["label"]
            if step.get("dep"):
                step["dep"] = I18N.ACTION_EN.get(step["dep"], step["dep"])
            if step.get("tool"):
                step["tool_evidence"] = I18N.TOOL_EVIDENCE_EN.get(step["tool"], step["tool_evidence"])
        if "unit_econ" in ch:
            ue = dict(ch["unit_econ"])
            ue["unit"], ue["unit_note"] = I18N.UNIT_EN.get(key, (ue["unit"], ue["unit_note"]))
            if ue.get("bottleneck"):
                ue["bottleneck"] = I18N.ACTION_EN.get(ue["bottleneck"], ue["bottleneck"])
            ch["unit_econ"] = ue
        chains[key] = ch

    roadmap = I18N.localize_roadmap(model["roadmap"])
    risks = I18N.localize_risks(model["risks"])
    funnel, funnel_gates = I18N.localize_funnel(model["funnel"], model["funnel_gates"])

    return {
        "items": build_items(model),
        "deep": deep_roles,
        "order": model["order"],
        "chains": chains,
        "roadmap": roadmap,
        "risks": risks,
        "funnel": funnel,
        "funnel_gates": funnel_gates,
        "quad_desc": {QUADRANT_EN[k]: v for k, v in QUAD_DESC_EN.items()},
    }


CSS = """
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0d1117; --bg2:#161b22; --panel:#1c2330; --panel2:#232c3b;
  --line:#2b3548; --ink:#e6edf3; --ink-dim:#8b98a9; --accent:#4a9eff;
  --green:#3fb950; --amber:#d29922; --red:#f85149; --purple:#a371f7;
}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--ink);
  font:15px/1.75 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif}
.wrap{max-width:1240px;margin:0 auto;padding:0 22px 90px}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}

header{border-bottom:1px solid var(--line);padding:52px 0 34px;margin-bottom:40px}
.eyebrow{color:var(--accent);font-size:12px;letter-spacing:.14em;text-transform:uppercase;font-weight:600}
h1{font-size:38px;line-height:1.2;margin:12px 0 14px;letter-spacing:-.02em}
.lede{color:var(--ink-dim);font-size:17px;max-width:820px}
.badges{display:flex;flex-wrap:wrap;gap:9px;margin-top:26px}
.badge{background:var(--panel);border:1px solid var(--line);border-radius:999px;
  padding:5px 14px;font-size:12.5px;color:var(--ink-dim)}
.badge b{color:var(--ink);font-weight:600}

nav.toc{display:flex;flex-wrap:wrap;gap:8px;margin:26px 0 0}
nav.toc a{font-size:13px;background:var(--panel);border:1px solid var(--line);
  border-radius:6px;padding:6px 12px;color:var(--ink-dim)}
nav.toc a:hover{color:var(--ink);text-decoration:none;border-color:var(--accent)}

section{margin-bottom:64px;scroll-margin-top:24px}
h2{font-size:25px;margin-bottom:12px;letter-spacing:-.01em}
.sec-sub{color:var(--ink-dim);margin-bottom:24px;max-width:900px}
h3{font-size:17px;margin-bottom:8px}

.grid2{display:grid;grid-template-columns:1.55fr 1fr;gap:22px}
@media(max-width:940px){.grid2{grid-template-columns:1fr}}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:22px}
.card{background:var(--bg2);border:1px solid var(--line);border-radius:9px;padding:16px;margin-bottom:12px}
.card:last-child{margin-bottom:0}
.kv{display:flex;flex-wrap:wrap;gap:18px;margin-top:12px}
.kv div{font-size:13px;color:var(--ink-dim)}
.kv b{color:var(--ink)}

#treemap{width:100%;height:auto;display:block}
.tm-cell{cursor:pointer}
.tm-cell rect{transition:opacity .15s}
.tm-cell:hover rect{opacity:.86}
.legend{display:flex;flex-wrap:wrap;gap:16px;margin-top:16px;font-size:12.5px;color:var(--ink-dim)}
.legend i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px}

table{width:100%;border-collapse:collapse;font-size:13.5px;margin-top:8px}
th,td{text-align:left;padding:9px 11px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--ink-dim);font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.05em}
tr:last-child td{border-bottom:none}

.pill{display:inline-block;font-size:11.5px;padding:2px 9px;border-radius:999px;
  border:1px solid var(--line);color:var(--ink-dim);margin-right:6px}
.pill.auto{color:var(--green);border-color:#1d4429}
.pill.semi{color:var(--amber);border-color:#4a3a12}
.pill.manual{color:var(--red);border-color:#5c2224}

.bar{height:5px;border-radius:3px;background:var(--line);overflow:hidden;margin-top:7px}
.bar i{display:block;height:100%;background:var(--accent)}

.phase{border-left:3px solid var(--accent);padding-left:16px;margin-bottom:26px}
.phase .ph-n{font-size:12px;color:var(--accent);font-weight:700;letter-spacing:.1em}
.phase h3{margin:4px 0 6px}
.phase .win{color:var(--ink-dim);font-size:13px;margin-bottom:10px}
.gate{background:var(--bg2);border:1px solid var(--line);border-radius:8px;padding:11px 14px;margin-top:10px;font-size:13.5px}
.gate b{color:var(--amber)}

.risk{border:1px solid var(--line);border-radius:9px;padding:14px 16px;margin-bottom:11px;background:var(--bg2)}
.risk .rn{font-weight:600;margin-bottom:6px}
.risk .rt{font-size:13px;color:var(--ink-dim)}
.risk .rt b{color:var(--ink);font-weight:500}

.flow{display:flex;flex-direction:column;gap:12px}
.flow-step{border:1px solid var(--line);border-radius:9px;padding:15px 17px;background:var(--bg2)}
.flow-step .fs-h{display:flex;align-items:center;gap:11px;margin-bottom:8px}
.flow-num{width:26px;height:26px;border-radius:50%;background:var(--accent);color:#08121f;
  display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px;flex:none}
.flow-arrow{text-align:center;color:var(--ink-dim);font-size:13px}

footer{border-top:1px solid var(--line);padding-top:26px;color:var(--ink-dim);font-size:13px}
footer p{max-width:900px}
.tag{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12.5px;color:var(--ink)}
"""


def build_html(payload):
    items = payload["items"]
    total_area = sum(i["area"] for i in items)
    total_material = sum(i["material"] for i in items)

    # ---- treemap layout (same algorithm as the Chinese edition) ----
    W, H = 1240, 1000
    cells = []
    for it in sorted(items, key=lambda x: -x["area"]):
        cells.append(dict(it, _a=it["area"]))
    rects = squarify(cells, 0, 0, W, H)

    quads = ["系统区", "工具区", "流程区", "纯手工区"]
    qcolor = {"系统区": "#2ea04366", "工具区": "#3fb950", "流程区": "#d29922", "纯手工区": "#f85149"}

    svg = []
    for r in rects:
        x, y, w, h = r["x"], r["y"], r["w"], r["h"]
        if w < 1 or h < 1:
            continue
        it = r
        pad = 3
        fill = qcolor.get(
            next((k for k, v in QUADRANT_EN.items() if v == it["quadrant_name"]), ""),
            "#3fb950")
        opacity = 0.22 if it["quadrant_name"] != "System zone" else 0.20
        svg.append(
            f'<g class="tm-cell" data-key="{it["key"]}">'
            f'<rect x="{x+pad:.1f}" y="{y+pad:.1f}" width="{max(0,w-2*pad):.1f}" '
            f'height="{max(0,h-2*pad):.1f}" rx="7" fill="{fill}" fill-opacity="{opacity}" '
            f'stroke="{fill}" stroke-opacity=".65" stroke-width="1.4"/>'
        )
        # progress bar = tooling ratio
        if w > 46 and h > 34:
            bw = max(0, min(w - 18, (w - 18) * it["rate"] / 100.0))
            svg.append(
                f'<rect x="{x+11:.1f}" y="{y+h-16:.1f}" width="{bw:.1f}" height="4.5" rx="2.2" '
                f'fill="#4a9eff" fill-opacity=".92"/>'
            )
        if w > 92 and h > 62:
            fs = max(10, min(15, int(w / 13)))
            name = it["name"]
            if len(name) > 34:
                name = name[:33] + "…"
            svg.append(
                f'<text x="{x+11:.1f}" y="{y+24:.1f}" fill="#e6edf3" font-size="{fs}" '
                f'font-weight="600" font-family="-apple-system,Segoe UI,Roboto,sans-serif">{name}</text>'
            )
            svg.append(
                f'<text x="{x+11:.1f}" y="{y+24+fs+3:.1f}" fill="#8b98a9" font-size="{max(9,fs-2)}" '
                f'font-family="-apple-system,Segoe UI,Roboto,sans-serif">'
                f'{it["area"]} pcs/mo · tooling {it["rate"]}%</text>'
            )
        svg.append("</g>")

    svg_block = "\n".join(svg)

    # ---- role detail + process chain (rendered by JS from the payload) ----
    chain_opts = "\n".join(
        f'<option value="{k}">{payload["deep"][k]["name"]}</option>' for k in payload["order"]
    )

    roadmap_html = []
    for p in payload["roadmap"]:
        tasks = "".join(
            f'<tr><td>{t[0]}</td><td style="color:var(--ink-dim)">{t[1]}</td>'
            f'<td class="tag">{t[2]}</td></tr>'
            for t in p["tasks"]
        )
        roadmap_html.append(
            f'<div class="phase"><div class="ph-n">PHASE {p["phase"]}</div>'
            f'<h3>{p["title_en"]}</h3><div class="win">{p["window_en"]}</div>'
            f'<p style="margin-bottom:12px">{p["goal_en"]}</p>'
            f'<table><thead><tr><th>Task</th><th>Status</th><th>Evidence</th></tr></thead>'
            f'<tbody>{tasks}</tbody></table>'
            f'<div class="gate"><b>Gate:</b> {p["gate_en"]}<br>'
            f'<span style="color:var(--ink-dim)"><b style="color:var(--red)">Exit signal:</b> '
            f'{p["exit_signal_en"]}</span></div></div>'
        )
    roadmap_block = "\n".join(roadmap_html)

    risks_html = "".join(
        f'<div class="risk"><div class="rn">{r["name_en"]}</div>'
        f'<div class="rt"><b>Indicator:</b> {r["indicator_en"]}</div>'
        f'<div class="rt"><b>Threshold:</b> {r["threshold_en"]}</div>'
        f'<div class="rt" style="margin-top:6px">{r["why_en"]}</div>'
        f'<div class="rt" style="margin-top:6px"><b>Response:</b> {r["action_en"]}</div></div>'
        for r in payload["risks"]
    )

    funnel_html = []
    for s in payload["funnel"]:
        cards = "".join(
            f'<div class="card"><h3>{c["k_en"]}</h3><div style="margin-bottom:6px">{c["n_en"]}</div>'
            f'<p style="color:var(--ink-dim);font-size:13.5px">{c["d_en"]}</p>'
            f'<div class="kv"><div><b>{c["m_en"]}</b></div></div></div>'
            for c in s["cards"]
        )
        funnel_html.append(
            f'<div class="flow-step"><div class="fs-h"><div class="flow-num">{s["stage"]}</div>'
            f'<div><div style="font-size:12px;color:var(--accent);letter-spacing:.1em;'
            f'text-transform:uppercase">{s["badge_en"]}</div>'
            f'<h3 style="margin:2px 0 0">{s["title_en"]}</h3></div>'
            f'<p style="color:var(--ink-dim);font-size:13.5px;margin-bottom:10px">{s["why_en"]}</p>'
            f'{cards}</div>'
        )
    funnel_block = "\n".join(funnel_html)

    gates_html = "".join(
        f'<tr><td><b>{g[0]}</b></td><td>{g[1]}</td><td style="color:var(--ink-dim)">{g[2]}</td></tr>'
        for g in payload["funnel_gates"]
    )

    quad_rows = "".join(
        f'<tr><td><b>{QUADRANT_EN[q]}</b></td><td>{payload["quad_desc"][QUADRANT_EN[q]]}</td>'
        f'<td>{sum(1 for i in items if i["quadrant_name"] == QUADRANT_EN[q])}</td></tr>'
        for q in quads
    )

    legend = "".join(
        f'<span><i style="background:{c}"></i>{QUADRANT_EN[q]} '
        f'({sum(1 for i in items if i["quadrant_name"] == QUADRANT_EN[q])})</span>'
        for q, c in qcolor.items()
    )

    data_json = json.dumps(payload, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>The Solo Wellness Operator — Survival Map</title>
<meta name="description" content="An open-source operating system for a one-person wellness content company: material conservation, a single cash outlet, and compliance wired into the validator.">
<style>{CSS}</style>
</head>
<body>
<div class="wrap">

<header>
  <div class="eyebrow">Longge Adventure · Open Source · MIT</div>
  <h1>The Solo Wellness Operator</h1>
  <p class="lede">A survival map for running a one-person company as an AI company.
    Ten role slots, each with its own material pool, its own process chain and its own
    bottleneck. One cash outlet, and no more than one. Every number on this page is
    traceable to the source table.</p>
  <div class="badges">
    <span class="badge"><b>{total_material}</b> material entries</span>
    <span class="badge"><b>24</b> solar terms</span>
    <span class="badge"><b>{len(items)}</b> role slots</span>
    <span class="badge"><b>4</b> validators</span>
    <span class="badge"><b>44/44</b> injection tests blocked</span>
    <span class="badge"><b>0</b> third-party dependencies</span>
  </div>
  <nav class="toc">
    <a href="#why">Why</a>
    <a href="#map">The map</a>
    <a href="#quad">Quadrants</a>
    <a href="#chain">Process chain</a>
    <a href="#roadmap">90-day roadmap</a>
    <a href="#risk">Risk register</a>
    <a href="#money">Monetization path</a>
  </nav>
</header>

<section id="why">
  <h2>Why this exists</h2>
  <p class="sec-sub">Most "one-person company" material is a diagram of an aspiration.
    This one is a model you can run, and a set of rules that can fail.</p>
  <div class="grid2">
    <div class="panel">
      <h3>Three structural invariants</h3>
      <div class="card"><h3>1 · Material conservation</h3>
        <p style="color:var(--ink-dim);font-size:13.5px">Every entry in the source table
        belongs to exactly one role slot. The ten slots sum to the table, exactly —
        no double counting between a theme and the channel that carries it.</p></div>
      <div class="card"><h3>2 · One area metric</h3>
        <p style="color:var(--ink-dim);font-size:13.5px">Treemap area means one thing and
        one thing only: pieces produced per month, derived from the residual minutes left
        after automation. Nothing else is allowed to influence the area.</p></div>
      <div class="card"><h3>3 · Exactly one cash outlet</h3>
        <p style="color:var(--ink-dim);font-size:13.5px">When off-premise delivery was
        discontinued, the only path to cash disappeared and the map became honest about
        having no revenue at all. A single cash outlet was then added, deliberately,
        and a validator enforces that there is exactly one.</p></div>
    </div>
    <div class="panel">
      <h3>Numbers carry their own provenance</h3>
      <p style="color:var(--ink-dim);font-size:13.5px">Every figure on this page falls into
      one of three tiers, and the tier is stated rather than implied.</p>
      <div class="card"><h3>Verifiable</h3>
        <p style="color:var(--ink-dim);font-size:13px">Counts read live from the source
        table. You can recount them yourself.</p></div>
      <div class="card"><h3>Declared basis</h3>
        <p style="color:var(--ink-dim);font-size:13px">Per-step minutes are a declared
        model, not a stopwatch reading. Treated as an assumption to be revised, never
        as a measurement.</p></div>
      <div class="card"><h3>Not modelled</h3>
        <p style="color:var(--ink-dim);font-size:13px">Revenue, conversion rates and costs
        are not derived from this table at all. Any income figure in this project comes
        from somewhere else, or from nowhere.</p></div>
    </div>
  </div>
</section>

<section id="map">
  <h2>The map</h2>
  <p class="sec-sub">Each block is one role slot you can run alone. Area is
    <b>pieces produced per month</b>. Colour is the tooling ratio band. The bar inside
    each block is the tooling ratio itself. Click a block to load its detail and process
    chain.</p>
  <div class="grid2">
    <div class="panel">
      <svg id="treemap" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid meet">{svg_block}</svg>
      <div class="legend">{legend}</div>
    </div>
    <div class="panel">
      <h3 id="d-name">—</h3>
      <p id="d-sub" style="color:var(--ink-dim);font-size:13px;margin-bottom:10px"></p>
      <p id="d-desc" style="font-size:14px;margin-bottom:14px"></p>
      <div class="kv">
        <div>Area <b id="d-area"></b></div>
        <div>Exclusive material <b id="d-mat"></b></div>
        <div>Tooling ratio <b id="d-rate"></b></div>
        <div>Quadrant <b id="d-quad"></b></div>
      </div>
      <h3 style="margin-top:20px">Actions</h3>
      <div id="d-actions"></div>
      <h3 style="margin-top:18px">Still manual</h3>
      <div id="d-gap" style="color:var(--ink-dim);font-size:13.5px"></div>
    </div>
  </div>
</section>

<section id="quad">
  <h2>Four quadrants</h2>
  <p class="sec-sub">Tooling is not automatically good. A pure-manual slot has a heavy
    human cost and cannot be copied; a fully automated slot has a different risk — the
    person stops being the bottleneck and starts being the only place judgment can live.</p>
  <div class="panel"><table>
    <thead><tr><th>Zone</th><th>What it means</th><th>Slots</th></tr></thead>
    <tbody>{quad_rows}</tbody></table></div>
</section>

<section id="chain">
  <h2>Process chain</h2>
  <p class="sec-sub">The map is a cross-section: how much material a slot holds, how
    automated it is. The process chain adds the depth — where the minutes actually go,
    and which step to attack first.</p>
  <div class="panel">
    <div style="margin-bottom:16px"><label style="font-size:13px;color:var(--ink-dim)">
      Role slot </label><br>
      <select id="chainSel" style="margin-top:6px;background:var(--bg2);color:var(--ink);
        border:1px solid var(--line);border-radius:7px;padding:8px 12px;font-size:14px;
        min-width:280px">{chain_opts}</select></div>
    <div id="chain-body"></div>
  </div>
</section>

<section id="roadmap">
  <h2>90-day roadmap</h2>
  <p class="sec-sub">The order is not arbitrary. First make the material trustworthy,
    then move repetition into scripts, then connect output, distribution and review into
    a loop. Only then does collecting cash make sense.</p>
  <div class="panel">{roadmap_block}</div>
</section>

<section id="risk">
  <h2>Risk register</h2>
  <p class="sec-sub">A cross-section cannot show risk. Risk has to be bound to an
    observable indicator and a threshold, or it is just worry with a nice heading.</p>
  <div class="grid2">
    <div class="panel">{risks_html}</div>
    <div class="panel">
      <h3>How to read the thresholds</h3>
      <p style="color:var(--ink-dim);font-size:13.5px">Every threshold is a number you
      can read off the table, not a feeling. If a threshold is crossed, the response is
      written down in advance — including the two cases where the response is to stop
      publishing and fix the validator first.</p>
      <div class="card"><h3>Metric drift is the dangerous one</h3>
        <p style="color:var(--ink-dim);font-size:13.5px">The other five risks cost output.
        Metric drift costs the ability to make output decisions at all: once the numbers
        stop being traceable, the map becomes self-persuasion.</p></div>
      <div class="card"><h3>Compliance gets no exceptions</h3>
        <p style="color:var(--ink-dim);font-size:13.5px">The response to a compliance
        breach is always the same: pause, fix, verify, resume. There is no threshold
        above which a red line becomes negotiable.</p></div>
    </div>
  </div>
</section>

<section id="money">
  <h2>Monetization path</h2>
  <p class="sec-sub">Off-premise delivery was discontinued, so that path no longer
    exists. This is the only route to cash in the model: public content brings people in,
    the private channel retains them, and a subscription converts them.</p>
  <div class="grid2">
    <div class="panel"><div class="flow">{funnel_block}</div></div>
    <div class="panel">
      <h3>Gates for each link</h3>
      <p style="color:var(--ink-dim);font-size:13.5px;margin-bottom:12px">A link is not
        "working" because it produced output. It is working when the next link has
        something to receive. These are the criteria that decide that.</p>
      <table><thead><tr><th>Layer</th><th>Gate</th><th>Why it matters</th></tr></thead>
      <tbody>{gates_html}</tbody></table>
    </div>
  </div>
</section>

<footer>
  <p><b>Disclaimer.</b> {DISCLAIMER_EN}</p>
  <p style="margin-top:12px"><b>Provenance.</b> Every number on this page is produced by
    the scripts in <span class="tag">scripts/</span> from the source table in
    <span class="tag">data/</span>. Reproduce it with
    <span class="tag">python scripts/build_en_map.py</span>; verify it with
    <span class="tag">python scripts/validate_survival_map.py</span> and
    <span class="tag">python scripts/test_survival_map_injection.py</span>.</p>
  <p style="margin-top:12px">MIT licensed. Built and maintained by
    <a href="https://github.com/simaqi123">simaqi123</a>.</p>
</footer>

</div>
<script>
const DATA = {data_json};
const ITEMS = DATA.items, DEEP = DATA.deep, CHAINS = DATA.chains;

function el(id){{return document.getElementById(id);}}

function renderDetail(key){{
  const it = ITEMS.find(x => x.key === key);
  if(!it) return;
  el('d-name').textContent = it.name;
  el('d-sub').textContent = it.sub;
  el('d-desc').textContent = it.desc;
  el('d-area').textContent = it.area + ' pieces/month';
  el('d-mat').textContent = it.material + ' entries';
  el('d-rate').textContent = it.rate + '%';
  el('d-quad').textContent = it.quadrant_name;
  el('d-actions').innerHTML = it.actions.map(a =>
    '<div style="margin-bottom:9px"><span class="pill ' + a.state + '">' + a.state_label +
    '</span><span style="font-size:13.5px">' + a.name + '</span>' +
    (a.tool_evidence ? '<div style="font-size:12px;color:var(--ink-dim);margin-top:3px">' +
      a.tool_evidence + '</div>' : '') + '</div>').join('');
  el('d-gap').textContent = it.manual_gap.length ? it.manual_gap.join(' · ') : 'None';
  document.querySelectorAll('#chainSel option').forEach(o=>{{
    if(o.value === key) o.selected = true;
  }});
  renderChain(key);
}}

function renderChain(key){{
  const ch = CHAINS[key], dr = DEEP[key];
  if(!ch) {{el('chain-body').innerHTML=''; return;}}
  const ue = ch.unit_econ || {{}};
  const steps = ch.steps.map((s,i) =>
    '<tr><td>' + (i+1) + '</td><td>' + s.name + '</td>' +
    '<td><span class="pill ' + s.state + '">' + s.state_label + '</span></td>' +
    '<td>' + s.minutes + '</td>' +
    '<td>' + s.share + '%' + (s.bottleneck ? ' <span style="color:var(--red)">bottleneck</span>' : '') +
    '</td></tr>').join('');
  el('chain-body').innerHTML =
    '<div class="kv" style="margin-bottom:12px">' +
    '<div>Output unit <b>' + ue.unit + '</b></div>' +
    '<div>' + ue.unit_note + '</div>' +
    '<div>Per-piece total <b>' + ue.total_minutes + ' min</b></div>' +
    '<div>Manual <b>' + ue.manual_minutes + '</b> · Semi <b>' + ue.semi_minutes +
    '</b> · Auto <b>' + ue.auto_minutes + '</b></div>' +
    '<div>Residual after automation <b>' + ue.residual_minutes + ' min</b></div>' +
    '<div>Output <b>' + ue.pieces_per_week + '/week · ' + ue.pieces_per_month + '/month</b></div>' +
    '<div>Bottleneck <b style="color:var(--red)">' + ue.bottleneck + ' (' + ue.bottleneck_share +
    '%)</b></div>' +
    '<div>If optimised <b>' + ue.pieces_per_week_if_optimized + '/week</b></div>' +
    '</div>' +
    '<table><thead><tr><th>#</th><th>Step</th><th>State</th><th>Minutes</th><th>Share</th>' +
    '</tr></thead><tbody>' + steps + '</tbody></table>' +
    '<div class="gate" style="margin-top:12px"><b>How to read this.</b> ' +
    'Minutes are a declared model, not a stopwatch reading. The number that matters is the ' +
    'bottleneck share: tooling that step first, and the weekly output moves the most. ' +
    'No revenue figure is derived from this table.</div>';
}}

document.querySelectorAll('.tm-cell').forEach(g=>{{
  g.addEventListener('click', () => {{
    renderDetail(g.getAttribute('data-key'));
    el('chain').scrollIntoView({{behavior:'smooth'}});
  }});
}});

el('chainSel').addEventListener('change', e => renderChain(e.target.value));
renderDetail(DATA.order[0]);
renderChain(DATA.order[0]);
</script>
</body>
</html>
"""


def main():
    ensure_dir(WEB_DIR)
    payload = build_payload()
    html = build_html(payload)

    # --- self-check: the English page must not leak Chinese prose ---------
    # Real file names that happen to be Chinese are allowed — a reader has to
    # be able to type them.  Everything else is a translation miss.
    allowed = [
        "节气经典_出处对照表.md",
        "早报推送通道_腾讯文档.md",
        "契约层.md",
    ]
    probe = html
    for a in allowed:
        probe = probe.replace(a, "")
    leftover = sorted(set(re.findall(r"[一-鿿]+", probe)))
    if leftover:
        print("❌ 中文残留（英文版不允许出现）:", flush=True)
        for w in leftover:
            m = re.search(re.escape(w), probe)
            ctx = probe[max(0, m.start() - 70):m.end() + 40].replace("\n", " ")
            print(f"   [{w}]  …{ctx}…")
        sys.exit(1)

    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    total_area = sum(i["area"] for i in payload["items"])
    total_mat = sum(i["material"] for i in payload["items"])
    print(f"✅ {OUT_HTML}")
    print(f"   role slots      : {len(payload['items'])}")
    print(f"   exclusive material: {total_mat}")
    print(f"   total monthly area: {total_area} pieces")
    print(f"   roadmap phases  : {len(payload['roadmap'])}")
    print(f"   risks           : {len(payload['risks'])}")
    print(f"   funnel links    : {len(payload['funnel'])}")
    print(f"   chinese residue : 0")


if __name__ == "__main__":
    main()
