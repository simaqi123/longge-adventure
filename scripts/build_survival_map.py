# -*- coding: utf-8 -*-
"""养生一人公司生存地图 · HTML 生成器

产出：`web/养生一人公司生存地图.html`（单文件、零外部依赖、双击即开）

对标陈磊「AI 一人公司生存地图」的页面骨架：
    顶部导航：生存地图 / 生成报告 / 生存模型 / 案例库
    左侧栏  ：状态分布图例 + 权威数据来源 + 生成报告按钮 + 发起人
    主区    ：treemap（面积=月产出件数，颜色=工具化率档位，块内带进度条）

差异点（有意为之，不是照抄）：
    陈磊的面积口径是自报的「案例样本数」，无法核验；
    本图的面积口径是**月产出件数**——由各工序链的残余工时推算，
    同单位、可比、可复算；素材供给量作为独立指标单列。

v3 修正（重要）：
    v2 把「内容主题」与「输出渠道」混在同一层，导致同一批 SSOT 素材
    被多个位次重复计入面积（十个位次面积和 569，而实际只有 205 条），
    且线下交付停办后仍保留「到店服务」位次，全图无现金出口。
    v3 改为：
      · 十个位次 = 六个素材位次 + 三个成品出口 + 一个现金出口（私域变现）
      · 素材互斥分摊，Σ 独占素材 ≡ SSOT 条目总数
      · 面积统一为月产出件数
      · 线下交付相关位次与动作全部移除
"""

import html
import json
import os
import sys

import survival_map_data as S
import survival_deep_model as D

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import WEB_DIR, SURVIVAL_MAP_HTML as OUT_HTML, SIM_JS  # noqa: E402
OUT_DIR = WEB_DIR

# 推演引擎（前端实时计算，独立文件避免超长内联字符串）
with open(SIM_JS, encoding="utf-8") as f:
    SIM_JS = f.read()

