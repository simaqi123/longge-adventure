# Deep Operating Model · Notes and Measurement Definitions

> Companion page: **One-Person Company Survival Map** (`web/养生一人公司生存地图.html`, 9 tabs)
> This document explains where every number on the page comes from, how credible it is, and how to recompute it.

---

## 1. Measurement Definitions (Important)

The numbers on the page fall into three layers. **Any number that does not declare its layer must not go on the page.**

### 1.1 Verifiable (from the SSOT and real script runs)

| Metric | Value | How to recompute |
|---|---|---|
| Material entries | 205 | `wc -l data/养生知识表.csv` |
| Content themes | 8 | Deduplicate the `主题` column of the SSOT |
| Solar term coverage | 24 / 24 | The `适用节气` column of the SSOT |
| Constitution coverage | 9 types | The `适用体质` column of the SSOT |
| Tooling ratio | Weighted by the state of each action node | `survival_map_data.py` |
| Exclusive material entries | Σ ≡ 205 (countable entry by entry after mutually exclusive allocation) | `allocate_materials()` |
| Monthly output units | Derived from the residual minutes of the process chain | `survival_deep_model.py` |
| Landed / pending tasks per stage | Corresponds to scripts and files that really exist | Checked item by item |

### 1.2 Declared-basis values (not measured; can be overwritten by real records)

**Per-unit minutes per process step** (`TIME_BASE`, unit: minutes per unit)

- Anchor basis: the net creation time for one finished piece of copy is significantly higher than a single proofreading pass; proofreading ≈ a small order of magnitude of creation
- Every role slot (one independently operable position inside a one-person company) can be overwritten with real records — **this is the layer that most deserves to be replaced by real data**

**Effective output factor 0.55**

A one-person company does not spend its time only on "producing content":

- Multi-platform distribution and layout adaptation
- Replying to comments and direct messages
- Reviewing data and adjusting topics
- Replenishing material and maintaining tooling
- State fluctuation (illness, mood, low-productivity hours)

A single process chain takes only about 55% of working time; the rest is maintenance overhead.

> **Skip this deduction and the computed capacity comes out significantly above what is actually achievable.**
> This is a real problem that was corrected: the first version computed "48 units per week", which distorted the result.

**Weekly available hours: 24 hours** (6 working days × 4 focused hours per day)

**Bottleneck threshold: 25%** (a step that eats up a quarter or more of your energy is the bottleneck)

### 1.3 What Is Deliberately Not Projected

**The projection contains no revenue, conversion rate, or cost forecast.**

Without real pricing and conversion data, any revenue number is fiction. The validator blocks:

- Expressions such as `预计月入`, `保底收入`, `预计收入`
- Expressions that present unit minutes as `实测`
- A projection area that fails to declare that it excludes revenue forecasts

---

## 2. Three Structural Invariants

### 2.1 `Σ exclusive material ≡ SSOT entry count`

**Why it is needed**: the area metric in v2 was "the number of entries in the role slot's own material pool inside the SSOT",
but the `themes` lists of the role slots overlap — those 79 `食养` entries were each counted once by the Food-Wellness Channel Lead, the short-video narration lead, the graphic-notes lead, and the Online Course Instructor.

Result: the areas of the ten role slots summed to **569 entries**, while the knowledge table actually holds only **205 entries**.
The same batch of material was counted repeatedly, the treemap area was completely distorted, and **the reading premise "bigger area = bigger role slot" no longer holds**.

**How to fix it**: introduce a `THEME_OWNER` attribution table — each theme is owned by exactly one primary role slot;
every other role slot that references that theme records it in `pool` (shared sourcing) and does not take up area again.

```python
THEME_OWNER = {
    "食养": "food_channel",   # → Food-Wellness Channel Lead
    "节气": "solar_channel",   # → Solar-Term Wellness Lead
    "体质": "constitution_channel",  # → Constitution Insight Lead
    "经典": "classic_channel", # → Classical Text Scholar
    "起居": "routine_channel", # → Daily Routine Lead
    "自省": "self_reflect",    # → 自省心性号主
    "边界": "monetize",        # → 私域变现主
    "项目": "monetize",        # → 私域变现主
}
```

