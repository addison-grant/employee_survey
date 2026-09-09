# SCCWRP staff survey explorer

An interactive view of the 2026 SCCWRP staff satisfaction survey: 24 questions
answered by 47 staff across four job classes, shown as mean scores with 95%
confidence intervals.

## What it does

Every bar is one job class's mean score on one question. The bar spans a 95%
confidence interval, and the notch inside marks the observed mean. Colour runs
dark navy for the most senior class down to bright blue for the least, so the
chart reads as a seniority gradient without labelling each bar.

The horizontal axis is pinned to the full Likert range so bar positions stay
comparable no matter which questions or groups you have on screen. There are no
hover tooltips anywhere in the app; exact figures live in the table under the
chart, which also exports to CSV.

**Scale.** The default runs 1&ndash;5, matching the raw survey. Switching to
*Centred on neutral* subtracts 3, so 0 marks "neither agree nor disagree" and
the sign of a score says whether a group is net-positive. This is a pure shift:
interval widths and every comparison between groups are identical either way.
Its value is that a bar crossing 0 has a plain meaning &mdash; that group is not
reliably on either side of neutral. Its risk is that ratios become tempting and
they are meaningless, because 0 is a midpoint rather than an absence of opinion.

**Job class controls.** Click a group to cycle it through three states:

| Glyph | State | Effect |
| --- | --- | --- |
| blank | included | Folded into a single pooled bar (the default for every class) |
| ✔ | singled out | Gets its own bar |
| ✕ | excluded | Left off the chart entirely |

**Headcount.** Each class has an optional headcount box. Leave it on auto and
the class is assumed to hold the same share of the staff as it holds of the
responses. Fill one in and the remaining classes split whatever staff are left
over. If you fill in all four, their sum becomes the total and the "Total staff"
box is ignored.

**Sorting.** *Survey order* keeps the questions in the order they were asked,
grouped under their section headings. The other two sort by mean score, and you
choose whether that score comes from all staff, the pooled "Everyone else"
group, or the singled-out groups.

## The two interval types

Both answer "the average I measured is 3.25, how far off could it be?" They
differ on where the respondents came from.

**Standard** treats the 47 responses as a sample from an effectively unlimited
pool — the right frame if you are generalising beyond this particular staff,
or asking whether the result would repeat next year.

**Census-adjusted** applies a finite population correction. There are only ~63
people at SCCWRP and 47 already answered, so at most 16 unknown opinions remain
and they can only move the average so far. With those numbers the interval
shrinks by √((63−47)/(63−1)) ≈ 0.51, roughly halving each bar. This is the right
frame for describing what *these* staff think.

Only one interval is drawn at a time — use the toggle to switch. Note that the
correction is derived for simple random sampling without replacement, whereas
these responses are self-selected, so it addresses sampling variability but not
the systematic difference between people who answered and people who did not.

The correction assumes non-responders resemble responders. In staff surveys they
often do not — people who are disengaged or worried are likelier to skip — so
treat the adjusted bars as a floor on the uncertainty, not a hard bound.

## Run it locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Push this folder to a **public** GitHub repository.
2. Sign in at [share.streamlit.io](https://share.streamlit.io) with that GitHub
   account and authorise repository access.
3. Choose **Create app → Deploy a public app from GitHub**, then select your
   repo, the branch, and `app.py` as the main file.
4. Deploy. The URL looks like
   `https://<your-app-name>.streamlit.app`.

Community Cloud reads `requirements.txt` on every build and redeploys whenever
you push to the tracked branch. The free tier gives you one private app and
unlimited public ones; apps sleep after a stretch of inactivity and wake on the
next visit.

Note that anything you push to a public repo is public, including the response
tallies in `survey_data.py`. If the results are sensitive, keep the repo private
and use the private app slot, or deploy somewhere access-controlled instead.

## Using a different year's data

The 2026 responses are built into `survey_data.py`, so the app runs with no data
files present. To look at other results without touching the code, upload a CSV
from the sidebar; it overrides the built-in data for that session only. The
sidebar also has a download button that hands you the built-in data in the exact
format an upload expects, which is the easiest starting template.

Columns an uploaded CSV needs:

| Column | Meaning |
| --- | --- |
| `Section_num` | Order the sections were asked in |
| `Section` | Section name |
| `Question_num` | Order within the section |
| `Question` | Full question wording |
| `Short label` | Chart label, roughly 32 characters |
| `Job Class` | Must match the names in `CLASS_ORDER` to get its ramp colour |
| the five Likert columns | Response tallies, strongly disagree through strongly agree |
| `No opinion` | Optional, counted toward headcount but excluded from the mean |

To change the built-in default permanently, edit the `QUESTIONS` list in
`survey_data.py`. Each entry holds one question and four tuples of tallies, one
per job class in `CLASSES` order, running strongly disagree through strongly
agree and ending with the no-opinion count.

## Layout

```
app.py                Streamlit UI and chart
survey_data.py        The 2026 response tallies
survey_stats.py       Scoring, intervals, population maths
requirements.txt
.streamlit/config.toml
```

Neither `survey_data.py` nor `survey_stats.py` imports Streamlit, so the numbers
can be checked or reused without launching the app:

```python
from survey_data import build_frame
from survey_stats import estimate, pool

frame = build_frame()
block = frame[(frame.Section == "Job satisfaction") & (frame.Question_num == 4)]
print(estimate(pool(block, ["4. Technician"]), population=21.45))
```