# ─────────────────────────────────────────────────────────────
# 视觉规范（沿用深墨底 + 语义色体系，与陈磊视觉规范同源）
#   金 = 品牌 / 结论      橙 = 行动 / 流程启动
#   蓝 = 证据 / 数据      绿 = 结果 / 闭环      红 = 风险 / 边界
# ─────────────────────────────────────────────────────────────
CSS = """
:root{
  --bg:#0d1117; --bg2:#161b22; --panel:#1c2330; --panel2:#232c3b;
  --line:#2b3547; --line2:#3a475c;
  --ink:#e6edf3; --ink-soft:#a8b6c8; --ink-dim:#75839a;
  --gold:#d4a24e; --orange:#e08a3c; --blue:#4b8fd4; --green:#4aa870;
  --red:#d0574f; --yellow:#d4b04a;
  --r:10px;
}
*{box-sizing:border-box;margin:0;padding:0}
body{
  background:var(--bg); color:var(--ink);
  font-family:"PingFang SC","Microsoft YaHei","Hiragino Sans GB",-apple-system,sans-serif;
  font-size:14px; line-height:1.6; -webkit-font-smoothing:antialiased;
}
a{color:var(--blue);text-decoration:none}
.wrap{max-width:1440px;margin:0 auto;padding:0 24px 64px}

/* ── 顶部 ── */
header{
  position:sticky; top:0; z-index:50;
  background:rgba(13,17,23,.94); backdrop-filter:blur(12px);
  border-bottom:1px solid var(--line);
}
.hd{max-width:1440px;margin:0 auto;padding:0 24px;
  display:flex;align-items:center;justify-content:space-between;height:64px}
.brand{display:flex;align-items:baseline;gap:12px}
.brand h1{font-size:19px;font-weight:600;letter-spacing:.5px}
.brand .sub{font-size:12px;color:var(--ink-dim)}
nav{display:flex;gap:2px}
nav button{
  background:none;border:none;color:var(--ink-dim);cursor:pointer;
  font-size:13px;padding:8px 16px;border-radius:6px;font-family:inherit;
  transition:.15s;
}
nav button:hover{color:var(--ink);background:var(--panel)}
nav button.on{color:var(--gold);background:var(--panel2)}

/* ── 布局 ── */
.main{display:grid;grid-template-columns:270px 1fr;gap:20px;margin-top:20px}
@media(max-width:960px){.main{grid-template-columns:1fr}}

/* ── 侧栏 ── */
.side{display:flex;flex-direction:column;gap:14px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:var(--r);padding:16px}
.card h3{font-size:12px;font-weight:600;color:var(--ink-dim);
  letter-spacing:1.2px;margin-bottom:12px;text-transform:uppercase}

.legend-item{display:flex;gap:9px;align-items:flex-start;padding:7px 0;cursor:default}
.dot{width:9px;height:9px;border-radius:50%;margin-top:6px;flex-shrink:0}
.legend-item b{display:block;font-size:13px;font-weight:600}
.legend-item span{font-size:11.5px;color:var(--ink-dim);line-height:1.45}
.legend-item em{font-style:normal;color:var(--ink-soft);font-size:11px}

.stat-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.stat{background:var(--bg2);border:1px solid var(--line);border-radius:7px;padding:10px}
.stat .n{font-size:19px;font-weight:600;color:var(--gold);line-height:1.2}
.stat .n small{font-size:12px;color:var(--ink-dim);font-weight:400}
.stat .l{font-size:11px;color:var(--ink-dim);margin-top:3px}

.btn{
  display:block;width:100%;text-align:center;padding:11px;border-radius:8px;
  font-size:13px;font-weight:600;cursor:pointer;border:1px solid transparent;
  font-family:inherit;transition:.15s;
}
.btn.primary{background:var(--red);color:#fff}
.btn.primary:hover{filter:brightness(1.12)}
.btn.ghost{background:transparent;border-color:var(--line2);color:var(--ink-soft);margin-top:8px}
.btn.ghost:hover{border-color:var(--gold);color:var(--gold)}

.founder{font-size:11.5px;color:var(--ink-dim);line-height:1.6}
.founder b{color:var(--ink-soft);font-weight:600}

/* ── 面板 ── */
.panel{display:none}
.panel.on{display:block}
.panel-hd{margin-bottom:14px}
.panel-hd h2{font-size:20px;font-weight:600;margin-bottom:5px}
.panel-hd p{font-size:13px;color:var(--ink-soft);max-width:820px}

.legend-bar{display:flex;gap:14px;flex-wrap:wrap;align-items:center;
  padding:11px 16px;background:var(--panel);border:1px solid var(--line);
  border-radius:var(--r);margin-bottom:14px;font-size:12px;color:var(--ink-soft)}
.legend-bar .li{display:flex;align-items:center;gap:6px}

/* ── treemap ── */
.tm-wrap{background:var(--panel);border:1px solid var(--line);border-radius:var(--r);
  padding:14px;position:relative}
#treemap{width:100%;display:block}
.tm-cell{cursor:pointer;transition:opacity .12s}
.tm-cell:hover{opacity:.82}
.tm-cell rect{stroke:var(--bg);stroke-width:2}
.tm-name{font-size:14px;font-weight:600;fill:#12181f;pointer-events:none}
.tm-sub{font-size:11px;fill:#12181f;opacity:.72;pointer-events:none}
.tm-rate{font-size:19px;font-weight:700;fill:#12181f;pointer-events:none}
.tm-rate small{font-size:11px;font-weight:600}
.tm-area{font-size:10.5px;fill:#12181f;opacity:.68;pointer-events:none}
.tm-quad{font-size:10px;fill:#12181f;opacity:.5;pointer-events:none;font-weight:600}
.tm-bar-bg{fill:rgba(18,24,31,.22);pointer-events:none}
.tm-bar-fg{fill:#12181f;pointer-events:none}

/* ── 详情抽屉 ── */
.detail{
  margin-top:14px;background:var(--panel);border:1px solid var(--line);
  border-radius:var(--r);padding:20px;display:none
}
.detail.on{display:block}
.detail-hd{display:flex;justify-content:space-between;align-items:flex-start;
  gap:16px;margin-bottom:14px;flex-wrap:wrap}
.detail-hd h3{font-size:17px;font-weight:600}
.detail-hd .meta{font-size:12px;color:var(--ink-dim);margin-top:3px}
.pill{display:inline-block;padding:3px 10px;border-radius:99px;font-size:11px;
  font-weight:600;margin-right:6px}
.pill.g{background:rgba(74,168,112,.16);color:#5fc490;border:1px solid rgba(74,168,112,.3)}
.pill.y{background:rgba(212,176,74,.16);color:#e0c264;border:1px solid rgba(212,176,74,.3)}
.pill.o{background:rgba(224,138,60,.16);color:#e8a163;border:1px solid rgba(224,138,60,.3)}
.pill.r{background:rgba(208,87,79,.16);color:#e0776f;border:1px solid rgba(208,87,79,.3)}

.act-list{display:grid;gap:8px;margin-top:6px}
.act{display:flex;gap:12px;align-items:flex-start;padding:11px 13px;
  background:var(--bg2);border:1px solid var(--line);border-radius:8px}
.act .st{flex-shrink:0;width:62px;font-size:11px;font-weight:600;text-align:center;
  padding:3px 0;border-radius:5px;margin-top:2px}
.act .st.auto{background:rgba(74,168,112,.15);color:#5fc490}
.act .st.semi{background:rgba(212,176,74,.15);color:#e0c264}
.act .st.manual{background:rgba(208,87,79,.15);color:#e0776f}
.act .nm{font-size:13px;font-weight:600;margin-bottom:2px}
.act .ev{font-size:11.5px;color:var(--ink-dim);line-height:1.5}

/* ── 表单 ── */
.form{max-width:760px}
.field{margin-bottom:20px}
.field label{display:block;font-size:13px;font-weight:600;margin-bottom:8px}
.field .hint{font-size:11.5px;color:var(--ink-dim);font-weight:400;margin-left:6px}
.opts{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:8px}
.opt{background:var(--bg2);border:1px solid var(--line);border-radius:8px;
  padding:11px 13px;cursor:pointer;transition:.15s;font-size:13px}
.opt:hover{border-color:var(--line2)}
.opt.on{border-color:var(--gold);background:rgba(212,162,78,.09)}
.opt .o-n{font-weight:600}
.opt .o-s{font-size:11px;color:var(--ink-dim);margin-top:2px}
.report{margin-top:18px;background:var(--panel);border:1px solid var(--line);
  border-radius:var(--r);padding:22px;display:none}
.report.on{display:block}
.report h3{font-size:17px;margin-bottom:4px}
.report .r-sub{font-size:12.5px;color:var(--ink-dim);margin-bottom:16px}
.r-sec{margin-bottom:18px}
.r-sec > h4{font-size:12px;color:var(--gold);letter-spacing:1px;margin-bottom:9px;
  text-transform:uppercase}
.r-sec ol,.r-sec ul{padding-left:20px}
.r-sec li{font-size:13px;margin-bottom:7px;line-height:1.65}
.r-sec li b{color:var(--ink)}
.r-next{background:rgba(75,143,212,.08);border:1px solid rgba(75,143,212,.25);
  border-left:3px solid var(--blue);border-radius:8px;padding:13px 15px;
  font-size:13px;line-height:1.65}
.warn{background:rgba(212,162,78,.07);border:1px solid rgba(212,162,78,.22);
  border-radius:8px;padding:13px 15px;font-size:12.5px;color:var(--ink-soft);
  line-height:1.7;margin-top:20px}

/* ── 模型页 ── */
.q-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(255px,1fr));gap:14px}
.q{background:var(--panel);border:1px solid var(--line);border-radius:var(--r);
  padding:18px;border-top:3px solid}
.q h4{font-size:15px;font-weight:600;margin-bottom:4px}
.q .th{font-size:11px;color:var(--ink-dim);margin-bottom:9px}
.q p{font-size:12.5px;color:var(--ink-soft);line-height:1.7}
.q .cnt{font-size:11px;color:var(--ink-dim);margin-top:11px;padding-top:11px;
  border-top:1px solid var(--line)}
.flow{margin-top:26px;background:var(--panel);border:1px solid var(--line);
  border-radius:var(--r);padding:22px}
.flow h3{font-size:15px;margin-bottom:16px}
.flow-step{display:flex;gap:14px;margin-bottom:14px;align-items:flex-start}
.flow-n{width:26px;height:26px;border-radius:50%;background:var(--panel2);
  color:var(--gold);display:flex;align-items:center;justify-content:center;
  font-size:12px;font-weight:600;flex-shrink:0}
.flow-t{font-size:13.5px;font-weight:600;margin-bottom:3px}
.flow-d{font-size:12.5px;color:var(--ink-soft);line-height:1.65}

/* ── 案例页 ── */
.cases{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:14px}
.case{background:var(--panel);border:1px solid var(--line);border-radius:var(--r);
  padding:18px;display:flex;flex-direction:column}
.case .tag{font-size:11px;color:var(--blue);margin-bottom:7px;letter-spacing:.5px}
.case h4{font-size:15px;font-weight:600;margin-bottom:8px}
.case p{font-size:12.5px;color:var(--ink-soft);line-height:1.7;flex:1}
.case .kv{display:flex;gap:16px;margin-top:13px;padding-top:13px;
  border-top:1px solid var(--line);font-size:11.5px;color:var(--ink-dim)}
.case .kv b{color:var(--green);font-weight:600}

/* ── 工序链 ── */
.ch-list{display:flex;flex-direction:column;gap:10px}
.ch-step{background:var(--bg2);border:1px solid var(--line);border-radius:8px;
  padding:13px 15px;position:relative}
.ch-step.bn{border-color:rgba(208,87,79,.5);background:rgba(208,87,79,.06)}
.ch-top{display:flex;align-items:center;gap:10px;margin-bottom:9px}
.ch-i{width:22px;height:22px;border-radius:50%;background:var(--panel2);
  color:var(--gold);display:flex;align-items:center;justify-content:center;
  font-size:11px;font-weight:600;flex-shrink:0}
.ch-nm{font-size:13.5px;font-weight:600;flex:1}
.ch-bn{background:rgba(208,87,79,.18);color:#e88b83;font-size:10.5px;
  padding:2px 7px;border-radius:4px;letter-spacing:.5px}
.ch-min{font-size:12px;color:var(--blue);font-weight:600}
.ch-bar{height:5px;background:var(--panel2);border-radius:3px;overflow:hidden;
  margin-bottom:8px}
.ch-bar i{display:block;height:100%;background:linear-gradient(90deg,var(--blue),var(--gold))}
.ch-step.bn .ch-bar i{background:linear-gradient(90deg,var(--orange),var(--red))}
.ch-meta{display:flex;align-items:center;gap:10px}
.ch-share{font-size:11px;color:var(--ink-dim)}
.ch-dep{font-size:11px;color:var(--ink-dim);margin-top:7px}
.ch-ev{font-size:11.5px;color:var(--ink-soft);margin-top:7px;line-height:1.6}
.ch-note{font-size:11.5px;color:var(--ink-dim);line-height:1.7;margin-top:11px}

/* ── 单位经济 ── */
.ue-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:10px}
.ue{background:var(--bg2);border:1px solid var(--line);border-radius:8px;padding:13px}
.ue-n{font-size:21px;font-weight:700;color:var(--gold);line-height:1.2}
.ue-n small{font-size:11px;color:var(--ink-dim);margin-left:2px;font-weight:400}
.ue-l{font-size:11px;color:var(--ink-dim);margin-top:5px}

/* ── 经营推演 ── */
.sim-ctrl{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
  gap:16px;margin-bottom:18px}
.sim-c{background:var(--bg2);border:1px solid var(--line);border-radius:8px;padding:14px 16px}
.sim-c-l{font-size:12px;color:var(--ink-soft);margin-bottom:9px;display:flex;
  justify-content:space-between;align-items:center}
.sim-c-l b{color:var(--gold);font-size:13px}
.sim-c input[type=range]{width:100%;accent-color:var(--gold);cursor:pointer}
.sim-c .hint{font-size:10.5px;color:var(--ink-dim);margin-top:7px;line-height:1.5}
.sim-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:11px}
.sim-kpi{background:var(--bg2);border:1px solid var(--line);border-radius:9px;padding:16px}
.k-n{font-size:26px;font-weight:700;color:var(--gold);line-height:1.15}
.k-n small{font-size:11px;color:var(--ink-dim);margin-left:3px;font-weight:400}
.k-l{font-size:12px;color:var(--ink-soft);margin-top:6px}
.k-d{font-size:11px;color:var(--ink-dim);margin-top:5px}
.cadence{margin-top:13px;padding:11px 14px;border-radius:7px;font-size:12.5px;
  line-height:1.6;border:1px solid var(--line)}
.cadence.hl-good{background:rgba(74,168,112,.09);border-color:rgba(74,168,112,.3);color:#7cc49a}
.cadence.hl-warn{background:rgba(212,162,78,.09);border-color:rgba(212,162,78,.3);color:#dcb878}
.cadence.hl-bad{background:rgba(208,87,79,.09);border-color:rgba(208,87,79,.3);color:#e88b83}
.sim-bars{display:flex;flex-direction:column;gap:8px}
.sim-bar-row{display:grid;grid-template-columns:minmax(110px,1.5fr) 2fr 56px 42px;
  gap:10px;align-items:center}
.sim-bar-nm{font-size:12px;color:var(--ink-soft);overflow:hidden;
  text-overflow:ellipsis;white-space:nowrap}
.sim-bar{height:8px;background:var(--panel2);border-radius:4px;overflow:hidden}
.sim-bar i{display:block;height:100%;background:linear-gradient(90deg,var(--blue),var(--gold))}
.sim-bar-v{font-size:11.5px;color:var(--ink);text-align:right}
.sim-bar-p{font-size:11px;color:var(--ink-dim);text-align:right}
.sim-health{list-style:none;padding:0}
.sim-health li{font-size:12.5px;padding:9px 13px;border-radius:7px;margin-bottom:7px;
  line-height:1.6;border:1px solid var(--line)}
.sim-health li.hl-good{background:rgba(74,168,112,.08);border-color:rgba(74,168,112,.26)}
.sim-health li.hl-warn{background:rgba(212,162,78,.08);border-color:rgba(212,162,78,.26)}
.sim-health li.hl-bad{background:rgba(208,87,79,.08);border-color:rgba(208,87,79,.26)}
.sim-health li.hl-info{background:var(--bg2)}

/* ── 路线图 ── */
.rm{position:relative;padding-left:30px}
.rm::before{content:'';position:absolute;left:9px;top:8px;bottom:8px;width:2px;
  background:var(--line)}
.rm-item{position:relative;margin-bottom:22px}
.rm-item::before{content:'';position:absolute;left:-26px;top:5px;width:12px;height:12px;
  border-radius:50%;background:var(--gold);border:3px solid var(--bg)}
.rm-hd{display:flex;align-items:baseline;gap:11px;flex-wrap:wrap;margin-bottom:6px}
.rm-ph{font-size:11px;color:var(--gold);letter-spacing:1px}
.rm-ti{font-size:15px;font-weight:600}
.rm-w{font-size:11.5px;color:var(--ink-dim)}
.rm-goal{font-size:12.5px;color:var(--ink-soft);line-height:1.7;margin-bottom:11px}
.rm-tasks{display:flex;flex-direction:column;gap:6px;margin-bottom:11px}
.rm-task{display:flex;align-items:center;gap:10px;font-size:12.5px;
  background:var(--bg2);border:1px solid var(--line);border-radius:7px;padding:9px 13px}
.rm-task .mark{width:16px;height:16px;border-radius:50%;flex-shrink:0;
  display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:700}
.rm-task.done .mark{background:rgba(74,168,112,.2);color:#7cc49a}
.rm-task.todo .mark{background:rgba(212,162,78,.16);color:#dcb878}
.rm-task .tt{flex:1;color:var(--ink-soft)}
.rm-task .ts{font-size:10.5px;color:var(--ink-dim);font-family:ui-monospace,monospace}
.rm-gate{font-size:12px;padding:10px 14px;border-radius:7px;line-height:1.6;
  background:rgba(75,143,212,.08);border:1px solid rgba(75,143,212,.26);color:#8fbbe8}
.rm-gate b{color:var(--blue)}
.rm-exit{font-size:11.5px;color:var(--ink-dim);margin-top:7px;line-height:1.6}

/* ── 风险 ── */
.rk{display:flex;flex-direction:column;gap:11px}
.rk-item{background:var(--panel);border:1px solid var(--line);border-radius:9px;
  padding:16px}
.rk-hd{display:flex;align-items:center;gap:11px;margin-bottom:11px}
.rk-nm{font-size:14.5px;font-weight:600;flex:1}
.rk-badge{font-size:10.5px;padding:3px 9px;border-radius:4px;letter-spacing:.5px;
  background:rgba(208,87,79,.16);color:#e88b83}
.rk-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:11px}
.rk-cell{background:var(--bg2);border-radius:7px;padding:11px 13px}
.rk-cell .ck{font-size:10.5px;color:var(--ink-dim);letter-spacing:.5px;margin-bottom:5px}
.rk-cell .cv{font-size:12.5px;color:var(--ink);line-height:1.6}
.rk-cell .cv.th{color:var(--orange);font-weight:600}
.rk-act{font-size:12.5px;color:var(--ink-soft);line-height:1.7;margin-top:11px;
  padding-top:11px;border-top:1px solid var(--line)}

/* ── 变现链路页（v3 新增）── */
.mn{display:flex;flex-direction:column;gap:0}
.mn-stage{position:relative;margin-bottom:0}
.mn-hd{display:flex;align-items:center;gap:12px;margin-bottom:12px;flex-wrap:wrap}
.mn-badge{font-size:10.5px;padding:3px 10px;border-radius:4px;letter-spacing:.5px;
  background:rgba(212,162,78,.16);color:var(--gold)}
.mn-badge.cash{background:rgba(74,168,112,.2);color:#7cc49a}
.mn-ti{font-size:15px;font-weight:600}
.mn-why{font-size:12px;color:var(--ink-dim);margin-left:auto}
.mn-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:11px}
.mn-card{background:var(--panel);border:1px solid var(--line);border-radius:9px;
  padding:14px}
.mn-card.cash{border-color:rgba(74,168,112,.42);background:rgba(74,168,112,.05)}
.mn-card .ck{font-size:10.5px;color:var(--ink-dim);letter-spacing:.5px;margin-bottom:6px}
.mn-card .cn{font-size:13.5px;font-weight:600;margin-bottom:7px}
.mn-card .cd{font-size:12px;color:var(--ink-soft);line-height:1.65}
.mn-card .cm{font-size:11px;color:var(--gold);margin-top:8px;font-family:ui-monospace,monospace}
.mn-arrow{display:flex;align-items:center;justify-content:center;padding:9px 0;
  color:var(--ink-dim);font-size:16px}
.mn-arrow span{font-size:11px;letter-spacing:1px}
.mn-note{background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--gold);
  border-radius:8px;padding:15px 17px;margin-top:16px}
.mn-note h4{font-size:13.5px;margin-bottom:9px}
.mn-note p{font-size:12.5px;color:var(--ink-soft);line-height:1.75}
.mn-note .nd{display:block;margin-top:8px;font-size:11.5px;color:var(--ink-dim)}

footer{margin-top:36px;padding-top:20px;border-top:1px solid var(--line);
  font-size:11.5px;color:var(--ink-dim);line-height:1.8}
"""

