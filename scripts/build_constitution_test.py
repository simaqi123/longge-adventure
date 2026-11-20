# -*- coding: utf-8 -*-
"""体质自测工具 · HTML 生成器

从 constitution_quiz.py 的题库生成单文件 HTML（离线可开、零外部依赖）。

红线（由 validate_constitution_html.py 机器校验）：
- 结果页：无联系方式、无 URL、无二维码、无外链、无电话、无社交账号
- 全页：无痛名、无疗效断言、无问诊诱导、无特定人群限定
- 结果页必须保留免责声明，且必须出现「不构成诊断」类表述

用法：python build_constitution_test.py
"""
import html
import os
import sys

import csv

from constitution_quiz import QUESTIONS, CONSTITUTIONS, RESULT_TEXT, load_ssot_constitution_rows

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import WEB_DIR as OUT_DIR, CONSTITUTION_HTML as OUT_HTML, SSOT_CSV as SSOT_PATH  # noqa: E402

# 选项 → 分值（李克特 5 级）
SCALE = [-3, -1, 0, 1, 3]


def build_quiz_js():
    """把题库序列化为 JS 数组。"""
    items = []
    for stem, o1, o2, o3, o4, o5, cons, weight in QUESTIONS:
        items.append({
            "stem": stem,
            "opts": [o1, o2, o3, o4, o5],
            "cons": cons,
            "w": weight,
        })
    return items


