"""
Static reference content for the AVYU Team Portal — the material that doesn't
change day to day (training, scripts, sheet structure, KPIs, SOPs, etc.).
Kept out of app.py so the interactive logic stays easy to read.
"""

TRAINING = {
    "Intern 1 — Lead Scout": """
### Role: Find SME owners who need DPDP compliance help

**Daily target:** 20 new leads, 20 outreach messages sent.

**Where to find them**
- LinkedIn: search "founder", "owner", "director" + city name (Hyderabad, Pune, Bangalore)
- Google Maps: search "clinics near me", "schools near me", "law firms near me" — any SME with a website
- IndiaMart / JustDial: SME directories, filter by category

**What counts as a lead**
- Indian SME with a live website that collects any personal data (contact forms, bookings, sign-ups)
- A named decision-maker you can message directly (not a generic info@ email)

**Outreach message template**
> Hi [Name], I noticed [Company]'s website collects [visitor info / bookings]. Under India's new DPDP Act, businesses handling personal data now have compliance obligations — most SMEs aren't aware yet. I run free 2-minute compliance checks for businesses like yours. Want me to send yours over?

**Rules**
- Never claim to be a lawyer or offer legal advice — you're offering an awareness check
- Log every message sent the same day, no exceptions
- Any reply that sounds interested = HOT LEAD → follow the Hot Lead SOP immediately
""",
    "Intern 2 — Reddit Ranger": """
### Role: Build organic awareness in relevant subreddits

**Daily target:** 10 comments posted across target subreddits.

**Target subreddits**
- r/india, r/IndianStartups, r/smallbusiness, r/legaladviceindia, r/developersIndia

**How to comment (without looking spammy)**
1. Find a genuinely relevant thread (someone asking about data privacy, compliance, GDPR-vs-India, website legal stuff)
2. Add real value first — answer the actual question
3. Only mention AVYU if it's a natural fit, and never in the first line
4. Never post the same comment text twice

**What NOT to do**
- Don't comment on unrelated threads just to hit your number
- Don't argue with people who push back — say thanks and move on
- Don't post links directly in comments; if asked, DM instead

**If a comment gets removed:** note the subreddit + reason in Tab 4, and adjust your approach for that subreddit.
""",
    "Intern 3 — Content Creator": """
### Role: Produce short-form video content that drives quiz clicks

**Daily target:** 2 Shorts edited and uploaded (once approved).

**Content pillars**
- "Did you know?" — DPDP Act facts most business owners don't know
- "3 signs your website isn't compliant" — quick visual checklist
- Case-study style: "This SME didn't know X — here's what it cost them"

**Workflow**
1. Write script (30–45 seconds), send for approval by 8pm the night before
2. Once approved, record, edit, add captions + a clear CTA ("Take the free 2-minute quiz — link in bio")
3. Upload, then log the post in Tab 3 with the link
4. Check views again at 24 hours and 7 days — record both

**Style rules:** no stock "corporate" music, keep it conversational, always caption for silent viewing.
""",
    "Intern 4 — Lead Manager / Tracker": """
### Role: The nervous system of the whole operation

**Daily target:** Every quiz submission logged within 2 hours, sheet fully updated by 5pm.

**Core responsibilities**
1. Monitor the quiz submissions inbox continuously
2. For each submission: log it, calculate the risk score, flag CRITICAL rows in red
3. Prepare a draft reply for every quiz taker (Admin reviews and sends)
4. Compile the Daily Report Summary (Tab 6) by 5pm — this is Admin's morning dashboard

**Risk scoring**
- Each "bad" answer (non-compliant practice) = 20 points
- 80–100 = Critical (flag immediately, draft reply same day)
- 40–79 = Moderate
- 0–39 = Low risk (still worth a light-touch follow-up)

**Golden rule:** if a number in your daily report is 0, Admin will ask why — have an answer ready before they ask.
""",
}

