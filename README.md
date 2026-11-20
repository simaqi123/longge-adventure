# Longge Adventure

> **The operating system for a one-person company.**
> A complete, runnable, verifiable **AI agent workflow** for running a solo
> content business as a **one-person company** — from a single source of truth
> to a survival map that tells you where the money comes from, where you are
> stuck, and when to stop.
>
> **Build in public.** MIT licensed, zero dependencies.

[中文版 README](README.zh-CN.md) · [Docs](docs/en/) · [Live demo](web/solo-wellness-map.en.html)

**Long Ge (张伟 / "Longge")** · [@simaqi123](https://github.com/simaqi123) · MIT

---

## Why this exists

Most personal projects don't fail because of laziness. They fail because nobody
can answer three questions:

1. **Where does the money come from?**
2. **What is actually blocking me?**
3. **When should I stop?**

This repository turns those three questions into a page you can look at — and,
more importantly, into a pipeline you can run, validate and break on purpose.

| What you think you're doing | What you're actually doing |
|---|---|
| Making content | Running 10 role slots, each with its own material pool, process chain and bottleneck marker |
| Looking for topics | Material is allocated mutually exclusively — Σ exclusive material ≡ SSOT entry count, exactly |
| Grinding out posts | The process chain expands step by step, and any step eating more than 25% of your minutes is flagged red |
| Wondering about income | A three-link monetization path: content brings people in → private channel retains them → subscription collects cash |

The map is the picture. The thing underneath it is the point: a generator, four
validators and an injection test suite, where every number on the page traces
back to a specific row in the data layer — and where a validator blocks the
build if you break it.

---

## What's in the box

| | |
|---|---|
| **205** | knowledge entries across 8 themes, 24 solar terms fully covered, every entry with a citation |
| **10** | independent role slots, each with a process chain and a unit-economics model |
| **4** | validators (structure, metrics, compliance, English red lines) |
| **44/44** | injection tests blocked — deliberately corrupted pages, all caught |
| **0** | third-party dependencies. Python 3.8+ standard library only |
| **1 file** | each output is a single self-contained HTML you open offline |

The knowledge table is a **knowledge base** with a strict contract: one writer,
every row cited, every row screened. The survival map is a
**one-person company dashboard** — it runs entirely on your own machine,
**self-hosted**, with no account, no server and no network access at runtime.

---

## Quick start

```bash
git clone https://github.com/simaqi123/longge-adventure.git
cd longge-adventure

# 1. Validate the source table (expect 0 errors)
python scripts/validate_ssot.py data/养生知识表.csv

# 2. Build the English knowledge table
python scripts/build_en_kb.py

# 3. Build the survival map → web/solo-wellness-map.en.html (open offline)
python scripts/build_en_map.py

# 4. Build the Chinese survival map → web/养生一人公司生存地图.html
python scripts/build_survival_map.py

# 5. Run every validator
python scripts/validate_survival_map.py
python scripts/validate_deep_model.py
python scripts/validate_en_kb.py

# 6. Injection tests: corrupt the page on purpose, confirm the validator catches it (44/44)
python scripts/test_survival_map_injection.py

# 7. Pre-release leak scan
python scripts/leak_scan.py
```

No pip install, no build step, no Node. Every generated page is a **single
self-contained HTML file with zero external dependencies** — double-click it
and it works offline.

**Fork it to your own account** (create an empty repo first):

```bash
bash scripts/push_to_github.sh https://github.com/<your-account>/<repo-name>.git
```

The script runs the full validation suite first and aborts if anything fails —
it will never push a half-broken state.

> **Want the operating model template kit?** The role-slot design sheet, the
> process-chain sheet, the 90-day roadmap and the monetization gate sheet — the
> files I actually fill in. Open an issue titled
> **"Claim the operating model template kit"**: it asks for an email and one
> question about how you make money right now. No newsletter vendor, no signup
> wall.
>
> Questions and adaptations go to [Discussions](https://github.com/simaqi123/longge-adventure/discussions)
> — *Q&A*, *Show and tell* and *Announcements*. Show-and-tell posts from
> people adapting this to their own niche are the most useful thing that can
> happen in that repo, so please post them.

---

## Three structural invariants

This is the foundation. You may change the code; breaking these three is a bug,
not a preference.

**① `Σ exclusive material ≡ SSOT entry count`**
Each theme belongs to **exactly one** primary role slot. The others list it in a
shared pool and do not occupy area. An earlier version broke this: the ten slots
summed to 569 while the table held 205 entries — the same material counted 2.8
times over, which destroys the treemap and makes "bigger block = bigger slot"
unreadable.

**② One area metric, and only one: monthly output pieces**
Mixing "number of material entries" with "number of pieces produced" produces a
map whose blocks cannot be compared. The metric is now derived from the residual
minutes left after automation, so every slot speaks the same unit and can be
recomputed. Material count survives as a separate, named metric.

**③ Exactly one cash outlet**
When off-premise delivery was discontinued, the map briefly had **no path to
revenue at all** — which is not an acceptable answer for a survival map. The
structure is now fixed at **6 material slots + 3 output slots + 1 cash outlet =
10 role slots**, and a validator enforces that there is exactly one.

---

## Numbers carry their own provenance

Every figure on the page declares which tier it belongs to. A number that does
not declare itself does not go on the page.

| Tier | Meaning | Example |
|---|---|---|
| **Verifiable** | Read live from the source table, recountable by you | 205 material entries · 24/24 solar-term coverage · tooling ratio |
| **Declared basis** | Derived from industry anchors, **not measured**, and overwritable by real records | per-step minutes · effective-output factor 0.55 · 25% bottleneck threshold |
| **Not modelled** | Explicitly out of scope | revenue · conversion rates · cost forecasts |

The effective-output factor of 0.55 is the one that matters most. A one-person
company does not spend all its time making content — there is multi-platform
distribution, formatting adaptation, comment and DM replies, review and topic
adjustment, material replenishment, tool maintenance, and plain state
fluctuation. A single process chain is roughly 55% of working time. **Without
that deduction, the capacity you compute is meaningfully higher than what you
can actually deliver** — the first version claimed "48 pieces per week".

There are no revenue numbers in the simulator. Without real pricing, conversion
and renewal data, any income projection is fiction. The validators block
"projected monthly income", "guaranteed earnings", and any wording that
presents declared minutes as measured ones.

---

## The compliance cliff, and why the code handles it

If you copy a generic "daily brief + topic selection + funnel" playbook into a
wellness or health niche, you will trip a wire. The relevant rule (Measures for
the Administration of Internet Advertising, Article 8) says that a page
introducing health and wellness knowledge **must not also carry** the operator's
address, contact details, or shopping links.

So the structure here is **separation, not disclaimer**:

```
Education content (blog / video / social)
    └── pure knowledge: no contact details, no purchase links, no "message me"
              ↓
Private channel (newsletter / community)
    └── the conversion context lives here, and what is published here is
        characterised as a service introduction, not as education
              ↓
Off-premise delivery — discontinued, and no longer a delivery path
```

These boundaries are **in the validators**, not in a paragraph asking you to
remember them:

- `validate_ssot.py` — a **compliance validator** covering 10 rule families:
  banned medical wording, efficacy claims, restricted audiences, consultation
  solicitation, invasive techniques, prescription-only material
- `validate_constitution_html.py` — 16 scans on the result page: phone numbers,
  handles, external links, QR codes, scan-to-add prompts — none allowed
- `validate_en_kb.py` — the English red lines: therapeutic claims, disease
  names, restricted audiences, consultation solicitation, with negation-context
  handling so that a *prohibition* is not mistaken for a *claim*
- `test_survival_map_injection.py` — 44 injection cases that corrupt the page
  on purpose and confirm the validators catch it

**Compliance in this repository is executable, not decorative.**

Full red-line list: [`docs/en/compliance-handbook.md`](docs/en/compliance-handbook.md).

---

## The English edition, and why it is not a full translation

`data/wellness_kb.en.csv` mirrors the Chinese table row for row — same 205 IDs,
same theme distribution, same structure — and the validator enforces that the
two stay aligned.

But it is deliberately **not** a machine translation of all 205 entries:

- **91 entries are fully translated**: the 24 solar terms, the nine-constitution
  framework — the **TCM constitution** types are named and cross-referenced —
  the classical texts with chapter-and-quote citations into the Huangdi
  Neijing, the five compliance boundary clauses, the self-reflection
  questions, and the non-clinical service entries. These carry the verifiable
  public standards, and an English reader can check them.
- **114 entries are structured templates**: daily routine and food-based
  wellness. They carry the *shape* of a good entry plus instructions on how to
  write one — because you supply your own subject matter.

The reason is compliance, not laziness. The FTC reads English health claims
strictly, and the FDA treats many herbs as drugs rather than supplements.
A clumsy translation of "养心安神" into "calms the spirit and nourishes the
heart" is precisely the kind of implied therapeutic claim that draws
regulatory attention — the English version would be *more* exposed than the
Chinese one. So disease names were stripped from the source column in both
editions, and the English table is screened by its own red-line validator.

Full explanation: [`docs/en/data-guide.md`](docs/en/data-guide.md).

---

## The monetization path

Off-premise delivery was discontinued, so that path no longer exists. What
remains is the only route to cash in the model:

```
1. Content layer      → public slots carry acquisition and trust, charge nothing
2. Retention layer    → the daily brief turns attention into a relationship
                        you can reach again tomorrow
3. Cash outlet        → the subscription converts a long companionship into
                        paid benefits
```

Each link has a gate that decides whether it is actually working:

| Layer | Gate |
|---|---|
| Public content | Four consecutive weeks at the planned rhythm, every piece carrying a citation and a disclaimer |
| Private retention | A measurable share of self-assessment users enter the brief subscription and leave a constitution record |
| Cash outlet | Renewal intent is recorded, not just one-off purchases |

**There is no revenue projection anywhere in this repository.** The gates are
the mechanism; the numbers come from your own records.

---

## 90-day roadmap

| Phase | Goal | Gate |
|---|---|---|
| 1 · Days 1–30 | Make the material trustworthy | SSOT validation at 0 errors and 0 warnings; any entry traceable to its source in 30 seconds |
| 2 · Days 31–60 | Move repetition into scripts | For one slot, only expression and judgment remain manual; bottleneck under 25% of per-piece minutes |
| 3 · Days 61–90 | Close the loop | Four consecutive weeks at the planned rhythm, every output carrying a citation and a disclaimer |
| 4 · Days 91–180 | Collect cash | All three links have four consecutive weeks of real records, and renewal intent is measurable |

---

## Reusing this for a different niche

The architecture is generic; wellness is just the first subject that ran end
to end.

| Layer | What you change |
|---|---|
| Data | Your own SSOT table (field spec in [`docs/en/contract-layer.md`](docs/en/contract-layer.md)) |
| Roles | `ROLES` and `THEME_OWNER` in `survival_map_data.py` |
| Execution | `TOOL_EVIDENCE` — point it at your own scripts |
| Compliance | Your industry's red-line word list and validators |

`THEME_OWNER` is the one place that needs thought: it is what makes the area
metric conserve. When you add a slot, decide first which of your themes it
owns, then make sure the identity `Σ exclusive material ≡ SSOT entry count`
still holds. The validator watches it for you.

---

## Repository layout

```
longge-adventure/
├── data/                       Single source of truth (SSOT)
│   ├── 养生知识表.csv            205 entries, 24 solar terms, 11 fields, cited
│   ├── wellness_kb.en.csv       English mirror — 91 translated, 114 templates
│   ├── 食药清单.json             Officially listed food-and-medicine substances
│   └── 节气经典_出处对照表.md      Quote-level cross-reference for the classics
├── scripts/                    Generation and validation pipeline
│   ├── paths.py                Single path resolution
│   ├── survival_map_data.py    Role definitions + theme ownership + allocation
│   ├── survival_deep_model.py  Process chains + minute basis + roadmap + risks
│   ├── build_survival_map.py   Chinese survival map generator
│   ├── build_en_map.py         English survival map generator
│   ├── build_en_kb.py          English knowledge table generator
│   ├── build_daily_brief.py    Daily brief generator
│   ├── build_constitution_test.py  Constitution self-assessment generator
│   ├── sanitize_for_public.py  Public-release sanitiser (self-checking)
│   ├── leak_scan.py            Pre-release leak scanner
│   ├── i18n_en.py              English locale for the data layer
│   └── validate_*.py           Validators + injection tests
├── web/                        Shipped artifacts (single file, offline)
│   ├── 养生一人公司生存地图.html
│   ├── solo-wellness-map.en.html
│   └── 体质自测.html
├── docs/en/                    English documentation (see below)
├── output/                     Generated artifacts (daily briefs)
├── AGENTS.md                   Project conventions for AI coding assistants
└── scripts/sim_engine.js       Business simulator (inlined into the HTML)
```

**For AI assistants**: open the repository root in Codex, Claude Code or
WorkBuddy and read [`AGENTS.md`](AGENTS.md) — it documents the directory
responsibilities, the change workflow and the three invariants.

**CI**: `.github/workflows/validate.yml` runs every validator plus the leak
scan on each push, and checks that the files in `web/` match a fresh rebuild.
If someone hand-edits a generated file, CI catches it.

---

## Documentation

English:

- [`docs/en/contract-layer.md`](docs/en/contract-layer.md) — the contract, the
  SSOT registration rule, who may write what
- [`docs/en/operating-model-notes.md`](docs/en/operating-model-notes.md) —
  every metric on the page, what it means and what it does not mean
- [`docs/en/data-guide.md`](docs/en/data-guide.md) — table structure, the
  English edition strategy, sanitisation rules
- [`docs/en/compliance-handbook.md`](docs/en/compliance-handbook.md) — the full
  red-line list, with the English wording substitutions
- [`docs/en/launch-kit.md`](docs/en/launch-kit.md) — launch and conversion
  playbook: SEO keyword map, social copy, funnel mechanics

Chinese: [`docs/`](docs/) — same content, original wording.

---

## License and disclaimer

**Code**: MIT — see [`LICENSE`](LICENSE).

**Knowledge table**: `data/养生知识表.csv` and `data/wellness_kb.en.csv` are the
public-release versions. They are sanitised — institution names, prices,
internal corpus structure, local paths and disease names in the source column
are removed. The sanitisation rules live in `scripts/sanitize_for_public.py`,
which self-checks and refuses to write a file if anything leaks. **The original
corpus is not in this repository and is not part of the public release.**

**Disclaimer**: this project produces wellness-oriented lifestyle information.
It is not medical advice, not a diagnosis, and not a treatment opinion. All
content follows the red lines of the Chinese wellness-services regulation and
the advertising rules it references. If you feel unwell, please consult a
qualified healthcare professional.

**Content is not for diagnosis or treatment** — that is a design constraint
enforced by the validators, not a disclaimer bolted on at the end.

---

## Contact

- GitHub: [@simaqi123](https://github.com/simaqi123)
- Working notes and the full Chinese edition: <https://www.workbuddy.cn/space/d/dWypMY8Cs3xhRhKP5BgyaQ>

---

<div align="center">

**Longge Adventure** · One person, one company, one verifiable system

</div>