def build_result_js():
    """结果页文案 → JS。建议文案直接引用 SSOT 条目原文，保证逐字可溯源。"""
    src = load_ssot_constitution_rows()
    by_id = {}
    with open(SSOT_PATH, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            by_id[r["ID"]] = r
    out = {}
    for c in CONSTITUTIONS:
        t = RESULT_TEXT[c]
        advice = []
        for sid in t["advice_ids"]:
            row = by_id.get(sid)
            if row is None:
                raise SystemExit(f"❌ 引用了不存在的 SSOT 条目：{sid}（体质 {c}）")
            advice.append({"id": sid, "text": row["内容要点"]})
        out[c] = {
            "tagline": t["tagline"],
            "desc": t["desc"],
            "advice": advice,
            "projects": t["projects"],
        }
    return out


CSS = """
:root{
  --bg:#f7f6f2; --card:#ffffff; --ink:#2f2c28; --ink-soft:#6b6560;
  --line:#e4e0d8; --accent:#7a8f6a; --accent-soft:#eef2e9;
  --accent2:#9a7b4f; --accent2-soft:#f6efe2; --warn:#8a5a4a;
}
*{box-sizing:border-box;margin:0;padding:0}
body{
  font-family:"PingFang SC","Microsoft YaHei","Hiragino Sans GB",sans-serif;
  background:var(--bg); color:var(--ink); line-height:1.75;
  padding:24px 16px 64px; -webkit-font-smoothing:antialiased;
}
.wrap{max-width:720px;margin:0 auto}
header.top{text-align:center;padding:28px 20px 24px;margin-bottom:22px}
header.top h1{font-size:1.55rem;font-weight:600;letter-spacing:.5px;margin-bottom:8px}
header.top .sub{color:var(--ink-soft);font-size:.92rem}
.badge{
  display:inline-block;margin-top:14px;padding:4px 13px;border-radius:999px;
  background:var(--accent-soft);color:var(--accent);font-size:.78rem;letter-spacing:.4px
}
.card{
  background:var(--card);border:1px solid var(--line);border-radius:14px;
  padding:26px 24px;margin-bottom:18px;
  box-shadow:0 1px 3px rgba(0,0,0,.03)
}
.card h2{font-size:1.1rem;font-weight:600;margin-bottom:6px}
.card .hint{color:var(--ink-soft);font-size:.86rem;margin-bottom:20px}
.q{padding:18px 0;border-bottom:1px dashed var(--line)}
.q:last-child{border-bottom:none}
.q .stem{font-size:.98rem;margin-bottom:12px}
.q .opts{display:flex;flex-wrap:wrap;gap:8px}
.opt{
  flex:1 1 auto;min-width:74px;text-align:center;padding:9px 8px;
  border:1px solid var(--line);border-radius:9px;background:#fbfaf7;
  font-size:.86rem;color:var(--ink-soft);cursor:pointer;
  transition:all .16s ease;user-select:none
}
.opt:hover{border-color:var(--accent);background:var(--accent-soft)}
.opt.sel{background:var(--accent);border-color:var(--accent);color:#fff}
.progress{height:5px;background:var(--line);border-radius:99px;overflow:hidden;margin:16px 0 22px}
.progress i{display:block;height:100%;background:var(--accent);border-radius:99px;transition:width .3s ease}
.bar-top{display:flex;justify-content:space-between;align-items:center;font-size:.82rem;color:var(--ink-soft);margin-bottom:6px;gap:10px}
.bar-top #step-desc{flex:1;text-align:center;color:#9a948c;font-size:.78rem}
.btn{
  display:block;width:100%;padding:13px;border:none;border-radius:10px;
  background:var(--accent);color:#fff;font-size:.97rem;font-weight:500;
  cursor:pointer;font-family:inherit;transition:opacity .16s
}
.btn:hover{opacity:.88}
.btn:disabled{background:#cfcbc3;cursor:not-allowed}
.btn.ghost{background:transparent;color:var(--ink-soft);border:1px solid var(--line);margin-top:10px}
.hidden{display:none}
.result-head{text-align:center;padding:8px 0 20px}
.result-head .emoji{font-size:2.4rem;margin-bottom:8px}
.result-head h2{font-size:1.4rem;font-weight:600;margin-bottom:6px}
.result-head .tagline{color:var(--accent);font-size:.95rem}
.result-desc{
  background:var(--accent-soft);border-left:3px solid var(--accent);
  padding:14px 16px;border-radius:0 8px 8px 0;font-size:.92rem;margin-bottom:20px
}
.sec-title{font-size:.95rem;font-weight:600;margin:22px 0 12px;color:var(--ink)}
.advice{display:flex;flex-direction:column;gap:10px}
.advice li{
  list-style:none;background:#fbfaf7;border:1px solid var(--line);
  border-radius:10px;padding:12px 14px;font-size:.9rem;position:relative;padding-left:34px
}
.advice li::before{content:"·";position:absolute;left:15px;color:var(--accent);font-weight:700}
.chips{display:flex;flex-wrap:wrap;gap:8px}
.chip{
  padding:6px 13px;border-radius:999px;background:var(--accent2-soft);
  color:var(--accent2);font-size:.84rem;border:1px solid #e8ddc8
}
.bar-item{margin-bottom:14px}
.bar-item .bl{display:flex;justify-content:space-between;font-size:.85rem;margin-bottom:5px}
.bar-item .bt{height:8px;background:var(--line);border-radius:99px;overflow:hidden}
.bar-item .bt i{display:block;height:100%;background:var(--accent);border-radius:99px;transition:width .5s ease}
.bar-item.alt .bt i{background:var(--accent2)}
.disclaim{
  margin-top:22px;padding:16px 18px;background:#fbfaf7;border:1px solid var(--line);
  border-radius:10px;font-size:.82rem;color:var(--ink-soft);line-height:1.8
}
.disclaim strong{color:var(--ink);font-weight:600}
.src{margin-top:14px;font-size:.8rem;color:var(--ink-soft)}
.foot{text-align:center;margin-top:26px;font-size:.78rem;color:var(--ink-soft);line-height:1.9}
@media (max-width:520px){
  body{padding:16px 12px 48px}
  .card{padding:20px 16px}
  .opt{min-width:0;flex:1 1 44%}
}
"""

JS = """
const QUESTIONS = __QUESTIONS__;
const RESULTS = __RESULTS__;
const CONS = __CONS__;
const SCALE = [-3,-1,0,1,3];

let answers = new Array(QUESTIONS.length).fill(null);
let current = 0;

const el = id => document.getElementById(id);
const stepTitle = el('step-title');
const stepDesc = el('step-desc');
const qBox = el('q-box');
const bar = el('bar');
const barTxt = el('bar-txt');
const btnNext = el('btn-next');

function render(){
  const q = QUESTIONS[current];
  stepTitle.textContent = '第 ' + (current+1) + ' 题 / 共 ' + QUESTIONS.length + ' 题';
  stepDesc.textContent = '请选择最接近你日常状态的一项';
  const done = answers.filter(a=>a!==null).length;
  const pct = Math.round(done / QUESTIONS.length * 100);
  bar.style.width = pct + '%';
  barTxt.textContent = '已完成 ' + done + ' / ' + QUESTIONS.length;

  let html = '<div class="q"><div class="stem">' + q.stem + '</div><div class="opts">';
  q.opts.forEach((o,i)=>{
    const sel = answers[current]===i ? ' sel' : '';
    html += '<div class="opt'+sel+'" data-i="'+i+'">'+o+'</div>';
  });
  html += '</div></div>';
  qBox.innerHTML = html;
  qBox.querySelectorAll('.opt').forEach(o=>{
    o.addEventListener('click', ()=>{
      answers[current] = parseInt(o.dataset.i);
      render();
    });
  });
  btnNext.textContent = current === QUESTIONS.length-1 ? '查看结果' : '下一题';
  btnNext.disabled = answers[current]===null;
  if(answers[current]!==null && current===QUESTIONS.length-1){ /* 允许直接查看 */ }
}

function score(){
  // 各体质独立累加：只统计「归属该体质的题」上的得分。
  // 不做跨体质扣分——否则只要多数题选中立，其余体质都会被压成 0%，
  // 分布条失去分辨力。跨体质的相对关系由「该体质在其 4 题上的净得分」体现。
  const sc = {}; CONS.forEach(c=>sc[c]=0);
  QUESTIONS.forEach((q,idx)=>{
    const v = SCALE[answers[idx]];
    sc[q.cons] += v * q.w;
  });
  return sc;
}

function showResult(){
  el('quiz-page').classList.add('hidden');
  el('result-page').classList.remove('hidden');
  window.scrollTo({top:0,behavior:'smooth'});
  const sc = score();
  const ranked = CONS.map(c=>({c:c,s:sc[c]})).sort((a,b)=>b.s-a.s);
  const top = ranked[0];
  const t = RESULTS[top.c];
  // 归一化：以最高分为 100% 基准，负分体质显示为 0%，
  // 同分体质显示同一百分比（只表达相对强弱，不作绝对解读）
  const maxS = Math.max(top.s, 1);
  const pctOf = s => s <= 0 ? 0 : Math.max(0, Math.min(100, Math.round(s / maxS * 100)));
  // 平局判定：最高分为 0 或与次高分差值过小 → 判为「九种体质分布均衡」
  const flat = top.s <= 0 || (top.s - ranked[1].s) < 4;

  let html = '<div class="result-head">'
    + '<div class="emoji">🌿</div>'
    + (flat
        ? '<h2>九种体质分布均衡</h2><div class="tagline">你的作答在各体质上差异不大</div>'
        : '<h2>' + top.c + '</h2><div class="tagline">' + t.tagline + '</div>')
    + '</div>'
    + '<div class="result-desc">'
    + (flat
        ? '你的选择没有明显偏向某一类体质，说明日常状态比较均衡。这类情况下，更实用的做法是按当下季节与体感来调整：换季时留意衣被增减，饮食随口味与食欲变化，不必刻意固定在某一种体质上。'
        : t.desc)
    + '</div>';

  if (flat) {
    html += '<div class="sec-title">通用的日常调养方向</div><ul class="advice">'
      + '<li>三餐定时，忌过饱过饥；每餐七分饱，饭后百步走</li>'
      + '<li>作息宜早，起居有常，忌通宵与过度耗神</li>'
      + '<li>起居随气温增减衣被，居室保持通风干爽</li>'
      + '</ul>';
  } else {

  html += '<div class="sec-title">日常调养方向</div><ul class="advice">';
  t.advice.forEach(a=>{ html += '<li>'+a.text+'</li>'; });
  html += '</ul>';

  html += '<div class="sec-title">可配合的养生项目</div><div class="chips">';
  t.projects.forEach(p=>{ html += '<span class="chip">'+p+'</span>'; });
  html += '</div>';
  }

  html += '<div class="sec-title">九种体质倾向分布</div>';
  ranked.forEach((r,i)=>{
    const w = pctOf(r.s);
    const cls = (i===0?'':' alt');
    html += '<div class="bar-item'+cls+'"><div class="bl"><span>'+r.c+'</span><span>'+w+'%</span></div>'
      + '<div class="bt"><i style="width:'+w+'%"></i></div></div>';
  });

  html += '<div class="disclaim"><strong>说明</strong><br>'
    + '本结果为体质倾向的自我观察参考，不是疾病判断，也不构成诊断。'
    + '评分只反映你此刻的选择倾向，同一个人在不同季节、不同阶段的结果可能不同。<br>'
    + '如需了解具体健康状况，请前往医疗机构由医师面诊。'
    + '</div>';

  el('result-box').innerHTML = html;
}

btnNext.addEventListener('click', ()=>{
  if(answers[current]===null) return;
  if(current === QUESTIONS.length-1){ showResult(); return; }
  current++; render();
});

el('btn-restart').addEventListener('click', ()=>{
  answers = new Array(QUESTIONS.length).fill(null);
  current = 0;
  el('result-page').classList.add('hidden');
  el('quiz-page').classList.remove('hidden');
  render();
});

render();
"""


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    src = load_ssot_constitution_rows()
    js = (JS
          .replace("__QUESTIONS__", repr(build_quiz_js()))
          .replace("__RESULTS__", repr(build_result_js()))
          .replace("__CONS__", repr(CONSTITUTIONS)))

    # 溯源清单：列出结果页实际引用的全部 SSOT 条目
    with open(SSOT_PATH, encoding="utf-8-sig", newline="") as f:
        by_id = {r["ID"]: r for r in csv.DictReader(f)}
    used_ids = []
    for c in CONSTITUTIONS:
        for sid in RESULT_TEXT[c]["advice_ids"]:
            if sid not in used_ids:
                used_ids.append(sid)
    src_rows = []
    for sid in used_ids:
        r = by_id[sid]
        src_rows.append(
            f"<li>{html.escape(r['ID'])}　{html.escape(r['条目名'])}"
            f"　<span style=\"color:#8a8378\">{html.escape(r['适用体质'])}</span></li>")
    src_block = "".join(src_rows)

    page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>体质倾向自测</title>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">

  <!-- ══ 答题页 ══ -->
  <div id="quiz-page">
    <header class="top">
      <h1>体质倾向自测</h1>
      <div class="sub">36 题 · 约 3 分钟 · 依据《黄帝内经》九种体质分型</div>
      <div class="badge">养生参考 · 不构成诊断</div>
    </header>

    <div class="card">
      <div class="bar-top">
        <span id="step-title">第 1 题</span>
        <span id="step-desc">请选择最接近你日常状态的一项</span>
        <span id="bar-txt">已完成 0 / 36</span>
      </div>
      <div class="progress"><i id="bar" style="width:0%"></i></div>
      <div id="q-box"></div>
      <button class="btn" id="btn-next" disabled>下一题</button>
      <button class="btn ghost" id="btn-restart-quiz" style="display:none"></button>
    </div>

    <div class="card">
      <h2>作答说明</h2>
      <div class="hint" style="margin-bottom:0">
        题目问的是日常状态与偏好，不涉及疾病。请按最近一两个月的真实感受作答，
        不必纠结"应该怎样"；没有对错，凭第一反应选即可。
      </div>
    </div>
  </div>

  <!-- ══ 结果页 ══ -->
  <div id="result-page" class="hidden">
    <header class="top">
      <h1>你的体质倾向</h1>
      <div class="sub">以下是根据你的选择得出的倾向分布</div>
    </header>
    <div class="card">
      <div id="result-box"></div>
    </div>
    <div class="card">
      <h2>内容溯源</h2>
      <div class="hint">本页调养建议取自《养生知识表》中的体质条目，逐条可溯：</div>
      <div class="src"><ul>{src_block}</ul></div>
    </div>
    <button class="btn ghost" id="btn-restart">重新测一次</button>
    <div class="foot">
      本工具仅作养生参考，不替代医疗诊断。<br>
      身体不适请至医疗机构就诊。
    </div>
  </div>

</div>
<script>{js}</script>
</body>
</html>
"""
    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"✅ 已生成：{OUT_HTML}")
    print(f"   题库 {len(QUESTIONS)} 题 · 体质 {len(CONSTITUTIONS)} 种 · 溯源条目 {len(src_rows)} 条")
    print(f"   文件大小 {os.path.getsize(OUT_HTML)} 字节")


if __name__ == "__main__":
    main()
