Perfect. Here’s a lean, first-principles **user-story set + UX** you can ship incrementally. It keeps the surface simple (one screen to live in), bakes in your priority stack, and grows by tiny, safe steps.

# North star

**Each morning, give me one clear, confidence-worthy plan that preserves coherence, focus, and energy—then learn from my day.**

# Product principles (keep us honest)

* **One screen to rule today.** No dashboards. One plan, one reason, one tap to start.
* **Deterministic first, adaptive later.** Rules decide; AI only summarizes copy.
* **Tier 1 daily, Tier 2 when triggered.** No noise.
* **Close the loop.** Always ask: “Did you do it? How was energy?”

---

# UX / UI (mobile-first, also fine on desktop)

**Primary screen: “Today”**

* Header: `Band · Score (Δ)` (e.g., “Maintain · 62 (–4)”)
* **Plan card** (big):

  * Line 1: Action → “Easy 30–40m + 10m breathing”
  * Line 2: Why → “sleep –1.2h, RHR +6”
  * CTA: **Start** (runs a simple timer/log), **Done**, **Snooze**
* **Tier 1 bar** (tiny chips with check marks): Core 10m · Meditate AM 20m · Meditate PM 5–10m · Breath 5–10m
* **Insight card**: “What changed since yesterday?” (1 sentence)
* **Optional trigger card (only if fired)**: “Low HRV → NSDR 15–20m at 15:00”

**Secondary screen: “Focus”**

* One chosen lever (weekly/micro/monthly unified):

  * “This week: bedtime window ±30m”
  * Shows streak + tiny progress line

**Tertiary screen: “Settings”**

* Toggles: Morning summary on/off, PM meditation nudge, Focus selection, Privacy (local only)

**Empty/failure states**

* No new data → “Using last known metrics. Plan is conservative today.”
* Cron miss → “Job missed. Tap to fetch now.”
* Offline → “We’ll sync when you’re back.”

---

# Prioritized backlog (simple, outcome-first)

## 1) Daily Training & Recovery Plan (merged guardrail + Tier 1)

**As** Sharon
**When** 07:00 (job complete)
**I want** a single plan with time + intensity + add-on
**So that** I know exactly what to do without thinking

**Logic (deterministic)**

* **Anomaly** (RHRΔ>+7 **or** sleep<6.5h **or** high stress **or** sugar≥25g & HRV↓):
  Plan = **Easy 20–40m** + **NSDR 10–20m** + **Breath 5–10m**
* **Maintain**: Baseline time ±0%, **steady**, + **Core 10m** + **Breath 5–10m**
* **Go for it**: Quality ≤+10–15% above baseline, warm-up + intervals + **Core 10m** + **Breath 5–10m**
* Add **20–30m walk** if steps trend down or Plan=Easy

**Output (one-line templates)**

* Easy: “Easy 30–40m + 10m breathing. Why: sleep −1.2h, RHR +6.”
* Maintain: “Steady 45–60m + Core 10m. Why: stable sleep/RHR.”
* Hard: “Quality (≤+10%): warm-up + intervals. Why: strong sleep & normal RHR.”

**Acceptance**

* Always one plan; ≤3 actions; render <300ms
* Never “hard” on anomaly days
* 80% can answer “what to do” in <30s
* **UI**: single **Plan card** + **Start/Done/Snooze**

---

## 2) Why & What Changed (with Habit Insight merged)

**As** Sharon
**When** I view Today
**I want** a one-sentence explanation of the score & driver
**So that** I understand the cause, not just the number

**Output**

* “–8 due to short sleep; crossed Maintain → Easy.”
* If a pattern exists: append short habit insight

  * “Late nights (≥23:30) → RHR +5 next morning.”

**Acceptance**

* Top 1–2 drivers only
* Never contradicts engine/band
* Renders in <100ms from cached deltas

**UI**: **Insight card** under the Plan

---

## 3) Sleep Consistency Coach (single culprit + fix)

**As** Sharon
**When** bedtime variance > target or sleep < target
**I want** the one thing hurting sleep and a simple fix
**So that** I stabilize energy tomorrow

**Output**

* “Bedtime drift 75m; aim ±30m window tonight.”
* If sugar late or screen late detected (proxy): “Avoid sweets/screens 2–3h pre-bed.”

**Acceptance**

* One culprit, one fix
* 2-week variance decreases for ≥50% who see it