# ─────────────────────────────────────────────────────────────
# treemap 布局（squarified treemap，纯 Python 实现）
# ─────────────────────────────────────────────────────────────


def squarify(items, x, y, W, H):
    """Squarified treemap 布局（Bruls/Huizing/van Wijk 思路的标准实现）。

    推导要点
    --------
    设当前矩形尺寸为 W×H，总面积 A=W×H，第 i 项的归一化面积为 a_i（Σa_i=1）。

    · 横排行（沿 x 铺满整行，厚度 h）：
        h = S·H              （S = 行内面积占比之和）
        项宽 w_i = a_i·W/S
        长宽比 w_i/h = W·a_i / (S²·H)
        ⇒ worst = max( W·a_max/(S²·H),  S²·H/(W·a_min) )

    · 竖排行（沿 y 铺满整列，厚度 w）：
        w = S·W
        项高 h_i = a_i·H/S
        长宽比 h_i/w = H·a_i / (S²·W)
        ⇒ worst = max( H·a_max/(S²·W),  S²·W/(H·a_min) )

    选行规则：逐项加入候选行，只要加入后 worst 不变差就继续加，
    否则封行并递归处理剩余项。
    """
    if not items or W <= 0 or H <= 0:
        return []
    total = sum(i["area"] for i in items)
    if total <= 0:
        return []
    nodes = sorted((dict(i) for i in items), key=lambda d: -d["area"])
    for n in nodes:
        n["_a"] = n["area"] / total     # 归一化面积
    out = []

    def worst(row, horizontal, w_rect, h_rect):
        s = sum(i["_a"] for i in row)
        if s <= 0:
            return float("inf")
        mx = max(i["_a"] for i in row)
        mn = min(i["_a"] for i in row)
        if horizontal:
            side_len, thick = w_rect, h_rect
        else:
            side_len, thick = h_rect, w_rect
        if thick <= 0 or side_len <= 0:
            return float("inf")
        return max(
            side_len * mx / (s * s * thick),
            s * s * thick / (side_len * mn),
        )

    def layout(itms, rect):
        rx, ry, rw, rh = rect
        if not itms:
            return
        if len(itms) == 1:
            itms[0].update(x=rx, y=ry, w=rw, h=rh)
            out.append(itms[0])
            return
        # 剩余项在该矩形内的归一化面积重新归一
        tot = sum(i["area"] for i in itms)
        for i in itms:
            i["_a"] = i["area"] / tot
        horizontal = rw >= rh

        row = []
        for it in itms:
            cand = row + [it]
            if not row:
                row = cand
                continue
            if worst(cand, horizontal, rw, rh) <= worst(row, horizontal, rw, rh):
                row = cand
            else:
                break
        rest = itms[len(row):]
        s = sum(i["_a"] for i in row)

        if horizontal:
            thick = s * rh                      # 行厚度
            cx = rx
            for it in row:
                iw = it["_a"] * rw / s if s > 0 else 0
                it.update(x=cx, y=ry, w=iw, h=thick)
                out.append(it)
                cx += iw
            layout(rest, (rx, ry + thick, rw, rh - thick))
        else:
            thick = s * rw                      # 列厚度
            cy = ry
            for it in row:
                ih = it["_a"] * rh / s if s > 0 else 0
                it.update(x=rx, y=cy, w=thick, h=ih)
                out.append(it)
                cy += ih
            layout(rest, (rx + thick, ry, rw - thick, rh))

    layout(nodes, (x, y, W, H))
    return out


