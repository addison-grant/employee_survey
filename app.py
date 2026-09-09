"""SCCWRP staff survey explorer.

Run locally with:  streamlit run app.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from survey_stats import (
    LIKERT_COLS,
    estimate,
    group_populations,
    load_survey,
    pool,
)

DATA_FILE = Path(__file__).parent / "data" / "sccwrp_survey_2026.csv"

# Job classes from most senior to least. The colour ramp runs dark navy for the
# most senior down to bright blue for the least, so the chart reads as a
# seniority gradient without needing labels on the bars.
CLASS_ORDER = [
    "1. Senior Management",
    "2. Scientist/Engineer",
    "3. Admin, IT, comms",
    "4. Technician",
]
CLASS_LABELS = {
    "1. Senior Management": "Senior management",
    "2. Scientist/Engineer": "Scientist/engineer",
    "3. Admin, IT, comms": "Admin, IT, comms",
    "4. Technician": "Technician",
}
RAMP = {
    "1. Senior Management": "#042C53",
    "2. Scientist/Engineer": "#185FA5",
    "3. Admin, IT, comms": "#378ADD",
    "4. Technician": "#7FBEF2",
}
POOLED_COLOUR = "#8A8880"

# Clicking a group cycles through these in order.
CYCLE = {"include": "singled", "singled": "exclude", "exclude": "include"}
STATE_GLYPH = {"include": "\u2003", "singled": "\u2714", "exclude": "\u2715"}
STATE_HELP = {
    "include": "Folded into Everyone else. Click to give it its own bar.",
    "singled": "Shown as its own bar. Click to drop it from the chart.",
    "exclude": "Left off the chart. Click to fold it back into Everyone else.",
}

SORT_DEFAULT = "Survey order"

st.set_page_config(page_title="SCCWRP staff survey", layout="wide")


# ---------------------------------------------------------------- data


@st.cache_data(show_spinner=False)
def read_default() -> pd.DataFrame:
    return load_survey(DATA_FILE)


with st.sidebar:
    st.markdown("### Data")
    upload = st.file_uploader(
        "Use a different survey file",
        type="csv",
        help="Same columns as data/sccwrp_survey_2026.csv. Leave empty for the 2026 results.",
    )

if upload is not None:
    try:
        data = load_survey(upload)
        st.sidebar.success(f"Loaded {upload.name}")
    except Exception as exc:  # noqa: BLE001 - surfaced to the user verbatim
        st.sidebar.error(str(exc))
        data = read_default()
else:
    data = read_default()

sections = (
    data[["Section_num", "Section"]]
    .drop_duplicates()
    .sort_values("Section_num")["Section"]
    .tolist()
)
present_classes = [c for c in CLASS_ORDER if c in set(data["Job Class"])]
present_classes += [c for c in data["Job Class"].unique() if c not in present_classes]

# How many people are in each class, taken as the largest number who answered
# any single question. "No opinion" still counts as a person on staff.
_answer_cols = LIKERT_COLS + (["No opinion"] if "No opinion" in data.columns else [])
_per_row = data.assign(_n=data[_answer_cols].sum(axis=1))
respondents = {
    c: int(_per_row.loc[_per_row["Job Class"] == c, "_n"].max()) for c in present_classes
}
total_responded = sum(respondents.values())


# ---------------------------------------------------------------- state

# Rebuilt whenever the set of job classes changes, so uploading a file with
# different classes cannot leave stale keys behind.
if st.session_state.get("group_state_keys") != present_classes:
    st.session_state.group_state = {
        c: ("singled" if c == "4. Technician" else "include") for c in present_classes
    }
    st.session_state.group_state_keys = present_classes


def cycle_group(job_class: str) -> None:
    current = st.session_state.group_state[job_class]
    st.session_state.group_state[job_class] = CYCLE[current]


# ---------------------------------------------------------------- controls

st.title("SCCWRP staff survey, 2026")

section_choice = st.radio(
    "Question group",
    ["All questions", *sections],
    horizontal=True,
    label_visibility="collapsed",
)

with st.container(border=True):
    st.caption(
        "Click a group to cycle it: blank folds it into Everyone else, "
        "a check gives it its own bar, a cross drops it from the chart."
    )

    overrides: dict[str, int | None] = {}
    for job_class in present_classes:
        state = st.session_state.group_state[job_class]
        cols = st.columns([0.7, 3.1, 1.7, 2.4], vertical_alignment="center")

        cols[0].button(
            STATE_GLYPH[state],
            key=f"cycle_{job_class}",
            on_click=cycle_group,
            args=(job_class,),
            help=STATE_HELP[state],
            width="stretch",
        )

        swatch = (
            RAMP.get(job_class, POOLED_COLOUR)
            if state == "singled"
            else POOLED_COLOUR
            if state == "include"
            else "transparent"
        )
        name = CLASS_LABELS.get(job_class, job_class)
        if state == "exclude":
            name = f"<s>{name}</s>"
        cols[1].markdown(
            f"<div style='display:flex;align-items:center;gap:9px;'>"
            f"<span style='width:11px;height:11px;border-radius:3px;background:{swatch};"
            f"border:1px solid rgba(128,128,128,.45);flex-shrink:0'></span>"
            f"<span style='opacity:{0.5 if state == 'exclude' else 1}'>{name}</span></div>",
            unsafe_allow_html=True,
        )

        cols[2].markdown(
            f"<span style='opacity:.6;font-size:.86rem'>{respondents[job_class]} responded</span>",
            unsafe_allow_html=True,
        )

        raw = cols[3].number_input(
            f"of N on staff ({job_class})",
            min_value=respondents[job_class],
            max_value=500,
            value=None,
            step=1,
            placeholder="auto",
            key=f"pop_{job_class}",
            label_visibility="collapsed",
        )
        overrides[job_class] = int(raw) if raw is not None else None

    left, right = st.columns([1, 3])
    total_staff = left.number_input(
        "Total staff",
        min_value=total_responded,
        max_value=1000,
        value=63,
        step=1,
        help="Used for job classes whose headcount you have left on auto.",
    )
    right.caption(
        "Headcount boxes are optional. A group left on auto is assumed to hold the same "
        "share of the staff as it holds of the responses."
    )

populations = group_populations(respondents, overrides, int(total_staff))
implied_total = sum(populations.values())

singled = [c for c in present_classes if st.session_state.group_state[c] == "singled"]
included = [c for c in present_classes if st.session_state.group_state[c] == "include"]

c1, c2, c3, c4 = st.columns([1.5, 1.4, 1.6, 1.5])
interval_mode = c1.radio(
    "Interval", ["Census-adjusted", "Standard"], horizontal=True,
    help=(
        "Census-adjusted narrows the interval because there are only so many staff whose "
        "opinion you have not heard. Standard treats these responses as a sample from an "
        "open-ended pool."
    ),
)
adjusted = interval_mode == "Census-adjusted"

sort_order = c2.selectbox("Sort", [SORT_DEFAULT, "Lowest score first", "Highest score first"])
sort_basis = c3.selectbox(
    "Score used for sorting",
    ["All staff", "Everyone else", "Singled-out groups"],
    disabled=sort_order == SORT_DEFAULT,
)
bar_height = c4.slider("Bar height", 4, 26, 12, help="Thickness of each bar in pixels.")


# ---------------------------------------------------------------- series

series: list[dict] = [
    {
        "key": c,
        "label": CLASS_LABELS.get(c, c),
        "members": [c],
        "population": populations[c],
        "colour": RAMP.get(c, POOLED_COLOUR),
    }
    for c in singled
]
if included:
    series.append(
        {
            "key": "__pooled__",
            "label": "Everyone else" if singled else "All staff",
            "members": included,
            "population": sum(populations[c] for c in included),
            "colour": POOLED_COLOUR,
        }
    )

basis_members = present_classes
basis_fallback = False
if sort_order != SORT_DEFAULT:
    if sort_basis == "Singled-out groups":
        basis_members, basis_fallback = (singled, False) if singled else (present_classes, True)
    elif sort_basis == "Everyone else":
        basis_members, basis_fallback = (included, False) if included else (present_classes, True)

visible = data if section_choice == "All questions" else data[data["Section"] == section_choice]
questions = (
    visible[["Section_num", "Section", "Question_num", "Question", "Short label"]]
    .drop_duplicates()
    .sort_values(["Section_num", "Question_num"])
)

rows = []
for _, q in questions.iterrows():
    block = visible[
        (visible["Section"] == q["Section"]) & (visible["Question_num"] == q["Question_num"])
    ]
    bars = []
    for s in series:
        est = estimate(pool(block, s["members"]), s["population"])
        if est is not None:
            bars.append({**s, "est": est})
    basis = estimate(pool(block, basis_members), implied_total)
    rows.append(
        {
            "section": q["Section"],
            "section_num": int(q["Section_num"]),
            "question_num": int(q["Question_num"]),
            "label": q["Short label"],
            "full": q["Question"],
            "bars": bars,
            "sort_key": basis.mean if basis else 0.0,
        }
    )

if sort_order == "Lowest score first":
    rows.sort(key=lambda r: (r["sort_key"], r["section_num"], r["question_num"]))
elif sort_order == "Highest score first":
    rows.sort(key=lambda r: (-r["sort_key"], r["section_num"], r["question_num"]))
else:
    rows.sort(key=lambda r: (r["section_num"], r["question_num"]))

show_headers = sort_order == SORT_DEFAULT and section_choice == "All questions"

st.caption(
    f"{total_responded} of {implied_total:,.0f} staff responded "
    f"({total_responded / implied_total:.0%}). Each bar is a 95% range for that group's mean "
    "on that question; the notch inside it is the observed mean."
)

if basis_fallback:
    st.warning(
        f"No group is currently {'singled out' if sort_basis == 'Singled-out groups' else 'folded into Everyone else'}, "
        "so the sort is using all staff instead."
    )


# ---------------------------------------------------------------- chart

if not series:
    st.info("Every group is dropped from the chart. Click a cross to bring one back.")
    st.stop()

ROW_PAD = 16
HEADER_H = 34
row_height = len(series) * bar_height + (len(series) - 1) * 3 + ROW_PAD

layout_rows = []
y = 0.0
last_section = None
for row in rows:
    if show_headers and row["section"] != last_section:
        layout_rows.append({"kind": "header", "y": y, "section": row["section"]})
        y += HEADER_H
        last_section = row["section"]
    layout_rows.append({"kind": "item", "y": y, "row": row})
    y += row_height
chart_height = y + 46

fig = go.Figure()
tick_positions, tick_labels = [], []
shapes, annotations = [], []

for entry in layout_rows:
    if entry["kind"] == "header":
        annotations.append(
            dict(
                xref="paper", x=0, xanchor="left",
                yref="y", y=entry["y"] + HEADER_H / 2, yanchor="middle",
                text=f"<b>{entry['section']}</b>",
                showarrow=False, font=dict(size=12.5), opacity=0.75,
            )
        )
        shapes.append(
            dict(
                type="line", xref="paper", x0=0, x1=1,
                yref="y", y0=entry["y"] + HEADER_H - 4, y1=entry["y"] + HEADER_H - 4,
                line=dict(width=1), opacity=0.18, layer="below",
            )
        )
        continue

    row = entry["row"]
    block_h = len(series) * bar_height + (len(series) - 1) * 3
    start = entry["y"] + (row_height - block_h) / 2
    tick_positions.append(entry["y"] + row_height / 2)
    tick_labels.append(row["label"])

    for i, bar in enumerate(row["bars"]):
        est = bar["est"]
        centre = start + i * (bar_height + 3) + bar_height / 2
        lo, hi = est.bounds(adjusted)
        wide_lo, wide_hi = est.bounds(False)

        # Standard interval, drawn faintly behind the solid bar.
        fig.add_trace(
            go.Scatter(
                x=[wide_lo, wide_hi], y=[centre, centre],
                mode="lines",
                line=dict(color=bar["colour"], width=max(1.5, bar_height / 3)),
                opacity=0.28, hoverinfo="skip", showlegend=False,
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[lo, hi], y=[centre, centre],
                mode="lines",
                line=dict(color=bar["colour"], width=bar_height),
                showlegend=False,
                hovertemplate=(
                    f"<b>{row['label']}</b><br>{bar['label']} &middot; n={est.n}"
                    f"<br>Mean {est.mean:.2f}"
                    f"<br>{interval_mode} range {lo:.2f}\u2013{hi:.2f}<extra></extra>"
                ),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[est.mean], y=[centre],
                mode="markers",
                marker=dict(
                    symbol="line-ns", size=bar_height,
                    line=dict(color="rgba(255,255,255,.85)", width=max(1, bar_height / 7)),
                ),
                hoverinfo="skip", showlegend=False,
            )
        )

lows = [b["est"].bounds(adjusted)[0] for r in rows for b in r["bars"]]
highs = [b["est"].bounds(adjusted)[1] for r in rows for b in r["bars"]]
x_lo = max(1.0, (min(lows) - 0.12) // 0.25 * 0.25) if lows else 3.0
x_hi = min(5.0, -(-(max(highs) + 0.12) // 0.25) * 0.25) if highs else 5.0
if x_hi - x_lo < 0.75:
    x_hi = min(5.0, x_lo + 0.75)

fig.update_layout(
    height=chart_height,
    margin=dict(l=210, r=24, t=34, b=12),
    shapes=shapes,
    annotations=annotations,
    hovermode="closest",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(
        range=[x_lo, x_hi], side="top", dtick=0.25,
        gridcolor="rgba(128,128,128,.18)", zeroline=False,
        title=None, fixedrange=True,
    ),
    yaxis=dict(
        range=[y, 0], tickmode="array",
        tickvals=tick_positions, ticktext=tick_labels,
        showgrid=False, zeroline=False, fixedrange=True,
    ),
)

st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

st.caption(
    "The faint line behind each bar is the standard 95% interval. The solid bar is that "
    "interval after the finite population correction, which assumes the staff who did not "
    "respond think like the staff who did."
)

with st.expander("Download the numbers behind this chart"):
    export = pd.DataFrame(
        [
            {
                "Section": r["section"],
                "Question_num": r["question_num"],
                "Question": r["full"],
                "Group": b["label"],
                "n": b["est"].n,
                "Mean": round(b["est"].mean, 3),
                "Low": round(b["est"].bounds(adjusted)[0], 3),
                "High": round(b["est"].bounds(adjusted)[1], 3),
                "Interval": interval_mode,
                "Assumed group size": round(b["population"], 1),
            }
            for r in rows
            for b in r["bars"]
        ]
    )
    st.dataframe(export, width="stretch", hide_index=True)
    st.download_button(
        "Download CSV",
        export.to_csv(index=False).encode("utf-8"),
        file_name="sccwrp_survey_estimates.csv",
        mime="text/csv",
    )
