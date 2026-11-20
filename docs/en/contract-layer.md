# Contract Layer · Four Non-Negotiable Foundations

> This layer is the foundation of the whole system. **The code may change; the contract must not break.**
> Any write operation that violates this document is a defect, not a workaround.

---

## Contract A · SSOT Registry (Single Source of Truth Registry)

> Core principle: **every data file has exactly one writer; all other roles are read-only.**
> This is the only foundation that lets multiple AI employees run in parallel without conflicts.

### Master Registry Table

| ID | SSOT File | Sole Writer | Read-Only Roles | Prohibitions |
|---|---|---|---|---|
| SSOT-01 | `data/养生知识表.csv` | Data Officer | Content Officer / Orchestrator / Engineering Delivery Officer | No role may hand-edit it; the "Content Key Points" column must not carry symptom indications or efficacy claims |
| SSOT-02 | `data/食药清单.json` | Data Officer | Content Officer / Orchestrator | List sources must be traceable to a National Health Commission announcement batch |
| SSOT-03 | `data/节气经典_出处对照表.md` | Classic-Text Scholar | All | Chapter titles and original sentences must be compared verbatim; paraphrase from memory is not allowed |

### Two Write Rules

1. **Sole writer**: only the role registered in the table may write it. If another role needs a change, go through "raise a request → the Data Officer writes it",
   and do not touch the file yourself. When two people edit one table at the same time, one of the edits is guaranteed to be overwritten.
2. **No tier skipping**: unregistered intermediate tables, temporary tables, and "just log it here for now" are forbidden.
   All data lands in the SSOT exactly once; everywhere else is a projection of it.

### Why This Is Necessary

A one-person company (one-person company / solo operator) most often dies by its own hand: think of an idea, open a new table;
three months later there are 12 tables, every number differs, and nobody can say which one is real.
The SSOT registry cuts those 12 tables back down to 1.

---

## Contract B · Authority Boundaries (Every Role Declares What It Does Not Own)

> Core mechanism — **write responsibility boundaries into prohibitions**.
> Every role must explicitly declare what it does not do. **Omitting the declaration = defaulting to overreach.**

### Role Boundary Table

**Data Officer (sole writer)**
- ✅ Owns: landing upstream raw data into the SSOT table; maintaining fields; tagging the data level; reporting data anomalies
- ❌ **Does not own**: writing body copy, writing conclusions, writing recommendations, making trend judgments, choosing topics
- ❌ Forbidden: substituting industry averages for missing measured values; letting "roughly" or "should be" into a data column

**Content Officer (topic selection and final drafts)**
- ✅ Owns: selecting materials from the SSOT; writing body copy and headlines; rewriting to match each platform's tone; attaching a source to every piece
- ❌ **Does not own**: modifying SSOT tables, adding new entries, deciding data levels
- ❌ Forbidden: publishing without a source; citing "derived"-level data as "measured"-level data

**Compliance Officer (red-line gatekeeper)**
- ✅ Owns: maintaining the banned-word list; scanning before publication; blocking non-compliant copy; issuing compliance records
- ❌ **Does not own**: rewriting body copy to "get around" its own rules
- ❌ Forbidden: publishing first and reviewing afterwards; using a disclaimer to excuse violations in the body (see below)

**Orchestrator (assignment and acceptance)**
- ✅ Owns: breaking down requirements, assigning work, accepting deliverables, arbitrating conflicts
- ❌ **Does not own**: writing the deliverable itself; accepting its own work
- ❌ Forbidden: skipping acceptance and publishing directly

**Engineering Delivery Officer (tooling and pipeline)**
- ✅ Owns: writing generators, validators, injection tests; keeping the numbers on the page consistent with the data layer
- ❌ **Does not own**: changing SSOT content; making topic judgments on behalf of the Content Officer
- ❌ Forbidden: writing a declared-basis value into the page as if it were a measured value

### The Exemption Boundary of Disclaimers (one easy-to-get-wrong rule)

A disclaimer **cannot** be used to exempt violations in the body.

- ❌ Wrong: "This issue's content is for reference only and does not constitute medical advice" + the body contains "treats hypertension" → **still a violation**
- ✅ Correct: the body itself contains no violating wording; the disclaimer is only a supplementary note

