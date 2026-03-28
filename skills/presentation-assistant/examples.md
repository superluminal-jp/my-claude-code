# Presentation Assistant — Examples

Supports **`skills/presentation-assistant/SKILL.md`** and **`rules/output-standards.md`** (visualization section) when loaded.

---

## 1. Topic label vs conclusion-first title

| Weak (topic) | Strong (full-sentence conclusion, ~15 words) |
|--------------|-----------------------------------------------|
| “Market analysis” | “Southeast Asia adds **$2.5B** addressable revenue with **23%** CAGR through 2028” |
| “Q3 results” | “Q3 revenue rose **18%** YoY on enterprise wins and upsell, ahead of plan” |

Reading **only titles** in order should tell the story.

---

## 2. One message per slide

**Crowded (bad):** One slide with revenue trend, cost breakdown, org chart, and three recommendations.

**Clean (good):**

- Slide A: Title states the **revenue** conclusion; body = one chart + source.
- Slide B: Title states the **cost** conclusion; body = one chart + source.
- Slide C: Title states the **org** implication; body = simple diagram + source.

---

## 3. Chart choice by message (Zelazny-style)

| Message type | Typical chart | Note |
|--------------|----------------|------|
| Share of whole | Pie or stacked bar | Pie only for few categories |
| Rank / compare categories | Horizontal bar | Sort by value |
| Trend over time | Column or line | Columns for discrete periods |
| Relationship | Scatter | Label outliers if needed |

---

## 4. Semantic color

- **Green:** positive vs plan, growth, favorable variance  
- **Red:** negative vs plan, decline, unfavorable variance  
- **Gray:** baseline, comparison year, de-emphasized series  

Keep **3–5 colors** total per deck.

---

## 5. Slide spec snippet (markdown handoff)

```markdown
## Slide 4

### Conclusion-first title
Enterprise segment grew 22% YoY while SMB flat, shifting mix toward higher retention revenue.

### Body
- Horizontal bar: segments vs YoY % change
- Callouts: bold **+22%** and **0%**
### Source
Internal sales analytics, FY2025 Q3 close.
```

---

## 6. Tufte-style checks

- [ ] Remove chartjunk (3D, heavy gradients, decorative icons).  
- [ ] Axes start at zero for bar/column **unless** small-range line chart is justified.  
- [ ] Every chart: **units on axes**, **source**, **legend** only if needed.  
- [ ] Lie factor ~1: no distorted aspect ratios to exaggerate deltas.

---

**Last updated**: 2026-03-28