SCRIPTS = {
    "LinkedIn outreach (Intern 1)": """
> Hi [Name], I noticed [Company]'s website collects [visitor info / bookings]. Under India's new DPDP Act, businesses handling personal data now have compliance obligations — most SMEs aren't aware yet. I run free 2-minute compliance checks for businesses like yours. Want me to send yours over?

**Follow-up (if no reply in 3 days):**
> Hi [Name], just following up — happy to send that free compliance check whenever's useful, no pressure either way!
""",
    "Reddit comment opener (Intern 2)": """
> Good question — under the DPDP Act, [specific point relevant to thread]. A lot of small businesses in India are still catching up on this since enforcement is fairly new. [1 more genuinely useful sentence.] If it's helpful, there's a free 2-minute check floating around that flags the obvious gaps — happy to share if you want it.
""",
    "Shorts script skeleton (Intern 3)": """
**Hook (0–3s):** "Your website could be breaking Indian law and you don't even know it."
**Body (3–30s):** [One specific, surprising DPDP fact, explained simply — no jargon.]
**CTA (30–45s):** "Take the free 2-minute compliance quiz — link in bio. Takes less time than this video."
""",
    "Quiz-taker draft reply (Intern 4, for Admin to review/send)": """
> Hi [Name], thanks for taking the DPDP compliance quiz for [Company]. Based on your answers, your risk level is [Low/Moderate/Critical]. [1–2 sentences on the biggest gap found.] I'd like to walk you through what this means and what a fix would look like — do you have 15 minutes this week for a quick call?
""",
    "Hot lead handoff (any intern → Admin, via WhatsApp)": """
> 🔥 HOT LEAD — [Company name]
> They said: "[paste their exact reply]"
> Source: [LinkedIn / Reddit / Quiz]
> I have NOT replied yet — over to you.
""",
}

SHEET_TABS = [
    {
        "title": "Tab 1 — Lead Pipeline (Intern 1 owns this)",
        "columns": ["Date found", "Company name", "Owner name", "Website URL", "Email / LinkedIn",
                    "Industry", "City / State", "Message sent? Y/N", "Date messaged", "Replied? Y/N",
                    "Reply date", "Quiz taken? Y/N", "Status", "Notes"],
        "notes": [
            "Intern 1 adds 20 rows per day",
            "Update \"Replied?\" column same day",
            "Status options: New / Messaged / Replied / Quiz Taken / Called / Paid / Dead",
        ],
    },
    {
        "title": "Tab 2 — Quiz Submissions (Intern 4 owns this)",
        "columns": ["Date submitted", "Email", "Name (if given)", "Quiz score (0–100)", "Risk level",
                    "Q1 answer", "Q2 answer", "Q3 answer", "Q4 answer", "Q5 answer",
                    "Draft reply ready? Y/N", "Mani sent email? Y/N", "Call booked? Y/N", "Paid? Y/N + Amount"],
        "notes": [
            "Intern 4 adds every quiz submission within 2 hours",
            "Calculate risk score manually: each bad answer = 20 points",
            "Flag \"Critical\" rows in RED so you see them immediately",
        ],
    },
    {
        "title": "Tab 3 — Content Tracker (Intern 3 owns this)",
        "columns": ["Date", "Platform", "Title / Topic", "Status (Draft/Approved/Posted)",
                    "YouTube link", "Reels link", "Views (24hr)", "Quiz clicks (if tracked)", "Notes"],
        "notes": [
            "Intern 3 logs every Short before and after posting",
            "Record views after 24 hours and 7 days",
            "Mark approval status — nothing posts without your OK",
        ],
    },
    {
        "title": "Tab 4 — Reddit Tracker (Intern 2 owns this)",
        "columns": ["Date", "Subreddit", "Post title (linked)", "Comment posted? Y/N", "Upvotes received",
                    "Replies received", "Quiz clicks (estimate)", "Comment removed? Y/N"],
        "notes": [
            "If a comment gets removed — note why, adjust future comments",
            "Track which subreddits give best engagement",
            "Target: at least 3 upvotes average per comment",
        ],
    },
    {
        "title": "Tab 5 — Revenue Tracker (You + Intern 4)",
        "columns": ["Date", "Client name", "Company", "Service sold", "Amount (₹)", "Payment method",
                    "Paid? Y/N", "Audit date", "Report sent? Y/N", "Testimonial? Y/N", "Upsell potential"],
        "notes": [
            "You own this tab — Intern 4 can view but not edit",
            "Update within 1 hour of receiving payment",
            "Track upsell column: does this client need monthly monitoring?",
        ],
    },
    {
        "title": "Tab 6 — Daily Report Summary (Intern 4 fills by 5pm)",
        "columns": ["Date", "I1: Leads found", "I1: Messages sent", "I2: Comments posted", "I2: Upvotes avg",
                    "I3: Shorts posted", "I3: Views (24hr)", "Quiz submissions today", "Calls booked today",
                    "Revenue today (₹)", "Blockers"],
        "notes": [
            "This is your dashboard — check this first every morning",
            "If any number is 0, ask the intern why immediately",
            "Intern 4 compiles this from all other tabs by 5pm sharp",
        ],
    },
]

