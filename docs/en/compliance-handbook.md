# Compliance Boundary Handbook

> Legal basis: Interim Provisions on TCM Health Preservation Services (Trial), Guo Zhong Yi Jie He Fa [2023] No. 3
> Advertising Law of the People's Republic of China, Articles 16, 17, 18, 19
> Internet Advertising Measures (SAMR Order No. 72), Articles 7, 8
>
> **This handbook is a mandatory filter. Every piece of external copy must pass it before publication.**
> Every row below corresponds to a code rule in `scripts/validate_ssot.py` and `scripts/validate_constitution_html.py`.
>
> The Chinese-language source of this document is `docs/合规边界手册.md`. This English edition is the
> version that governs English-language output; where the two differ in wording, the stricter reading wins.

---

## 0. The positioning this document protects

> **We sell operating systems, not medical advice.**

This repository is an operating system for a one-person company. The wellness material is the
worked example, not the product. The product is the pipeline, the invariants, and the validators.

The commercial positioning and the compliance boundary are the same decision:

- We sell **structure** (how a single operator allocates material, sequences work, and routes money).
- We never sell **outcomes** (no cure, no treatment, no efficacy promise, no diagnosis).
- Everything below exists so that the second statement stays true no matter how the copy is written,
  who writes it, and which market it ships into.

**A disclaimer does not legalize a violation.** Copy that trips a red line is a defect, regardless of
what footer sits under it. The validator treats a disclaimer as an independent dimension: it can
never offset a hit in the body.

---

## 1. Two lines must be separated first: wellness (non-medical) vs medical practice

The legal boundary between these two is a **hard wall**, not a gradient.

| | Medical Institution | Non-diagnostic Wellness Service |
|---|---|---|
| Basis | TCM Law; Regulations on Medical Institutions | Interim Provisions on TCM Health Preservation Services (Trial) |
| May perform acupuncture | Yes (licensed physician required) | Absolutely prohibited |
| May write prescriptions | Yes | Absolutely prohibited |
| May advertise treatment | Requires Medical Advertising Review Certificate | Absolutely prohibited |
| May perform cupping / tuina / moxibustion | Yes | Yes (non-invasive) |
| May administer oral Chinese medicinal decoction pieces | Yes (by prescription) | Limited to the food-medicine / health-food substance lists |

### Prohibited list for non-diagnostic services (Article 5, implemented row by row)

| # | Prohibited behaviour | How it is enforced |
|---|---|---|
| 1 | Acupuncture, scar moxibustion, blistering moxibustion, traction, manipulation (ban fa), minimally invasive TCM techniques, TCM herbal enemas | `FORBIDDEN_PROJECTS` scan over the "Related Programs" field |
| 2 | Writing a prescription for medicine | `FORBIDDEN_TERMS` contains prescribe / prescription / doctor's orders |
| 3 | Oral administration of decoction pieces not on the "Substances Both Food and Medicine" or "Substances Usable in Health Food" lists | `PRESCRIPTION_HERBS` + item-by-item verification against `data/食药清单.json` |
| 4 | Conducting medical qigong | Manual review + terminology review |
| 5 | Any other diagnostic or treatment activity | Manual re-check by the validator operator |

> Moxibustion must be split: **gentle / suspended / warm moxibustion (thermal stimulation, non-invasive) is compliant**;
> **scar moxibustion and blistering moxibustion (both break the skin) are prohibited**.
> Descriptions of thermal services must avoid clinical vocabulary such as "dispel dampness and cold"
> or "activate blood and resolve stasis" (see Section 2).

---

## 2. Efficacy and functional-claim red lines (Advertising Law, Articles 17, 18)

### Absolutely prohibited expressions

