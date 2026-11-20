# Launch Kit

> An execution manual for open-sourcing Longge Adventure.
> Repo slug: `longge-adventure` · Public name: **Longge Adventure**
> Author: Zhang Wei / Long Ge · GitHub: `@simaqi123`
>
> Every number in this document is verifiable in the repository. There are no projections of stars,
> users, or revenue anywhere in this file, and there never will be.

---

## 1. Positioning

### One-line value proposition

> **Longge Adventure is an open-source operating system for running a one-person company with AI
> agents — a knowledge table, a validated content pipeline, and a survival map, in one repo you can
> clone and run in three minutes.**

### Who this is for

- Solo developers who want AI agents doing real production work, not chatbot demos.
- People building a one-person company who need to know where the money comes from, where they are
  stuck, and when to stop.
- Practitioners who want their expertise structured into an AI-agent system rather than trapped in
  a head and a notebook.

### Who this is not for

- Anyone looking for medical advice, a diagnosis, or a treatment protocol.
- Anyone looking for a passive-income promise. The repository explicitly refuses to model revenue.
- Anyone who wants a finished audience or audience-growth service. This repo is the machinery, not
  the traffic.

### Why "operating system" and not "health content"

Health content is commodity. Anyone with an LLM can produce a daily wellness post. It does not
survive contact with a platform, it does not compound, and it does not transfer to anyone else.

An operating system does survive contact. It encodes decisions, not content:

| Layer | What it decides | Why it is reusable |
|---|---|---|
| Data layer | One source of truth, one writer per file | Stops the "12 tables, 12 versions of the truth" death |
| Role layer | Which material belongs to which role | Makes capacity legible instead of vibes-based |
| Execution layer | Which step is automated, and where the tool evidence lives | Turns "I work fast" into a checkable claim |
| Compliance layer | What may never be said, enforced by code | Makes the boundary survive a change of author |

The wellness domain is the first sample that runs end to end. The architecture is the product.
> We sell operating systems, not medical advice.

### The four things that make it credible (in priority order)

1. **Three structural invariants that can be falsified.**
   Material conservation (`Σ exclusive material ≡ SSOT row count`), a single area metric
   (monthly output pieces), and exactly one cash outlet. These are checkable, not slogans. The
   previous version of the model violated the first one and the treemap was measuring nothing.
2. **Compliance lives in the validator, not in a document.** 20 content red lines in
   `scripts/validate_ssot.py`, 16 result-page scan categories in
   `scripts/validate_constitution_html.py`, and 44/44 injection tests that deliberately break the
   page and confirm the validators catch it.
3. **Zero third-party dependencies.** Python 3.8+ standard library. Clone, run, done. No
   `pip install`, no lockfile rot, no supply-chain surface.
4. **Numbers are tiered by honesty.** Verifiable / calibration value / not extrapolated. Revenue,
   conversion rate, and cost forecasts are excluded on purpose.

---

## 2. The funnel, stage by stage

```
Reach      GitHub long-tail SEO + X/LinkedIn build-in-public, daily
   ↓
Trust      README readable in three minutes + clone-and-run + green CI + reproducible build
   ↓
Capture    GitHub Discussions subscription (native email notification, zero-cost tooling)
   ↓
Claim     Issue form "Claim the operating model template kit" → user voluntarily leaves an
           email → receives the kit
   ↓
Monetize  Email weekly (build-in-public retro) → paid tiers (template kit / 1v1 operating
           diagnosis / community)
   ↓
Feed back Subscriber-produced cases → become README proof → bring more SEO traffic
```

### Stage 1 — Reach

- **Goal:** put the repo in front of people who are already looking for what it does.
- **Actions:** daily one-post build-in-public on X and LinkedIn; keep every post pointing at one
  file in the repo; let GitHub's own search pick up the long tail.
- **Metrics to watch:** repo impressions and unique visitors per week; X impressions per post;
  LinkedIn post impressions; search-console impressions for the mapped keywords; count of
  inbound links from non-promotional sources.
- **Most common failure mode:** posting a "look what I built" announcement with no reason for a
  stranger to care. Every post must contain one transferable idea, otherwise reach converts to
  nothing.

### Stage 2 — Trust

- **Goal:** a stranger becomes convinced the thing actually runs, in under three minutes.
- **Actions:** keep the three-minute-run block at the top of the README; keep CI green on every
  push; keep the build reproducible so CI can detect hand-edited artifacts; make the invariants
  visible without reading code.
- **Metrics to watch:** clone count; fork count; time from clone to first successful local run
  (watch issues for where people get stuck); number of issues that report a successful run.
- **Most common failure mode:** the README describes a system that does not run. One failed
  `python scripts/build_survival_map.py` costs more trust than a hundred good posts earn.

### Stage 3 — Capture

- **Goal:** convert an interested visitor into a reachable subscriber without any paid tooling.
- **Actions:** use GitHub Discussions, not a mailing-list vendor. Subscribing is a native GitHub
  action with native email notification and zero cost. Ask for it explicitly at the end of every
  build-in-public post.
- **Metrics to watch:** Discussions subscriber count; weekly Discussion posts and replies;
  ratio of subscribers who have ever opened a thread; Questions answered per week.
