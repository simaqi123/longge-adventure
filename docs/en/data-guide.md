# Data Guide · Wellness Knowledge Table

> `data/养生知识表.csv` — SSOT (single source of truth), 205 entries, 11 fields.
> This document explains the table structure, the measurement basis, and the sanitization process.

---

## 1. Table Structure

| Column | Required | Description |
|---|---|---|
| `ID` | ✅ | Stable identifier `W-001` ~ `W-205`, never recycled once assigned, never reordered |
| `主题` | ✅ | 8 categories: `食养` / `体质` / `起居` / `节气` / `经典` / `自省` / `边界` / `项目` |
| `条目名` | ✅ | Entry title, **must not contain a disease name** |
| `适用体质` | | Comma-separated constitution tendencies, or `ALL` |
| `适用节气` | | Solar term name, or `ALL` |
| `内容要点` | ✅ | Entry body text, **must be de-medicalized, free of symptom indications and efficacy claims** |
| `出处` | ✅ | Traceable source, see section 3 |
| `食材清单` | | `食材名(归属标签)` separated by commas; if none, fill in `无` |
| `关联项目` | | Related non-diagnostic service; if none, fill in `无` |
| `数据级别` | ✅ | Exactly one of `实测` / `推算` / `估算` |
| `备注` | | Processing notes, ingredient basis, boundary basis |

### Theme Distribution

| Theme | Count | Description |
|---|---|---|
| `食养` | 79 | Everyday meals, by far the largest material consumer |
| `体质` | 37 | Tuning directions for the nine constitution types |
| `起居` | 35 | Daily routine and everyday rhythms |
| `节气` | 19 | Seasonal routine (full coverage of the 24 solar terms) |
| `自省` | 12 | One question a day, on mood and routine |
| `经典` | 10 | Quotations from the Huangdi Neijing, each with its own source |
| `项目` | 8 | Suitability tendencies plus compliance boundaries for non-diagnostic services |
| `边界` | 5 | The compliance red-line entries themselves |

---

## 2. Three Write Rules

### 2.1 `内容要点` Must Be De-medicalized

The following are forbidden in `内容要点`:

- Disease-treatment wording (`治疗` / `根治` / `治愈` / `专治` / `防治`)
- Medical-procedure wording (`消炎` / `杀菌` / `排毒` / `祛湿` / `活血化瘀` / `滋阴补阳` / `疏通经络`)
- Efficacy claims (`养心安神` / `健脾` / `补气` / `降压` / `增强免疫` … 52 items in total)
- Specific-population restrictions (`孕产` / `术后` / `婴幼儿` / `康复期` / `化疗` / `放疗` …)
- Consultation lures (`哪里不舒服` / `什么症状` / `开方` / `帮我诊` …)

**Rule**: state only what to do and what you might feel, never what disease it treats or how effective it is.

### 2.2 `出处` Must Be Traceable

A source comes in exactly one of three forms:

| Form | Example | Publicly verifiable |
|---|---|---|
| Classical text quotation | `《素问·四气调神大论篇第二》：「春三月，此谓发陈……」` | ✅ Verifiable |
| Public standard / regulation | `《中医九种体质》标准`, `中医养生保健服务规范(试行)` | ✅ Verifiable |
| Topic-level material | `慢病主题资料·慢病合集` | ⚠️ Internal material. Cites the corpus as a whole; no disease is named |

**An empty source is not allowed, and neither is `NONE`.**

### 2.3 `食材清单` Must Carry an Attribution Tag

Every ingredient must carry a real attribution tag, consistent with `data/食药清单.json`:

| Tag | Meaning |
|---|---|
| `食药清单内` | Listed in the National Health Commission's "List of Items Both Food and Medicine" |
| `保健食品级` | Listed in the "List of Items Usable in Health Food" |
| `普通食品` | Ordinary food explicitly named in an announcement |
| `普通食材` | Everyday crops / livestock / aquatic products / seasonings |