| Category | Prohibited term examples | Validator word list |
|---|---|---|
| Disease treatment | treat / cure / eradicate / prevent-and-treat hypertension and diabetes, specialty treatment of cervical spondylosis, treats tumours, prevents and fights cancer | `FORBIDDEN_TERMS` |
| Medical behaviour | anti-inflammatory, sterilises, detoxifies, dispels dampness, repairs damaged cells, regulates the endocrine system | `FORBIDDEN_TERMS` |
| Medical concepts easily confused with something else | food-medicine homology (when used to promote ordinary food), TCM conditioning (in non-medical or drug advertising), acupoint therapy | `FORBIDDEN_TERMS` |
| Common but non-compliant TCM vocabulary | unblock the meridians, dispel dampness and cold, activate blood and resolve stasis, nourish yin and supplement yang, cure with ancient methods | `FORBIDDEN_TERMS` + `EFFICACY_CLAIMS` |
| Absolute superlatives | national level, highest grade, best, top grade, finest, number one brand, ancestral secret formula, the only | Manual review |
| Guaranteed efficacy | no side effects at all, guaranteed to work, guaranteed results, results in one session | `FORBIDDEN_TERMS` |
| Expert endorsement | Using the name or likeness of an expert, physician, pharmacist or patient as recommendation evidence | Manual review |

### Permitted substitution table

| What you mean | Not allowed | Allowed |
|---|---|---|
| Thermal service eases cold sensitivity | dispel dampness and cold, dispel cold and relieve pain | warming relaxation, warm-nourishment body feel, seasonal solar-term care |
| Massage eases soreness | treat cervical spondylosis, relax tendons and unblock collaterals to relieve pain | everyday ease, post-sitting relaxation, post-exercise muscle relaxation |
| Constitution assessment | diagnose sub-health, treat by pattern differentiation | constitution tendency assessment, wellness suggestions |
| Sleep routine | treat insomnia, improve severe insomnia | routine and sleep-cadence suggestions, calming food-based sleep support |
| Meridians | unblock the meridians (in the treatment sense) | acupoint self-massage, surface body-zone orientation |

> Principle: **say only "what is done" and "what is felt", never "what disease is treated" and "how well it works".**

### Efficacy-claim term list (`EFFICACY_CLAIMS`, 52 items)

The list below is the English reading of the machine-enforced word list. The enforced strings themselves
live in Chinese in `scripts/validate_ssot.py`, because the knowledge table that this pipeline consumes is
Chinese-language. For English-language copy, treat every entry below as a phrase to avoid.

`calms the spirit and settles the heart` `settles the spirit` `clears and moistens, nourishes yin` `nourishes yin`
`strengthens the spleen and nourishes the stomach` `strengthens the spleen` `strengthens the spleen and drains dampness`
`moves qi and transforms phlegm` `transforms phlegm` `dissipates nodules` `clears the liver and brightens the eyes`
`clears the liver` `moistens the lungs and relieves cough` `moistens the lungs` `moves blood and dispels stasis`
`moves blood` `regulates menstruation` `moves qi` `gently tonifies qi and blood` `warmly tonifies qi and blood`
`augments qi and nourishes blood` `tonifies qi` `courses the liver and moves qi` `moves qi and harmonizes the stomach`
`clears damp-heat` `transforms dampness` `generates fluids` `nourishes the stomach` `clears heat and benefits the gallbladder`
`disperses dampness` `drains dampness` `promotes urination and reduces swelling` `lowers blood pressure`
`lowers blood lipids` `transforms phlegm and relieves cough` `warms the kidneys and supports yang` `warms yang`
`supports yang` `enriches yin` `strengthens yang` `warms the channels` `unblocks the collaterals` `detoxifies`
`strengthens immunity` `raises immunity` `promotes digestion` `improves sleep` `relieves fatigue` `antioxidant`
`lowers the three highs (blood pressure, lipids, glucose)` `softens blood vessels` `stimulates appetite and aids digestion`
`digests food stagnation` `relieves cough and transforms phlegm` `relieves wheezing`

---

## 3. Special limits on internet publishing (Internet Advertising Measures, Article 8 + Advertising Law, Article 19)

This is the rule that the wellness vertical trips most often, and the one that almost nobody notices.