- **Most common failure mode:** building the email list on infrastructure that costs money before
  there is anything worth subscribing to. Discussions costs nothing and is already where
  developers read.

### Stage 4 — Claim

- **Goal:** turn a subscriber into an identified person who asked for something.
- **Actions:** open one Issue titled "Claim the operating model template kit"; the issue body
  contains a short form; the user fills it in and gets the kit. Consent is explicit and the
  reason for asking is stated.
- **Metrics to watch:** number of form submissions; completion rate (opened the issue vs.
  submitted the form); time from submit to delivery.
- **Most common failure mode:** gating the template kit behind a generic "star the repo" or
  "follow me" request. People comply with a direct request and resist a vague one.

### Stage 5 — Monetize

- **Goal:** a subscriber who already sees weekly value decides to pay for the next level.
- **Actions:** the weekly email is free and is the product demonstration. Paid tiers are the
  operating model template kit, a 1v1 operating diagnosis, and the community for peers doing
  build-in-public retros.
- **Metrics to watch:** email open rate; reply rate; number of paid conversions per month;
  number of subscribers who reply with a result.
- **Most common failure mode:** putting a paywall in front of the weekly retro. The retro is what
  earns the right to sell anything else.

### Stage 6 — Feed back

- **Goal:** turn subscriber outcomes into public proof that attracts the next cohort.
- **Actions:** ask subscribers for a case; publish the case with their permission; add it to the
  README as proof; each case becomes new long-tail search surface.
- **Metrics to watch:** number of published cases; cases referenced from README vs. from the
  newsletter; new subscribers attributed to a case.
- **Most common failure mode:** inventing a success story to fill the section. An empty proof
  section is honest; a fabricated one ends the project.

---

## 3. SEO keyword map

Long-tail English keywords that map to a specific file in the repository. Intent types:
informational (learn), commercial (evaluate a solution), transactional (buy or start something).

| Keyword | Target file | Section / title | Intent |
|---|---|---|---|
| one-person company | `README.md` | What this is | informational |
| solo founder AI stack | `README.md` | Directory structure | informational |
| build in public | `README.md` | Three structural invariants | informational |
| AI agent workflow | `AGENTS.md` | Directory responsibilities | informational |
| content business for solo entrepreneurs | `README.md` | What this is | informational |
| how to structure a knowledge base with AI | `docs/en/data-guide.md` | Source-of-truth table | informational |
| one person company dashboard | `web/solo-wellness-map.en.html` | The map | informational |
| solar term wellness | `web/solo-wellness-map.en.html` | Solar term role | informational |
| TCM constitution type | `data/wellness_kb.en.csv` | Constitution theme, 37 entries | informational |
| self-hosted content pipeline | `README.md` | Three-minute setup | informational |
| validate content compliance script | `scripts/validate_ssot.py` | Red-line word lists | informational |
| injection testing for generated content | `scripts/test_survival_map_injection.py` | Injection cases | informational |
| treemap business model | `web/solo-wellness-map.en.html` | The map | informational |
| compliance validator for AI content | `docs/en/compliance-handbook.md` | Red lines | informational |
| zero dependency python html generator | `scripts/build_en_map.py` | Generator entry | informational |
| single file offline html dashboard | `README.md` | Three-minute setup | informational |
| content pipeline bottleneck analysis | `scripts/survival_deep_model.py` | Process chains | informational |
| sanitize dataset before open sourcing | `scripts/sanitize_for_public.py` | Sanitiser rules | informational |
| 90 day plan solo business | `web/solo-wellness-map.en.html` | 90-day roadmap | informational |
| scan repo for leaked secrets | `scripts/leak_scan.py` | Scan rules | informational |
| MIT licensed AI agent template | `LICENSE` | MIT License | informational |
| source of truth for AI content | `docs/en/contract-layer.md` | Contract A | informational |
| AI content compliance disclaimer | `docs/en/compliance-handbook.md` | Disclaimer templates | informational |
| one-person company operating system | `README.md` | What this is | commercial |
| solo creator monetization system | `README.md` | Monetisation path | commercial |
| AI content operating system template | `docs/en/launch-kit.md` | Conversion mechanics | commercial |
| founder build-in-public launch checklist | `docs/en/launch-kit.md` | Launch assets | commercial |
| content pipeline for a solo creator | `docs/en/data-guide.md` | Pipeline stages | commercial |
| one person company operating kit | `docs/en/launch-kit.md` | Conversion mechanics | transactional |
| 1v1 solo business diagnosis | `docs/en/launch-kit.md` | Conversion mechanics | transactional |
| solo creator build-in-public community | `docs/en/launch-kit.md` | Conversion mechanics | transactional |

> Files whose paths are non-English are the Chinese source of truth; the English editions live under
> `docs/en/`. Keep both, and let the English path be the one search engines are pointed at.

---

## 4. Launch assets

### 4.1 X (Twitter) thread, 10 posts

**Post 1 — launch day**

