"""The 2026 SCCWRP staff survey, embedded so the app needs no data files.

Replace the tallies here to make a different year the built-in default, or
leave this alone and upload a CSV from the sidebar to override it for a
session.
"""

from __future__ import annotations

import pandas as pd

YEAR = 2026

# Most senior first. The chart's colour ramp follows this order.
CLASSES = (
    "1. Senior Management",
    "2. Scientist/Engineer",
    "3. Admin, IT, comms",
    "4. Technician",
)

LIKERT_COLS = [
    "1 Strongly disagree",
    "2 Somewhat disagree",
    "3 Neither agree/disagree",
    "4 Somewhat agree",
    "5 Strongly agree",
]

# One entry per question. "counts" holds one tuple per job class in CLASSES
# order, each running:
#   strongly disagree, somewhat disagree, neither, somewhat agree,
#   strongly agree, no opinion
QUESTIONS: list[dict] = [
    {
        "section_num": 1,
        "section": "Job satisfaction",
        "question_num": 1,
        "question": "I enjoy working at SCCWRP.",
        "label": "Enjoy working here",
        "counts": (
            (0, 0, 1, 0, 6, 0),
            (0, 1, 0, 5, 10, 0),
            (0, 0, 0, 3, 5, 0),
            (0, 1, 3, 4, 8, 0),
        ),
    },
    {
        "section_num": 1,
        "section": "Job satisfaction",
        "question_num": 2,
        "question": "I have a healthy work-life balance at SCCWRP.",
        "label": "Healthy work-life balance",
        "counts": (
            (0, 1, 1, 2, 3, 0),
            (1, 1, 1, 5, 8, 0),
            (0, 0, 2, 2, 4, 0),
            (2, 3, 2, 3, 6, 0),
        ),
    },
    {
        "section_num": 1,
        "section": "Job satisfaction",
        "question_num": 3,
        "question": "I would recommend working at SCCWRP to a friend.",
        "label": "Would recommend to a friend",
        "counts": (
            (0, 0, 1, 1, 5, 0),
            (0, 1, 2, 5, 8, 0),
            (0, 0, 0, 3, 5, 0),
            (2, 3, 3, 4, 4, 0),
        ),
    },
    {
        "section_num": 1,
        "section": "Job satisfaction",
        "question_num": 4,
        "question": "I am satisfied with my career development opportunities at SCCWRP.",
        "label": "Career development opportunities",
        "counts": (
            (0, 0, 1, 0, 6, 0),
            (0, 1, 1, 5, 9, 0),
            (1, 0, 1, 3, 2, 1),
            (4, 1, 3, 3, 5, 0),
        ),
    },
    {
        "section_num": 1,
        "section": "Job satisfaction",
        "question_num": 5,
        "question": "I feel appreciated by SCCWRP.",
        "label": "Feel appreciated",
        "counts": (
            (0, 0, 1, 2, 4, 0),
            (0, 0, 2, 7, 7, 0),
            (0, 0, 1, 3, 4, 0),
            (1, 5, 0, 5, 5, 0),
        ),
    },
    {
        "section_num": 1,
        "section": "Job satisfaction",
        "question_num": 6,
        "question": "My team/department works effectively together.",
        "label": "My team works well together",
        "counts": (
            (0, 0, 0, 3, 4, 0),
            (0, 1, 1, 4, 10, 0),
            (0, 0, 2, 3, 3, 0),
            (0, 2, 1, 5, 8, 0),
        ),
    },
    {
        "section_num": 1,
        "section": "Job satisfaction",
        "question_num": 7,
        "question": "My team/department works effectively with other teams/departments.",
        "label": "My team works well with others",
        "counts": (
            (0, 0, 1, 2, 4, 0),
            (0, 0, 1, 7, 8, 0),
            (1, 0, 0, 3, 4, 0),
            (0, 1, 3, 6, 5, 1),
        ),
    },
    {
        "section_num": 1,
        "section": "Job satisfaction",
        "question_num": 8,
        "question": "I have access to the right equipment and training to do my job.",
        "label": "Right equipment and training",
        "counts": (
            (0, 0, 1, 0, 6, 0),
            (0, 1, 0, 4, 11, 0),
            (0, 0, 1, 3, 4, 0),
            (0, 0, 2, 6, 8, 0),
        ),
    },
    {
        "section_num": 1,
        "section": "Job satisfaction",
        "question_num": 9,
        "question": "I receive support from SCCWRP when I ask for it.",
        "label": "Receive support when I ask",
        "counts": (
            (0, 0, 1, 0, 6, 0),
            (0, 0, 2, 7, 7, 0),
            (0, 0, 0, 3, 5, 0),
            (1, 0, 1, 5, 8, 1),
        ),
    },
    {
        "section_num": 1,
        "section": "Job satisfaction",
        "question_num": 10,
        "question": "I feel comfortable expressing ideas and concerns to my supervisor.",
        "label": "Comfortable raising concerns",
        "counts": (
            (1, 0, 0, 0, 6, 0),
            (0, 2, 1, 1, 12, 0),
            (0, 0, 1, 2, 5, 0),
            (1, 2, 0, 6, 7, 0),
        ),
    },
    {
        "section_num": 1,
        "section": "Job satisfaction",
        "question_num": 11,
        "question": "I feel safe filling out this survey truthfully.",
        "label": "Safe answering this survey",
        "counts": (
            (1, 0, 0, 0, 6, 0),
            (0, 1, 0, 3, 12, 0),
            (1, 0, 0, 1, 6, 0),
            (1, 3, 4, 2, 6, 0),
        ),
    },
    {
        "section_num": 2,
        "section": "SCCWRP executive management",
        "question_num": 1,
        "question": "Executive management keeps SCCWRP running smoothly.",
        "label": "Keeps SCCWRP running smoothly",
        "counts": (
            (0, 0, 0, 2, 4, 1),
            (0, 0, 0, 5, 11, 0),
            (0, 0, 0, 2, 5, 1),
            (0, 2, 1, 5, 8, 0),
        ),
    },
    {
        "section_num": 2,
        "section": "SCCWRP executive management",
        "question_num": 2,
        "question": "Executive management has a clear vision for SCCWRP’s directions as an organization.",
        "label": "Has a clear vision",
        "counts": (
            (0, 0, 0, 1, 5, 1),
            (0, 0, 0, 1, 15, 0),
            (0, 0, 0, 2, 5, 1),
            (0, 0, 0, 4, 11, 1),
        ),
    },
    {
        "section_num": 2,
        "section": "SCCWRP executive management",
        "question_num": 3,
        "question": "Executive management communicates well with SCCWRP staff.",
        "label": "Communicates well with staff",
        "counts": (
            (0, 1, 1, 3, 1, 1),
            (0, 3, 4, 6, 3, 0),
            (0, 1, 0, 3, 4, 0),
            (0, 3, 6, 3, 3, 1),
        ),
    },
    {
        "section_num": 2,
        "section": "SCCWRP executive management",
        "question_num": 4,
        "question": "Executive management leads by example.",
        "label": "Leads by example",
        "counts": (
            (0, 0, 1, 2, 3, 1),
            (0, 1, 1, 6, 8, 0),
            (0, 1, 0, 3, 4, 0),
            (1, 2, 6, 3, 3, 1),
        ),
    },
    {
        "section_num": 3,
        "section": "Understanding of SCCWRP",
        "question_num": 1,
        "question": "I understand SCCWRP's mission.",
        "label": "Understand the mission",
        "counts": (
            (0, 0, 0, 1, 6, 0),
            (0, 0, 0, 0, 16, 0),
            (0, 0, 1, 2, 5, 0),
            (0, 0, 0, 5, 11, 0),
        ),
    },
    {
        "section_num": 3,
        "section": "Understanding of SCCWRP",
        "question_num": 2,
        "question": "I understand how the work I do advances SCCWRP’s mission.",
        "label": "My work advances the mission",
        "counts": (
            (0, 0, 0, 1, 6, 0),
            (0, 0, 0, 4, 12, 0),
            (0, 0, 0, 3, 5, 0),
            (0, 1, 2, 3, 10, 0),
        ),
    },
    {
        "section_num": 3,
        "section": "Understanding of SCCWRP",
        "question_num": 3,
        "question": "I understand how SCCWRP evaluates my job performance.",
        "label": "Understand my performance review",
        "counts": (
            (0, 0, 0, 1, 6, 0),
            (0, 1, 1, 2, 12, 0),
            (0, 1, 1, 1, 5, 0),
            (1, 2, 2, 6, 5, 0),
        ),
    },
    {
        "section_num": 3,
        "section": "Understanding of SCCWRP",
        "question_num": 4,
        "question": "I understand how SCCWRP evaluates the organization's performance.",
        "label": "Understand org performance review",
        "counts": (
            (0, 0, 0, 1, 6, 0),
            (0, 1, 0, 4, 11, 0),
            (0, 0, 3, 0, 5, 0),
            (1, 0, 4, 5, 6, 0),
        ),
    },
    {
        "section_num": 3,
        "section": "Understanding of SCCWRP",
        "question_num": 5,
        "question": "I understand SCCWRP’s business model.",
        "label": "Understand the business model",
        "counts": (
            (0, 0, 0, 1, 6, 0),
            (0, 1, 0, 7, 8, 0),
            (0, 0, 2, 1, 5, 0),
            (1, 2, 2, 7, 4, 0),
        ),
    },
    {
        "section_num": 4,
        "section": "Working at SCCWRP",
        "question_num": 1,
        "question": "SCCWRP fosters a safe, inclusive work environment.",
        "label": "Safe, inclusive environment",
        "counts": (
            (0, 0, 1, 0, 6, 0),
            (0, 1, 0, 4, 11, 0),
            (0, 0, 0, 1, 7, 0),
            (0, 3, 1, 4, 8, 0),
        ),
    },
    {
        "section_num": 4,
        "section": "Working at SCCWRP",
        "question_num": 2,
        "question": "SCCWRP values its employees.",
        "label": "Values its employees",
        "counts": (
            (0, 0, 1, 1, 5, 0),
            (0, 0, 2, 7, 7, 0),
            (0, 0, 1, 3, 4, 0),
            (1, 2, 3, 7, 3, 0),
        ),
    },
    {
        "section_num": 4,
        "section": "Working at SCCWRP",
        "question_num": 3,
        "question": "SCCWRP treats its employees fairly.",
        "label": "Treats employees fairly",
        "counts": (
            (0, 0, 1, 1, 5, 0),
            (0, 2, 1, 6, 7, 0),
            (0, 0, 1, 1, 6, 0),
            (2, 2, 2, 6, 4, 0),
        ),
    },
    {
        "section_num": 4,
        "section": "Working at SCCWRP",
        "question_num": 4,
        "question": "SCCWRP’s staff is diverse.",
        "label": "Staff is diverse",
        "counts": (
            (0, 1, 1, 1, 4, 0),
            (0, 2, 2, 9, 3, 0),
            (0, 0, 1, 3, 4, 0),
            (0, 2, 1, 5, 8, 0),
        ),
    },
]


def build_frame() -> pd.DataFrame:
    """Expand QUESTIONS into the long-format frame the app works with."""
    records = []
    for q in QUESTIONS:
        for job_class, tallies in zip(CLASSES, q["counts"]):
            record = {
                "Section_num": q["section_num"],
                "Section": q["section"],
                "Question_num": q["question_num"],
                "Question": q["question"],
                "Short label": q["label"],
                "Job Class": job_class,
                "No opinion": tallies[5],
                "Year": YEAR,
            }
            record.update(dict(zip(LIKERT_COLS, tallies[:5])))
            records.append(record)

    columns = [
        "Section_num", "Section", "Question_num", "Question", "Short label",
        "Job Class", *LIKERT_COLS, "No opinion", "Year",
    ]
    return pd.DataFrame.from_records(records)[columns]