> **Original text:** "It is prohibited to publish, in disguised form, advertisements for medical services,
> drugs, medical devices, health food, or food for special medical purposes by introducing health and
> wellness knowledge. Where health and wellness knowledge is introduced, the **address, contact
> information, or purchase links** of the relevant operator of medical services, drugs, medical devices,
> health food, or food for special medical purposes **must not appear on the same page or at the same time**."

### Practical consequences

| Content form | Compliant |
|---|---|
| A WeChat article on insomnia food therapy with a WeChat ID in the footer | Violation |
| A WeChat Channels video about wellness with a shopping link on the same screen | Violation |
| A wellness article whose footer says "more examples in the comments" | Compliant |
| A standalone **service introduction page** (listing programs and prices) | Compliant (not mixed into a science post on the same page) |
| A wellness explainer with a **non-transactional** account card in the footer (no link, no purchase entry) | Grey area, depends on whether it constitutes disguised advertising |

### Structural fix: physically separate education from conversion

```
Science content (public account / short-video channel / lifestyle app)
    └── pure knowledge: no contact details, no purchase links, no "add me to ask"
              ↓
Private-channel retention (chat group / paid community)
    └── conversion happens here, but group content is characterised as a
        "service introduction", not as science content
              ↓
Offline delivery (discontinued, no longer a delivery path)
```

### Machine-enforced list (self-assessment result page, 16 categories)

Enforced by `scripts/validate_constitution_html.py`.

| Category | Matching shape |
|---|---|
| Mobile phone number | `1[3-9]\d{9}` |
| Landline number | `\d{3,4}-\d{7,8}` |
| WeChat handle | WeChat / VX / vx / weixin keyword + 4 or more account characters |
| QQ number | QQ / qq keyword + 5 or more digits |
| Contact detail field | phone / mobile / contact / contact address keyword + colon |
| QR-scan prompt | scan / QR code / scan it / long-press to recognise |
| Social account field | WeChat / official account / mini program / Douyin / Xiaohongshu / Channels / WeCom keyword + colon |
| http(s) external link | `https?://` |
| www external link | `www\.` |
| Suspected domain | `*.com/*.cn/*.net/*.org/*.top/*.xyz/*.cc` |
| Email link | `mailto:` |
| Phone link | `tel:` |
| Hyperlink tag | `<a href=...>` |
| QR code | the literal word "QR code" |
| Private-domain solicitation | add me / chat me privately / scan / join the group |
| Purchase solicitation | buy / place an order / pay / discount price |

> **Hard red line: the result page of the self-assessment must carry no contact details, no external
> links, no QR codes, no scan prompts, and no purchase path of any kind.** Not in the footer, not in
> a comment, not in a data attribute. This is asserted by the validator, not by reviewer discipline.

---

## 4. Special risks of metaphysical and fate-calculation content

Content in the "destiny-luck / birth-data care" style has its own risk profile when published alongside
TCM wellness material:

| Risk point | Explanation | Disposition |
|---|---|---|
| Superstition orientation | If fate content claims to predict illness, lifespan or wealth | Strictly prohibit predictions, certainties, and guaranteed outcomes |
| Conflation with efficacy | Stating a fate-calculation conclusion as a medical diagnosis | Must separate "wellness reference" from "medical diagnosis" |
| Data collection | Collecting birth-date-and-time data is personal information and constitutes sensitive inference | Purpose must be disclosed; no automatic retention |
| Platform rules | Lifestyle and short-video platforms throttle superstition content heavily | Fate content must not be the main line of the account |

### Dual-chain structure

| Chain | Positioning | Content | Monetisation |
|---|---|---|---|
| **TCM wellness chain** (primary) | Professional, medically backed | constitution, pattern reading, food therapy, solar terms, external therapy | membership subscription + consultations |
| **Fate and luck chain** (secondary) | Cultural experience, emotional value | five movements and six qi, routine suggestions, constitution tendencies | paid community subscription |

**Key point**: the fate chain only produces "routine cadence suggestions and constitution tendency
reference" and **must never appear in the same frame as an efficacy promise**. A birth-data care
result must never be presented as a reason to come in for treatment of a specific condition.