> Open-sourced the operating system I use to run my one-person company with AI agents.
>
> It's not a content pack. It's a knowledge table, a validated pipeline, and a survival map that
> shows where the work actually goes.
>
> 205 knowledge entries. 24 solar terms covered. 10 roles. 4 validators. Zero third-party
> dependencies, Python 3.8+ standard library.
>
> The thing I'm proudest of: the compliance boundary is a validator, not a disclaimer. 44/44
> injection tests break the page on purpose to prove the validators catch it.
>
> MIT licensed. Clone and run.
>
> Image: the generated survival map treemap, full-bleed, no text overlay.
> Hashtags: #buildinpublic #opensource #solofounder

**Post 2 — demo screenshot day**

> The output is a single HTML file. Double-click it, it opens offline, zero external requests.
>
> Treemap on the left: 10 roles sized by one metric only — monthly output pieces. Not a mixed
> unit. Not an approximation. The area sum reconciles against the knowledge table row count, and
> a validator fails the build if it ever stops doing that.
>
> Earlier version of this model summed to 569 pieces against a 205-row table. The chart was
> measuring the same material 2.8 times over. Now it reconciles.
>
> Image: the treemap plus the process-chain panel, side by side.
> Hashtags: #buildinpublic #dataviz #opensource

**Post 3 — build-in-public day**

> Day 3 of shipping this thing in public.
>
> Today I re-ran the whole pipeline from a clean clone and diffed the generated files against
> what's committed. Empty diff. That's the check that matters most: if someone hand-edits a
> generated artifact, CI fails.
>
> Generated pages are outputs. The data layer is the source. Edit the data, regenerate, let the
> validators argue.
>
> Image: terminal output of the CI validation steps, unedited.
> Hashtags: #buildinpublic #ci #reproduciblebuilds

**Post 4 — technical breakdown day**

> The invariant most people get wrong when they build a "content pipeline" is material allocation.
>
> If two roles both claim the same material, your capacity model double-counts. Mine did. The
> fix was an ownership table: every theme belongs to exactly one role, everything else shares a
> pool. Now Σ exclusive material ≡ SSOT row count, and the validator enforces it on every build.
>
> It's one table. It changes what the chart means.
>
> Image: the ownership table, hand-annotated with the invariant on top.
> Hashtags: #buildinpublic #datamodel #solofounder

**Post 5 — contrarian opinion day**

> Unpopular: most "AI content business" advice is about output volume, and output volume is the
> wrong variable.
>
> If you can't tell me which single step eats 25% of your time, you don't know your business.
> You have a hobby with a publishing schedule.
>
> So I built the model to answer one question: where does the time go? Every role has a process
> chain with per-step time, and one step lights up red when it crosses a quarter of the total.
>
> Cutting the bottleneck is worth more than publishing twice as much.
>
> Image: the bottleneck row highlighted red inside the process-chain panel.
> Hashtags: #buildinpublic #solofounder #productivity

**Post 6 — "I would not recommend this" day**

> If you're a solo creator, I would not start by building an agent system.
>
> Start with one spreadsheet and one rule: write down where the time actually went. Not where you
> planned it. Where it went.
>
> Most of what I built is a way to make that one rule enforceable. The agents, the treemap, the
> validators — they're the enforcement, not the point.
>
> If you can't keep one manual pipeline honest for a month, agents will just hide the mess
> faster.
>
> Image: plain text on a plain background. No chart this time.
> Hashtags: #buildinpublic #solofounder #advice

**Post 7 — tutorial day**

> How to repoint this pipeline at your own domain in about ten minutes.
>
> 1. Replace the knowledge table with your own rows. Keep the field contract — the validator
>    checks the fields, not the topic.
> 2. Edit the role table. Each role needs a theme owner, or material conservation breaks.
> 3. Point the tool evidence at your own scripts.
> 4. Replace the red-line word lists with your industry's terms.
>
> Step 4 is the one people skip. Don't.
>
> Image: the four files to edit, listed.
> Hashtags: #buildinpublic #tutorial #opensource

**Post 8 — data day**

> Where the numbers in this repo come from, and where they deliberately stop.
>
> Tier 1, verifiable: 205 entries, 24 solar terms, 10 roles, tooling rate. Traceable to a file
> and a script run.
>
> Tier 2, calibration value: per-step minutes, the 0.55 effective output factor, the 25%
> bottleneck threshold. Industry anchors, explicitly labelled as not measured, meant to be
> overwritten by real records.
>
> Tier 3, not extrapolated: revenue, conversion rate, cost. Not in the simulation at all. With
> no real pricing and renewal data, any revenue number would be fiction.
>
> Image: the three tiers as a labelled list.
> Hashtags: #buildinpublic #datahonesty #opensource

**Post 9 — retro day**

> What broke while shipping this.
>
> The area metric mixed two units — material rows and output pieces — so no two roles were
> comparable and the chart meant nothing. Now there's one metric and everything derives from it.
>
> The 0.55 factor existed because I'd been over-estimating capacity. Deducting maintenance,
> distribution, replies, and low-energy days brought the estimate back to something I could
> actually hit.
>
> Both versions are in the repo. The broken one is the more useful documentation.
>
> Image: the two versions side by side, labelled v2 and v3.
> Hashtags: #buildinpublic #solofounder #retrospective

**Post 10 — CTA day**