The validator therefore treats the disclaimer as an **independent dimension**: no disclaimer may ever offset a body-text hit.
Only entries whose theme is "Boundary" (entries that themselves state a prohibited rule) enjoy the meta-discourse exemption.

---

## Contract C · Three-Tier Rule Precipitation

> Core mechanism — **corrections must be tiered, so that a one-off preference is never promoted into a global iron rule**.
> This is the layer most often overlooked, yet the one that most affects long-term stability.

### Tier Definitions

| Tier | Meaning | Storage | Validity | Example |
|---|---|---|---|---|
| **Case-specific preference** | One-off taste, temporary choice, special requirement of a single task | Within the conversation | One-off | "Use short sentences for the headline this time" |
| **Local rule** | Long-term agreement of one project or one business line | That project's `MEMORY.md` | Project-level | "The data layer is physically isolated; never mix tables" |
| **Global rule** | Hard constraint that holds across projects | User-level `MEMORY.md` | Long-term | "Entries without a source must not be written" |

### Promotion Threshold

| From | To | Requirement |
|---|---|---|
| Case-specific preference | Local rule | **The same kind of feedback repeats ≥3 times**, with the same reason each time |
| Local rule | Global rule | Proven effective in **at least two different projects** |

**Promoting without meeting the threshold = a local preference contaminating global rules.**
This is the most common failure in AI collaboration: an accidental preference gets written into a global rule,
and three months later it starts affecting a completely unrelated business line, with nobody remembering where it came from.

### Demotion and Expiry

- A global rule proven false in two projects is automatically demoted to a local rule
- A local rule not triggered for 90 days is marked "pending review" rather than deleted outright
- Every rule must be able to answer: "When was this rule last in effect?"

---

## Contract D · Security Review for External Skill Intake (7 checks)

> Any Skill or script obtained from GitHub, a plugin marketplace, or someone else's share **must pass this table before intake**.
> Tiers: low risk = may be ingested; medium risk = ingest but note the trigger boundary; high risk = must be sandboxed, trial-run, and manually confirmed.

### Checklist

- [ ] **1. Sensitive directories**: does not touch `~/.ssh/`, `~/.aws/`, `~/.gnupg/`, key files, browser profiles
- [ ] **2. Credential reads**: does not read other credentials under the home directory (`.env`, `credentials`, `token`)
- [ ] **3. Config changes**: does not modify MCP connector configuration or local toolchain configuration
- [ ] **4. Network behavior**: whether external request targets are explicit, and whether data is reported
- [ ] **5. Write scope**: whether it writes to directories outside the workspace; whether delete operations have a confirmation mechanism
- [ ] **6. Prompt injection**: whether it contains text such as "ignore previous instructions"; whether it reads untrusted content and splices it into instructions
- [ ] **7. Dependency sources**: whether it pulls in packages from unknown origins; whether versions are pinned

### Tiered Handling

| Tier | Determination | Handling |
|---|---|---|
| Low risk | All 7 checks pass | May be ingested directly |
| Medium risk | Involves write operations or network access, but the targets are explicit | Ingest + note the trigger boundary in the file header |
| High risk | Touches sensitive directories / credentials / prompt injection | **Usable only after a sandboxed trial run + manual confirmation** |

### This Repository's Own Practice

All scripts in this repository follow:
- read-only on `data/`, write-only on `web/` and `output/`, never touching directories outside the repository
- zero third-party dependencies; runs on the Python standard library
- no network requests
- run `scripts/test_survival_map_injection.py` before every release (44 cases)

---

## How Contracts Are Enforced

Contracts are not enforced by people remembering them; they are enforced by machines:

| Contract | Enforced by | Trigger |
|---|---|---|
| A · SSOT | `validate_ssot.py` | Before data is consumed |
| B · Authority boundaries | `validate_ssot.py` + `validate_constitution_html.py` | On every draft |
| C · Three-tier rules | Human + `MEMORY.md` archiving | When a correction arrives |
| D · Intake review | `scripts/` directory review | When an external script is introduced |

**The cost of violating a contract is explicit: the validator does not pass → the artifact does not ship.**
