"""
Shared data layer for the AVYU Team Portal (Streamlit edition).

Persists to a local JSON file so Admin and all 4 interns see the same
live data no matter which browser/device they're on — as long as they're
all pointed at the same running app instance.

IMPORTANT — read this before you deploy:
Streamlit Community Cloud's filesystem is EPHEMERAL. Every time the app
sleeps/restarts or you push a new commit, this JSON file is wiped and you
lose all data. For anything beyond a quick trial, swap `load_store` /
`save_store` below for a real database (see README.md for options).
"""
import json
import os
import threading
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DATA_FILE = os.path.join(DATA_DIR, "avyu_store.json")
_lock = threading.Lock()

# ---------------------------------------------------------------------------
# Accounts — change these before handing the app to your real team.
# ---------------------------------------------------------------------------
USERS = {
    "admin":   {"password": "admin@2026",  "role": "admin",  "name": "Mani Sir"},
    "intern1": {"password": "lead@123",    "role": "intern", "id": "intern1",
                "name": "Intern 1", "role_title": "Lead Scout — LinkedIn", "accent": "#7F77DD"},
    "intern2": {"password": "reddit@123",  "role": "intern", "id": "intern2",
                "name": "Intern 2", "role_title": "Reddit Ranger", "accent": "#1D9E75"},
    "intern3": {"password": "content@123", "role": "intern", "id": "intern3",
                "name": "Intern 3", "role_title": "Content Creator (Shorts)", "accent": "#BA7517"},
    "intern4": {"password": "manager@123", "role": "intern", "id": "intern4",
                "name": "Intern 4", "role_title": "Lead Manager (Tracker)", "accent": "#D85A30"},
}

DEFAULT_TASKS = {
    "intern1": [
        "Find 20 new SME leads",
        "Send 20 LinkedIn/email messages",
        "Follow up on any hot leads from yesterday",
        "Log everything in the Lead Pipeline sheet",
    ],
    "intern2": [
        "Post 10 Reddit comments across target subreddits",
        "Check replies on previous comments",
        "Log thread links + upvotes in the Reddit Tracker",
    ],
    "intern3": [
        "Edit and upload 2 Shorts",
        "Check 24-hour view counts on yesterday's posts",
        "Get today's script approved before recording",
    ],
    "intern4": [
        "Log all quiz submissions within 2 hours",
        "Calculate risk scores and flag CRITICAL rows",
        "Prepare draft replies for every quiz taker",
        "Sheet fully updated by 5pm",
    ],
}

INTERN_IDS = [uid for uid, u in USERS.items() if u["role"] == "intern"]


# ---------------------------------------------------------------------------
# Store shape + persistence
# ---------------------------------------------------------------------------
def _empty_intern_record():
    return {
        "leads": [],
        "worklinks": [],
        "status_history": [],
        "current_status": None,
        "tasks_by_date": {},
        "time_sessions": [],
        "active_session": None,
    }


def _empty_store():
    return {
        "users": USERS.copy(),
        "interns": {uid: _empty_intern_record() for uid in INTERN_IDS},
        "profiles": {},
        "chat": [],
    }


def _ensure_file():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump(_empty_store(), f, indent=2)


def load_store():
    """Read the shared store from disk, patching in any fields older data might be missing."""
    _ensure_file()
    with _lock:
        try:
            with open(DATA_FILE, "r") as f:
                store = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            store = _empty_store()

    store.setdefault("users", USERS.copy())
    store.setdefault("interns", {})
    store.setdefault("profiles", {})
    store.setdefault("chat", [])
    for uid in INTERN_IDS:
        store["interns"].setdefault(uid, _empty_intern_record())
    for rec in store["interns"].values():
        rec.setdefault("leads", [])
        rec.setdefault("worklinks", [])
        rec.setdefault("status_history", [])
        rec.setdefault("current_status", None)
        rec.setdefault("tasks_by_date", {})
        rec.setdefault("time_sessions", [])
        rec.setdefault("active_session", None)
    return store


def save_store(store):
    """Atomic-ish write: write to a temp file then swap it in, so a crash mid-write can't corrupt data."""
    with _lock:
        os.makedirs(DATA_DIR, exist_ok=True)
        tmp_path = DATA_FILE + ".tmp"
        with open(tmp_path, "w") as f:
            json.dump(store, f, indent=2)
        os.replace(tmp_path, DATA_FILE)


# ---------------------------------------------------------------------------
# Daily tasks
# ---------------------------------------------------------------------------
def today_key():
    return datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d")


def pretty_date(key):
    d = datetime.strptime(key, "%Y-%m-%d")
    return d.strftime("%A, %d %B")


def default_tasks_for(intern_id):
    return [{"id": f"d{i}", "text": t, "done": False} for i, t in enumerate(DEFAULT_TASKS.get(intern_id, []))]


def get_today_tasks(record, intern_id):
    """Returns (and lazily creates) today's checklist inside an already-loaded intern record."""
    key = today_key()
    if key not in record["tasks_by_date"]:
        record["tasks_by_date"][key] = {"items": default_tasks_for(intern_id)}
    return record["tasks_by_date"][key]


def compute_streak(record):
    """Consecutive days with every task checked off. Today doesn't break the streak while it's still in progress."""
    streak = 0
    cursor = datetime.now(ZoneInfo("Asia/Kolkata"))
    for i in range(365):
        key = cursor.strftime("%Y-%m-%d")
        day = record["tasks_by_date"].get(key)
        all_done = bool(day) and len(day["items"]) > 0 and all(t["done"] for t in day["items"])
        if i == 0 and not all_done:
            cursor -= timedelta(days=1)
            continue
        if not all_done:
            break
        streak += 1
        cursor -= timedelta(days=1)
    return streak


# ---------------------------------------------------------------------------
# Time tracking
# ---------------------------------------------------------------------------
def start_of_week(dt):
    d = dt - timedelta(days=dt.weekday())  # Monday = 0
    return d.replace(hour=0, minute=0, second=0, microsecond=0)


def summarize_time(record):
    """Returns (today_ms, week_ms, all_ms), counting a currently-running session live."""
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = start_of_week(now)
    today_ms = week_ms = all_ms = 0

    for s in record["time_sessions"]:
        dur = s["duration_ms"]
        all_ms += dur
        start_dt = datetime.fromtimestamp(..., ZoneInfo("Asia/Kolkata"))
        if start_dt >= today_start:
            today_ms += dur
        if start_dt >= week_start:
            week_ms += dur

    active = record.get("active_session")
    if active:
        live_ms = now.timestamp() * 1000 - active["start"]
        all_ms += live_ms
        start_dt = datetime.fromtimestamp(..., ZoneInfo("Asia/Kolkata"))
        if start_dt >= today_start:
            today_ms += live_ms
        if start_dt >= week_start:
            week_ms += live_ms

    return today_ms, week_ms, all_ms


def ms_to_hm(ms):
    total_min = max(0, round(ms / 60000))
    return f"{total_min // 60}h {total_min % 60}m"


def ms_to_hms(ms):
    total_sec = max(0, int(ms / 1000))
    h, rem = divmod(total_sec, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def fmt_ts(ms):
    return datetime.fromtimestamp(ms / 1000, IST).strftime("%d %b, %I:%M %p")


def fmt_clock(ms):
    return datetime.fromtimestamp(ms / 1000, IST).strftime("%I:%M %p")

def fmt_date_short(ms):
    return datetime.fromtimestamp(ms / 1000, IST).strftime("%d %b")


def now_ms():
    return int(datetime.now(IST).timestamp() * 1000)