COMMS_GUIDE = """
### Daily rhythm

- **9:00am** — Each intern sends a "starting work" message with today's plan (or just uses the Daily Tasks tab here)
- **1:00pm** — Quick midday check-in if anything's blocking progress
- **6:00pm** — End-of-day status update + numbers for the day
- **Anytime** — Hot leads and content approvals don't wait for the schedule — flag immediately

### Escalation rule
If Admin hasn't responded to something urgent (hot lead, content approval) within the expected window, the intern sends **one** polite reminder — they don't post/reply without approval regardless of how long it takes.

### Tone
Direct, numbers-first, no fluff. "20 leads found, 3 replies, 1 hot (see above)" beats a paragraph of narrative every time.
"""

KPI_TABLE = [
    {"role": "Intern 1 — Lead Scout", "daily": "20 leads found + messaged", "weekly": "100 leads, 15%+ reply rate",
     "quality_bar": "Every lead is a real decision-maker at a real SME, not a generic inbox"},
    {"role": "Intern 2 — Reddit Ranger", "daily": "10 comments posted", "weekly": "50 comments, 3+ avg upvotes",
     "quality_bar": "Comments read as genuinely helpful, not promotional"},
    {"role": "Intern 3 — Content Creator", "daily": "2 Shorts edited/uploaded", "weekly": "10 Shorts, growing 24hr views",
     "quality_bar": "Every script approved before recording, captions always on"},
    {"role": "Intern 4 — Lead Manager", "daily": "All submissions logged within 2hrs", "weekly": "Zero missed critical leads",
     "quality_bar": "Daily Report Summary complete and accurate by 5pm, every day"},
]

INCENTIVES = """
### Performance incentives (suggested structure — adjust to your budget)

- **Monthly top performer** (by KPI hit-rate): ₹2,000 bonus + public shout-out in Team Chat
- **Hot lead → paid client**: ₹500 finder's bonus to whichever intern surfaced the original lead
- **Perfect week** (100% of daily targets hit, 5 days straight): small bonus or an extra day off
- **Referral**: any intern who refers a new hire that stays past 30 days gets ₹1,000

### Why this matters
Interns doing repetitive outreach burn out fast without visible progress markers. The streaks and live stats in Daily Tasks & Time are designed to make progress visible — pair that with real incentives so the numbers mean something.
"""