QUAD_FILL = {
    "green": "#4aa870",
    "yellow": "#d4b04a",
    "orange": "#e08a3c",
    "red": "#d0574f",
}
# 低饱和背景 + 高对比文字：陈磊原图用浅底深字，这里保持同一思路
QUAD_TINT = {
    "green": "#5cba83",
    "yellow": "#d9bb62",
    "orange": "#e39c58",
    "red": "#d97a72",
}


def render_treemap(items, W=1240, H=1000):
    """把布局结果渲染成 SVG 片段。"""
    laid = squarify([dict(i) for i in items], 0, 0, W, H)
    parts = []
    for it in laid:
        x, y, w, h = it["x"], it["y"], it["w"], it["h"]
        if w < 8 or h < 8:
            continue
        fill = QUAD_TINT[it["quadrant_color"]]
        rate = it["rate"]
        pad = 3
        rx, ry = x + pad, y + pad
        rw, rh = w - pad * 2, h - pad * 2
        parts.append(
            f'<g class="tm-cell" data-key="{html.escape(it["key"])}" '
            f'tabindex="0" role="button" aria-label="{html.escape(it["name"])}">'
            f'<rect x="{rx:.1f}" y="{ry:.1f}" width="{rw:.1f}" height="{rh:.1f}" '
            f'rx="6" fill="{fill}"/>'
        )
        # 块内文字：按尺寸决定显示多少
        if h >= 96 and w >= 110:
            parts.append(
                f'<text class="tm-name" x="{rx+12:.1f}" y="{ry+24:.1f}">'
                f'{html.escape(it["name"])}</text>'
            )
            parts.append(
                f'<text class="tm-sub" x="{rx+12:.1f}" y="{ry+42:.1f}">'
                f'{html.escape(it["sub"])}</text>'
            )
            parts.append(
                f'<text class="tm-rate" x="{rx+12:.1f}" y="{ry+74:.1f}">'
                f'工具化 {rate}%</text>'
            )
            bar_w = min(rw - 24, 132)
            parts.append(
                f'<rect class="tm-bar-bg" x="{rx+12:.1f}" y="{ry+84:.1f}" '
                f'width="{bar_w:.1f}" height="5" rx="2.5"/>'
            )
            parts.append(
                f'<rect class="tm-bar-fg" x="{rx+12:.1f}" y="{ry+84:.1f}" '
                f'width="{bar_w*rate/100:.1f}" height="5" rx="2.5"/>'
            )
            if h >= 130:
                # v3：面积口径改为月产出件数（工序链推导），素材供给单列
                parts.append(
                    f'<text class="tm-area" x="{rx+12:.1f}" y="{ry+104:.1f}">'
                    f'月产 {it["area"]} 件 · 独占素材 {it.get("material", 0)} 条</text>'
                )
            # 位次类型角标：素材位次 / 成品出口 / 现金出口
            kind = "现金出口" if it.get("is_cash") else (
                "成品出口" if it.get("is_channel") else "素材位次")
            parts.append(
                f'<text class="tm-kind" x="{rx+12:.1f}" y="{ry+rh-11:.1f}">'
                f'{kind}</text>'
            )
            # 象限角标：贴在方块右下角，大块也能看出归属
            parts.append(
                f'<text class="tm-quad" x="{rx+rw-11:.1f}" y="{ry+rh-11:.1f}" '
                f'text-anchor="end">{html.escape(it["quadrant_name"])}</text>'
            )
        elif h >= 52 and w >= 90:
            parts.append(
                f'<text class="tm-name" x="{rx+10:.1f}" y="{ry+22:.1f}" '
                f'style="font-size:12.5px">{html.escape(it["name"])}</text>'
            )
            parts.append(
                f'<text class="tm-rate" x="{rx+10:.1f}" y="{ry+42:.1f}" '
                f'style="font-size:14px">工具化 {rate}%</text>'
            )
        elif w >= 66 and h >= 34:
            parts.append(
                f'<text class="tm-name" x="{rx+8:.1f}" y="{ry+18:.1f}" '
                f'style="font-size:11px">{html.escape(it["name"])}</text>'
            )
        parts.append("</g>")
    return "\n".join(parts)


def build_report_js(items):
    """把生成报告的逻辑注入前端（数据已由 Python 算好，前端只做呈现）。"""
    payload = {}
    for r in S.ROLES:
        payload[r["key"]] = S.build_report(r["key"], "system")
    # 四种阶段各算一份
    allstage = {}
    for r in S.ROLES:
        allstage[r["key"]] = {
            st: S.build_report(r["key"], st) for st in ("manual", "tool", "pipeline", "system")
        }
    return json.dumps(
        {
            "roles": {i["key"]: i for i in items},
            "reports": allstage,
            "stageNames": {
                "manual": "全手工",
                "tool": "有工具",
                "pipeline": "有流程",
                "system": "要闭环",
            },
        },
        ensure_ascii=False,
    )


CASES = [
    {
        "tag": "已落地 · 契约层",
        "title": "SSOT 单一真相源登记表",
        "body": "每个数据文件有且只有一个写入者，其余角色只读。知识表与"
                "内容素材物理隔离，避免权限外溢。写入者提出变更、"
                "其他角色确认后才可落盘。",
        "kv": [("2 张真相源表", "物理隔离"), ("只写不读", "写入者唯一")],
    },
    {
        "tag": "已落地 · 数据层",
        "title": "养生知识表 205 条",
        "body": "八个主题分类，逐条标注适用体质、适用节气、内容要点、出处、"
                "食材清单与关联项目。出处全部回填至篇名级，节气条目达到原句级，"
                "26 条节气与经典条目可逐条回查对照表。",
        "kv": [("205 条", "全部带出处"), ("24/24", "节气覆盖")],
    },
    {
        "tag": "已落地 · 安全审查",
        "title": "10 类校验 + 14 项注入测试",
        "body": "校验脚本覆盖断言类、用药类、特定人群、问询类、项目类、"
                "食材目录归属等十类规则。另有独立注入测试验证防线本身有效，"
                "不是只看合规样本通过。",
        "kv": [("0 错误", "205 条全过"), ("14/14", "注入拦截")],
    },
    {
        "tag": "已落地 · 内容层",
        "title": "养生日课早报六卡",
        "body": "按日期与节气自动生成节气快照、体质画像、经典条文、今日养护、"
                "自省问答、明日预告六张卡片，附出处与免责说明，"
                "可直接推送到云文档空间。",
        "kv": [("6 卡", "每日一套"), ("自动", "生成即校验")],
    },
    {
        "tag": "已落地 · 工具层",
        "title": "体质自测单文件应用",
        "body": "36 题覆盖九种体质倾向，结果页建议逐条引用知识表原文，"
                "溯源是结构性的而非人工比对。页面零外部依赖，离线双击即开。",
        "kv": [("36 题", "九种体质"), ("单文件", "零外部依赖")],
    },
    {
        "tag": "已落地 · 分发层",
        "title": "推送通道与自检",
        "body": "早报转结构化文档上传，上传前执行十项自检：组件白名单、"
                "无表达式、颜色令牌、无联系方式、无外链、无购物导流、免责在位，"
                "任一不过即中止上传。",
        "kv": [("10 项", "上传前自检"), ("不过即停", "阻断上传")],
    },
    {
        "tag": "已修正 · 数据层",
        "title": "面积口径从重复计数改为互斥分摊",
        "body": "原口径把「内容主题」与「输出渠道」混在一层，同一批素材被多个"
                "位次各算一遍，十个位次面积合计 569 条，而知识表实际只有 205 条。"
                "现按主题唯一归属重新分摊，各位次独占素材合计精确等于 205 条，"
                "面积口径统一为月产出件数，同单位可比、可复算。",
        "kv": [("569 → 205", "重复计数已消除"), ("Σ 精确守恒", "逐条可回溯")],
    },
    {
        "tag": "已修正 · 经营层",
        "title": "线下交付停办后的现金出口重建",
        "body": "原模型中唯一产生现金的位次是线下门店交付，线下交付停办后该路径消失，"
                "全图无任何位次通向现金。现新增私域变现主作为唯一现金出口，"
                "承接内容位次的流量，把长期陪伴转为会员订阅；"
                "项目与边界类条目降级为知识素材，不再作为服务环节。",
        "kv": [("1 个", "现金出口位次"), ("9 + 1", "内容位次 + 变现位次")],
    },
]


