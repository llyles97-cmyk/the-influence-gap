<img src="banner.svg" alt="The Comeback Index" width="100%"/>

<br/>

![SQL](https://img.shields.io/badge/SQL-SQLite-c9a84c?style=flat-square&logo=sqlite&logoColor=white&labelColor=111111)
![Data](https://img.shields.io/badge/Data-Billboard_Hot_100-c9a84c?style=flat-square&logoColor=white&labelColor=111111)
![Scope](https://img.shields.io/badge/Scope-2010–2021-c9a84c?style=flat-square&logoColor=white&labelColor=111111)
![Records](https://img.shields.io/badge/Records-61%2C900-c9a84c?style=flat-square&logoColor=white&labelColor=111111)
![Re--entries](https://img.shields.io/badge/Re--entries-1%2C130-c9a84c?style=flat-square&logoColor=white&labelColor=111111)
[![Portfolio](https://img.shields.io/badge/Portfolio-lylesmom-c9a84c?style=flat-square&logoColor=white&labelColor=111111)](https://lylesmomportfolio.my.canva.site)

---

# The Comeback Index
### A SQL Analysis of Chart Re-entries in the Streaming Era, 2010–2021

---

## The Question

Does a chart comeback reflect genuine audience reconnection — or is it just infrastructure?

The Billboard Hot 100 treats every re-entry identically. This analysis argues it shouldn't.

---

## The Framework

Three comeback types emerge from the data:

**Calendar Return** — Predictable, seasonal, infrastructure-driven. Holiday catalog songs that return every December by calendar, not by culture. High revenue predictability. Low signal value for new audience acquisition.

**Cultural Surge** — Event-triggered. Tied to grief, biographical moments, or viral content. Unpredictable timing but high listener intent. Avicii, Juice WRLD, Mac Miller.

**Slow Burn** — Latent discovery. Songs that debut quietly and find their audience over time through sync licensing, platform surfacing, or genre crossover. Cruise by Florida Georgia Line is the archetype — debuted at #99, re-entered at #8.

Treating these as a single category produces noise, not insight.

---

## The Data

- **Source:** Billboard Hot 100 weekly chart data via Kaggle
- **Scope:** 2010–2021 (streaming era)
- **Tool:** SQLite via DB Browser
- **Size:** 61,900 chart entries, 5,313 unique songs, 2,763 artists
- **Re-entries identified:** 1,130 events

**Re-entry definition:**
```sql
WHERE last_week_rank IS NULL AND weeks_on_board > 1
```
A song with no prior-week position but confirmed chart history — absent last week, back this week.

---

## The Findings

**1. Re-entries are accelerating.**
Re-entry volume grew 89% from 2014 to 2020 — from 89 events to 168. The sharpest acceleration: 2019 to 2020, coinciding with TikTok's Western market expansion. The platform effect is structural, not incidental.

**2. A small group of artists drives disproportionate comebacks.**
Taylor Swift leads with 23 re-entries across 17 songs — catalog breadth. Mariah Carey has 9 re-entries from a single song — seasonal institution. Travis Scott has 11 re-entries across only 5 songs — deep fan loyalty. Three artists, three completely different comeback mechanics.

**3. Debut rank is not destiny.**
Cruise by Florida Georgia Line debuted at #99 and re-entered at #8 — a 91-rank improvement, the largest in the dataset. Lucid Dreams improved 66 ranks posthumously. Wildest Dreams improved 61 ranks via TikTok revival. Songs that debut quietly can become cultural anchors later.

**4. Comeback attention is a spike, not a rebuild.**
Re-entry songs average 6.28 weeks on chart per appearance. First-entry songs that stick average 10.99 weeks. The 4.71-week gap is the clearest quantitative signal that comebacks and sustained debuts are fundamentally different phenomena.

**5. The chart makes no distinction between calendar and culture.**
Kelly Clarkson returns every December by calendar. Juice WRLD returned after his death. The Hot 100 counts both identically. That's an analytical problem with real strategic consequences for labels, platforms, and measurement teams.

---

## Files

| File | Description |
|------|-------------|
| `schema.sql` | Table definitions and view creation |
| `queries.sql` | All five analysis queries with methodology comments |
| `insights.md` | Extended written findings |
| `The-Comeback-Index.pdf` | Full presentation deck |

---

## SQL Techniques Used

JOINs, CTEs, Window functions, UNION ALL, JULIANDAY for gap calculations, CASE WHEN segmentation, subqueries, CREATE VIEW

---

## Why This Matters

Counting a re-entry identically to a debut overstates new audience acquisition in catalog performance reports. If a song returns to the chart for the sixth December in a row, that is retention of an existing seasonal audience — not new reach. KPI frameworks that conflate the two mislead stakeholders and misallocate spend.

The Comeback Index framework isn't just a finding. It's a measurement layer any label, platform, or analytics team could build on top of existing chart data.

---

*Attention returns. Loyalty is built differently.*
