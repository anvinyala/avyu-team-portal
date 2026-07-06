# AVYU Team Portal — Streamlit edition

A Python/Streamlit rebuild of the HTML portal: Admin + 4 interns (Lead Scout,
Reddit Ranger, Content Creator, Lead Manager), with daily task checklists,
a work timer, lead/work-link logging, a live team chat, and reference
material (training, scripts, sheet layout, KPIs, incentives, scale plan, SOP).

## Files

```
app.py            Main app — pages, navigation, all UI
avyu_data.py      Data layer: shared JSON-file storage, task/time math
content.py        Static reference content (training, scripts, SOP, etc.)
requirements.txt  Python dependencies
.streamlit/config.toml   Theme colors
data/             Created automatically on first run — holds avyu_store.json
```

## Run it locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the URL it prints (usually `http://localhost:8501`). Log in with:

- **Admin:** `admin` / `admin@2026`
- **Interns:** `intern1`–`intern4` / `lead@123`, `reddit@123`, `content@123`, `manager@123`

**Change these before giving real people access** — edit the `USERS` dict at
the top of `avyu_data.py`.

## Deploying so your team can actually use it

The simplest free option is **Streamlit Community Cloud**:

1. Push this folder to a GitHub repo.
2. Go to [share.streamlit.io](https://share.streamlit.io), connect the repo, point it at `app.py`.
3. Share the resulting URL with Admin and all 4 interns — everyone opens the *same* link.

Because it's one shared web app instance, everyone who opens that link sees
the same live data (unlike the old HTML file, which only synced through a
live Claude artifact link).

## ⚠️ Important limitation: data persistence

This app stores data in a local JSON file (`data/avyu_store.json`) for
simplicity. That's fine for local use or a quick trial, but:

- **Streamlit Community Cloud's disk is ephemeral.** Every time the app
  restarts (goes to sleep from inactivity, gets redeployed, etc.), this file
  is wiped and all leads/tasks/chat history are lost.
- It also won't survive if you ever run multiple instances behind a load
  balancer (each instance would have its own file).

**For anything beyond a trial, swap in a real database.** The only two
functions you need to change are `load_store()` and `save_store()` in
`avyu_data.py` — everything else reads/writes through them, so the rest of
the app doesn't need to change. Good low-effort options:

- **Supabase** (free tier, Postgres + simple Python client) — store the
  whole store as one JSON row, or normalize into real tables later.
- **Firebase Firestore** — similar idea, generous free tier.
- **A small SQLite file on a persistent volume** if you self-host (e.g. a
  ₹300/month VPS) instead of Streamlit Community Cloud.

Happy to wire up any of these for you — just say which one.

## What's the same as the HTML version, and what's different

**Same:** all 4 intern roles, daily task checklists that reset every day,
the work timer with today/week/all-time totals, leads + work links logging,
live team chat, profile editing, CSV export, streak badges, "working now"
indicators, and all the reference content (training, scripts, sheet layout,
KPIs, incentives, scale plan, SOP).

**Different / better:**
- Real hosting — no more "must stay open as a live Claude artifact."
- Native Streamlit widgets (forms, tables, metrics) instead of hand-rolled HTML/CSS.
- Live-updating panels (Team Activity, Team Chat, Daily Tasks & Time, the
  running timer) use `st.fragment(run_every=...)` so they refresh without
  reloading the whole page — needs Streamlit ≥ 1.37 (already pinned in
  `requirements.txt`).

**Not carried over (let me know if you want any of these back):**
- The exact original visual styling — this uses Streamlit's own look,
  themed to the same blue accent color.
- The password fields aren't hashed — fine for a small trusted team behind
  a shared link, but not meant for public-internet-facing use as-is.