**A false attribution is rejected by the validator.** In addition:

- Substances an announcement explicitly designates as "not ordinary food" must never be used as ingredients on any channel
- The 6 substances restricted to use only as spices and seasonings must not be used as primary ingredients, and must carry the `·仅限香辛料` qualifier
- Prescription-only medicinal materials (`柴胡` / `黄芩` / `附子` / `麻黄` / `桂枝` / `大黄` / `半夏` / `细辛` …) must never appear

---

## 3. Sanitization

What this repository publishes is the **public release version**. The original corpus and the internal structure **are not in the repository and are not within public scope**.

### 3.1 What Was Processed

| Category | Processing |
|---|---|
| Institution names | Replaced with neutral wording such as `非诊疗类养生服务机构` |
| Pricing information | Removed entirely |
| Commercial wording (price list / membership card) | Replaced with neutral wording such as `服务项目清单 / 服务套餐` |
| Internal paragraph numbering (the private corpus' own segment ids) | Normalised to a topic-level label |
| Private corpus file names | Normalised to `慢病主题资料·慢病合集`. **Disease names are dropped entirely** — a disease name in a citation column reads as an indication, which is exactly what the red lines forbid. The public table cites the corpus as a whole, not a disease segment |
| Service names carrying internal commercial tone | Normalized to `温热灸服务 / 砭石温敷服务 / 全身推拿服务 / 拔罐服务 / 养生咨询服务` |
| Local paths, cross-project information | Cleared entirely |

### 3.2 What Was Preserved

- **Entry count conserved**: 205 entries, not one fewer and not one more. The downstream survival map's area metric depends on this number
- **Field structure**: all 11 fields preserved in full
- **Theme distribution**: the 8-category distribution is unchanged
- **Publicly verifiable sources**: classical quotations, public standards, and public regulations kept verbatim
- **Ingredient attribution tags**: kept entry by entry, so they can be cross-checked against `食药清单.json`

### 3.3 The Sanitizer Is Part of the Repository

`scripts/sanitize_for_public.py` is not just a one-off script — it **carries its own leak self-check**:

```bash
python scripts/sanitize_for_public.py --in your-table.csv --out data/养生知识表.csv
```

The pipeline:

1. Field-level replacement (institution / pricing / commercial wording / internal numbering / private file names)
2. **Entry count conservation assertion** — sanitization never changes the number of entries
3. **Leak self-check** — 15 regex classes plus a source whitelist, scanned in both directions
4. **Abort without writing the file if the self-check fails**

This design is deliberate: **the public version must be script-generated, not hand-edited**.
Manual sanitization cannot guarantee repeatability, nor prove that nothing leaked.

---

## 4. How to Change This Table

1. Edit `data/养生知识表.csv` (this is the SSOT, the only write point)
2. `python scripts/validate_ssot.py data/养生知识表.csv` → must be 0 errors
3. `python scripts/build_survival_map.py` → rebuild the survival map
4. `python scripts/validate_survival_map.py` → numbers match the SSOT item by item
5. `python scripts/validate_deep_model.py` → bidirectional verification between page and data layer
6. `python scripts/test_survival_map_injection.py` → 44/44 blocked

**Consequence of skipping step 2**: the page will show numbers that disagree with the data layer, and the validator will block it.

---

## 5. Solar Terms and Classical Sources

`data/节气经典_出处对照表.md` provides a line-by-line quotation cross-reference, with full coverage of the 24 solar terms.

Sources for `节气` entries come from the seasonal ordinances in 《素问·四气调神大论篇第二》.
Sources for `经典` entries come from the chapter titles and original sentences across 《素问》 and 《灵枢》.

**Chapter titles and original sentences must be compared character by character**, never paraphrased from memory — this is what Contract A demands of the Classical Text Scholar role slot, and it is also why that slot has the lowest tooling ratio (source verification is purely manual).