SCALE_PLAN = """
### 90-day scale plan — with 4 interns

Month 1 proves the model. Month 2 doubles it. Month 3 systemises it.

---

**Month 1 — Prove it** (Weeks 1–4) · Target: ₹1.5–3L
- Focus: India only — Telangana, AP, Karnataka
- I1 contacts 400 SMEs total (20/day × 20 days)
- I2 posts 200 Reddit comments
- I3 uploads 40 Shorts
- I4 logs every lead, zero misses
- You close 6–12 audits at ₹25,000 each
- Collect 3+ testimonials for Month 2 social proof
- Goal: know which channel converts best

---

**Month 2 — Double it** (Weeks 5–8) · Target: ₹3–6L
- Double best-performing channel from Month 1
- I1 now targets hospitals + educational institutions specifically
- Add WhatsApp outreach — I1 joins 5 SME WhatsApp groups
- I3 repurposes best Shorts into LinkedIn video posts
- You raise price to ₹35,000–₹40,000 per audit (you have proof now)
- Launch monthly monitoring ₹8,000/month — sell to Month 1 clients first
- Expand to Hyderabad, Pune, Bangalore SMEs

---

**Month 3 — Systemise it** (Weeks 9–12) · Target: ₹6–10L
- You have case studies, testimonials, proof
- Launch SE Asia or UK market — I1 finds international SMEs on LinkedIn
- I3 creates English-only Shorts for global audience
- You train 1 intern to do basic audit prep (reduce your audit time from 5hrs to 3hrs)
- Add ₹1L+ DPDP compliance package as a premium offer
- Build referral system — every client who refers gets ₹2,000
- Target: 10 recurring monitoring clients + 10 new audits/month

---

### Revenue math — conservative 90-day projection

| Month | Revenue | Breakdown |
|---|---|---|
| Month 1 | ₹2L | 8 audits × ₹25K |
| Month 2 | ₹4.5L | 10 audits × ₹35K + 5 retainers × ₹8K |
| Month 3 | ₹8L | 12 audits × ₹40K + 15 retainers × ₹8K + 2 packages × ₹1L |
| **Quarter 1 total** | **₹14.5L** | All from your 4-intern system |
"""

SOP = """
### Content approval SOP
1. **Intern creates draft** — LinkedIn post, Short script, or Reddit comment — intern writes it and sends to you via WhatsApp by 8pm the night before.
2. **You review (5–10 min)** — Check facts, tone, and the offer wording. Edit if needed. Reply "Approved" or "Change: [specific edit]".
3. **Intern posts the approved version** — Nothing goes live without your "Approved" message. If you don't reply by 9am next day, intern sends a reminder — they do not post without approval.
4. **Intern logs post link in sheet** — Tab 3 for Shorts. Tab 4 for Reddit. LinkedIn posts tracked by date in Tab 6.

---

### Hot lead SOP (when someone replies positively)
1. **Intern gets a warm reply** — Any reply that says "interested", "tell me more", "how much does it cost", or "what do you offer" — this is a HOT lead.
2. **Intern does NOT respond** — They screenshot the message, paste it to you directly on WhatsApp IMMEDIATELY. They say nothing back to the prospect yet.
3. **You respond within 1 hour** — You take over the conversation. You either reply from your account or tell the intern exactly what to say word-for-word.
4. **Intern logs the outcome** — Update the lead's status in Tab 1 once you know how it went.

---

### Quiz submission SOP
1. Intern 4 monitors the inbox and logs every submission within 2 hours.
2. Risk score calculated immediately — Critical rows flagged in red.
3. Draft reply prepared for every submission — Admin reviews and sends within the same business day for Critical leads.
4. Call booked? Logged. Payment received? Logged within 1 hour, moved to the Revenue Tracker.

---

### What to do if something goes wrong
- **Missed a daily target** — log it honestly in your status update with the reason. Hiding it is worse than missing it.
- **Posted something without approval by mistake** — tell Admin immediately, don't wait for them to notice.
- **A prospect is rude or hostile** — don't engage, screenshot if needed, move on. Never argue publicly.
- **Not sure if something is compliant / appropriate to say** — ask before you post, not after.
"""