# ─────────────────────────────────────────────────────────────
# 前端脚本（独立常量，避开 f-string 花括号转义）
# ─────────────────────────────────────────────────────────────
JS_BLOCK = r"""
const DATA = __PAYLOAD__;

// ── 页签 ──
function go(tab){
  document.querySelectorAll('.panel').forEach(p=>p.classList.remove('on'));
  document.querySelectorAll('nav button').forEach(b=>b.classList.remove('on'));
  const el = document.getElementById('panel-'+tab);
  if(el) el.classList.add('on');
  const btn = document.querySelector('nav button[data-tab="'+tab+'"]');
  if(btn) btn.classList.add('on');
  window.scrollTo({top:0,behavior:'smooth'});
}
// 从地图跳到工序链时，同步位次选择
function gotoChain(key){
  const opt = document.querySelector('#chainOpts .opt[data-role="'+key+'"]');
  if(opt){
    document.querySelectorAll('#chainOpts .opt').forEach(x=>x.classList.remove('on'));
    opt.classList.add('on');
    renderChain(key);
  }
  go('chain');
}
function gotoSim(key){
  const opt = document.querySelector('#simOpts .opt[data-role="'+key+'"]');
  if(opt){
    document.querySelectorAll('#simOpts .opt').forEach(x=>x.classList.remove('on'));
    opt.classList.add('on');
    simRole = key;
    renderSim();
  }
  go('sim');
}
document.querySelectorAll('nav button').forEach(b=>{
  b.addEventListener('click',()=>go(b.dataset.tab));
});

// ── treemap 详情 ──
const QUAD_PILL = {green:'g',yellow:'y',orange:'o',red:'r'};
function showDetail(key){
  const it = DATA.roles[key];
  if(!it) return;
  const acts = it.actions.map(a=>
    '<div class="act"><div class="st ' + a.state + '">' + a.state_label + '</div>' +
    '<div><div class="nm">' + a.name + '</div>' +
    '<div class="ev">' + (a.tool_evidence || '该环节含判断与表达，由人完成') + '</div></div></div>'
  ).join('');
  const html =
    '<div class="detail-hd"><div><h3>' + it.name + '</h3>' +
    '<div class="meta">' + it.sub + ' · 素材池 ' + it.area_note + '</div></div>' +
    '<div><span class="pill ' + QUAD_PILL[it.quadrant_color] + '">' + it.quadrant_name + '</span>' +
    '<span class="pill ' + QUAD_PILL[it.quadrant_color] + '">工具化 ' + it.rate + '%</span></div></div>' +
    '<p style="font-size:13px;color:var(--ink-soft);margin-bottom:16px;line-height:1.7">' + it.desc + '</p>' +
    '<div class="r-sec"><h4>动作拆解</h4><div class="act-list">' + acts + '</div></div>' +
    (it.manual_gap.length
      ? '<div class="r-sec"><h4>仍需人工</h4><ul>' +
        it.manual_gap.map(g=>'<li>'+g+'</li>').join('') + '</ul></div>'
      : '') +
    (it.pool.length
      ? '<div class="r-sec"><h4>可复用素材池</h4><p style="font-size:12.5px;color:var(--ink-soft)">' +
        it.pool.join(' · ') + '</p></div>'
      : '') +
    (it.unit_econ
      ? '<div class="r-sec"><h4>单位经济</h4>' +
        '<div class="ue-grid">' +
        '<div class="ue"><div class="ue-n">' + it.unit_econ.total_minutes + '<small>分</small></div><div class="ue-l">单件总工时</div></div>' +
        '<div class="ue"><div class="ue-n">' + it.unit_econ.residual_minutes + '<small>分</small></div><div class="ue-l">自动化后残余</div></div>' +
        '<div class="ue"><div class="ue-n">' + it.unit_econ.pieces_per_week + '<small>件</small></div><div class="ue-l">周产能</div></div>' +
        '</div>' +
        '<div class="warn" style="margin-top:11px">瓶颈工序：<b>' + it.unit_econ.bottleneck +
        '</b>（占单件工时 ' + it.unit_econ.bottleneck_share + '%）。' +
        '<button class="btn ghost" style="margin-top:9px" onclick="go(\'chain\')">查看完整工序链</button></div></div>'
      : '');
  const d = document.getElementById('detail');
  d.innerHTML = html;
  d.classList.add('on');
  d.scrollIntoView({behavior:'smooth',block:'nearest'});
}
document.querySelectorAll('.tm-cell').forEach(g=>{
  g.addEventListener('click',()=>showDetail(g.dataset.key));
  g.addEventListener('keydown',e=>{
    if(e.key==='Enter'||e.key===' '){e.preventDefault();showDetail(g.dataset.key);}
  });
});

// ── 生成报告 ──
let selRole = null, selStage = 'system';
function renderReport(){
  if(!selRole) return;
  const r = DATA.reports[selRole][selStage];
  const role = DATA.roles[selRole];
  const pill = QUAD_PILL[role.quadrant_color];
  const picks = r.picks.map(p=>
    '<li><b>' + p.name + '</b>（' + p.kind + '）—— ' + p.detail + '</li>').join('');
  const html =
    '<h3>' + role.name + ' · 位次报告</h3>' +
    '<div class="r-sub">当前工作方式：' + r.stage_name + '　|　' +
    '工具化率 ' + role.rate + '%　|　' +
    '<span class="pill ' + pill + '">' + role.quadrant_name + '</span>' +
    '<span class="pill ' + pill + '">素材池 ' + role.area_note + '</span></div>' +
    '<div class="r-sec"><h4>现状判定</h4><p style="font-size:13px;color:var(--ink-soft);line-height:1.7">' +
    role.desc + '</p></div>' +
    '<div class="r-sec"><h4>动作拆解与建议</h4><ol>' + picks + '</ol></div>' +
    '<div class="r-sec"><h4>仍需人工</h4><p style="font-size:13px;color:var(--ink-soft)">' +
    r.gap_text + '</p></div>' +
    '<div class="r-sec"><h4>下一步</h4><div class="r-next">' + r.next_step + '</div></div>' +
    '<div class="warn">提示：本报告依据工具化率与素材供给现状给出，与个人健康状况无关。' +
    '内容仅用于养生日常起居参考，不构成诊断或治疗建议；身体不适请至正规医疗机构就诊。</div>';
  const el = document.getElementById('report');
  el.innerHTML = html;
  el.classList.add('on');
}
document.querySelectorAll('#roleOpts .opt').forEach(o=>{
  o.addEventListener('click',()=>{
    document.querySelectorAll('#roleOpts .opt').forEach(x=>x.classList.remove('on'));
    o.classList.add('on');
    selRole = o.dataset.role;
    renderReport();
  });
});
document.querySelectorAll('#stageOpts .opt').forEach(o=>{
  o.addEventListener('click',()=>{
    document.querySelectorAll('#stageOpts .opt').forEach(x=>x.classList.remove('on'));
    o.classList.add('on');
    selStage = o.dataset.stage;
    renderReport();
  });
});

// ══════════════════════════════════════════════
// 深度模型：工序链 / 经营推演 / 90天路线 / 风险预警
// ══════════════════════════════════════════════

// ── 工序链下钻 ──
function renderChain(key){
  const r = MODEL.roles[key];
  if(!r) return;
  const u = r.unit_econ;
  const steps = r.chain_steps.map((s,i)=>{
    const depTxt = s.dep ? '<div class="ch-dep">前置：'+s.dep+'</div>' : '';
    const bn = s.bottleneck ? '<span class="ch-bn">瓶颈</span>' : '';
    return '<div class="ch-step' + (s.bottleneck?' bn':'') + '">' +
      '<div class="ch-top"><span class="ch-i">'+(i+1)+'</span>' +
      '<div class="ch-nm">'+s.name+'</div>' + bn +
      '<div class="ch-min">'+s.minutes+' 分</div></div>' +
      '<div class="ch-bar"><i style="width:'+Math.min(100,s.share)+'%"></i></div>' +
      '<div class="ch-meta"><span class="st '+s.state+'">'+s.state_label+'</span>' +
      '<span class="ch-share">占单件 '+s.share+'%</span></div>' +
      depTxt +
      (s.tool_evidence ? '<div class="ch-ev">'+s.tool_evidence+'</div>' : '') +
      '</div>';
  }).join('');

  const html =
    '<h3>'+r.name+' · 工序链</h3>' +
    '<div class="r-sub">产出单位：'+u.unit+'（'+u.unit_note+'）　|　' +
    '单件总工时 '+u.total_minutes+' 分　|　自动化后残余 '+u.residual_minutes+' 分</div>' +
    '<div class="r-sec"><h4>工序顺序与工时占比</h4><div class="ch-list">'+steps+'</div></div>' +
    '<div class="r-sec"><h4>单位经济</h4>' +
    '<div class="ue-grid">' +
    '<div class="ue"><div class="ue-n">'+u.total_minutes+'<small>分</small></div><div class="ue-l">单件总工时</div></div>' +
    '<div class="ue"><div class="ue-n">'+u.manual_minutes+'<small>分</small></div><div class="ue-l">纯手工占用</div></div>' +
    '<div class="ue"><div class="ue-n">'+u.auto_saved_minutes+'<small>分</small></div><div class="ue-l">自动化已省</div></div>' +
    '<div class="ue"><div class="ue-n">'+u.residual_minutes+'<small>分</small></div><div class="ue-l">当前残余</div></div>' +
    '<div class="ue"><div class="ue-n">'+u.pieces_per_week+'<small>件</small></div><div class="ue-l">周产能</div></div>' +
    '</div>' +
    '<p class="ch-note">工时为口径值（非实测），用于横向比较与瓶颈识别；' +
    '实际投入可按真实记录覆盖。周产能已扣除维持性开销（分发、回复、复盘、素材补充）。</p></div>' +
    '<div class="r-sec"><h4>瓶颈</h4><div class="warn" style="margin-top:0">' +
    '当前瓶颈工序为「'+u.bottleneck+'」，占单件工时 '+u.bottleneck_share+'%。' +
    '优化它对产能的边际收益最大——可到「经营推演」页调整参数看效果。</div></div>';
  document.getElementById('chain').innerHTML = html;
  document.getElementById('chain').classList.add('on');
}
document.querySelectorAll('#chainOpts .opt').forEach(o=>{
  o.addEventListener('click',()=>{
    document.querySelectorAll('#chainOpts .opt').forEach(x=>x.classList.remove('on'));
    o.classList.add('on');
    renderChain(o.dataset.role);
  });
});

// ── 经营推演 ──
// 默认位次取内容量最大的那个（用数据层排序后的第一个），避免写死 key 失效
let simRole = MODEL.order[0];
function renderSim(){
  const r = MODEL.roles[simRole];
  const res = SIM.run(simRole, simHours, simOpt, simAuto);
  if(!res) return;
  const u = r.unit_econ;

  const bars = res.steps.map(s=>
    '<div class="sim-bar-row"><div class="sim-bar-nm">'+s.name+'</div>' +
    '<div class="sim-bar"><i style="width:'+Math.min(100,s.share)+'%"></i></div>' +
    '<div class="sim-bar-v">'+s.minutes+' 分</div>' +
    '<div class="sim-bar-p">'+s.share+'%</div></div>'
  ).join('');

  const health = res.health.map(h=>
    '<li class="hl-'+h.level+'">'+h.text+'</li>').join('');

  const html =
    '<h3>经营推演 · '+r.name+'</h3>' +
    '<div class="r-sub">产出单位 '+res.unit+'　|　投入 '+simHours+' 小时/周　|　' +
    '瓶颈优化 '+simOpt+'%　|　自动化投入 '+simAuto+'%</div>' +

    '<div class="r-sec"><h4>推演结果</h4>' +
    '<div class="sim-grid">' +
    '<div class="sim-kpi"><div class="k-n">'+res.piecesPerWeek+'<small>件/周</small></div>' +
    '<div class="k-l">稳定产能</div><div class="k-d">'+res.piecesPerDay+' 件/日</div></div>' +
    '<div class="sim-kpi"><div class="k-n">'+res.pieces90+'<small>件</small></div>' +
    '<div class="k-l">90 天累计</div><div class="k-d">约 12.9 周产量</div></div>' +
    '<div class="sim-kpi"><div class="k-n">'+res.residualMinutes+'<small>分</small></div>' +
    '<div class="k-l">单件残余工时</div><div class="k-d">较基线省 '+res.savedMinutes+' 分</div></div>' +
    '<div class="sim-kpi"><div class="k-n">'+res.newBottleneckShare+'<small>%</small></div>' +
    '<div class="k-l">新瓶颈占比</div><div class="k-d">'+res.newBottleneck+'</div></div>' +
    '</div>' +
    '<div class="cadence hl-'+res.cadence.level+'">'+res.cadence.text+'</div></div>' +

    '<div class="r-sec"><h4>优化后工序工时结构</h4><div class="sim-bars">'+bars+'</div>' +
    '<p class="ch-note">瓶颈工序「'+res.bottleneckName+'」在本轮优化中削减了 ' +
    res.bottleneckSaved+' 分钟。工时为口径值，不含收入预测——' +
    '没有真实定价与转化数据时，任何收入数字都是虚构。</p></div>' +

    '<div class="r-sec"><h4>结构体检</h4><ul class="sim-health">'+health+'</ul></div>' +

    '<div class="r-sec"><h4>基线对照</h4>' +
    '<div class="ue-grid">' +
    '<div class="ue"><div class="ue-n">'+u.residual_minutes+'<small>分</small></div><div class="ue-l">当前残余</div></div>' +
    '<div class="ue"><div class="ue-n">'+res.residualMinutes+'<small>分</small></div><div class="ue-l">推演后残余</div></div>' +
    '<div class="ue"><div class="ue-n">'+u.pieces_per_week+'<small>件</small></div><div class="ue-l">当前周产能</div></div>' +
    '<div class="ue"><div class="ue-n">'+res.piecesPerWeek+'<small>件</small></div><div class="ue-l">推演后周产能</div></div>' +
    '<div class="ue"><div class="ue-n">'+u.bottleneck_share+'<small>%</small></div><div class="ue-l">当前瓶颈占比</div></div>' +
    '</div></div>' +

    '<div class="warn">本推演只测算产能与工时结构，不含收入、转化率与成本预测——' +
    '这些需要真实经营数据支撑，在没有实测数据前给出数字属于虚构。' +
    '内容仅用于养生日常起居参考，不构成诊断或治疗建议。</div>';
  document.getElementById('sim').innerHTML = html;
  document.getElementById('sim').classList.add('on');
}
document.querySelectorAll('#simOpts .opt').forEach(o=>{
  o.addEventListener('click',()=>{
    document.querySelectorAll('#simOpts .opt').forEach(x=>x.classList.remove('on'));
    o.classList.add('on');
    simRole = o.dataset.role;
    renderSim();
  });
});
['simHours','simOpt','simAuto'].forEach(id=>{
  const el = document.getElementById(id);
  if(el) el.addEventListener('input',()=>{
    if(id==='simHours') simHours = +el.value;
    if(id==='simOpt') simOpt = +el.value;
    if(id==='simAuto') simAuto = +el.value;
    const lbl = document.getElementById(id+'Val');
    if(lbl) lbl.textContent = el.value + (id==='simHours'?' 小时':'%');
    renderSim();
  });
});

// ── 首屏预渲染 ──
(function(){
  const first = document.querySelector('#chainOpts .opt');
  if(first) first.classList.add('on');
  renderChain(MODEL.order[0]);
  const sfirst = document.querySelector('#simOpts .opt');
  if(sfirst) sfirst.classList.add('on');
  renderSim();
})();
"""