> If you want the operating model templates I actually use — role design sheet, process chain
> sheet, 90-day roadmap template, monetisation path criteria table — open an issue on the repo
> titled "Claim the operating model template kit" and fill in the form.
>
> It asks for an email and one question: how do you make money right now?
>
> The weekly build-in-public retro goes out to everyone in Discussions. It's free, and it's the
> thing worth reading before you decide anything.
>
> Image: the issue title and form, nothing else.
> Hashtags: #buildinpublic #solofounder

### 4.2 LinkedIn long post

I spent three years building a content business that did not work. Not because I was lazy. Because
I could not answer three questions: where does the money come from, where am I actually stuck, and
when should I stop.

I could not answer them because I was tracking output. Posts published, pieces shipped, hours
logged. Output felt like progress. It was mostly a way to avoid looking at the real constraint,
which was that a meaningful part of every single deliverable went into work that produced no
deliverable at all.

So I started measuring time instead of output. Which sounds obvious. It took me two rewrites and a
burnt-down model to get it right, and the interesting part is why the first version was wrong.

The first version sized each role of my business by how much raw material it consumed. That felt
like a proxy for importance. It was not. Two different roles drew from the same material pool, so
the same knowledge entries got counted in both. My chart summed to 569 units of material against a
table that actually contained 205. Same material, counted roughly three times over, and the whole
visualisation was measuring an artefact of my accounting rather than my business.

The fix was small and unglamorous. One ownership table where every topic belongs to exactly one
role, and every other role that touches that topic gets a shared-pool reference instead of a
second claim on it. After that, the sum of the exclusive material reconciles against the rows in
the table. Not approximately. Exactly. And because it is a rule and not a snapshot, a validator can
fail the build the moment it stops being true.

The second correction was about units. I was mixing material rows and output pieces in the same
area calculation, which made the numbers incomparable across roles. Now there is exactly one area
metric, derived from the process chain, and every role is measured the same way.

The third was the one that changed my behaviour most. I had been estimating my own capacity
optimistically, because the estimate came from the part of the work I found interesting. But a
one-person operation also spends time on distribution and formatting per platform, on replies and
comments, on reviewing data and adjusting topics, on keeping the tooling alive, and on weeks when
the work simply goes slower. I put an effective output factor in the model to account for that, and
the honest version of my weekly capacity dropped by nearly half. The number was not flattering. It
was correct, and it was the first number in the whole model I could actually plan against.

The other thing I did not expect was how much the compliance work would matter. My content sits in
a traditional Chinese medicine wellness space, and I had assumed compliance was a section at the
bottom of a document. It is not a document problem. It is a tooling problem. If the rule lives in
prose, it gets violated by whoever is in a hurry, and probably by me. If the rule lives in the
validator, it gets enforced at exactly the moment someone is tempted to skip it.

So the red lines are code. There are 20 categories of content red lines that run against every row
of the knowledge table, and 16 categories of scan that run against the self-assessment result page,
covering contact details, external links, QR codes, scan prompts, and purchase paths. That last
one has a hard constraint behind it: on a page that explains health information, the operator's
contact information and purchase links may not appear on the same page. So the result page carries
none of them. Not in the footer, not in a comment, not in a data attribute.

The part I like most is the injection test suite. 44 cases that deliberately break the generated
page in different ways and confirm the validators catch every one of them. A validator that reports
"all clear" on a healthy page proves very little. What proves something is whether it can catch a
page that has been deliberately broken. The current score is 44 out of 44.

I have open-sourced the whole thing under MIT. Python 3.8 and the standard library, no
dependencies, no build step, no account. Clone it and the pipeline runs. The knowledge table has
205 entries with 24 solar terms covered and a citation on every row. The generated survival map is
a single HTML file that opens offline by double-click. There is a self-assessment with 36 questions
across 9 constitution types, and its result page is a tendency profile, never a diagnosis.

What is not in the repository is just as deliberate. There are no revenue numbers anywhere in the
simulation. No conversion rate, no cost forecast, no monthly income projection. I do not have real
pricing and renewal data, so any of those numbers would be fiction dressed up as a forecast. The
model stops where the honesty stops. The tier system that separates verifiable counts from
calibration values from things that are not extrapolated at all is there so that anyone reading the
output knows which numbers they are looking at.

The architecture is not TCM-specific. Swap the knowledge table, the role table, the tool evidence,
and the red-line word lists, and you have the same system pointed at a different domain. The
compliance layer is the part most people assume is specific to the vertical, and it is actually the
most reusable layer, because every vertical has its own set of things that must never be said.

I have also written down what I deliberately do not do. I do not make medical claims of any kind.
I do not buy stars or pay for placement. I do not run paid ads. I do not promise income, ever,
not even a range, not even "based on industry averages". If the system is worth using, it will show
up in the work you can verify.

If you want the operating model templates I actually use — role design sheet, process chain sheet,
90-day roadmap template, and the monetisation path criteria table — open an issue on the repository
titled "Claim the operating model template kit". The form asks for an email and one question: how
do you make money right now? The second question is not a qualification exercise. It is how I
decide what to send you and how I learn which part of the system is actually the bottleneck for
someone else.

And if you would rather just watch, the weekly build-in-public retro goes out to everyone who
subscribes to Discussions on the repository. It is free, and it covers what broke that week, what
the model got wrong, and what I changed as a result. No newsletter vendor, no signup wall, no
email sequence. Just the notes.