---

## 5. Pre-publication self-check list (every piece of copy must pass)

```
[ ] Any claim of a disease treatment function?        -> yes -> delete
[ ] Any prohibited clinical vocabulary?                -> yes -> substitute
[ ] Any absolute superlative or efficacy guarantee?    -> yes -> delete
[ ] Any expert / physician / patient likeness endorsement? -> yes -> delete
[ ] Any contact detail or purchase link on a science page? -> yes -> move to private channel or offline
[ ] Is every ingredient in the food recipe on the food-medicine / health-food list?
                                                     -> unsure -> drop the recipe or generalise to general dietary advice
[ ] Does any program involve an invasive technique (acupuncture / thread embedding / blistering moxibustion)?
                                                     -> yes -> move to the medical institution channel
[ ] Is any fate-calculation conclusion stated as a diagnosis or prediction? -> yes -> rewrite as a reference suggestion
[ ] Any implication that "this product or program is required for health"? -> yes -> delete
[ ] Any restricted-audience claim (pregnancy / postpartum / infants / post-operative / rehabilitation)?
                                                     -> yes -> rewrite in general terms
```

---

## 6. Disclaimer templates

A disclaimer is a supporting statement. It never substitutes for compliant body copy.

**Short form (result page footer, self-assessment)**

```
This tool is for wellness reference only and does not replace medical diagnosis.
If you feel unwell, please consult a qualified healthcare professional.
```

**Long form (article or video description)**

```
The content on this page is general lifestyle information about daily routines and
seasonal habits. It is not medical advice, not a diagnosis, and not treatment guidance.
It does not claim to prevent, treat, cure, or manage any disease. If you are unwell,
please consult a qualified healthcare professional. Where a claim would require clinical
substantiation we do not make it at all - we describe the practice, not the outcome.
```

**Repository-level disclaimer**

```
The outputs of this project are wellness-oriented lifestyle suggestions, not medical
diagnoses, and do not constitute any clinical opinion. All content follows the red lines
of the Interim Provisions on TCM Health Preservation Services (Trial) and the Advertising
Law. If you feel unwell, please seek care at a licensed medical institution.

Content is not intended for diagnosis or treatment - this is a design constraint, not a
disclaimer.
```

---

## 7. Citation sources

| Provision | Source |
|---|---|
| Prohibited practices for wellness services (Articles 5, 6) | Interim Provisions on TCM Health Preservation Services (Trial), Guo Zhong Yi Jie He Fa [2023] No. 3 |
| Prohibition of clinical vocabulary (Article 17) | Advertising Law of the People's Republic of China |
| Health food advertising (Article 18) | Advertising Law of the People's Republic of China |
| Prohibition of disguised advertising (Article 8) | Internet Advertising Measures, SAMR Order No. 72 |
| Science content must not carry contact details (Article 19) | Advertising Law of the People's Republic of China |
| Food-medicine substance lists | Four National Health Commission announcement batches, see `data/食药清单.json` |

---

## Appendix: methodology source and differences in this vertical

The "one-person company survival map" structure of this project borrows from a publicly shared
one-person-company content methodology. What can be carried over:

| Practice | Can it be carried over | Explanation |
|---|---|---|
| Daily brief card + topic engine | Yes | The skeleton is generic |
| Distributing content to multiple platforms | Yes | The form must be adjusted per platform rules |
| Daily brief in a private group | Yes | Group content is not a "science page" |
| Membership card / live course | Yes | In-group content is characterised as a "service introduction" |
| Daily brief carrying a guidance script + prompt to add WeChat | No | Wellness science content must not carry contact details |
| Long-form WeChat article with real data | Partly | Allowed, but must be de-medicalised and de-efficacy |
| Short-video wellness with a shopping link on screen | No | A shopping link must not appear on the same screen |
| Free tool (self-assessment) as a lead magnet | Partly | The result page must carry no purchase entry and no contact details, enforced by the validator |
