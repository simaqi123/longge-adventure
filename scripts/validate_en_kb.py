#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Validator for the English knowledge table.

Two jobs:

1. Apply the English red lines to the English table.  The Chinese validator
   blocks Chinese efficacy wording; this blocks the English equivalents —
   and the English equivalents are the ones that matter internationally,
   because the FTC reads English health claims strictly and the FDA treats
   many herbal substances as drugs rather than supplements.

2. Cross-check the English table against the Chinese one.  Both tables are
   supposed to describe the same 205 entries with the same IDs and the same
   theme distribution.  If they drift apart, the "English edition" stops being
   an edition and starts being a different dataset.

Usage:
    python scripts/validate_en_kb.py
    python scripts/validate_en_kb.py data/wellness_kb.en.csv
"""

import csv
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import DATA_DIR, SSOT_CSV  # noqa: E402

EN_CSV = os.path.join(DATA_DIR, "wellness_kb.en.csv")

EN_FIELDS = [
    "ID", "Theme", "Entry", "Constitutions", "SolarTerms", "KeyPoints",
    "Source", "Ingredients", "Programs", "EvidenceLevel", "Notes",
]

VALID_LEVELS_EN = {"Measured", "Derived", "Estimated"}

# ── English red lines ───────────────────────────────────────────
# Therapeutic claims.  Blocked outright in the KeyPoints column.
EFFICACY_CLAIMS_EN = [
    "cure", "cures", "cured", "heal", "heals", "healing",
    "treat", "treats", "treating", "treatment",
    "therapeutic", "remedy", "remedies",
    "diagnose", "diagnosis", "prescription", "prescribe",
    "guaranteed", "guarantee", "guarantees",
    "prevents disease", "reverses", "cures cancer",
    "detox", "detoxify", "detoxifying",
    "boosts immunity", "improve immunity", "immune boosting",
    "anti-inflammatory", "relieves fatigue", "improves sleep",
    "lowers blood pressure", "reduces cholesterol", "regulates blood sugar",
    "weight loss", "anti-aging", "longevity",
    "shrinks tumor", "anti-cancer", "anticancer",
    "anti tumour", "anti tumor", "boosts your metabolism",
]

# Disease names.  A disease name in a wellness table reads as an indication,
# which is exactly what the red lines are there to prevent.
DISEASE_NAMES_EN = [
    "cancer", "tumour", "tumor", "leukaemia", "leukemia", "lymphoma",
    "stroke", "diabetes", "hypertension", "thyroid", "carcinoma",
    "atherosclerosis", "arrhythmia", "asthma", "bronchitis", "pneumonia",
    "ulcer", "gastritis", "hepatitis", "cirrhosis", "renal failure",
    "kidney failure", "heart failure", "myocardial infarction",
    "breast cancer", "colon cancer", "lung cancer", "gastric cancer",
    "gallstone", "gallstones", "cholesterol", "uric acid", "anaemia",
    "anemia", "cholangitis", "hyperlipidaemia", "hyperlipidemia",
]

# Restricted audiences — a wellness service may not be targeted at these.
SPECIFIC_POPULATION_EN = [
    "pregnant", "pregnancy", "postpartum", "post-partum", "breastfeeding",
    "infant", "infants", "babies", "newborn", "post-surgery", "post surgery",
    "post-operative", "postoperative", "chemotherapy", "radiotherapy",
    "dialysis", "transplant", "cancer patient", "cancer patients",
    "ICU patient", "ICU patients", "in recovery",
]

# Consultation solicitation — a wellness companion may not invite diagnosis.
DIAGNOSTIC_PROBES_EN = [
    "what symptoms", "what are your symptoms", "describe your symptoms",
    "open a prescription", "write a prescription", "can you diagnose",
    "book a consultation", "come in for a check-up", "bring your records",
    "how serious is it", "is it a disease",
]

# Negation context: a sentence that forbids or disclaims is not a claim.
NEGATION_EN = [
    "no ", "not ", "never ", "cannot ", "can not ", "must not ", "mustn't ",
    "does not ", "doesn't ", "do not ", "don't ", "without ", "avoid ",
    "avoiding", "prohibit", "prohibited", "may not ", "mayn't ",
    "is not ", "isn't ", "are not ", "aren't ", "neither ", "nor ",
    "rather than ", "instead of ", "never ", "nothing ",
]


def _hits_by_sentence(text, terms):
    """Terms found in a sentence that does NOT contain a negation marker.

    Word-boundary matching matters here: "retreat" contains "treat", and
    "heat therapy" / "food therapy" are legitimate descriptions of a
    non-clinical service, not therapeutic claims.
    """
    found = set()
    for sentence in re.split(r"[.;!?\n]", (text or "").lower()):
        if any(neg in sentence for neg in NEGATION_EN):
            continue
        for term in terms:
            if re.search(r"\b" + re.escape(term.lower()) + r"\b", sentence):
                found.add(term)
    return sorted(found)


def validate_english_table(path):
    errors, warns, stats = [], [], {"rows": 0, "themes": {}}

    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return (["表头为空或无法解析"], [], stats)

        missing = [c for c in EN_FIELDS if c not in reader.fieldnames]
        if missing:
            errors.append(f"缺少必需列: {', '.join(missing)}")

        required = ["ID", "Theme", "Entry", "KeyPoints", "Source", "EvidenceLevel"]

        for i, row in enumerate(reader, start=2):
            stats["rows"] += 1
            line = f"row {i}"
            theme = (row.get("Theme") or "").strip()
            if theme:
                stats["themes"][theme] = stats["themes"].get(theme, 0) + 1

            for c in required:
                if c in row and not (row.get(c) or "").strip():
                    errors.append(f"{line}: required field '{c}' is empty")

            level = (row.get("EvidenceLevel") or "").strip()
            if level and level not in VALID_LEVELS_EN:
                errors.append(
                    f"{line}: 'EvidenceLevel' = '{level}' not in {sorted(VALID_LEVELS_EN)}")

            points = (row.get("KeyPoints") or "").strip()
            entry = (row.get("Entry") or "").strip()
            is_meta = theme == "Boundaries"

            if not is_meta:
                hit = _hits_by_sentence(points, EFFICACY_CLAIMS_EN)
                if hit:
                    errors.append(
                        f"{line}: 'KeyPoints' contains therapeutic wording {hit}")
                hit = _hits_by_sentence(points, DISEASE_NAMES_EN)
                if hit:
                    errors.append(
                        f"{line}: 'KeyPoints' contains a disease name {hit} "
                        f"— reads as an indication")
                hit = _hits_by_sentence(entry, DISEASE_NAMES_EN)
                if hit:
                    errors.append(
                        f"{line}: 'Entry' contains a disease name {hit}")
                hit = _hits_by_sentence(points, SPECIFIC_POPULATION_EN)
                if hit:
                    errors.append(
                        f"{line}: 'KeyPoints' targets a restricted audience {hit}")
                hit = _hits_by_sentence(points, DIAGNOSTIC_PROBES_EN)
                if hit:
                    errors.append(
                        f"{line}: 'KeyPoints' solicits a consultation {hit}")

            # the source column must be a public, verifiable reference
            src = (row.get("Source") or "").strip()
            if src and not (
                src.startswith("Huangdi Neijing")
                or src.startswith("Regulation on")
                or src.startswith("Measures for")
                or src.startswith("Standard for")
                or src.startswith("Non-clinical")
                or src.startswith("Private wellness corpus")
            ):
                warns.append(f"{line}: 'Source' = '{src[:50]}' is not a known public source")

    return errors, warns, stats


def cross_check(en_path, cn_path):
    """The English table must mirror the Chinese one row for row."""
    errors = []
    with open(en_path, encoding="utf-8-sig", newline="") as f:
        en = list(csv.DictReader(f))
    with open(cn_path, encoding="utf-8-sig", newline="") as f:
        cn = list(csv.DictReader(f))

    if len(en) != len(cn):
        errors.append(
            f"row count differs: en={len(en)} cn={len(cn)} — the two tables must mirror each other")
    if [r["ID"] for r in en] != [r["ID"] for r in cn]:
        errors.append("ID sequence differs between the English and Chinese tables")

    from collections import Counter
    en_themes = Counter(r["Theme"] for r in en)
    cn_themes = Counter(r["主题"] for r in cn)
    if len(en_themes) != len(cn_themes):
        errors.append(f"theme count differs: en={len(en_themes)} cn={len(cn_themes)}")
    return errors, en_themes, cn_themes


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else EN_CSV
    if not os.path.exists(path):
        print(f"[跳过] {path} 不存在")
        return

    print(f"=== English knowledge table · {path} ===")
    errors, warns, stats = validate_english_table(path)
    print(f"  rows      : {stats['rows']}")
    print(f"  themes    : {stats['themes']}")

    cross_errors, en_themes, cn_themes = cross_check(path, SSOT_CSV)
    errors.extend(cross_errors)
    print(f"  mirror cn : en themes={dict(en_themes)}")
    print(f"              cn themes={dict(cn_themes)}")

    if warns:
        print(f"\n  警告 {len(warns)} 条：")
        for w in warns[:15]:
            print(f"    {w}")

    if errors:
        print(f"\n❌ 错误 {len(errors)} 条：")
        for e in errors[:25]:
            print(f"    {e}")
        sys.exit(1)

    print("\n✅ 全部通过。")


if __name__ == "__main__":
    main()
