# progress_store.py
"""
Lightweight local JSON-backed persistence for practice/quiz results and
activity history.

Why this exists: the Home/Progress/Profile screens must reflect *real*
usage, not fabricated numbers. This module is the single source of truth
for that data, stored at data_store/progress.json (gitignored, local to
this machine).
"""
import json
import os
from datetime import date, datetime

STORE_PATH = os.path.join("data_store", "progress.json")

_DEFAULT = {
    "activity": [],
    "practice_sessions": [],
    "quiz_sessions": [],
}


def _ensure_dir():
    os.makedirs(os.path.dirname(STORE_PATH), exist_ok=True)


def load_store():
    _ensure_dir()
    if not os.path.exists(STORE_PATH):
        return {k: list(v) for k, v in _DEFAULT.items()}
    try:
        with open(STORE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        for key, default in _DEFAULT.items():
            data.setdefault(key, list(default))
        return data
    except (json.JSONDecodeError, OSError):
        return {k: list(v) for k, v in _DEFAULT.items()}


def save_store(data):
    _ensure_dir()
    with open(STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def log_activity(kind, subject, chapter, detail):
    """kind: 'tutor' | 'practice' | 'quiz'"""
    data = load_store()
    data["activity"].insert(0, {
        "type": kind,
        "subject": subject,
        "chapter": chapter,
        "detail": detail,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    })
    data["activity"] = data["activity"][:50]
    save_store(data)


def log_practice_result(subject, chapter, difficulty, total, correct):
    data = load_store()
    data["practice_sessions"].append({
        "subject": subject, "chapter": chapter, "difficulty": difficulty,
        "total": total, "correct": correct,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    })
    save_store(data)
    log_activity("practice", subject, chapter, f"{correct}/{total} correct")


def log_quiz_result(subject, chapter, difficulty, total, correct, time_taken_sec=None):
    data = load_store()
    data["quiz_sessions"].append({
        "subject": subject, "chapter": chapter, "difficulty": difficulty,
        "total": total, "correct": correct, "time_taken_sec": time_taken_sec,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    })
    save_store(data)
    log_activity("quiz", subject, chapter, f"{correct}/{total} correct")


def get_stats():
    """Compute all derived stats from real logged sessions/activity."""
    data = load_store()
    sessions = data["practice_sessions"] + data["quiz_sessions"]

    total_q = sum(s["total"] for s in sessions)
    total_correct = sum(s["correct"] for s in sessions)
    accuracy = round((total_correct / total_q) * 100) if total_q else 0

    activity_dates = sorted(
        {datetime.fromisoformat(a["timestamp"]).date() for a in data["activity"]},
        reverse=True,
    )
    streak = 0
    if activity_dates:
        cursor = date.today()
        for d in activity_dates:
            if d == cursor:
                streak += 1
                cursor = date.fromordinal(cursor.toordinal() - 1)
            elif d < cursor:
                break

    def _accuracy_by(key):
        buckets = {}
        for s in sessions:
            b = buckets.setdefault(s[key], {"total": 0, "correct": 0})
            b["total"] += s["total"]
            b["correct"] += s["correct"]
        return {
            k: round((v["correct"] / v["total"]) * 100) if v["total"] else 0
            for k, v in buckets.items()
        }

    subject_accuracy = _accuracy_by("subject")
    chapter_accuracy = _accuracy_by("chapter")
    weak_topics = sorted(chapter_accuracy.items(), key=lambda kv: kv[1])[:5]

    return {
        "total_questions": total_q,
        "total_sessions": len(sessions),
        "accuracy": accuracy,
        "streak": streak,
        "concepts": len(chapter_accuracy),
        "subject_accuracy": subject_accuracy,
        "chapter_accuracy": chapter_accuracy,
        "weak_topics": weak_topics,
        "recent_activity": data["activity"][:8],
        "activity_dates": activity_dates,
    }