Clone it. Break it. The validators will tell you what broke, and if they do not, the injection
tests will.

### 4.3 Reddit post

**Suggested title:** Built an open-source operating system for running a one-person company with AI agents — and put the compliance rules in the validator instead of a disclaimer

**Body:**

Disclosure first: this is my own project and I am sharing it because it is open source. I am not
asking for upvotes and I am not going to post this anywhere else. If it is not useful to you, please
ignore it.

The short version. I run a one-person content business and I kept failing at the same three things:
not knowing where the money comes from, not knowing which part of my work is actually the
bottleneck, and not knowing when to stop. So I built a system that answers all three, and I
open-sourced it.

What is in it:

- A knowledge table: 205 entries, 24 solar terms covered, a citation on every row, one source of
  truth with a single writer per file.
- Ten roles, sized by one metric only, so the chart is actually comparable across roles.
- A process chain per role with per-step time, and the bottleneck step highlighted when it crosses
  a quarter of the total.
- Generators and validators that ship with it. 4 validators, and 44 injection tests that break the
  generated page on purpose to confirm the validators catch it. Currently 44 out of 44.
- Zero third-party dependencies. Python 3.8 standard library. Clone and run.
- MIT licensed.

The domain happens to be TCM wellness content, which is where the compliance machinery came from
and, honestly, the most interesting part. Health content has a hard constraint most technical
projects never hit: on a page explaining health information, you may not also put your contact
details or purchase links. So those rules are not a paragraph in a README. They are 20 red-line
categories checked against every knowledge row, plus 16 scan categories on the self-assessment
result page. If a rule is prose, it gets violated by whoever is in a hurry. If it is code, it gets
enforced.

Two things I would genuinely like criticism on, because I am not sure they are right:

1. The effective output factor. I use 0.55 to account for the time that goes nowhere near a
   deliverable — distribution, formatting, replies, data review, tooling maintenance, and slow
   weeks. It drops my stated capacity by nearly half versus the naive number, and it is the number
   I am least sure about. It is a calibration value, not a measurement, and it is labelled as such
   everywhere it appears.
2. The cash outlet model. There is exactly one cash outlet by construction, and the offline
   delivery path was discontinued. I would like to know whether forcing exactly one outlet is the
   right constraint or whether it just fits my situation and I generalised from one sample.

I also deliberately left revenue out of the simulation entirely. No income projection, no conversion
rate, no cost forecast, and the validator blocks those strings. Without real pricing and renewal
data, those numbers would be fiction.

If you want to look at it, the repository is linked from my profile. The README has a three-minute
run. If you spot something wrong, please say so in the comments — especially the two points above.
I would rather argue about the bottleneck factor than collect stars.

### 4.4 Hacker News title options

HN punishes marketing smell. These read like findings, not launches.

1. **"Show HN: I put the compliance rules of a health content business in a validator instead of a disclaimer"**
   — Leads with the unusual engineering decision, not the product. The 20 red lines and 16 result-page
   scans are the hook.
2. **"Show HN: A content pipeline that fails the build when you double-count your own source material"**
   — Leads with the concrete bug it prevents. The conservation invariant is checkable and therefore
   interesting.
3. **"Show HN: 44 tests that break my generated page on purpose, because a validator that says 'all clear' proves nothing"**
   — Leads with the injection-testing methodology, which is a testing idea rather than a business
   idea.
4. **"Show HN: Measuring a one-person company in output pieces instead of hours, and being wrong by half"**
   — Leads with the finding. The 0.55 factor and the "measurement was measuring my accounting"
   admission are the substance.
5. **"Show HN: Zero-dependency Python that generates a single-file offline HTML dashboard from one CSV"**
   — Leads with the technically checkable claim. Clone-and-run with no install step is the easiest
   thing for a reader to verify in ten seconds.

> If you actually post it, lead with the number that can be checked, link the repository, and put
> the business model in a comment rather than in the title. Do not submit the same link to multiple
> communities on the same day.

### 4.5 Launch email (for Discussions subscribers)

Subject: The repo is live, and here is what I want from you

Body:

The repository is up. MIT licensed, Python 3.8 standard library, no dependencies, no account needed.

Inside: a 205-entry knowledge table with 24 solar terms covered and a citation on every row; 10
roles measured by a single metric; 4 validators; and 44 injection tests that break the generated
page on purpose to prove the validators catch it. Currently 44 out of 44.

There is deliberately no revenue projection anywhere in the model. Without real pricing and renewal
data, a revenue number would be fiction, so the validator blocks those strings.

The weekly build-in-public retro is free and goes to everyone in Discussions.

Two things I need from you:

- If you clone it and something breaks, open an issue. I would rather have the failure than the
  star.
- Tell me which part of the retro is actually useful. I do not know yet.

If you want the operating model templates I use, open an issue titled "Claim the operating model
template kit".

It asks for an email and one question: how do you make money right now? The second question is
not a filter. It is how I learn where the bottleneck is for someone who is not me.

Zhang Wei / Long Ge

---

## 5. Build-in-public content calendar, 4 weeks