def build_html():
    # 深度模型一次性构建，横向地图与纵向工序链共用同一份数据
    model = D.build_deep_model()
    items = [model["roles"][k] for k in model["order"]]
    stats = model["stats"]
    payload = build_report_js(items)

    # 左侧状态分布
    from collections import Counter as _C
    qcount = _C(i["quadrant_name"] for i in items)
    legend = []
    for q in S.QUADRANTS:
        n = qcount.get(q["name"], 0)
        # 空象限不写「当前 0 个位次」——那读起来像体系有缺口；
        # 改为说明它是待进入的阶段
        cnt_text = (f'门槛 {q["threshold"]} · 当前 {n} 个位次'
                    if n else f'门槛 {q["threshold"]} · 暂无位次，待进入')
        legend.append(
            f'<div class="legend-item"><span class="dot" style="background:'
            f'{QUAD_TINT[q["color"]]}"></span><div><b>{q["name"]}</b>'
            f'<span>{q["desc"]}</span>'
            f'<em>{cnt_text}</em></div></div>'
        )
    legend_html = "\n".join(legend)

    # 左侧数据来源
    n_material_roles = sum(1 for i in items if not i["is_channel"])
    n_channel_roles = sum(1 for i in items if i["is_channel"])
    stat_items = [
        (len(items), "个", "在图位次总数"),
        (stats["素材总条数"], "条", "知识表素材总量"),
        (n_material_roles, "个", "素材加工位次"),
        (n_channel_roles, "个", "成品出口位次"),
        (stats["内容主题数"], "类", "内容主题分类"),
        (stats["节气覆盖"], "", "节气全覆盖"),
        (stats["体质分类数"], "种", "基础体质分类"),
        (stats["红线注入测试"], "", "红线注入测试"),
    ]
    stat_html = "\n".join(
        f'<div class="stat"><div class="n">{n}<small>{u}</small></div>'
        f'<div class="l">{l}</div></div>'
        for n, u, l in stat_items
    )

    # 案例卡
    case_html = "\n".join(
        f'<div class="case"><div class="tag">{html.escape(c["tag"])}</div>'
        f'<h4>{html.escape(c["title"])}</h4><p>{html.escape(c["body"])}</p>'
        f'<div class="kv">'
        + "".join(f'<span>{html.escape(k)} <b>{html.escape(v)}</b></span>' for k, v in c["kv"])
        + "</div></div>"
        for c in CASES
    )

    # 四象限卡（模型页）
    q_html = "\n".join(
        f'<div class="q" style="border-top-color:{QUAD_TINT[q["color"]]}">'
        f'<h4>{html.escape(q["name"])}</h4>'
        f'<div class="th">门槛 {html.escape(q["threshold"])}</div>'
        f'<p>{html.escape(q["desc"])}</p>'
        + (f'<div class="cnt">当前落在该象限：{qcount.get(q["name"], 0)} 个位次</div>'
           if qcount.get(q["name"], 0)
           else '<div class="cnt">当前无位次落在该象限，属于待进入阶段</div>')
        + '</div>'
        for q in S.QUADRANTS
    )

    # 位次选项（生成报告页）
    opt_html = "\n".join(
        f'<div class="opt" data-role="{html.escape(i["key"])}">'
        f'<div class="o-n">{html.escape(i["name"])}</div>'
        f'<div class="o-s">{html.escape(i["sub"])}</div></div>'
        for i in items
    )

    stage_html = "\n".join(
        f'<div class="opt" data-stage="{k}"><div class="o-n">{v}</div>'
        f'<div class="o-s">{d}</div></div>'
        for k, v, d in [
            ("manual", "全手工", "所有内容靠人手写"),
            ("tool", "有工具", "有脚本但没有统一流程"),
            ("pipeline", "有流程", "关键动作已进管线"),
            ("system", "要闭环", "想跑完整闭环"),
        ]
    )

    # ── 深度模型：工序链 / 推演 / 路线 / 风险 ──
    model_json = json.dumps(model, ensure_ascii=False, separators=(",", ":"))
    deep_items = items

    # 工序链与推演的位次选项（用同一套 option 样式）
    chain_opt_html = "\n".join(
        f'<div class="opt" data-role="{html.escape(i["key"])}">'
        f'<div class="o-n">{html.escape(i["name"])}</div>'
        f'<div class="o-s">{html.escape(i["unit_econ"]["unit"])} · '
        f'残余 {i["unit_econ"]["residual_minutes"]} 分</div></div>'
        for i in deep_items
    )
    sim_opt_html = chain_opt_html

    # 路线图
    roadmap_html = "\n".join(
        f'<div class="rm-item"><div class="rm-hd">'
        f'<span class="rm-ph">阶段 {p["phase"]}</span>'
        f'<span class="rm-ti">{html.escape(p["title"])}</span>'
        f'<span class="rm-w">{html.escape(p["window"])}</span></div>'
        f'<div class="rm-goal">{html.escape(p["goal"])}</div>'
        f'<div class="rm-tasks">'
        + "".join(
            f'<div class="rm-task {"done" if t[1] == "已落地" else "todo"}">'
            f'<span class="mark">{"✓" if t[1] == "已落地" else "○"}</span>'
            f'<span class="tt">{html.escape(t[0])}</span>'
            f'<span class="ts">{html.escape(t[2])}</span></div>'
            for t in p["tasks"]
        )
        + '</div>'
        f'<div class="rm-gate"><b>出口条件：</b>{html.escape(p["gate"])}</div>'
        f'<div class="rm-exit"><b>未达成则：</b>{html.escape(p["exit_signal"])}</div></div>'
        for p in model["roadmap"]
    )

    # 风险判据
    risk_html = "\n".join(
        f'<div class="rk-item"><div class="rk-hd">'
        f'<span class="rk-nm">{html.escape(r["name"])}</span>'
        f'<span class="rk-badge">高关注</span></div>'
        f'<div class="rk-grid">'
        f'<div class="rk-cell"><div class="ck">观测指标</div>'
        f'<div class="cv">{html.escape(r["indicator"])}</div></div>'
        f'<div class="rk-cell"><div class="ck">判定阈值</div>'
        f'<div class="cv th">{html.escape(r["threshold"])}</div></div>'
        f'</div>'
        f'<div class="rk-act"><b>成因：</b>{html.escape(r["why"])}<br>'
        f'<b>应对：</b>{html.escape(r["action"])}</div></div>'
        for r in model["risks"]
    )

    # 变现链路（v3 新增）
    funnel_parts = []
    for i, st in enumerate(model["funnel"]):
        if i > 0:
            funnel_parts.append(
                '<div class="mn-arrow"><span>▼</span></div>')
        cards = "".join(
            f'<div class="mn-card{" cash" if st["stage"] == 3 else ""}">'
            f'<div class="ck">{html.escape(c["k"])}</div>'
            f'<div class="cn">{html.escape(c["n"])}</div>'
            f'<div class="cd">{html.escape(c["d"])}</div>'
            f'<div class="cm">{html.escape(c["m"])}</div></div>'
            for c in st["cards"]
        )
        funnel_parts.append(
            f'<div class="mn-stage"><div class="mn-hd">'
            f'<span class="mn-badge{" cash" if st["stage"] == 3 else ""}">'
            f'{html.escape(st["badge"])}</span>'
            f'<span class="mn-ti">{html.escape(st["title"])}</span>'
            f'<span class="mn-why">{html.escape(st["why"])}</span></div>'
            f'<div class="mn-row">{cards}</div></div>'
        )
    funnel_html = "\n".join(funnel_parts)

    gates_html = "".join(
        f'<p><b>{html.escape(g[0])}：</b>{html.escape(g[1])}'
        f'<span class="nd">若不成立 —— {html.escape(g[2])}</span></p>'
        for g in model["funnel_gates"]
    )

    js = JS_BLOCK.replace("__PAYLOAD__", payload)
    js = js.replace("__MODEL_JSON__", model_json)
    js = js.replace("__SIM_JS__", SIM_JS)
    html_text = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>养生一人公司生存地图</title>
