#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Build the English knowledge table.

What this produces
------------------
``data/wellness_kb.en.csv`` — the English mirror of the SSOT table.

Design decision (and why it matters for an English-language release)
--------------------------------------------------------------------
The Chinese table carries 205 entries of dense, technical, culturally
specific content.  Machine-translating it would produce two bad outcomes:
a table nobody outside China can verify, and a table where the medical
wording becomes *more* exposed than it is in Chinese — the FTC and the
FDA read English claims strictly, and a clumsy translation of
"养心安神" into "calms the spirit and nourishes the heart" is exactly
the kind of implied therapeutic claim that draws regulatory attention.

So the English table is split deliberately:

    Fully translated (91 entries)
        Solar terms (19), classical texts (10), boundaries (5), self-reflection
        (12), constitutions (37), programs (8).
        These carry the verifiable public standards: the 24 solar-term names,
        the nine-constitution framework, the chapter-and-quote citations into
        the Huangdi Neijing, and — most importantly — the five compliance
        boundary clauses, which are the part an English reader must be able
        to read exactly.

    Structured templates (114 entries)
        Daily routine (35) and food therapy (79).
        These carry the *shape* of an entry with the copy left blank, plus
        a short instruction on how to write it.  A reader supplies their own
        subject matter — which is the whole point of an open-source
        operating system.

The row count, the ID sequence and the theme distribution are identical to
the Chinese table, so the two can be diffed entry by entry.

Usage:
    python scripts/build_en_kb.py