Daily posting. The subject of each day is a process or a judgement, never a victory lap: this
audience is peers, and peers disengage from a feed of achievements.

| Date | Day | Content topic | Channel | Funnel stage |
|---|---|---|---|---|
| 2026-11-23 | Mon | Launch: what the repo is and the three invariants | X + LinkedIn | Reach |
| 2026-11-24 | Tue | Demo: the generated survival map, one-file offline | X | Reach |
| 2026-11-25 | Wed | Build-in-public: clean-clone rebuild and empty diff | X | Reach |
| 2026-11-26 | Thu | Technical: why the area metric must have one unit | X | Reach |
| 2026-11-27 | Fri | Invitation to Discussions — subscribe | X + LinkedIn | Capture |
| 2026-11-28 | Sat | Why the compliance rules are code, not a document | LinkedIn | Reach |
| 2026-11-29 | Sun | Weekly retro #1: what broke this week | Email | Capture |
| 2026-11-30 | Mon | Contrarian: output volume is the wrong variable | X | Reach |
| 2026-12-01 | Tue | Deep dive: the material ownership table | X | Reach |
| 2026-12-02 | Wed | Deep dive: the 44 injection cases | X | Reach |
| 2026-12-03 | Thu | Data tiers: verifiable vs calibration vs not extrapolated | LinkedIn | Reach |
| 2026-12-04 | Fri | Weekly retro #2: the week the 0.55 factor was questioned | Email | Capture |
| 2026-12-05 | Sat | "I would not recommend this" advice post | X | Reach |
| 2026-12-06 | Sun | Tutorial: repoint the pipeline at your own domain | X | Reach |
| 2026-12-07 | Mon | The self-assessment: tendency profile, never diagnosis | X + LinkedIn | Reach |
| 2026-12-08 | Tue | Why no revenue number appears anywhere | X | Reach |
| 2026-12-09 | Wed | One cash outlet and what that forces | X | Reach |
| 2026-12-10 | Thu | The 20 red-line categories, one at a time | X | Reach |
| 2026-12-11 | Fri | Weekly retro #3: reader questions and answers | Email | Capture |
| 2026-12-12 | Sat | What a red line looks like in English | LinkedIn | Reach |
| 2026-12-13 | Sun | Reading the first subscriber case | X | Feed back |
| 2026-12-14 | Mon | Template kit announcement and issue form | X + Email | Claim |
| 2026-12-15 | Tue | How the issue form question shapes what I send | X | Claim |
| 2026-12-16 | Wed | The 90-day roadmap as four observable gates | X | Reach |
| 2026-12-17 | Thu | What I got wrong about the bottleneck threshold | LinkedIn | Reach |
| 2026-12-18 | Fri | Weekly retro #4: the month in review | Email | Capture |
| 2026-12-19 | Sat | Reader case published in the README | X | Feed back |
| 2026-12-20 | Sun | Month-end: what changed, what is next, how to subscribe | X + LinkedIn | Capture |

Cadence rules:

- One idea per post. If a post contains two ideas, it is two posts.
- Every post ends with the next concrete step: run it, subscribe, or open the issue.
- No post claims a result that has not been measured. If a number is not verifiable, it does not
  appear.
- Retro days are where the honesty lives. A week where nothing broke is itself worth posting.

---

## 6. Conversion mechanics

### 6.1 Where the CTA goes in the README, and three candidate wordings

Placement, in order of expected effect:

1. **Right after the three-minute run block.** The reader has just been told it is three minutes.
   The highest-intent moment is immediately after that promise is kept.
2. **At the end of "What this is"**, next to the line that explains the real problem being solved.
3. **In the footer of the README**, once, with the exact issue title so the click is unambiguous.

Do not put a CTA above the fold of the value section. Do not put three CTAs in one section. One
per section.

**CTA A — after the run block**

> If this was useful, the operating model templates I actually use are a single issue away.
> Open an issue titled "Claim the operating model template kit" — it asks for an email and one
> question about how you make money now. No newsletter vendor, no signup wall.

**CTA B — after the problem statement**

> Most solo projects fail because nobody can say where the money comes from or when to stop.
> This repository answers both, and it is open source.
> Want the operating model templates? Open an issue titled "Claim the operating model template kit".

**CTA C — in the footer, minimal**

> **Want the operating model template kit?** Open an issue titled exactly that. It takes two
> fields and one question about how you make money right now.

What all three share: the exact issue title is quoted, the request is specific, the cost of the
form is stated, and nothing is implied that is not delivered.

### 6.2 Discussions category structure

Three categories, and the reason for each:

| Category | Purpose | Why it exists |
|---|---|---|
| Q&A | Questions about how the model works or how to repoint it | Keeps unanswered questions visible instead of buried in a chat thread |
| Show and tell | Readers post their own adapted pipeline, output, or diagrams | This is the proof section, written by users instead of by me |
| Announcements | Releases, template kit updates, retro summaries | One place to check for changes; keeps announcements out of the question flow |

**Why subscribers must be able to see how other people use it.** A new reader's first question is
not "is this well made", it is "does anyone like me actually use this". If the only visible
activity is the author talking, the answer is no and the reader leaves. Show and tell exists
specifically so that a subscriber's first impression of the community is another member's work.
It also does the marketing for me, because a user's post reaches their audience in a way my own
posts never will.