So the identity holds: **Σ exclusive material across all role slots ≡ actual SSOT entry count**.
The validator check `L3 素材互斥分摊守恒` verifies it on every build.

### 2.2 A Single Area Metric: Monthly Output Units

In v2 the area mixed two quantities (material entries and output units), whose units are not comparable.
v3 standardizes on **monthly output units** — derived from the residual minutes of each process chain, so all ten role slots share one unit and are comparable and recomputable.

Material entries are no longer the area; they become a standalone "exclusive material" metric.

> Recompute: `output units = (available hours × effective output factor) / total minutes per unit`
> The validator checks that "the areas of the 10 role slots match the monthly output units derived from the process chain".

### 2.3 There Must Be Exactly One Cash Outlet

After the offline diagnostic services were shut down, the map had no cash outlet at all — a "survival map" with not a single path to money does not hold up.

The structure is therefore fixed as:

| Layer | Count | Role slots |
|---|---|---|
| Material role slots (exclusive material, counted in the area) | 6 | Food Therapy / Constitution / Solar Term / Classical Text / Daily Routine / Self-Reflection |
| Product outlets (material comes from upstream, not exclusive) | 3 | Short-Video & Carousel / Community & Private-Channel / Online Course |
| Cash outlet | 1 | Monetization Lead |

The validator check `L3 现金出口位次在位` forces the assertion that there is exactly one cash-outlet role slot.

---

## 3. The Nine Tabs in Detail

### 3.0 Monetization Path (panel-funnel)

Answers the question "where does the money come from now that offline delivery has stopped". Three layers:

| Layer | Carrying role slot | Function |
|---|---|---|
| Content layer | Short-video & carousel / graphic notes / course | Acquiring new users and building trust; not charged directly |
| Accumulation layer | Community & Private-Channel Lead (daily brief push) | Turning attention into a relationship you can reach again and again |
| Cash outlet | Monetization Lead (membership subscription) | Catching the accumulated relationship and turning it into a paid subscription |

Each layer gives two cards: the carrying role slot and its function, and what capability holds it up (including the tooling ratio or the compliance-validation basis).

**Compliance discipline**: this page contains **no revenue numbers at all**. Without real pricing, conversion, and renewal data,
any revenue projection is fiction. What is given instead is the "three-link path criteria":

- Public content layer: 4 consecutive weeks of output on schedule, every piece carrying a source and a disclaimer
- Private-domain accumulation layer: among users of the constitution self-assessment tool, a clear proportion enter the daily brief subscription and leave a constitution record
- Cash outlet layer: subscribers' renewal intent can be recorded, rather than only counting a one-off payment

These are observable criteria, filled in by the operator with their own real data.

### 3.1 Process Chain (panel-chain)

The complete delivery process of each role slot, shown step by step:

- Step number, name, state label (`已进管线` / `半自动` / `纯手工`)
- Minutes per unit, and the share of total minutes per unit (with a progress bar)
- Upstream dependencies (from `CHAIN_DEPS`, keeping only the actions that really exist within that role slot)
- Tool evidence (pointing at scripts that really exist in the repository)
- Bottleneck marker (anything at ≥25% is flagged red)

The bottom gives the five-cell unit economics panel: total minutes per unit / manual-only minutes / automation share / monthly output units / effective output factor.

### 3.2 Operating Simulation (panel-sim)

Three parameters compute capacity in real time:

| Parameter | Default | Meaning |
|---|---|---|
| Weekly focused hours | 24 h | The focused time actually put in each week |
| Bottleneck optimization | Off | Raise the automation level of the bottleneck step by one tier |
| Automation investment | 0 | Extra minutes added to automated steps after investing more |

**The projection gives units, never money.** The page states this in both the projection area and the engine comments.

### 3.3 Generated Report (panel-report)

Compresses the whole map into a one-page printable report: role slot list, material distribution, tooling ratio, quadrant assignment.

### 3.4 Survival Model (panel-model)

