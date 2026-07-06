"""
AVYU Team Portal — Streamlit edition.

A team management app for an Admin + 4 interns (Lead Scout, Reddit Ranger,
Content Creator, Lead Manager): daily task checklists, a work timer, lead
and work-link logging, a live team chat, and reference material (training,
scripts, SOPs, KPIs).

Run locally:   streamlit run app.py
Deploy:        see README.md
"""
import csv
import io
from datetime import datetime

import pandas as pd
import streamlit as st

import avyu_data as db
import content
from database import get_connection

st.set_page_config(page_title="AVYU Team Portal", page_icon="🛡️", layout="wide")

# ---------------------------------------------------------------------------
# Live-refresh helper — degrades gracefully on older Streamlit versions
# ---------------------------------------------------------------------------
def live_fragment(run_every=5):
    if hasattr(st, "fragment"):
        return st.fragment(run_every=run_every)
    return lambda f: f


# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------
st.markdown("""
<style>
  .block-container { padding-top: 2rem; }
  div[data-testid="stMetricValue"] { font-size: 1.6rem; }
  .avyu-badge {
      display: inline-block; padding: 2px 10px; border-radius: 20px;
      font-size: 12px; font-weight: 600; background: #E7F0FE; color: #3B6FE0;
  }
  .avyu-live {
      display: inline-block; padding: 2px 10px; border-radius: 20px;
      font-size: 12px; font-weight: 600; background: #E5F6EF; color: #1D9E75;
  }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
if "user" not in st.session_state:
    st.session_state.user = None


def login_screen():
    st.markdown("# 🛡️ AVYU Team Portal")
    st.caption("Sign in to continue")

    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        with st.container(border=True):
            role_choice = st.radio("I am...", ["Admin", "Intern"], horizontal=True)
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Log in", type="primary", use_container_width=True):
                store = db.load_store()
                u = store["users"].get(username.strip())

                expected_role = "admin" if role_choice == "Admin" else "intern"

                if not u:
                    st.error("User not found.")

                elif u["password"] != password:
                    st.error("Wrong password.")

                elif u["role"] != expected_role:
                    st.error("Wrong role selected.")

                else:
                    st.session_state.user = {
                        "username": username.strip(),
                        **u
                    }

                    st.rerun()


if st.session_state.user is None:
    login_screen()
    st.stop()

user = st.session_state.user
store = db.load_store()
profile = store["profiles"].get(user["username"], {})
display_name = profile.get("name") or user["name"]


# ---------------------------------------------------------------------------
# Sidebar — nav, profile, logout
# ---------------------------------------------------------------------------
ADMIN_PAGES = [
    "Team Activity",
    "Daily Tasks & Time",
    "Intern Management",
    "Team Chat",
    "Training",
    "Scripts",
    "Google Sheet",
    "Communication",
    "KPIs",
    "Incentives",
    "Scale Plan",
    "SOP"
]
INTERN_PAGES = ["Work Status", "Daily Tasks", "Time Tracker", "Leads", "Work Links", "Team Chat",
                "Training", "Scripts", "Google Sheet", "Communication", "KPIs", "Incentives", "Scale Plan", "SOP"]

with st.sidebar:
    st.markdown("### 🛡️ AVYU Portal")
    page = st.radio("Navigate", ADMIN_PAGES if user["role"] == "admin" else INTERN_PAGES, label_visibility="collapsed")

    st.divider()
    with st.expander(f"👤 {display_name}"):
        st.caption(user.get("role_title", "Full access") if user["role"] == "intern" else "Full access")
        p_name = st.text_input("Display name", value=profile.get("name", user["name"]), key="profile_name")
        p_email = st.text_input("Email", value=profile.get("email", ""), key="profile_email")
        p_phone = st.text_input("Phone", value=profile.get("phone", ""), key="profile_phone")
        if st.button("Save profile", use_container_width=True):
            fresh = db.load_store()
            fresh["profiles"][user["username"]] = {"name": p_name.strip(), "email": p_email.strip(), "phone": p_phone.strip()}
            db.save_store(fresh)
            st.success("Profile updated")
            st.rerun()

    if st.button("Log out", use_container_width=True):

        if user["role"] == "intern":

            s = db.load_store()

            rec = s["interns"][user["id"]]

            if rec["active_session"]:

                end = db.now_ms()

                start = rec["active_session"]["start"]

                rec["time_sessions"].append({
                    "id": end,
                    "start": start,
                    "end": end,
                    "duration_ms": end - start
                })

                rec["active_session"] = None

                db.save_store(s)

        st.session_state.user = None

        st.rerun()


# ---------------------------------------------------------------------------
# Shared: Team Chat (used by both roles)
# ---------------------------------------------------------------------------
def page_team_chat():
    st.subheader("Team Chat")
    st.caption("A live, shared channel between Admin and all interns — everyone sees every message as it's posted.")

    @live_fragment(5)
    def feed():
        s = db.load_store()
        messages = s["chat"]
        with st.container(height=420, border=True):
            if not messages:
                st.info("No messages yet — say hi to the team.")
            for m in messages:
                avatar = "🛡️" if m["role"] == "admin" else "🧑‍💻"
                with st.chat_message(m["role"], avatar=avatar):
                    st.markdown(f"**{m['name']}**  ·  _{db.fmt_clock(m['ts'])}_")
                    st.write(m["text"])
    feed()

    text = st.chat_input("Message the team...")
    if text:
        s = db.load_store()
        s["chat"].append({
            "username": user["username"], "name": display_name, "role": user["role"],
            "text": text, "ts": db.now_ms(),
        })
        db.save_store(s)
        st.rerun()


# ---------------------------------------------------------------------------
# Intern pages
# ---------------------------------------------------------------------------
def page_work_status():
    s = db.load_store()
    record = s["interns"][user["id"]]
    st.subheader("Work Status")
    st.caption("Post an update — Admin sees this immediately in Team Activity.")

    with st.form("status_form", clear_on_submit=True):
        text = st.text_area("What are you working on / what did you finish?", height=100)
        submitted = st.form_submit_button("Post update", type="primary")
    if submitted and text.strip():
        s = db.load_store()
        rec = s["interns"][user["id"]]
        rec["status_history"].append({"ts": db.now_ms(), "text": text.strip()})
        rec["current_status"] = text.strip()
        db.save_store(s)
        st.success("Status posted")
        st.rerun()

    st.divider()
    st.markdown("**Update history**")
    if record["status_history"]:
        for entry in reversed(record["status_history"][-25:]):
            st.markdown(f"- _{db.fmt_ts(entry['ts'])}_ — {entry['text']}")
    else:
        st.info("No updates yet.")


def page_daily_tasks_intern():
    s = db.load_store()
    record = s["interns"][user["id"]]
    today = db.get_today_tasks(record, user["id"])
    db.save_store(s)  # persist the default checklist the first time it's created today

    st.subheader(f"Today's tasks — {db.pretty_date(db.today_key())}")
    st.caption("Resets fresh every day. Check items off as you finish — Admin sees your progress live.")

    done = sum(1 for t in today["items"] if t["done"])
    st.markdown(f'<span class="avyu-badge">{done} / {len(today["items"])} done</span>', unsafe_allow_html=True)
    st.write("")

    for item in today["items"]:
        c1, c2 = st.columns([6, 1])
        key = f"task_{item['id']}_{db.today_key()}"

        def _toggle(task_id=item["id"], k=key):
            s2 = db.load_store()
            rec2 = s2["interns"][user["id"]]
            t2 = db.get_today_tasks(rec2, user["id"])
            for it in t2["items"]:
                if it["id"] == task_id:
                    it["done"] = st.session_state[k]
            db.save_store(s2)

        c1.checkbox(item["text"], value=item["done"], key=key, on_change=_toggle)
        if c2.button("✕", key=f"rm_{item['id']}_{db.today_key()}", help="Remove this task"):
            s3 = db.load_store()
            rec3 = s3["interns"][user["id"]]
            t3 = db.get_today_tasks(rec3, user["id"])
            t3["items"] = [t for t in t3["items"] if t["id"] != item["id"]]
            db.save_store(s3)
            st.rerun()

    with st.form("add_task_form", clear_on_submit=True):
        new_text = st.text_input("Add an extra task for today")
        added = st.form_submit_button("Add task")
    if added and new_text.strip():
        s4 = db.load_store()
        rec4 = s4["interns"][user["id"]]
        t4 = db.get_today_tasks(rec4, user["id"])
        t4["items"].append({"id": f"u{db.now_ms()}", "text": new_text.strip(), "done": False})
        db.save_store(s4)
        st.rerun()


def page_time_tracker_intern():
    s = db.load_store()
    record = s["interns"][user["id"]]
    active = record["active_session"]

    st.subheader("Time Tracker")
    st.caption("Start the timer when you begin work, stop it when you're done. Admin sees your hours automatically.")

    with st.container(border=True):
        if active:
            @live_fragment(1)
            def ticking_clock():
                s2 = db.load_store()
                rec2 = s2["interns"][user["id"]]
                act = rec2["active_session"]
                if act:
                    elapsed = db.now_ms() - act["start"]
                    st.markdown(f"<h1 style='text-align:center;'>{db.ms_to_hms(elapsed)}</h1>", unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align:center;color:gray;'>Running since {db.fmt_clock(act['start'])}</p>", unsafe_allow_html=True)
            ticking_clock()
        else:
            st.markdown("<h1 style='text-align:center;'>00:00:00</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align:center;color:gray;'>Timer is stopped</p>", unsafe_allow_html=True)

        _, mid, _ = st.columns([1, 1, 1])
        with mid:
            label = "Stop timer" if active else "Start timer"
            if st.button(label, type="primary", use_container_width=True):
                s5 = db.load_store()
                rec5 = s5["interns"][user["id"]]
                if rec5["active_session"]:
                    end = db.now_ms()
                    start = rec5["active_session"]["start"]
                    rec5["time_sessions"].append({"id": end, "start": start, "end": end, "duration_ms": end - start})
                    rec5["active_session"] = None
                else:
                    rec5["active_session"] = {"start": db.now_ms()}
                db.save_store(s5)
                st.rerun()

    today_ms, week_ms, all_ms = db.summarize_time(record)
    c1, c2, c3 = st.columns(3)
    c1.metric("Logged today", db.ms_to_hm(today_ms))
    c2.metric("Logged this week", db.ms_to_hm(week_ms))
    c3.metric("All-time logged", db.ms_to_hm(all_ms))

    st.divider()
    st.markdown("**Session history**")
    if record["time_sessions"]:
        rows = [{
            "Date": db.fmt_date_short(sesh["start"]),
            "Start": db.fmt_clock(sesh["start"]),
            "End": db.fmt_clock(sesh["end"]),
            "Duration": db.ms_to_hm(sesh["duration_ms"]),
        } for sesh in reversed(record["time_sessions"])]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No sessions logged yet — hit Start above.")


def page_leads():
    s = db.load_store()
    record = s["interns"][user["id"]]
    st.subheader("Leads")

    with st.form("add_lead_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        company = c1.text_input("Company")
        owner = c2.text_input("Owner name")
        email = c1.text_input("Email")
        phone = c2.text_input("Contact Number")
        linkedin = st.text_input("LinkedIn Profile URL")
        platform_src = c2.selectbox("Source", ["LinkedIn", "Reddit", "Quiz", "Referral", "Other"])
        status = st.selectbox("Status", ["New", "Messaged", "Replied", "Quiz Taken", "Called", "Paid", "Dead"])
        notes = st.text_area("Notes", height=70)
        submitted = st.form_submit_button("Add lead", type="primary")
    if submitted and company.strip():
        s2 = db.load_store()
        intern_id = user["id"].strip().lower()

        rec = s2["interns"][intern_id]
        rec["leads"].append({
            "ts": db.now_ms(),
            "company": company.strip(),
            "owner": owner.strip(),
            "email": email.strip(),
            "phone": phone.strip(),
            "linkedin": linkedin.strip(),
            "platform": platform_src,
            "status": status,
            "notes": notes.strip(),
        })
        db.save_store(s2)
        st.success("Lead added")
        st.rerun()

    st.divider()
    st.caption(f"{len(record['leads'])} leads logged")
    if record["leads"]:
        rows = [{
            "Date": db.fmt_ts(l["ts"]),
            "Company": l["company"],
            "Owner": l["owner"],
            "Email": l.get("email", ""),
            "Phone": l.get("phone", ""),
            "LinkedIn": l.get("linkedin", ""),
            "Source": l["platform"],
            "Status": l["status"],
            "Notes": l["notes"],
        } for l in reversed(record["leads"])]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No leads yet — add your first one above.")


def page_work_links():
    s = db.load_store()
    record = s["interns"][user["id"]]
    st.subheader("Work Links")

    with st.form("add_link_form", clear_on_submit=True):
        url = st.text_input("Link (post, doc, sheet row, anything)")
        platform_src = st.selectbox("Platform", ["LinkedIn", "Reddit", "YouTube/Shorts", "Google Sheet", "Other"])
        description = st.text_area("What is this?", height=70)
        submitted = st.form_submit_button("Add link", type="primary")
    if submitted and url.strip():
        s2 = db.load_store()
        intern_id = user["id"].strip().lower()

        rec = s2["interns"][intern_id]
        rec["worklinks"].append({"ts": db.now_ms(), "url": url.strip(), "platform": platform_src, "description": description.strip()})
        db.save_store(s2)
        st.success("Link added")
        st.rerun()

    st.divider()
    st.caption(f"{len(record['worklinks'])} links submitted")
    if record["worklinks"]:
        for l in reversed(record["worklinks"]):
            with st.container(border=True):
                st.markdown(f"**{l['platform']}** · _{db.fmt_ts(l['ts'])}_")
                st.write(l["description"] or "—")
                st.markdown(f"[{l['url']}]({l['url']})")
    else:
        st.info("No links submitted yet.")


# ---------------------------------------------------------------------------
# Admin pages
# ---------------------------------------------------------------------------
def _leads_csv(s):
    buf = io.StringIO()
    writer = csv.writer(buf)

    writer.writerow([
        db.fmt_ts(l["ts"]),
        user["name"],
        l["company"],
        l["owner"],
        l.get("email", ""),
        l.get("phone", ""),
        l.get("linkedin", ""),
        l["platform"],
        l["status"],
        l["notes"]
    ])

    store = db.load_store()

    for uid, user in store["users"].items():

        if user["role"] != "intern":
            continue

        for l in s["interns"][uid]["leads"]:

            writer.writerow([
                db.fmt_ts(l["ts"]),
                user["name"],
                l["company"],
                l["owner"],
                l["contact"],
                l["platform"],
                l["status"],
                l["notes"]
            ])

    return buf.getvalue()


def page_team_activity():
    st.subheader("Team Activity")
    st.caption("Live view of what each intern is doing — refreshes automatically every 5 seconds.")

    c1, c2, c3 = st.columns([1, 1.4, 3])

    if c1.button("↻ Refresh now"):
        st.rerun()

    c2.download_button(
        "⬇ Export all leads (CSV)",
        data=_leads_csv(db.load_store()),
        file_name=f"avyu_leads_{db.today_key()}.csv",
        mime="text/csv",
    )

    c3.markdown('<span class="avyu-live">● Live</span>', unsafe_allow_html=True)

    s = db.load_store()
    store = db.load_store()

    intern_ids = [
        uid for uid, usr in store["users"].items()
        if usr["role"] == "intern" and uid in s["interns"]
    ]

    total_leads = sum(len(s["interns"][uid]["leads"]) for uid in intern_ids)
    total_links = sum(len(s["interns"][uid]["worklinks"]) for uid in intern_ids)
    today_total_ms = sum(db.summarize_time(s["interns"][uid])[0] for uid in intern_ids)

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Leads", total_leads)
    m2.metric("Total Work Links", total_links)
    m3.metric("Team Hours Today", db.ms_to_hm(today_total_ms))

    st.divider()

    cols = st.columns(2)

    interns = [
        (uid, usr)
        for uid, usr in store["users"].items()
        if usr["role"] == "intern"
    ]

    for i, (uid, usr) in enumerate(interns):

        if uid not in s["interns"]:
            continue

        rec = s["interns"][uid]

        with cols[i % 2]:
            with st.container(border=True):

                working = " 🟢 Working now" if rec.get("active_session") else ""

                st.markdown(f"**{usr['name']}** — {usr['role_title']}{working}")

                st.write(rec["current_status"] or "_No status update yet_")

                c1, c2 = st.columns(2)

                c1.metric("Leads", len(rec["leads"]))
                c2.metric("Work Links", len(rec["worklinks"]))

    st.divider()
    st.subheader(" All Intern Leads")

    lead_rows = []

    for uid, usr in interns:

        rec = s["interns"][uid]

        for lead in rec["leads"]:
            lead_rows.append({
                "Intern": usr["name"],
                "Date": db.fmt_ts(lead["ts"]),
                "Company": lead["company"],
                "Owner": lead["owner"],
                "Email": lead.get("email", ""),
                "Phone": lead.get("phone", ""),
                "LinkedIn": lead.get("linkedin", ""),
                "Source": lead["platform"],
                "Status": lead["status"],
                "Notes": lead["notes"]
            })

    if lead_rows:
        st.dataframe(pd.DataFrame(lead_rows), use_container_width=True, hide_index=True)
    else:
        st.info("No leads added yet.")

    st.divider()
    st.subheader("🔗 All Work Links")

    work_rows = []

    for uid, usr in interns:

        rec = s["interns"][uid]

        for work in rec["worklinks"]:
            work_rows.append({
                "Intern": usr["name"],
                "Date": db.fmt_ts(work["ts"]),
                "Platform": work["platform"],
                "Description": work["description"],
                "URL": work["url"],
            })

    if work_rows:
        st.dataframe(pd.DataFrame(work_rows), use_container_width=True, hide_index=True)
    else:
        st.info("No work links submitted yet.")
            
def page_daily_tasks_time_admin():
    st.subheader("Daily Tasks & Time")
    st.caption("Today's checklist and logged hours for each intern — resets automatically every day. "
               "Assign tasks here; interns check them off from their side.")

    @live_fragment(5)
    def cards():
        s = db.load_store()
        changed = False
        cols = st.columns(2)
        store = db.load_store()

        interns = [
            (uid, user)
            for uid, user in store["users"].items()
            if user["role"] == "intern"
        ]

        for i, (uid, user) in enumerate(interns):
        
            if uid not in s["interns"]:
                continue
                
            rec = s["interns"][uid]

            today = db.get_today_tasks(rec, uid)

            changed = True

            done = sum(1 for t in today["items"] if t["done"])

            streak = db.compute_streak(rec)

            today_ms, week_ms, all_ms = db.summarize_time(rec)

            with cols[i % 2]:
                with st.container(border=True):
                    working = "  🟢 Working now" if rec["active_session"] else ""
                    header = f"**{user['name']}**{working}"
                    badges = f'<span class="avyu-badge">{done}/{len(today["items"])} done</span>'
                    if streak > 0:
                        badges = f'<span class="avyu-live">🔥 {streak}d streak</span> ' + badges
                    st.markdown(header)
                    st.markdown(badges, unsafe_allow_html=True)
                    st.write("")

                    for item in today["items"]:
                        rc1, rc2 = st.columns([6, 1])
                        rc1.markdown(f"{'~~' if item['done'] else ''}{item['text']}{'~~' if item['done'] else ''}")
                        if rc2.button("✕", key=f"admin_rm_{uid}_{item['id']}"):
                            s2 = db.load_store()
                            t2 = db.get_today_tasks(s2["interns"][uid], uid)
                            t2["items"] = [t for t in t2["items"] if t["id"] != item["id"]]
                            db.save_store(s2)
                            st.rerun()

                    with st.form(f"assign_task_{uid}", clear_on_submit=True):
                        new_text = st.text_input("Assign a new task for today", key=f"newtask_{uid}")
                        submitted = st.form_submit_button("Assign task")
                    if submitted and new_text.strip():
                        s3 = db.load_store()
                        t3 = db.get_today_tasks(s3["interns"][uid], uid)
                        t3["items"].append({"id": f"a{db.now_ms()}", "text": new_text.strip(), "done": False})
                        db.save_store(s3)
                        st.rerun()

                    st.divider()
                    st.markdown(f"**Today:** {db.ms_to_hm(today_ms)}  ·  **This week:** {db.ms_to_hm(week_ms)}  ·  **All-time:** {db.ms_to_hm(all_ms)}")
        if changed:
            db.save_store(s)  # persist any freshly-created default checklists
    cards()


# ---------------------------------------------------------------------------
# Reference / static content pages (shared by both roles)
# ---------------------------------------------------------------------------
def page_training():
    st.subheader("Training")
    tabs = st.tabs(list(content.TRAINING.keys()))
    for tab, text in zip(tabs, content.TRAINING.values()):
        with tab:
            st.markdown(text)


def page_scripts():
    st.subheader("Scripts & templates")
    for name, text in content.SCRIPTS.items():
        with st.expander(name):
            st.markdown(text)


def page_sheet():
    st.subheader("Google Sheet setup — your team's single source of truth")
    st.caption("One sheet, 6 tabs. Interns fill it. You read it. Nothing falls through the cracks.")
    for tab in content.SHEET_TABS:
        with st.expander(tab["title"]):
            st.write(" · ".join(tab["columns"]))
            for n in tab["notes"]:
                st.markdown(f"- {n}")


def page_comms():
    st.subheader("Communication")
    st.markdown(content.COMMS_GUIDE)


def page_kpi():
    st.subheader("KPIs")
    df = pd.DataFrame(content.KPI_TABLE)
    df.columns = ["Role", "Daily target", "Weekly target", "Quality bar"]
    st.dataframe(df, use_container_width=True, hide_index=True)


def page_incentives():
    st.subheader("Incentives")
    st.markdown(content.INCENTIVES)


def page_scale():
    st.subheader("Scale Plan")
    st.markdown(content.SCALE_PLAN)


def page_sop():
    st.subheader("SOPs")
    st.markdown(content.SOP)

def page_intern_management():

    st.subheader(" Intern Management")

    st.markdown("##  Create New Intern")

    with st.form("create_intern"):

        fullname = st.text_input("Full Name")

        username = st.text_input("Username")

        password = st.text_input("Password", type="password")

        role_title = st.selectbox(
            "Role",
            [
                "Lead Scout",
                "Reddit Ranger",
                "Content Creator",
                "Lead Manager",
                "Graphic Designer",
                "Video Editor",
                "Social Media Manager",
                "Digital Marketing",
                "SEO Executive",
                "Email Marketing",
                "Web Developer",
                "Python Developer",
                "Flutter Developer",
                "Cyber Security Analyst",
                "SOC Analyst",
                "Legal Research",
                "Business Development",
                "Sales Executive",
                "HR Executive",
                "Support Executive",
                "Custom Role"
            ]
        )

        if role_title == "Custom Role":
            role_title = st.text_input("Enter Role Name")

        submit = st.form_submit_button("Create Intern")                

    if submit:

        store = db.load_store()

        # Check if username already exists
        if username in store["users"]:
            st.error("Username already exists!")

        else:

            intern_id = username.strip().lower()
            username = username.strip().lower()

            # Create login account
            store["users"][username] = {
                "password": password,
                "role": "intern",
                "id": intern_id,
                "name": fullname,
                "role_title": role_title,
                "accent": "#3B6FE0"
            }

            # Create empty intern record
            store["interns"][intern_id] = {
                "leads": [],
                "worklinks": [],
                "status_history": [],
                "current_status": None,
                "tasks_by_date": {},
                "time_sessions": [],
                "active_session": None,
            }

            db.save_store(store)

            st.success("Intern Created Successfully!")

            st.rerun()

    st.divider()

    st.markdown("## Existing Interns")

    store = db.load_store()

    for uname, user in store["users"].items():

        if user["role"] != "intern":
            continue

        with st.container(border=True):

            c1, c2 = st.columns([4, 1])

            with c1:
                st.write(f"### {user['name']}")
                st.write(f"**Username:** {uname}")
                st.write(f"**Role:** {user['role_title']}")

            with c2:
                if st.button(" Edit", key=f"edit_{uname}"):
                    st.session_state["edit_user"] = uname
                    st.rerun()

                if st.button(" Delete", key=f"delete_{uname}"):
                    store = db.load_store()

                    store["users"].pop(uname, None)
                    store["interns"].pop(user["id"], None)
                    store["profiles"].pop(uname, None)

                    db.save_store(store)

                    st.success("Intern deleted successfully.")
                    st.rerun()
# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------
ROUTES = {
    "Team Activity": page_team_activity,
    "Daily Tasks & Time": page_daily_tasks_time_admin,
    "Intern Management": page_intern_management,
    "Work Status": page_work_status,
    "Daily Tasks": page_daily_tasks_intern,
    "Time Tracker": page_time_tracker_intern,
    "Leads": page_leads,
    "Work Links": page_work_links,
    "Team Chat": page_team_chat,
    "Training": page_training,
    "Scripts": page_scripts,
    "Google Sheet": page_sheet,
    "Communication": page_comms,
    "KPIs": page_kpi,
    "Incentives": page_incentives,
    "Scale Plan": page_scale,
    "SOP": page_sop,
}

ROUTES[page]()