Rules that keep this healthy: one announcement thread per release, no cross-posting between
categories, and no author-only replies in Show and tell.

### 6.3 What the issue form collects, and why it collects two fields

| Field | Type | Why |
|---|---|---|
| Email | Required, plain email address | The only way to deliver the kit. Explicitly consented to. |
| How do you make money right now? | Required, free text | Qualification and research in one question |

**Why the second question is asked.** It does three jobs that a separate survey would fail at:

1. **It filters without a form.** Someone who cannot name a current revenue path is not the
   person the templates help, and they will find that out from the templates rather than from a
   rejection email. The question self-selects.
2. **It tells me what to send.** If fifty people describe content monetisation and five describe
   client work, that is the market for a 1v1 diagnosis, and I learn that from the form instead of
   from a survey I would not send.
3. **It is the seed of the feed-back loop.** Every answer is a sentence in somebody's business
   model. With permission, those sentences become the README proof section, and the proof brings
   in the next cohort. The question is the mechanism that closes the loop.

What the form must not do: ask for a phone number, ask for a company, or present the email field
as optional. Every extra field costs completions, and the two above are the only two that earn
their place.

### 6.4 Fixed column structure of the weekly email

Same slots every week, in the same order. Readers subscribe to a shape, not to a surprise.

| # | Column | What goes in it |
|---|---|---|
| 1 | What broke this week | One thing that failed, and what it cost in time |
| 2 | What the model got wrong | A number or an assumption that turned out to be wrong |
| 3 | What I changed | The concrete diff, in the repository, with the file named |
| 4 | One idea you can steal | The transferable lesson, with no mention of my business |
| 5 | Open questions | What I am actually stuck on, and what would help |
| 6 | Reader case | One subscriber outcome, with permission, or explicitly "none this week" |

Column 1 and column 2 are the ones that earn the subscription. Column 6 being allowed to say
"none this week" is deliberate: the alternative is manufacturing a case, and a single fabricated
case ends the whole loop.

---

## 7. What we deliberately do not do

This section is not a disclaimer. It is a list of decisions, and reversing any of them would
require saying so out loud.

- **No medical claims. Ever.** Not in the README, not in a post, not in the DM. The content domain
  is wellness lifestyle information, and the boundary is enforced by the validator. A disclaimer
  underneath a claim does not make the claim legal.
- **No star buying, no star trading, no paid placement.** No engagement service, no "I will
  reciprocate" deal, no reciprocal-star arrangement, no ask-for-review campaign. If the repository
  is worth a star, someone will star it because it helped them.
- **No paid advertising.** No ads on the newsletter, no sponsored posts, no boosted content, no
  paid distribution. The channel is organic distribution and the repository.
- **No income promises.** No revenue forecast, no "expected monthly income", no earnings range, no
  "based on industry averages". The simulation contains no income, conversion rate, or cost
  figures at all, and the validator blocks those strings.
- **No fabricated usage numbers.** No "used by 10,000 teams". No invented testimonials, no
  paraphrased user quotes, no case studies that are composites presented as real.
- **No vanity metrics as proof.** Stars are not proof. A reproducible build, a passing injection
  suite, and a number traced to a file are proof. Where proof is missing, the README says so.
- **No dark patterns on the email.** No confirmation sequence, no "we noticed you didn't open",
  no countdowns, no urgency theatre. One email a week, one unsubscribe link.
- **No gatekeeping the free layer.** The repository, the validators, the injection tests, the
  generated pages, and the weekly retro stay free permanently. The paid tiers sell templates,
  diagnosis, and company — not access to safety.
- **No splitting the compliance layer to sell it.** The red lines, the word lists, and the
  validators are in the public repository under MIT. Making safety paywalled would be selling the
  absence of a guardrail to people who need one.
- **No platform farming.** No cross-posting the same link to many communities on the same day, no
  comment-section promotion, no drive-by replies that restate the pitch.
- **No fake urgency.** No launch countdown, no "limited spots", no cohort that does not exist.
- **No pretending the model is finished.** The calibration values are labelled as calibration
  values, the known limitations are listed, and the broken earlier version stays in the repository
  as documentation.
- **No expansion into a regulated service.** No consultation practice, no diagnosis, no treatment
  protocol, no prescription. The cash outlet is a subscription for content and tooling.

---

## 8. Compliance guardrails for the English market

The Chinese compliance boundary is the harder constraint, and it is documented in
`docs/en/compliance-handbook.md`. This section covers the additional exposure that comes with
publishing in English, where the audience reads under the FTC, the FDA, and state consumer
protection law.

### 8.1 What the FTC actually cares about

- **Net impression.** The FTC evaluates the ad as a whole, not phrase by phrase. A headline that
  reads as a treatment claim cannot be rescued by a body that reads as wellness. If a reasonable
  consumer would read the ad as a treatment claim, that is the claim you made.
- **Substantiation before dissemination.** Health claims require a reasonable basis *before* the
  ad runs. For health claims generally, that means competent and reliable scientific evidence, and
  the 2022 Health Products Compliance Guidance expects randomised controlled human clinical trials
  as the general form of support for health-related benefits.
