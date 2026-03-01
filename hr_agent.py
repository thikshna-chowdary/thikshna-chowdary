import pandas as pd
import json
from datetime import datetime, timedelta
import os
import re

# =========================================================
# UNIVERSAL FILE PATHS (NO HARDCODED WINDOWS PATHS)
# =========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RESUME_FILE = os.path.join(BASE_DIR, "resume_dataset_1200.csv")
LEAVE_FILE = os.path.join(BASE_DIR, "leave_dataset.xlsx")

# =========================================================
# UTILITIES
# =========================================================
def normalize_columns(df):
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return text.split()

def find_column(columns, keywords):
    for col in columns:
        for key in keywords:
            if key in col:
                return col
    return None

# =========================================================
# LOAD RESUME DATA
# =========================================================
if not os.path.exists(RESUME_FILE):
    raise FileNotFoundError("resume_dataset_1200.csv not found in project folder.")

resume_df = pd.read_csv(RESUME_FILE)
resume_df = normalize_columns(resume_df)

name_col = find_column(resume_df.columns, ["name"])
skills_col = find_column(resume_df.columns, ["skill", "expertise"])
exp_col = find_column(resume_df.columns, ["experience"])
job_col = find_column(resume_df.columns, ["job", "target"])

if not all([name_col, skills_col, exp_col, job_col]):
    raise Exception("Required columns missing in resume dataset.")

resume_df[skills_col] = resume_df[skills_col].fillna("")
resume_df[exp_col] = resume_df[exp_col].fillna(0)

# =========================================================
# RESUME–JOB MATCHING + MRR
# =========================================================
def compute_score(skills, job_desc, experience):
    skill_tokens = set(clean_text(skills))
    job_tokens = set(clean_text(job_desc))

    overlap = len(skill_tokens & job_tokens)
    req_score = overlap / max(len(job_tokens), 1)
    exp_score = min(float(experience) / 15, 1.0)

    return round(0.7 * req_score + 0.3 * exp_score, 3)

ranking_output = {}
mrr_scores = {}

valid_jobs = resume_df[job_col].dropna().unique()

for job in valid_jobs:
    job_df = resume_df.copy()

    job_df["score"] = job_df.apply(
        lambda r: compute_score(r[skills_col], job, r[exp_col]), axis=1
    )

    ranked = job_df.sort_values(by="score", ascending=False)
    top5 = ranked.head(5)

    ranking_output[job] = []
    reciprocal_rank = None

    for i, (_, row) in enumerate(top5.iterrows(), start=1):
        ranking_output[job].append({
            "rank": i,
            "candidate": row[name_col],
            "score": row["score"]
        })

        if reciprocal_rank is None and row["score"] > 0:
            reciprocal_rank = 1 / i

    mrr_scores[job] = round(reciprocal_rank or 0, 3)

# =========================================================
# INTERVIEW QUESTION GENERATION
# =========================================================
def generate_questions(skills):
    tokens = clean_text(skills)
    questions = []

    for skill in tokens[:3]:
        questions.append(f"Explain your experience with {skill}.")
        questions.append(f"Describe a project where you used {skill}.")

    questions.append("Describe a challenging team situation and how you handled it.")
    questions.append("Why are you interested in this role?")

    return questions

interview_questions = {}

for job in ranking_output:
    interview_questions[job] = {}
    for c in ranking_output[job]:
        candidate_row = resume_df[resume_df[name_col] == c["candidate"]].iloc[0]
        interview_questions[job][c["candidate"]] = generate_questions(
            candidate_row[skills_col]
        )

# =========================================================
# PIPELINE STATE MANAGEMENT (STRICT)
# =========================================================
VALID_STATES = ["applied", "screened", "interviewed", "offered", "hired"]
pipeline_logs = []

def transition(candidate, current, next_state):
    if next_state == "rejected":
        pipeline_logs.append({
            "candidate": candidate,
            "from": current,
            "to": next_state,
            "timestamp": str(datetime.now())
        })
        return True

    if current in VALID_STATES and next_state in VALID_STATES:
        if VALID_STATES.index(next_state) == VALID_STATES.index(current) + 1:
            pipeline_logs.append({
                "candidate": candidate,
                "from": current,
                "to": next_state,
                "timestamp": str(datetime.now())
            })
            return True

    raise Exception("Invalid pipeline transition detected.")

for job in ranking_output:
    for c in ranking_output[job]:
        transition(c["candidate"], "applied", "screened")
        transition(c["candidate"], "screened", "interviewed")

# =========================================================
# CONFLICT-FREE SCHEDULING
# =========================================================
interview_slots = [datetime.now() + timedelta(hours=i) for i in range(20)]
scheduled = []
used_slots = set()

for job in ranking_output:
    for c in ranking_output[job]:
        for slot in interview_slots:
            if slot not in used_slots:
                scheduled.append({
                    "candidate": c["candidate"],
                    "job": job,
                    "slot": str(slot)
                })
                used_slots.add(slot)
                break

# =========================================================
# LEAVE POLICY ENGINE
# =========================================================
leave_results = []

if os.path.exists(LEAVE_FILE):
    leave_df = pd.read_excel(LEAVE_FILE)
    leave_df = normalize_columns(leave_df)

    emp_col = find_column(leave_df.columns, ["employee", "name"])
    leave_type_col = find_column(leave_df.columns, ["leave"])
    days_col = find_column(leave_df.columns, ["taken", "requested"])
    remaining_col = find_column(leave_df.columns, ["remaining", "balance"])

    approved_registry = {}

    for _, row in leave_df.iterrows():
        employee = row[emp_col]
        leave_type = row[leave_type_col]
        requested = float(row[days_col])
        remaining = float(row[remaining_col])

        balance_ok = requested <= remaining
        conflict = employee in approved_registry

        if balance_ok and not conflict:
            decision = "Approved"
            rule = "Requested <= Remaining Balance + No Conflict"
            approved_registry[employee] = True
        else:
            decision = "Rejected"
            rule = "Policy Violation"

        leave_results.append({
            "employee": employee,
            "leave_type": leave_type,
            "requested_days": int(requested),
            "remaining_days": int(remaining),
            "decision": decision,
            "policy_rule": rule
        })

# =========================================================
# QUERY ESCALATION
# =========================================================
def check_escalation(query):
    keywords = ["legal", "harassment", "lawsuit", "discrimination"]
    for word in keywords:
        if word in query.lower():
            return "Escalated to Human HR"
    return "Handled by Agent"

query_escalation = [
    {"query": "Need leave extension", "status": check_escalation("Need leave extension")},
    {"query": "Harassment complaint", "status": check_escalation("Harassment complaint")}
]

# =========================================================
# EXPORT
# =========================================================
def export_results():
    output = {
        "resume_ranking": ranking_output,
        "mrr_scores": mrr_scores,
        "interview_questions": interview_questions,
        "leave_compliance": leave_results,
        "pipeline_logs": pipeline_logs,
        "scheduled_interviews": scheduled,
        "query_escalation": query_escalation
    }

    with open(os.path.join(BASE_DIR, "hr_agent_output.json"), "w") as f:
        json.dump(output, f, indent=4)

    return output

export_results()

print("HR Agent Execution Completed Successfully.")
print("All outputs exported to hr_agent_output.json")