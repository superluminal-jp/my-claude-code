# Document Assistant — Examples

Supports **`skills/document-assistant/SKILL.md`** and, when loaded, **`rules/output-standards.md`**. These illustrate **structure and tone**; **never copy framework labels** into real deliverables.

---

## 1. BLUF vs buried lede

**Weak (information-only opening)**:

> In Q4 we ran several campaigns across channels. Email open rates varied by segment. The operations team updated the CRM fields in November.

**Strong (BLUF)**:

> **We should pause paid social in Segment B and shift budget to email for Q1** — Segment B’s CAC rose 40% QoQ while email conversion improved 12% after the November CRM fix. Below: evidence, risks, and owners.

---

## 2. Fact → implication → action

**Weak**:

> Page load time is 3.2s.

**Strong**:

> **Page load is 3.2s (p95, last 7 days, RUM)** — *Implication:* checkout abandonment is likely contributing to the 8% cart drop vs. benchmark. **Action:** assign frontend to reduce LCP to &lt;2.5s by [date]; measure checkout completion weekly.

---

## 3. Phrasing: internal rubric vs client-ready text

| Avoid in deliverables | Use instead |
|----------------------|-------------|
| “Applying MECE…” | “These three drivers are separate; together they cover total cost.” |
| “Pyramid structure…” | “Bottom line first: …” |
| “SCQA introduction…” | “Context: … Why it matters: … Decision needed: … Our answer: …” |
| “So what?” (as a label) | “This means …” / “Therefore …” |

---

## 4. Recommendation block (owner, time, outcome)

```markdown
## Recommendation

**Decision:** Approve pilot in [region] starting [month].

| Action | Owner | By | Expected outcome | Resources |
|--------|-------|-----|-------------------|-----------|
| Finalize partner shortlist | [role] | [date] | 3 qualified bids | 40h BD |
| Launch 90-day pilot | [role] | [date] | NPS ≥ [x], CAC ≤ [y] | $[z] budget |
```

---

## 5. Calibrated uncertainty (when data is thin)

> **With medium confidence:** demand will grow **~15–20% YoY** next year, based on [source A, 2025] and [source B, 2024]. **Low confidence** on the upper bound: competitive entry could cap growth; if [competitor] launches in Q2, revise down to ~10%.

---

**Last updated**: 2026-03-28