- **Implied claims count.** Images of lab coats, microscopes, medical journals, or a "clinically
  tested" line are claims. So is a product name that implies a disease, like an arthritis-branded
  balm.
- **Disclaimers cannot contradict the claim.** A footer saying "not intended to treat any
  disease" under a headline that says it treats acne is worse than useless, because the disclaimer
  is evidence that the claim is a claim. Disclaimers also have to be unavoidable, not hidden in a
  link.
- **Traditional use is not a defence.** Long use in a tradition does not substantiate efficacy in
  the US.
- **Material omissions.** A health benefit can be misleading if the ad omits information material
  to that benefit.

Practical consequence for this project: we make no efficacy claim at all, so we never enter the
substantiation queue. Every claim we make is about structure, method, or arithmetic — "these 205
rows cover 24 solar terms" is checkable by anyone.

### 8.2 What the FDA cares about

- FDA regulates products, not systems. There is no approval pathway for "TCM" as a category; the
  product is a drug if it is intended to diagnose, treat, cure, mitigate, prevent, or otherwise
  affect the structure or function of the body.
- Structure/function claims on a supplement that imply a disease benefit convert the product into
  an unapproved drug.
- No herbal product may be marketed with disease claims unless it is an approved drug. Do not
  imply FDA review, approval, or endorsement, and do not describe a facility as "FDA registered"
  or "FDA approved" to imply otherwise.
- Safety is a separate matter from efficacy: an ingredient may be safe and still not make any
  claim. Certain botanicals carry their own restrictions.
- This project sells no products and makes no ingredient claims. Keep it that way.

### 8.3 "Wellness" and "treatment" are different categories, not different intensities

| | Treatment language | Wellness language |
|---|---|---|
| Claim target | A disease, symptom, or condition | A general practice, routine, or habit |
| Verification | Needs clinical evidence | Needs to be true and non-misleading |
| Subject | The patient's condition | The reader's own practice |
| Example | "treats high blood pressure" | "a daily wind-down routine" |
| Our risk | Regulated claim, substantiation required | Still must not mislead |

The trap is the middle register: language that is technically about routine but reads as treatment.
"Supports healthy blood pressure" is a structure/function claim that implies a disease benefit.
The safe version describes what a person does, not what their body achieves.

### 8.4 Substitution table for English copy

| Never write | Write instead |
|---|---|
| "cures high blood pressure" | "a daily routine to support a consistent wind-down" |
| "treats insomnia" | "an evening wind-down routine for people who want a steadier bedtime" |
| "relieves joint pain" | "a warm-up routine for people who sit a lot" |
| "detoxifies your liver" | "a seasonal food routine with less fried food and more warm dishes" |
| "boosts your immune system" | "everyday habits that keep your routine steady in winter" |
| "clinically proven" | "the source line is cited on every row, and the method is described in full" |
| "safe for everyone" | "general lifestyle information, not medical advice" |
| "your constitution is Qi-deficient, so you need this" | "your self-assessment result is a tendency, and the routine below is a starting point" |
| "ask me about your symptoms" | "tell me what you have been eating and how your routine goes" |
| "our diagnostic identifies your condition" | "our self-assessment maps tendencies; it never diagnoses" |
| "this program is necessary for your health" | "this program is one option for structuring your routine" |
| "doctor recommended" / "clinician approved" | "the underlying classical source is cited in the knowledge table" |
| "works within minutes" | "how long the routine takes, stated plainly" |
| "you will see results in 7 days" | "what the routine is designed to do, described without an outcome promise" |
| "FDA approved formula" | omit entirely; never imply FDA review or approval |

### 8.5 Structural rules that keep the English output safe

1. **Result page carries nothing.** No contact details, no external links, no QR code, no scan
   prompt, no purchase path. The 16 scan categories in `scripts/validate_constitution_html.py`
   enforce this. The English version of the page needs the same enforcement, not a manual review.
2. **Disclaimer below compliant body copy, never instead of it.** If the body trips a red line,
   the disclaimer does not help. The body must be clean on its own.
3. **State the source, not the outcome.** Every wellness item cites its source line. A citation is
   verifiable; an outcome is a promise.
4. **No restricted-audience claims.** No pregnancy, postpartum, infant, post-operative,
   chemotherapy, dialysis, or transplant content — in English as in Chinese. These audiences
   belong under clinical care.
5. **No consultation solicitation.** The self-assessment asks about daily state and preferences
   only, never symptoms, never duration, never "come in and I will take a look".
6. **No expert or practitioner endorsement.** No named physicians, no "as seen in" clinical
   figures, no borrowed authority.
7. **No comparative superiority.** No "better than", no "safest", no national-level or
   best-in-class superlatives.
8. **No income claims attached to health content.** This is where the two risk surfaces meet, and
   the separation between the operating-system product and the wellness material has to hold in
   the copy as well as in the code.
9. **Search terms are not claims, but check the landing page.** If an SEO keyword promises a
   treatment, the page it lands on becomes an ad for that treatment, whatever the keyword map
   says.
10. **When in doubt, cut the claim.** The repository's position is that describing a practice is
    always safe and promising an outcome is never worth the risk.