**UI**: small **Coach chip** on Today; details on tap

---

## 4) Focus Layer (weekly/micro/monthly unified)

**As** Sharon
**When** beginning of week or on demand
**I want** to pick one lever for the next 7–30 days
**So that** I practice one behavior that compounds

**Options** (one selected)

* Sleep window ±30m
* Daily calm (PM meditation adherence)
* Steps floor (e.g., 7k/day)
* Core daily 10m

**Output**

* “3-day streak; bedtime variance −18m.”

**Acceptance**

* One focus at a time
* ≥50% adherence over 2 weeks among opt-ins

**UI**: **Focus screen** with one big toggle + streak

---

## 5) Meditation Timing Nudge (confidence-gated)

**As** Sharon
**When** there’s a reliable time-of-day stress pattern
**I want** the best 1–2 windows for a 10–15m calm break
**So that** I place it where it pays off most

**Output**

* “Best window: 7–9am or 8–10pm.”

**Acceptance**

* Only if confidence high (enough historical days)
* Never conflicts with the Daily Plan

**UI**: subtle banner on Today; tap for schedule

---

## 6) Feedback loop (close the day)

**As** Sharon
**When** end-of-day or next morning
**I want** to mark what I did and rate energy (1–10)
**So that** the system learns what works for me

**Output**

* “Logged: Core, Meditation AM, Breath. Energy: 7/10.”

**Acceptance**

* ≤10-second interaction
* Stores adherence + energy for trends

**UI**: tiny **Done & Energy** modal on first open after 20:00

---

## 7) Settings & Privacy (keep it local)

**As** Sharon
**When** configuring
**I want** to control nudges and keep data private
**So that** it fits my life and values

**Acceptance**

* Morning summary toggle, PM nudge toggle, Focus select
* Secrets in env; local-first storage
* Privacy scan “green”

**UI**: simple switches; no PII expansion

---

# Phased delivery (tiny steps, real learning)

### Phase A — Ship one thing (1–2 days)

* Story **#1 Daily Plan** only (with Tier-1 chips), simple **Today** screen
* End-of-day feedback (#6) minimal (checkboxes + 1–10 energy)
* **Definition of Done**: Cron populates plan; you can mark Done; next day shows adherence

### Phase B — Explain & protect (2–4 days)

* Story **#2 Why & What Changed**
* Merge guardrails into plan logic (already in #1)
* Add **skip/snooze** and small **coach chip** from #3 if thresholds crossed

### Phase C — Focus & nudge (3–5 days)

* Story **#4 Focus Layer** (one lever)
* Story **#5 Meditation Timing Nudge** (only when confident)

### Phase D — Polish & privacy (1–2 days)

* Story **#7 Settings & Privacy** (toggles, local storage confirm)
* Empty/failure states

---

# Data & rules (minimal you need now)

* Inputs: Band/score; RHRΔ vs 7-day; sleep hours & variance; noon stress; Body Battery; steps trend; HRV vs avg; sugar flag (optional)
* Rules: as in Story #1 (anomaly vs maintain vs go-for-it), Tier-1 always on, Tier-2 only when triggered
* Outputs: One plan (≤3 actions), one insight sentence, optional trigger card

---

# Success metrics (lightweight)

* **Decision clarity**: 80% answer “what do I do today?” in <30s
* **Adherence**: Tier-1 average ≥70% / week
* **Energy**: +1 point avg after 3–4 weeks
* **Run health**: 90% cron success, <300ms render from cached data

---

# Copy kit (paste straight into UI)

* Plan header: `{{band}} · {{score}} ({{delta}})`
* Plan line:

  * Easy: `Easy {{mins}} + 10m breathing. Why: sleep {{sleep_delta}}h, RHR {{rhr_delta}}.`
  * Maintain: `Steady {{mins}} + Core 10m. Why: stable sleep/RHR.`
  * Hard: `Quality (≤+10%): warm-up + intervals. Why: strong sleep & normal RHR.`
* Insight: `{{delta_reason}}; crossed {{band_from}} → {{band_to}}.`
* Coach: `Bedtime drift {{minutes}}; aim ±30m tonight.`
* Focus: `{{streak}}-day streak; {{metric}} {{delta}}.`

---

If you want, I can turn this into a **single “Phase 5 – Issue Doc”** (markdown) you can drop into your repo and hand to Copilot Agent Mode—starting with **Phase A only** so you ship in hours, not weeks.