Cross-section reading of the map: the decision rules and thresholds for the quadrants (`System zone` / `Tooling zone` / `Process zone` / `Manual zone`).

### 3.5 Case Library (panel-cases)

The mapping between role slots and material, used to trace back which batch of material a given piece came from.

### 3.6 90-Day Roadmap (panel-roadmap)

Four stages; each stage gives: the goal, the exit condition, and what to do if it is not met.

### 3.7 Risk Alerts (panel-risk)

Six risk criteria, each bound to an **observable metric + decision threshold**:

| Risk | Criteria |
|---|---|
| Material running dry | Exclusive material consumption rate > replenishment rate |
| Single-point dependency | Share of a single material source > 60% |
| Metric drift | Derived-level data cited as measured-level data |
| Capacity overestimate | Actual output units < 70% of the projected figure |
| Compliance risk | Any red-line hit appears |
| Broken cash chain | Content output is normal but subscription conversion is 0 in a row |

### 3.8 Disclaimer and Definitions (panel-notes)

Disclaimer in place + layered measurement definitions + known limitations.

---

## 4. How the Process Chain Is Modeled

### 4.1 The Three States of an Action Node

| State | Meaning | Tooling ratio weight |
|---|---|---|
| `auto` | A script can produce it directly | 1.0 |
| `semi` | The script produces a first draft, a human rewrites it | 0.5 |
| `manual` | Purely manual, no tooling | 0.0 |

Role slot tooling ratio = the state-weighted mean of all action nodes in that role slot.

### 4.2 Deriving Monthly Output from Residual Minutes

```
total minutes per unit = Σ(minutes per unit of each action of that role slot)
manual-only minutes = Σ(minutes per unit of manual actions)
automatable minutes = total minutes per unit − manual-only minutes
minutes per output = automatable minutes × effective output factor + manual-only minutes × 1.0
monthly output units = monthly available hours / minutes per output
```

### 4.3 Bottleneck Determination

A step whose share of minutes per unit is **≥25%** is flagged red. The decision threshold is written in `survival_deep_model.py`,
and the threshold labeled on the page must match the data layer — the validator check `D3 每个风险条目的判定阈值与数据层一致` verifies it.

---

## 5. Validation and Injection Tests

| Validator | Coverage |
|---|---|
| `validate_ssot.py` | 20 compliance red lines + mandatory source + ingredient-list attribution check + data level enum |
| `validate_survival_map.py` | Structural integrity + every number matching the SSOT item by item + material conservation + unique cash outlet + no extra area labels |
| `validate_deep_model.py` | Process chain self-consistency + bidirectional page/data-layer verification + valid role slots on the first screen + no revenue promises + no passing projections off as measurements |
| `validate_constitution_html.py` | 16 red lines on the result page + 6 word lists across the whole page + 92-entry disease-name list + verbatim traceability + zero external dependencies |
| `test_survival_map_injection.py` | 44 injection cases: deliberately break the page and confirm the validator catches it |

**Injection tests are the only source of credibility.** A validator declaring "everything passed" by itself means nothing;
what matters is whether it **can catch a deliberately broken page**. 44/44 blocked, and re-verification passes after restoring the page.

---

## 6. Known Limitations

> Listed honestly:

1. **Unit minutes are declared-basis values, not measured values.** Real minutes per unit only become meaningful after running a full production cycle.
   The current values are derived from industry anchors; once real records overwrite them, the page recalculates automatically.
2. **No real revenue data.** The monetization path gives path criteria, not amounts.
3. **The knowledge table is oriented toward wellness**; entries in the disease direction were stripped of disease names and symptom pointers at intake,
   so what it supports is "lifestyle advice" rather than "disease management".
4. **The validator is rule matching, not semantic understanding.** It can block known violation patterns,
   but it cannot block entirely new violation phrasings. The word lists therefore need continuous top-up — this is long-term work, not a one-off.
5. **Single-operator execution, with no multi-agent concurrency validation.** The concurrency-conflict mechanism in the contract layer is a design,
   but in practice only the single-operator scenario has been run.
