"""Generate fictional Egyptian education-center student snapshots and future outcomes."""

import argparse
import logging
from pathlib import Path

import numpy as np
import pandas as pd

DEFAULT_PATH = Path(__file__).resolve().parent / "raw" / "student_academic_risk.csv"
FIRST = "آية مريم نور سلمى ياسمين منة ليلى فاطمة ملك هنا يوسف عمر كريم مروان آسر سليم علي زياد أحمد أدهم".split()
FAMILY = "منصور الشرقاوي شريف الجندي المصري النجار زهران شاهين حسن إبراهيم خليل رضوان حمدي خيري السعيد".split()


def generate_data(count: int = 3000, seed: int = 42) -> pd.DataFrame:
    """Simulate one pre-outcome snapshot per fictional student."""
    if count < 1:
        raise ValueError("count must be positive")
    rng = np.random.default_rng(seed)
    group = rng.integers(0, 30, count)
    group_effect = rng.normal(0, 2, 30)[group]
    engagement = rng.normal(0, 1, count)
    mastery = 0.46 * engagement + 0.89 * rng.normal(size=count)
    attendance_p = 1 / (1 + np.exp(-(1.38 + 0.85 * engagement)))
    # Last eight eligible sessions. Unknown and excused marks are outside the rate denominator.
    statuses = rng.random((count, 8))
    recorded = statuses >= 0.07
    present = recorded & (statuses < 0.07 + 0.93 * attendance_p[:, None])
    missed = (recorded & ~present).sum(axis=1)
    prior_present = rng.binomial(16, attendance_p)
    attendance = (prior_present + present.sum(axis=1)) / (16 + recorded.sum(axis=1))
    homework = rng.binomial(14, 1 / (1 + np.exp(-(1.13 + engagement)))) / 14
    participation = np.clip(66 + 16 * engagement + rng.normal(0, 9, count), 0, 100)
    level = 66 + 12 * mastery + group_effect + 4 * engagement
    change = rng.normal(0, 3.5, count)
    quizzes = np.clip(level[:, None] + change[:, None] * np.arange(-2, 3)
                      + rng.normal(0, 6, (count, 5)), 0, 100)
    midterm = np.clip(level + rng.normal(0, 8, count), 0, 100)
    # A later assessment with independent variation supplies the label only.
    future = (0.36 * level + 0.22 * midterm + 0.16 * quizzes[:, -1]
              + 12 * homework + 9 * attendance + 0.05 * participation
              + 1.4 * change + rng.normal(0, 7, count))
    fees = np.where(rng.random(count) < 0.23, 1 + rng.negative_binomial(2, 0.17, count), 0)
    names = [" ".join(parts) for parts in zip(rng.choice(FIRST, count),
                                               rng.choice(FAMILY, count), rng.choice(FAMILY, count))]
    data = pd.DataFrame({
        "student_id": [f"EG-{i:05d}" for i in range(1, count + 1)],
        "name": names, "group_id": [f"G-{i + 1:02d}" for i in group],
        "attendance_rate": attendance.round(4), "homework_completion_rate": homework.round(4),
        "average_quiz_score": quizzes.mean(axis=1).round(2), "midterm_score": midterm.round(2),
        "participation_score": participation.round(2), "missed_sessions_count": missed,
        "fee_delayed_days": fees, "is_at_risk": (future < 57).astype(int),
    })
    for index, field in enumerate(("quiz_oldest", "quiz_middle", "quiz_latest"), start=2):
        data[field] = quizzes[:, index].round(2)
        data.loc[rng.random(count) < 0.12, field] = np.nan
    for field in ("midterm_score", "participation_score", "average_quiz_score"):
        data.loc[rng.random(count) < 0.03, field] = np.nan
    return data


def main() -> None:
    """Write a reproducible UTF-8 raw CSV."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=3000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=DEFAULT_PATH)
    args = parser.parse_args()
    data = generate_data(args.count, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(args.output, index=False, encoding="utf-8", lineterminator="\n")
    logging.basicConfig(level=logging.INFO)
    logging.info("Wrote %d synthetic students to %s", len(data), args.output)


if __name__ == "__main__":
    main()
