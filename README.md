## Hi there 👋
we are team TECH_TITANS

Team Lead : M Thikshna Chowdary

Team Member : Harini Kollolli




NETRIK TRACK 1 - AI HR WORKFLOW AGENT
1. Problem Understanding

HR departments manage repetitive, high-volume workflows such as resume screening, interview scheduling, candidate pipeline tracking, and leave approvals.

These workflows require:

->Deterministic decision-making

->Policy compliance

->Auditability

->Conflict-free coordination

The objective of this project was to design and implement a fully deterministic autonomous HR agent that automates these workflows while strictly enforcing system constraints and export standards defined in the evaluation rubric.


2. Design Philosophy

While building this system, I focused on:

->Determinism (identical output across runs)

->Strict state validation

->Conflict prevention

->Policy-based decision logic

->Structured JSON export for automated evaluation

No randomness is used anywhere in the system to ensure stability and reproducibility.


3. System Architecture Overview

The system is modular and divided into the following components:

1.Resume Ranking Engine

2.Interview Question Generator

3.Conflict-Safe Scheduling Engine

4.Pipeline State Machine

5.Leave Policy Compliance Engine

6.Query Escalation Module

7.Standardized Export Layer (export_results())

Each module operates independently but integrates into a single structured JSON output.


4. Core Implementation Details
   
   
4.1 Resume Parsing and Ranking Engine

Logic Used:

->Normalize text (lowercase + remove special characters)

->Extract candidate skills

->Compare against Job Description using keyword overlap

->Compute weighted score:

`Skill Match Score

`Experience Weight Score

->Sort candidates deterministically

->Compute Mean Reciprocal Rank (MRR)

This ensures stable ranking output under identical input conditions.

Why deterministic scoring?
Because the rubric explicitly evaluates rank stability and reproducibility.


4.2 Interview Question Generation

For each top-ranked candidate:

Extract top skills

Generate technical questions per skill

Add behavioral assessment questions

This ensures interviews are contextual and role-specific.


4.3 Conflict-Aware Scheduling Engine

Implementation strategy:

->Predefined interview time slots

->Maintain a registry of used slots

->Assign first available unused slot

->Prevent duplicate allocation

This guarantees:

->Zero interview overlaps

->Deterministic slot assignment

->Strict adherence to scheduling constraints


4.4 Pipeline State Machine Enforcement

Valid sequence enforced:

applied -> screened -> interviewed -> offered -> hired

Rules implemented:

->No skipping intermediate states

->No backward transitions

->"rejected" allowed from any state

->Invalid transitions raise exceptions

->All transitions logged with timestamps

This ensures workflow compliance and audit traceability.


4.5 Leave Policy Compliance Engine

For each leave request:

->Check available leave balance

->Validate leave type eligibility

->Detect potential conflicts

->Prevent balance underflow

->Output decision along with applied policy rule

All decisions are deterministic and auditable.


4.6 Query Escalation Module

Sensitive HR cases (for example harassment or legal issues) are automatically escalated to human HR instead of automated handling.

This prevents improper automation of critical cases.


5. Edge Case Handling

The system includes safeguards for:

->Missing dataset columns

->Empty skill fields

->Null experience values

->Absent leave entries

->Invalid state transitions

This improves robustness under imperfect real-world data conditions.


6. Output Format and Export

All modules generate structured dictionaries which are consolidated in:

export_results()

Running the program generates:

hr_agent_output.json

This file contains:

->resume_ranking

->mrr_scores

->interview_questions

->scheduled_interviews

->pipeline_logs

->leave_compliance

->query_escalation

The JSON structure is standardized for automated evaluation harness compatibility.


7. How to Run the Project

Requirements:

->Python 3.x

->pandas library

Install dependency:

pip install pandas

Execution Steps:

1.Ensure the following files are in the same folder:

->hr_agent.py

->resume_dataset_1200.csv

->leave_dataset.xlsx

2.Open terminal in that folder.

3.Run:

python hr_agent.py

Output:

After execution, the file:

hr_agent_output.json

will be generated in the same directory.

This file contains the complete structured results of the autonomous HR agent.


8. Technologies Used

->Python 3

->pandas

->json

->datetime

->os

->re

No external ML frameworks were used to preserve deterministic behavior as required by the rubric.


9. Conclusion

This project delivers a deterministic, modular, and policy-compliant autonomous HR workflow system aligned with the updated evaluation rubric.

The implementation ensures:

->Stable ranking outputs

->Zero scheduling conflicts

->Strict pipeline enforcement

->Deterministic leave decisions

->Structured export compliance

The system is designed for reproducibility, auditability, and automated evaluation compatibility.