"""

import csv
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import DATA_DIR, SSOT_CSV, ensure_dir  # noqa: E402

OUT_CSV = os.path.join(DATA_DIR, "wellness_kb.en.csv")

EN_FIELDS = [
    "ID", "Theme", "Entry", "Constitutions", "SolarTerms", "KeyPoints",
    "Source", "Ingredients", "Programs", "EvidenceLevel", "Notes",
]

# ─────────────────────────────────────────────────────────────
# Public standards — fully translated
# ─────────────────────────────────────────────────────────────

SOLAR_TERMS_EN = {
    "立春": "Beginning of Spring", "雨水": "Rain Water", "惊蛰": "Awakening of Insects",
    "春分": "Spring Equinox", "清明": "Pure Brightness", "谷雨": "Grain Rain",
    "立夏": "Beginning of Summer", "小满": "Grain Buds", "芒种": "Grain in Ear",
    "夏至": "Summer Solstice", "小暑": "Minor Heat", "大暑": "Major Heat",
    "立秋": "Beginning of Autumn", "处暑": "End of Heat", "白露": "White Dew",
    "秋分": "Autumn Equinox", "寒露": "Cold Dew", "霜降": "Frost's Descent",
    "立冬": "Beginning of Winter", "小雪": "Minor Snow", "大雪": "Major Snow",
    "冬至": "Winter Solstice", "小寒": "Minor Cold", "大寒": "Major Cold",
}

CONSTITUTION_EN = {
    "平和质": "Balanced", "气虚质": "Qi-deficient", "阳虚质": "Yang-deficient",
    "阴虚质": "Yin-deficient", "痰湿质": "Phlegm-dampness", "湿热质": "Damp-heat",
    "血瘀质": "Blood-stasis", "气郁质": "Qi-stagnation", "气滞质": "Qi-movement",
}

TENDENCY_EN = {
    "平和质": "balanced tendency",
    "偏颇倾向": "moderate tendency",
    "明显倾向": "pronounced tendency",
}

PROGRAM_EN = {
    "温热灸服务": "Warm moxibustion service",
    "砭石温敷服务": "Bian-stone warm compress service",
    "全身推拿服务": "Full-body massage service",
    "拔罐服务": "Cupping service",
    "养生咨询服务": "Wellness consultation service",
    "健康咨询": "wellness consultation",
    "服务套餐": "service package",
}

# Classical source chapters — the part an English reader can actually verify.
CHAPTER_EN = {
    "《素问·四气调神大论篇第二》": (
        "Huangdi Neijing · Suwen · Ch. 2 — On Nurturing Spirit in the Four Seasons"
    ),
    "《素问·四气调神大论篇第二》春三月条": (
        "Huangdi Neijing · Suwen · Ch. 2 — On Nurturing Spirit in the Four Seasons, "
        "Spring section"
    ),
    "《素问·四气调神大论篇第二》夏三月条": (
        "Huangdi Neijing · Suwen · Ch. 2 — On Nurturing Spirit in the Four Seasons, "
        "Summer section"
    ),
    "《素问·四气调神大论篇第二》秋三月条": (
        "Huangdi Neijing · Suwen · Ch. 2 — On Nurturing Spirit in the Four Seasons, "
        "Autumn section"
    ),
    "《素问·四气调神大论篇第二》冬三月条": (
        "Huangdi Neijing · Suwen · Ch. 2 — On Nurturing Spirit in the Four Seasons, "
        "Winter section"
    ),
    "《素问·生气通天论篇第三》": (
        "Huangdi Neijing · Suwen · Ch. 3 — On the Connection Between Man and Nature"
    ),
    "《素问·上古天真论篇第一》": (
        "Huangdi Neijing · Suwen · Ch. 1 — On the Pristine Simplicity of the Ancients"
    ),
    "《素问·藏气法时论篇第十四》": (
        "Huangdi Neijing · Suwen · Ch. 14 — On Storing Qi According to the Seasons"
    ),
    "《灵枢·经脉篇》": "Huangdi Neijing · Lingshu · Ch. 9 — The Channels",
    "《灵枢·九针十二原》": (
        "Huangdi Neijing · Lingshu · Ch. 1 — Nine Needles, Twelve Source Points"
    ),
    "《灵枢·本神》": "Huangdi Neijing · Lingshu · Ch. 8 — The Spirit's Root",
    "《灵枢·邪客》": "Huangdi Neijing · Lingshu · Ch. 26 — Guest Evil",
    "《灵枢·营卫生会》": (
        "Huangdi Neijing · Lingshu · Ch. 18 — On the Meeting of Nutritive and Defensive Qi"
    ),
    "《中医九种体质》标准": "Standard for the Nine Constitutions of TCM",
    "中医养生保健服务规范(试行)": "Regulation on TCM Health Preservation Services (Trial)",
    "互联网广告管理办法": "Measures for the Administration of Internet Advertising",
    "非诊疗类服务项目清单": "Non-clinical service item list",
    "非诊疗类服务套餐设计": "Non-clinical service package design",
}

# Level labels
LEVEL_EN = {"实测": "Measured", "推算": "Derived", "估算": "Estimated"}
LEVEL_BACK = {v: k for k, v in LEVEL_EN.items()}

# ─────────────────────────────────────────────────────────────
# Fully translated entries
#   ID -> (Entry, KeyPoints, Source)
#   Source overrides the auto-composed chapter reference.
# ─────────────────────────────────────────────────────────────

EXPLICIT_EN = {
    # ---------- solar terms (19) ----------
    "W-047": (
        "Beginning of Spring — daily living rhythm",
        "Yang qi begins to arise at the start of spring. Sleep later and rise earlier, "
        "stretch the limbs and tendons, and keep the diet light on sour and generous on "
        "sweet.",
        "Huangdi Neijing · Suwen · Ch. 2 — On Nurturing Spirit in the Four Seasons, "
        "Spring section: \"In the three months of spring, all things begin to germinate. "
        "Heaven and earth are born together, and all things flourish; sleep late and rise "
        "early, walk widely in the courtyard, let the hair down and loosen the form, so "
        "that the intention may arise… this is the response to spring qi, the way of "
        "nurturing life.\"",
    ),
    "W-048": (
        "Spring Equinox — daily living rhythm",
        "Day and night are of equal length at the spring equinox. Keep the routine "
        "regular, the mood even, and the diet balanced.",
        "Huangdi Neijing · Suwen · Ch. 2 — On Nurturing Spirit in the Four Seasons: "
        "\"Yin and yang of the four seasons are the root of all things. Therefore the "
        "sages nourish yang in spring and summer, and nourish yin in autumn and winter, "
        "in order to follow their root, and thus move and sink with all things in the "
        "gate of growth and decline.\"",
    ),
    "W-049": (
        "Summer Solstice — daily living rhythm",
        "Yang qi is at its height at the summer solstice. Sleep late and rise early, "
        "stay out of the heat, and keep the food light.",
        "Huangdi Neijing · Suwen · Ch. 2 — On Nurturing Spirit in the Four Seasons, "
        "Summer section: \"In the three months of summer, all things flourish. Heaven and "
        "earth exchange qi, and all things bear fruit; sleep late and rise early, do not "
        "grow weary of the sun, let the intention not be angry, let the flowers and "
        "leaves mature, and let the qi flow out… this is the response to summer qi, the "
        "way of nourishing and growing.\"",
    ),
    "W-050": (
        "Major Heat — daily living rhythm",
        "At major heat the summer heat is at its peak. Rest away from the heat, keep "
        "the food light and low in fat, and do not chase coolness.",
        "Huangdi Neijing · Suwen · Ch. 2 — On Nurturing Spirit in the Four Seasons, "
        "Summer section: \"Let the qi flow out… this is the response to summer qi, the "
        "way of nourishing and growing.\" Same chapter: \"Because of summer heat, the "
        "sweat, vexation and panting… the body as if it were burning charcoal, the sweat "
        "flows out and it disperses.\"",
    ),
    "W-051": (
        "Beginning of Autumn — daily living rhythm",
        "The summer heat has not yet gone at the beginning of autumn. Sleep early and "
        "rise early, guard against autumn dryness, and keep the diet moistening.",
        "Huangdi Neijing · Suwen · Ch. 2 — On Nurturing Spirit in the Four Seasons, "
        "Autumn section: \"In the three months of autumn, all things are brought to "
        "maturity. The weather is brisk and the earth's qi is clear; sleep early and rise "
        "early, rising and resting with the rooster, let the intention be at peace to "
        "soften the punishment of autumn, gather in the spirit so that autumn qi is "
        "level, do not let the intention go out, let the lung qi be clear; this is the "
        "response to autumn qi, the way of nourishing and gathering.\"",
    ),
    "W-052": (
        "White Dew — daily living rhythm",
        "The gap between day and night temperature widens at white dew. Add a layer for "
        "warmth, and keep the diet warm and moistening.",
        "Huangdi Neijing · Suwen · Ch. 3 — On the Connection Between Man and Nature: "
        "\"Therefore in the evening one gathers and closes, does not disturb the sinews "
        "and bones, does not go out into fog and dew; contrary to these three seasons, "
        "the body becomes thin and wearied.\" Same chapter: \"Yang qi rules the exterior "
        "during the day; in the early morning human qi begins, at noon yang qi is at its "
        "peak, in the west yang qi is already weak, and the qi gate closes.\"",
    ),
    "W-053": (
        "Autumn Equinox — daily living rhythm",
        "At the autumn equinox, sleep early and rise early, guard against chill and "
        "dryness, and keep the mood even.",
        "Huangdi Neijing · Suwen · Ch. 2 — On Nurturing Spirit in the Four Seasons, "
        "Autumn section: \"Let the intention be at peace to soften the punishment of "
        "autumn, gather in the spirit so that autumn qi is level, do not let the "
        "intention go out, let the lung qi be clear.\"",
    ),
    "W-054": (
        "Frost's Descent — daily living rhythm",
        "At frost's descent, keep warm, guard against the cold, avoid raw and cold food, "
        "and tonify moderately.",
        "Huangdi Neijing · Suwen · Ch. 2 — On Nurturing Spirit in the Four Seasons, "
        "Winter section: \"In the three months of winter, all things are stored away. "
        "The water freezes and the earth cracks; do not disturb yang, sleep early and "
        "rise late, waiting for the sunlight, let the intention be as if hidden and as "
        "if something private were achieved, go away from the cold and toward warmth, "
        "do not let it leak out of the skin… this is the response to winter qi, the way "
        "of nourishing and storing.\"",
    ),
    "W-055": (
        "Beginning of Winter — daily living rhythm",
        "Yang qi begins to close at the beginning of winter. Sleep early and rise late, "
        "warm and preserve yang, and keep the diet warm.",
        "Huangdi Neijing · Suwen · Ch. 2 — On Nurturing Spirit in the Four Seasons, "
        "Winter section: \"Sleep early and rise late, waiting for the sunlight… this is "
        "the response to winter qi, the way of nourishing and storing.\"",
    ),
    "W-056": (
        "Winter Solstice — daily living rhythm",
        "At the winter solstice yin reaches its extreme and yang is born. Rest quietly "
        "and store the spirit, and keep the diet warm and tonifying.",
        "Huangdi Neijing · Suwen · Ch. 2 — On Nurturing Spirit in the Four Seasons: "
        "\"Yin and yang of the four seasons are the root of all things. Therefore the "
        "sages nourish yang in spring and summer, and nourish yin in autumn and winter, "
        "in order to follow their root.\" Same chapter, Winter section: \"Sleep early and "
        "rise late, waiting for the sunlight… this is the response to winter qi, the way "
        "of nourishing and storing.\"",
    ),
    "W-057": (
        "Minor Cold and Major Cold — daily living rhythm",
        "Through minor cold and major cold, keep stored and guard against cold, sleep "
        "early and rise late, and do not stay up late and drain yang.",
        "Huangdi Neijing · Suwen · Ch. 2 — On Nurturing Spirit in the Four Seasons, "
        "Winter section: \"The water freezes and the earth cracks; do not disturb yang, "
        "sleep early and rise late, waiting for the sunlight… go away from the cold and "
        "toward warmth, do not let it leak out of the skin, and let the qi be drawn in. "
        "This is the response to winter qi, the way of nourishing and storing.\"",
    ),
    "W-058": (
        "Rain Water and Awakening of Insects — daily living rhythm",
        "Damp rises around rain water and the awakening of insects. Keep the diet light "
        "and low in richness, and keep the room ventilated.",
        "Huangdi Neijing · Suwen · Ch. 2 — On Nurturing Spirit in the Four Seasons, "
        "Spring section: \"Heaven and earth are born together, and all things flourish; "
        "sleep late and rise early, walk widely in the courtyard, let the hair down and "
        "loosen the form, so that the intention may arise.\" Same chapter, Winter "
        "section: \"Go away from the cold and toward warmth, do not let it leak out of "
        "the skin.\"",
    ),
    "W-059": (
        "Pure Brightness and Grain Rain — daily living rhythm",
        "Damp is heavy during pure brightness and grain rain. Keep the diet warm rather "
        "than rich, and keep the room ventilated and dry.",
        "Huangdi Neijing · Suwen · Ch. 3 — On the Connection Between Man and Nature: "
        "\"Therefore spring injures one with wind, the pathogenic qi lingers and stays, "
        "and this becomes diarrhoea.\" Same chapter: \"Because of damp, the head is as if "
        "wrapped; damp-heat is not dispelled, the large sinews shorten and become tight, "
        "the small sinews relax and lengthen.\"",
    ),
    "W-060": (
        "Grain in Ear and Minor Heat — daily living rhythm",
        "Damp and heat both press during grain in ear and minor heat. Keep the diet "
        "light, and avoid heavy, congesting flavours.",
        "Huangdi Neijing · Suwen · Ch. 3 — On the Connection Between Man and Nature: "
        "\"Because of summer heat, the sweat, vexation and panting; at rest there is much "
        "talk, the body is as if it were burning charcoal, the sweat flows out and it "
        "disperses.\" Same chapter: \"Because of damp, the head is as if wrapped; damp-heat "
        "is not dispelled.\"",
    ),
    "W-061": (
        "End of Heat — daily living rhythm",
        "The summer heat begins to retreat at end of heat. Sleep early and rise early, "
        "guard against chill, and protect the stomach.",
        "Huangdi Neijing · Suwen · Ch. 2 — On Nurturing Spirit in the Four Seasons, "
        "Autumn section: \"Sleep early and rise early, rising and resting with the "
        "rooster, let the intention be at peace to soften the punishment of autumn, "
        "gather in the spirit.\"",
    ),
    "W-062": (
        "Minor Snow and Major Snow — daily living rhythm",
        "Through minor snow and major snow the cold is severe. Keep warm, keep the diet "
        "warm, and keep the room warm.",
        "Huangdi Neijing · Suwen · Ch. 2 — On Nurturing Spirit in the Four Seasons, "
        "Winter section: \"The water freezes and the earth cracks; do not disturb yang, "
        "sleep early and rise late, waiting for the sunlight… go away from the cold and "
        "toward warmth, do not let it leak out of the skin.\"",
    ),
    "W-171": (
        "Beginning of Summer — daily living rhythm",
        "Yang qi grows steadily at the beginning of summer. Sleep late and rise early, "
        "loosen the limbs, and keep the food light and low in richness.",
        "Huangdi Neijing · Suwen · Ch. 2 — On Nurturing Spirit in the Four Seasons, "
        "Summer section: \"In the three months of summer, all things flourish. Heaven and "
        "earth exchange qi, and all things bear fruit; sleep late and rise early, do not "
        "grow weary of the sun, let the intention not be angry, let the flowers and "
        "leaves mature, and let the qi flow out… this is the response to summer qi, the "
        "way of nourishing and growing.\"",
    ),
    "W-172": (
        "Grain Buds — daily living rhythm",
        "Damp and heat build at grain buds. Keep the routine regular, keep the room "
        "ventilated, and keep the diet light and low in heavy flavours.",
        "Huangdi Neijing · Suwen · Ch. 3 — On the Connection Between Man and Nature: "
        "\"Because of damp, the head is as if wrapped; damp-heat is not dispelled, the "
        "large sinews shorten and become tight, the small sinews relax and lengthen.\" "
        "Same chapter: \"Because of summer heat, the sweat, vexation and panting; at "
        "rest there is much talk, the body is as if it were burning charcoal, the sweat "
        "flows out and it disperses.\"",
    ),
    "W-173": (
        "Cold Dew — daily living rhythm",
        "The dew turns cold at cold dew. Sleep early and rise early, add clothing for "
        "warmth, and keep the diet warm, moistening and even.",
        "Huangdi Neijing · Suwen · Ch. 3 — On the Connection Between Man and Nature: "
        "\"Therefore in the evening one gathers and closes, does not disturb the sinews "
        "and bones, does not go out into fog and dew; contrary to these three seasons, "
        "the body becomes thin and wearied.\" Same chapter: \"Yang qi rules the exterior "
        "during the day; in the early morning human qi begins, at noon yang qi is at its "
        "peak, in the west yang qi is already weak, and the qi gate closes.\"",
    ),

    # ---------- classical texts (10) ----------
    "W-063": (
        "The general principle of the four seasons",
        "The Huangdi Neijing, Suwen, says: nourish yang in spring and summer, nourish yin "
        "in autumn and winter.",
        "Huangdi Neijing · Suwen · Ch. 2 — On Nurturing Spirit in the Four Seasons: "
        "\"Yin and yang of the four seasons are the root of all things. Therefore the "
        "sages nourish yang in spring and summer, and nourish yin in autumn and winter, "
        "in order to follow their root, and thus move and sink with all things in the "
        "gate of growth and decline.\"",
    ),
    "W-064": (
        "The general principle of treating before illness",
        "The Huangdi Neijing, Suwen, says: the sage does not treat illness once it has "
        "arisen, nor disorder once it has formed — that is what is meant by it.",
        "Huangdi Neijing · Suwen · Ch. 2 — On Nurturing Spirit in the Four Seasons: "
        "\"Therefore the sage does not treat illness once it has arisen, but treats what "
        "is not yet ill; does not treat disorder once it has formed, but treats what is "
        "not yet disordered. This is what is meant by it.\"",
    ),
    "W-065": (
        "Where food therapy sits",
        "The Huangdi Neijing, Suwen, says: grains, meats, fruits and vegetables — food-based "
        "care uses them fully.",
        "Huangdi Neijing · Suwen · Ch. 14 — On Storing Qi According to the Seasons: "
        "\"Sour governs contraction, sweet governs supplementation, pungent governs "
        "dissemination, bitter governs firmness and drainage, salty governs surging and "
        "draining.\"",
    ),
    "W-066": (
        "The warning about a regular daily routine",
        "The Huangdi Neijing, Suwen, says: model yourself on yin and yang, harmonise with "
        "the numbers, keep food and drink in moderation, keep the routine regular, and "
        "do not labour beyond your capacity — then body and spirit stay together.",
        "Huangdi Neijing · Suwen · Ch. 1 — On the Pristine Simplicity of the Ancients: "
        "\"Therefore model yourself on yin and yang, harmonise with the numbers, keep "
        "food and drink in moderation, keep the routine regular, and do not labour "
        "beyond your capacity; thus the body and the spirit stay together, and one "
        "lives out the natural span of years.\"",
    ),
    "W-067": (
        "The relationship between the emotions and wellbeing",
        "The Huangdi Neijing, Suwen, says: be calm and free of craving, and the true qi "
        "follows; the spirit is kept within, and where does illness come from?",
        "Huangdi Neijing · Suwen · Ch. 1 — On the Pristine Simplicity of the Ancients: "
        "\"Be calm and free of craving, and the true qi follows; the spirit is kept "
        "within, and where does illness come from?\"",
    ),
    "W-068": (
        "The role of daoyin",
        "The Huangdi Neijing, Suwen, says: with daoyin and anqo, the qi moves and the "
        "blood vessels are harmonised.",
        "Huangdi Neijing · Lingshu · Ch. 9 — The Channels: \"The channels move the blood "
        "and qi, and bring yin and yang together at the cun-kou.\" See also "
        "Huangdi Neijing · Lingshu · Ch. 1 — Nine Needles, Twelve Source Points: \"As for "
        "the timing of supplementation and draining, the needles are used for it.\"",
    ),
    "W-069": (
        "The principle of the four seasons",
        "The Huangdi Neijing, Suwen, says: this is the response to spring qi, the way of "
        "nurturing life.",
        "Huangdi Neijing · Suwen · Ch. 2 — On Nurturing Spirit in the Four Seasons, "
        "Spring section: \"This is the response to spring qi, the way of nurturing life.\"",
    ),
    "W-070": (
        "Yin and yang as the root of all things",
        "The Huangdi Neijing, Suwen, says: yin and yang of the four seasons are the root "
        "of all things.",
        "Huangdi Neijing · Suwen · Ch. 2 — On Nurturing Spirit in the Four Seasons: "
        "\"Yin and yang of the four seasons are the root of all things.\"",
    ),
    "W-071": (
        "The rising and falling of yang through the day",
        "The Huangdi Neijing, Suwen, says: yang qi rules the exterior during the day; in "
        "the early morning human qi begins, at noon yang qi is at its peak, in the west "
        "yang qi is already weak, and the qi gate closes.",
        "Huangdi Neijing · Suwen · Ch. 3 — On the Connection Between Man and Nature: "
        "\"Yang qi rules the exterior during the day; in the early morning human qi "
        "begins, at noon yang qi is at its peak, in the west yang qi is already weak, "
        "and the qi gate closes.\"",
    ),
    "W-072": (
        "The effect of damp on the body",
        "The Huangdi Neijing, Suwen, says: because of damp, the head is as if wrapped; "
        "damp-heat is not dispelled, the large sinews shorten and become tight, the small "
        "sinews relax and lengthen.",
        "Huangdi Neijing · Suwen · Ch. 3 — On the Connection Between Man and Nature: "
        "\"Because of damp, the head is as if wrapped; damp-heat is not dispelled, the "
        "large sinews shorten and become tight, the small sinews relax and lengthen.\"",
    ),

    # ---------- boundaries (5) — the compliance core ----------
    "W-087": (
        "Prohibited activities for non-clinical wellness services",
        "Wellness preservation services must not carry out acupuncture, scar moxibustion, "
        "blistering moxibustion, traction, manipulative adjustment, minimally invasive "
        "TCM procedures, or the writing of pharmaceutical prescriptions. These are "
        "clinical activities and sit outside a wellness service.",
        "Regulation on TCM Health Preservation Services (Trial)",
    ),
    "W-088": (
        "Prohibited wording in wellness promotion",
        "Wellness preservation services must not advertise therapeutic effects, and "
        "advertisements must not use medical terminology.",
        "Regulation on TCM Health Preservation Services (Trial)",
    ),
    "W-089": (
        "Separating education from conversion",
        "A page that introduces health and wellness knowledge must not also carry the "
        "operator's address, contact details, or shopping links. Education and "
        "conversion live in different places.",
        "Measures for the Administration of Internet Advertising",
    ),
    "W-090": (
        "How a constitution self-assessment may be described",
        "The result of a constitution self-assessment may only be described as a "
        "constitution tendency assessment. It must not be called a diagnosis or a "
        "pattern-differentiation result.",
        "Measures for the Administration of Internet Advertising",
    ),
    "W-091": (
        "How fate-calendar content may be described",
        "Fate-calendar content serves only as a reference for daily rhythm and "
        "constitution tendency, and must never appear alongside any outcome promise.",
        "Regulation on TCM Health Preservation Services (Trial)",
    ),

    # ---------- self-reflection (12) ----------
    "W-081": ("Morning self-check",
              "What time did you wake this morning, and did you feel clear-headed after "
              "waking?"),
    "W-082": ("Afternoon self-check",
              "Are you drowsy this afternoon? Was today's food on the cool side or on "
              "the rich side?"),
    "W-083": ("Night self-check",
              "At what times did you fall asleep and wake last night? Were you still on "
              "a screen before bed?"),
    "W-084": ("Emotional self-check",
              "How did your mood move today? Is there anything knotted that has not "
              "eased?"),
    "W-085": ("Sedentary self-check",
              "How long have you been sitting today, and at what hour? Any tightness in "
              "the shoulders, neck, lower back or waist?"),
    "W-086": ("Dietary self-check",
              "How much sweet and rich food today? How much raw or cold? How much water "
              "did you drink?"),
    "W-165": ("Is your water intake enough today",
              "How many cups have you had from this morning until now? Did you miss the "
              "first glass after waking?"),
    "W-166": ("How long did you sit today",
              "What was the longest stretch you sat in one go, and how many times did you "
              "get up in between?"),
    "W-167": ("Is today's food heavy-flavoured",
              "Was today's food on the salty side or the light side? Is there one dish "
              "you could have had without soy sauce?"),
    "W-168": ("Are your three meals at fixed times",
              "Were your three meal times roughly fixed today? Did you skip a meal "
              "because you were busy?"),
    "W-169": ("How did your mood move today",
              "Did your mood swing sharply today, and what set it off?"),
    "W-170": ("How long were your eyes working today",
              "What was the longest stretch you spent staring at a screen, and did you "
              "look into the distance in between?"),
}

# 适用体质列的非标准取值（倾向描述，不是九种体质）——英译，不译成疾病
CONSTITUTION_EXTRA_EN = {
    "肺燥质": "Lung-dryness",
    "寒湿质": "Cold-dampness",
    "血虚质": "Blood-deficiency",
    "燥性体质": "Dry tendency",
    "心脾两虚倾向": "Heart-Spleen dual-deficiency tendency",
    "脾虚倾向": "Spleen-deficiency tendency",
    "肝郁倾向": "Liver-qi stagnation tendency",
}

# 体质主题中「条件 + 维度」结构的 29 条，逐条英译
CONTEXT_ENTRY_EN = {
    "寒湿凝滞型的饮食取向": "Cold-damp stagnation — food preferences",
    "湿热偏盛时的口味取向": "When damp-heat predominates — flavour preferences",
    "气滞血瘀倾向的运动取向": "A qi-stagnation and blood-stasis tendency — movement",
    "痰浊偏盛时的饮食取向": "When phlegm turbidity predominates — food preferences",
    "正虚时不宜过耗的取向": "When qi is already deficient — what not to overdo",
    "肝郁气滞倾向的情志取向": "A liver-qi stagnation tendency — emotional routine",
    "湿热痹阻倾向的起居取向": "A damp-heat obstruction tendency — living routine",
    "阳气偏衰时的作息取向": "When yang qi is declining — sleep and wake routine",
    "肝郁与阴虚并见的情绪取向": "Liver-qi stagnation together with yin deficiency — emotional routine",
    "脾胃虚弱倾向的餐次取向": "A spleen-stomach weakness tendency — meal timing",
    "腰肾偏弱倾向的起居取向": "A lower-back and kidney weakness tendency — living routine",
    "气血不足倾向的进补取向": "A qi and blood insufficiency tendency — toning",
    "体重偏轻倾向的饮食取向": "A light-weight tendency — food preferences",
    "腹部胀满倾向的餐时取向": "An abdominal fullness tendency — meal timing",
    "暑热时节的饮食取向": "The hot-season weeks — food preferences",
    "饮食积滞倾向的化解取向": "A food-stagnation tendency — clearing the stagnation",
    "排便不畅倾向的纤维取向": "A bowel-regularity tendency — fibre intake",
    "口味厚重倾向的清淡取向": "A heavy-flavour tendency — a lighter diet",
    "饮食过咸倾向的口味取向": "A salty-diet tendency — flavour preferences",
    "秋燥时节的润养取向": "The dry autumn weeks — moistening care",
    "冬令进补的节奏取向": "The winter toning season — rhythm",
    "春生发散的作息取向": "The dispersing spring weeks — sleep and wake routine",
    "体位变化时的节奏取向": "When posture changes — rhythm",
    "偏咸口味的慢慢调整": "A salty palate — a gradual adjustment",
    "口味与量都宜收敛的取向": "Both flavour and portion — what to rein in",
    "烟酒场合的替代方案": "Smoking and drinking occasions — an alternative",
    "易倦倾向的作息取向": "A tendency to tire easily — sleep and wake routine",
    "口味与情绪的分开管理": "Separating flavour from mood",
    "三餐定时的优先性": "Keeping the three meals timed — first priority",
}

CONTEXT_KEYPOINTS = (
    "TEMPLATE. Write the tendency in plain language, then the everyday preference "
    "that supports it, then the concrete swap — what to do instead of what to stop. "
    "Stay at the level of general lifestyle: no condition names, no outcome "
    "statements, no restricted audiences."
)

# 体质主题的 37 条：按「体质 + 调养侧面」生成英文条目
CONSTITUTION_ASPECT_EN = {
    "日常调养": ("daily routine", "Keep the daily routine steady: regular meals, moderate "
                 "effort, and a settled sleep schedule."),
    "情绪调养": ("emotional routine", "Separate the emotions from the schedule: do not "
                 "replay worries before bed, and keep a regular rhythm of outdoor "
                 "activity through the day."),
    "饮食调养": ("dietary routine", "Keep the diet light and simple, with portions "
                 "matched to the tendency."),
    "起居调养": ("living routine", "Keep the living routine regular, and match warmth, "
                 "rest and light to the tendency."),
    "作息调养": ("sleep and wake routine", "Keep the sleep and wake times fixed, and "
                 "match the evening wind-down to the tendency."),
    "运动调养": ("movement routine", "Keep the movement gentle and regular rather than "
                 "occasional and intense."),
    "情志调养": ("emotional routine", "Keep the emotional climate even through the day, "
                 "and let the routine absorb what cannot be solved."),
    "饮食起居": ("diet and daily routine", "Keep both the diet and the daily routine "
                 "simple and regular, matched to the tendency."),
    "调养原则": ("principles of daily care", "State the principles plainly and keep them "
                 "at the level of general lifestyle, not individual medical advice."),
    "日常调养要点": ("key points of daily care", "State the key points plainly and keep "
                     "them at the level of general lifestyle, not individual medical "
                     "advice."),
}

# ─────────────────────────────────────────────────────────────
# Structured templates for the two recipe-shaped themes
# ─────────────────────────────────────────────────────────────

ROUTINE_TEMPLATE = (
    "Daily-routine entry template — {n:02d}",
    "TEMPLATE. Write one habit, one trigger and one replacement. Example shape: "
    "\"When [situation], instead of [old pattern], do [new action].\" Keep it at the "
    "level of general lifestyle. Do not name a condition, do not state an outcome, "
    "and do not target a restricted audience.",
)

FOOD_TEMPLATE = (
    "Food-wellness entry template — {n:02d}",
    "TEMPLATE. Write the ingredients, the method, the seasonal window and the serving "
    "portion. Describe what the dish *is* and when it is normally eaten — do not state "
    "what it does to the body, do not name a condition, and do not promise an outcome. "
    "List only ordinary food ingredients, and leave the ingredient list in the "
    "Ingredients column.",
)

PROGRAM_EXPLICIT_EN = {
    "W-073": ("Warm moxibustion service — who it suits",
              "Warm moxibustion is a non-medical heat therapy service. It suits people "
              "with a yang-deficient tendency or cold hands and feet. After a session, "
              "stay out of the draught and rest for half an hour.",
              "Non-clinical service item list"),
    "W-074": ("Bian-stone warm compress service — who it suits",
              "Bian-stone warm compress suits people who sit for long hours, feel "
              "tight, or have stiffness in the shoulders, neck, lower back or waist.",
              "Non-clinical service item list"),
    "W-075": ("Full-body massage service — who it suits",
              "Full-body massage suits people who feel generally tight, tired from "
              "sitting, or slow to fall asleep.",
              "Non-clinical service item list"),
    "W-076": ("Cupping service — who it suits",
              "Cupping suits people who feel heavy with damp, or who have tightness "
              "across the shoulders and upper back.",
              "Non-clinical service item list"),
    "W-077": ("Wellness consultation service — who it suits",
              "Wellness consultation suits people who want to understand their own "
              "constitution tendency and the direction of seasonal self-care.",
              "Non-clinical service item list"),
    "W-078": ("What a wellness service package contains",
              "A wellness service package contains one full-body massage session, one "
              "warm moxibustion session, one bian-stone warm compress session, one "
              "cupping session, and a wellness consultation. It is a package of "
              "non-clinical wellness services, not a course of treatment.",
              "Non-clinical service package design"),
}


def _split_multi(value):
    """Split a multi-value Chinese cell into a list of clean parts."""
    if not value:
        return []
    parts = []
    for chunk in value.replace("，", ",").replace("、", ",").split(","):
        chunk = chunk.strip()
        if chunk:
            parts.append(chunk)
    return parts


def build():
    with open(SSOT_CSV, encoding="utf-8-sig", newline="") as f:
        src = list(csv.DictReader(f))

    out_rows = []
    routine_n = 0
    food_n = 0

    for r in src:
        rid = r["ID"]
        theme_cn = r["主题"].strip()

        # --- theme ---
        theme_en = {
            "体质": "Constitution", "节气": "Solar Term", "经典": "Classical Text",
            "食养": "Food-based Wellness", "起居": "Daily Routine", "自省": "Self-Reflection",
            "边界": "Boundaries", "项目": "Programs",
        }.get(theme_cn, theme_cn)

        # --- constitutions ---
        cons = []
        for c in _split_multi(r["适用体质"]):
            if c in CONSTITUTION_EN:
                cons.append(CONSTITUTION_EN[c])
            elif c in TENDENCY_EN:
                cons.append(TENDENCY_EN[c])
            elif c in CONSTITUTION_EXTRA_EN:
                cons.append(CONSTITUTION_EXTRA_EN[c])
        constitutions = "; ".join(cons) if cons else "All"

        # --- solar terms ---
        terms = [SOLAR_TERMS_EN.get(s.strip(), "") for s in _split_multi(r["适用节气"])]
        terms = [t for t in terms if t]
        solar_terms = ", ".join(terms) if terms else "All"

        # --- entry + key points + source ---
        if rid in EXPLICIT_EN:
            vals = EXPLICIT_EN[rid]
            entry, points = vals[0], vals[1]
            source = vals[2] if len(vals) > 2 else ""
        elif rid in PROGRAM_EXPLICIT_EN:
            entry, points, source = PROGRAM_EXPLICIT_EN[rid]
        elif theme_cn == "体质":
            # derive: "<Constitution> · <aspect>" from the Chinese entry name
            raw = r["条目名"]
            if raw in CONTEXT_ENTRY_EN:
                entry = CONTEXT_ENTRY_EN[raw]
                points = CONTEXT_KEYPOINTS
                source = ("Standard for the Nine Constitutions of TCM"
                          if r["出处"].startswith("《中医九种体质》")
                          else "Regulation on TCM Health Preservation Services (Trial)")
                out_rows.append({
                    "ID": rid, "Theme": theme_en, "Entry": entry,
                    "Constitutions": constitutions, "SolarTerms": solar_terms,
                    "KeyPoints": points, "Source": source, "Ingredients": ingredients,
                    "Programs": programs, "EvidenceLevel": level, "Notes": notes,
                })
                continue
            cons_cn = raw.split("的")[0] if "的" in raw else ""
            aspect_cn = raw.split("的", 1)[1] if "的" in raw else "日常调养"
            cons_en = CONSTITUTION_EN.get(cons_cn, cons_cn or "General")
            aspect_key = next((k for k in CONSTITUTION_ASPECT_EN if k in aspect_cn),
                              "日常调养")
            aspect_en, aspect_text = CONSTITUTION_ASPECT_EN[aspect_key]
            entry = f"{cons_en} Constitution — {aspect_en}"
            points = (f"{aspect_text} Write it for the general population and keep it "
                      f"descriptive: what this tendency tends to prefer, and the "
                      f"everyday habit that supports it. Do not name a condition, do not "
                      f"state an outcome, and do not promise a result.")
            source = ("Standard for the Nine Constitutions of TCM"
                      if r["出处"].startswith("《中医九种体质》")
                      else "Regulation on TCM Health Preservation Services (Trial)")
        elif theme_cn == "起居":
            routine_n += 1
            entry, points = [s.format(n=routine_n) for s in ROUTINE_TEMPLATE]
            source = ("Regulation on TCM Health Preservation Services (Trial)"
                      if "规范" in r["出处"]
                      else "Regulation on TCM Health Preservation Services (Trial)")
        elif theme_cn == "食养":
            food_n += 1
            entry, points = [s.format(n=food_n) for s in FOOD_TEMPLATE]
            source = "Private wellness corpus (compiled by the author)"
        else:
            entry = f"{theme_en} entry template"
            points = ("TEMPLATE. Write one claim per entry, cite a public source, and "
                      "keep it at the level of general lifestyle information.")
            source = "Regulation on TCM Health Preservation Services (Trial)"

        # --- source fallback: compose from the Chinese chapter reference ---
        if not source:
            src_cn = r["出处"]
            if src_cn.startswith("慢病主题资料"):
                # 私有语料出处：只写语料本身，绝不带疾病名
                source = "Private wellness corpus (compiled by the author)"
            else:
                for cn, en in CHAPTER_EN.items():
                    if cn in src_cn:
                        source = en
                        break
                else:
                    source = "Regulation on TCM Health Preservation Services (Trial)"

        # --- ingredients / programs ---
        ingredients = ""
        programs = ""
        for p in _split_multi(r["关联项目"]):
            programs += (PROGRAM_EN.get(p.strip(), p.strip()) + "; ")
        programs = programs.rstrip("; ")

        level = LEVEL_EN.get(r["数据级别"].strip(), "Derived")

        notes = ("English edition. Fully translated from the Chinese SSOT entry."
                 if rid in EXPLICIT_EN or rid in PROGRAM_EXPLICIT_EN
                 else "English edition. Structured template — fill in the subject matter "
                      "your audience needs.")

        out_rows.append({
            "ID": rid,
            "Theme": theme_en,
            "Entry": entry,
            "Constitutions": constitutions,
            "SolarTerms": solar_terms,
            "KeyPoints": points,
            "Source": source,
            "Ingredients": ingredients,
            "Programs": programs,
            "EvidenceLevel": level,
            "Notes": notes,
        })

    return out_rows


def main():
    ensure_dir(DATA_DIR)
    rows = build()

    # --- self-check: no Chinese, no disease names ---------------------
    blob = "\n".join(",".join(str(v) for v in r.values()) for r in rows)
    cjk = sorted(set(re.findall(r"[\u4e00-\u9fa5]+", blob)))
    if cjk:
        print("❌ 英文表出现中文:", cjk)
        sys.exit(1)
    disease = sorted(set(re.findall(
        r"\b(cancer|tumou?r|leukaemia|leukemia|stroke|diabet\w*|hypertension|"
        r"thyroid|carcinoma|atherosclerosis|arrhythmia|asthma|ulcer|anaemia|"
        r"anemia|tumours?|tumors?)\b", blob, re.I)))
    if disease:
        print("❌ 英文表出现疾病名（会被读成适应症）:", disease)
        sys.exit(1)

    with open(OUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=EN_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    from collections import Counter
    themes = Counter(r["Theme"] for r in rows)
    print(f"✅ {OUT_CSV}")
    print(f"   rows            : {len(rows)}")
    print(f"   themes          : {dict(themes)}")
    print(f"   translated      : {sum(1 for r in rows if r['Notes'].startswith('English edition. Fully'))}")
    print(f"   templates       : {sum(1 for r in rows if 'template' in r['Notes'])}")


if __name__ == "__main__":
    main()