<style>{CSS}</style>
</head>
<body>
<header>
  <div class="hd">
    <div class="brand">
      <h1>养生一人公司生存地图</h1>
      <span class="sub">位次 × 月产出产能 × 工具化程度</span>
    </div>
    <nav>
      <button class="on" data-tab="map">生存地图</button>
      <button data-tab="chain">工序链</button>
      <button data-tab="sim">经营推演</button>
      <button data-tab="funnel">变现链路</button>
      <button data-tab="roadmap">90天路线</button>
      <button data-tab="risk">风险预警</button>
      <button data-tab="report">生成报告</button>
      <button data-tab="model">生存模型</button>
      <button data-tab="cases">案例库</button>
    </nav>
  </div>
</header>

<div class="wrap">
<div class="main">
  <!-- ══ 侧栏 ══ -->
  <aside class="side">
    <div class="card">
      <h3>位次状态分布</h3>
      {legend_html}
    </div>
    <div class="card">
      <h3>数据来源</h3>
      <div class="stat-grid">{stat_html}</div>
      <div style="margin-top:11px;font-size:11px;color:var(--ink-dim);line-height:1.6">
        面积口径为<b>月产出件数</b>，由各工序链的残余工时推算；
        独占素材条数可逐条回溯至 data/养生知识表.csv，十个位次合计 205 条；
        工具化率由各动作节点的工具化状态加权得出。
      </div>
    </div>
    <div class="card">
      <button class="btn primary" onclick="go('report')">生成我的报告</button>
      <button class="btn ghost" onclick="go('cases')">查看案例</button>
    </div>
    <div class="card founder">
      <b>项目发起</b><br>
      面积 = 月产出件数<br>
      进度条 = 工具化率<br>
      <span style="display:inline-block;margin-top:9px;padding:2px 8px;
        border-radius:4px;background:rgba(212,162,78,.14);
        color:var(--gold);font-size:10.5px">真实业务数据</span>
    </div>
  </aside>

  <!-- ══ 主区 ══ -->
  <main>
    <!-- 生存地图 -->
    <section class="panel on" id="panel-map">
      <div class="panel-hd">
        <h2>养生内容与服务的十种一人位次</h2>
        <p>每个方块是一类可独立经营的内容或服务位次。方块面积代表该位次可调用的
          素材规模，颜色与进度条代表工具化程度——即有多少动作已经进管线、
          人只需做定稿。点击任一方块查看该位次的动作拆解。</p>
      </div>
      <div class="legend-bar">
        <span style="color:var(--ink-dim)">工具化率</span>
        <span class="li"><span class="dot" style="background:{QUAD_TINT['red']}"></span>纯手工区 &lt;30%</span>
        <span class="li"><span class="dot" style="background:{QUAD_TINT['orange']}"></span>工具区 30–55%</span>
        <span class="li"><span class="dot" style="background:{QUAD_TINT['yellow']}"></span>流程区 55–80%</span>
        <span class="li"><span class="dot" style="background:{QUAD_TINT['green']}"></span>系统区 ≥80%</span>
        <span style="margin-left:auto;color:var(--ink-dim)">面积 = 可调用素材条数</span>
      </div>
      <div class="tm-wrap">
        <svg id="treemap" viewBox="0 0 1240 1000" role="img"
             aria-label="养生一人公司位次与工具化程度分布图">
          {render_treemap(items)}
        </svg>
      </div>
      <div class="detail" id="detail"></div>
    </section>

    <!-- 工序链 -->
    <section class="panel" id="panel-chain">
      <div class="panel-hd">
        <h2>工序链 · 从一条素材到一件成品</h2>
        <p>地图给出的是横截面：这���位次有多大素材、多高工具化率。
          工序链补上纵深——一件事到底经过哪几道工序、每道占多少工时、
          哪一道是真正的瓶颈。选择位次查看完整链路。</p>
      </div>
      <div class="form">
        <div class="field">
          <label>选择位次</label>
          <div class="opts" id="chainOpts">{chain_opt_html}</div>
        </div>
      </div>
      <div class="report" id="chain"></div>
    </section>

    <!-- 经营推演 -->
    <section class="panel" id="panel-sim">
      <div class="panel-hd">
        <h2>经营推演 · 一人公司到底能产出多少</h2>
        <p>拖动三个参数，实时看产能如何变化：每周投入多少工时、
          瓶颈工序优化到什么程度、额外投入多少自动化。
          推演只算产能与工时结构，不做收入预测——没有真实定价与转化数据时，
          任何收入数字都是虚构。</p>
      </div>
      <div class="form">
        <div class="field">
          <label>选择位次</label>
          <div class="opts" id="simOpts">{sim_opt_html}</div>
        </div>
        <div class="field">
          <label>推演参数</label>
          <div class="sim-ctrl">
            <div class="sim-c">
              <div class="sim-c-l"><span>每周投入工时</span><b id="simHoursVal">20 小时</b></div>
              <input type="range" id="simHours" min="4" max="60" step="1" value="20">
              <div class="hint">一人公司的真实上限受维持性开销挤压，
                有效产出系数已按 {int(model['config']['effective_factor']*100)}% 计入。</div>
            </div>
            <div class="sim-c">
              <div class="sim-c-l"><span>瓶颈优化力度</span><b id="simOptVal">40%</b></div>
              <input type="range" id="simOpt" min="0" max="100" step="5" value="40">
              <div class="hint">把占比最高的工序接进管线或做减法的力度，
                直接决定单件残余工时。</div>
            </div>
            <div class="sim-c">
              <div class="sim-c-l"><span>自动化投入</span><b id="simAutoVal">40%</b></div>
              <input type="range" id="simAuto" min="0" max="100" step="5" value="40">
              <div class="hint">额外投入在自动化上的精力，
                用于压缩半自动环节的定稿工时。</div>
            </div>
          </div>
        </div>
      </div>
      <div class="report" id="sim"></div>
    </section>

    <!-- 变现链路 -->
    <section class="panel" id="panel-funnel">
      <div class="panel-hd">
        <h2>变现链路 · 线下交付停办后钱从哪来</h2>
        <p>线下交付已停办，这条路径不再存在。本页说明养生链现在
          唯一的现金路径：从公开内容到私域沉淀，再到会员订阅。
          每一环给出承载位次、靠什么能力撑住，以及这一环通了的判据。
          <b>本页不出现任何收入数字</b> —— 没有真实的定价、转化与续订数据时，
          收入预测都是虚构；判据是可观测口径，由你自己的真实数据来填。</p>
      </div>
      <div class="mn">{funnel_html}</div>
      <div class="mn-note">
        <h4>三环通路判据</h4>
        {gates_html}
        <span class="nd">判据只描述「怎么算通」，不预设「会赚多少」。
          收入、转化率与成本一律不由本表推算。</span>
      </div>
    </section>

    <!-- 90 天路线 -->
    <section class="panel" id="panel-roadmap">
      <div class="panel-hd">
        <h2>90 天推进路线 · 三阶段与出口条件</h2>
        <p>工具化的次序不是随意的。先让素材可信，再让重复进管线，
          最后接上分发与复盘。每个阶段都有明确的出口条件，
          达不到就说明还没到进入下一阶段的条件。</p>
      </div>
      <div class="rm">{roadmap_html}</div>
    </section>

    <!-- 风险预警 -->
    <section class="panel" id="panel-risk">
      <div class="panel-hd">
        <h2>风险预警 · 六条可观测的判据</h2>
        <p>生存地图的横截面看不出风险。风险必须绑定到可观测指标和判定阈值上，
          否则只是担心，不是管理。以下每条都给出观测口径、阈值与应对。</p>
      </div>
      <div class="rk">{risk_html}</div>
    </section>

    <!-- 生成报告 -->
    <section class="panel" id="panel-report">
      <div class="panel-hd">
        <h2>生成我的养生位次报告</h2>
        <p>选择你实际在做的位次与当前工作方式，报告会给出该位次的工具化率现状、
          仍需人工的动作，以及按依赖关系排序的下一步。每条建议都指向工作区里
          已经存在的能力，不是空泛建议。</p>
      </div>
      <div class="form">
        <div class="field">
          <label>你的位次</label>
          <div class="opts" id="roleOpts">{opt_html}</div>
        </div>
        <div class="field">
          <label>当前工作方式<span class="hint">决定报告给出的下一步</span></label>
          <div class="opts" id="stageOpts">{stage_html}</div>
        </div>
      </div>
      <div class="report" id="report"></div>
    </section>

    <!-- 生存模型 -->
    <section class="panel" id="panel-model">
      <div class="panel-hd">
        <h2>四象限生存模型</h2>
        <p>工具化程度不是越高越好。纯手工区的问题是人力占用重、无法复制；
          系统区的风险是人不再是瓶颈、内容失去温度。健康的形态是——
          让可重复的搬运工作进管线，把判断与表达留给自己。</p>
      </div>
      <div class="q-grid">{q_html}</div>
      <div class="flow">
        <h3>升级路径</h3>
        <div class="flow-step"><div class="flow-n">1</div><div>
          <div class="flow-t">先把素材沉淀成表</div>
          <div class="flow-d">内容先落成结构化条目，逐条标注出处、适用条件与
            边界。表格是所有后续自动化的地基，也是唯一真相源。</div></div></div>
        <div class="flow-step"><div class="flow-n">2</div><div>
          <div class="flow-t">再把重复动作写成脚本</div>
          <div class="flow-d">拆分、校验、改写、配对、推送这类搬运工作写成
            可重跑的脚本，输入是表，输出是成品。</div></div></div>
        <div class="flow-step"><div class="flow-n">3</div><div>
          <div class="flow-t">用校验器守住红线</div>
          <div class="flow-d">每次产出自动过一遍合规校验，命中即阻断。
            校验器本身还要用注入测试验证，不能只看合规样本通过。</div></div></div>
        <div class="flow-step"><div class="flow-n">4</div><div>
          <div class="flow-t">最后接上分发通道</div>
          <div class="flow-d">产出自动推到阅读场景，形成每日或每周的固定节律。
            分发前同样保留自检环节。</div></div></div>
        <div class="flow-step"><div class="flow-n">5</div><div>
          <div class="flow-t">把人留在判断与表达上</div>
          <div class="flow-d">经典释读、当面沟通、选材判断这些含判断的环节
            刻意保留手工。工具化率的满分不是 100%，而是不该自动化的部分
            确实留在了人手上。</div></div></div>
      </div>
    </section>

    <!-- 案例库 -->
    <section class="panel" id="panel-cases">
      <div class="panel-hd">
        <h2>已落地的养生链案例</h2>
        <p>以下每一项都已在工作区落地并通过校验，可直接查阅对应文件。
          这不是能力清单，是已经跑通的部分。</p>
      </div>
      <div class="cases">{case_html}</div>
    </section>
  </main>
</div>

<footer>
  本页所有数字取自 data/养生知识表.csv 与实际脚本运行结果，可逐条回溯。<br>
  内容仅用于养生日常起居参考，不构成诊断或治疗建议；身体不适请至正规医疗机构就诊。
</footer>
</div>

<script>
__SIM_JS__
const MODEL = __MODEL_JSON__;
let simHours = 20, simOpt = 40, simAuto = 40;
__JS_BLOCK__
</script>
</body>
</html>
"""
    # 替换顺序：先注入数据与引擎，再注入主脚本块
    html_text = html_text.replace("__SIM_JS__", SIM_JS)
    html_text = html_text.replace("__MODEL_JSON__", model_json)
    return html_text.replace("__JS_BLOCK__", js)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    html_text = build_html()
    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_text)
    items = S.build_map()
    print(f"✅ 已生成 {OUT_HTML}")
    print(f"   {len(html_text):,} 字节 · {len(items)} 个位次 · 单文件零外部依赖")
    return OUT_HTML


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
