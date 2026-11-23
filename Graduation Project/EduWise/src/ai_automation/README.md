# AI automation module

This directory contains the automation workflows, Telegram bot integration, grading engines, and event dispatchers for the EduWise platform.

The system connects student submissions and teacher evaluations to automated feedback pipelines using n8n Cloud, Google Gemini Vision, and Telegram.

---

## Architecture overview

The automation architecture combines asynchronous messaging, visual AI evaluation, and structured webhook dispatch:

1. Student and parent interface: A Telegram bot (`@EduWiseBot`) receives homework images, test queries, commands, and conversational center questions from students and guardians.
2. Workflow orchestrator: Two production workflows on n8n Cloud manage message routing, media downloads, model calls, and delivery state.
3. Multimodal vision grading: Google Gemini processes handwritten or printed homework images, extracts answers, scores visible questions, and outputs Arabic feedback.
4. Parental intervention alerts: Academic risk predictions and attendance thresholds trigger automated parent notifications with targeted coaching recommendations.
5. Conversational center assistant: An integrated Gemini assistant handles 24/7 inquiries regarding schedules, center branches, tuition fees, and makeup sessions.
6. Local persistence and API bridge: FastAPI endpoints and an SQLite database record delivery audit trails, manage rubric configurations, and enforce idempotency.

---

## Workflow specifications

EduWise maintains two active workflows hosted on n8n Cloud:

### 1. Smart parental intervention alert (`C04gl8dLAMCxy4Zm`)

This workflow receives student risk evaluations and delivers tailored Arabic notifications to guardians.

- Trigger: Webhook trigger at `POST /webhook/student-eval` or direct sub-workflow execution from the vision assistant.
- Decision logic: The workflow evaluates whether `missed_sessions_count >= 3` or `is_at_risk == true`. If neither condition is met, it exits or returns an explanatory message without notifying parents.
- Content generation: A Gemini node selects approved Arabic coaching advice matching the student's risk category.
- Delivery: The Telegram node delivers formatted HTML messages to the registered guardian chat ID.

### 2. Vision AI homework and quiz assistant (`U0KUH311xbf2GLmZ`)

This workflow processes incoming Telegram messages, handles student homework photos, answers center inquiries, and routes interactive commands.

- Trigger: Telegram trigger listening to private messages sent to `@EduWiseBot`.
- Message router: Directs photo submissions to the vision grader, demo commands (`/parent_risk`, `/parent_absence`, `/parent_ok`) to demo handlers, menu commands (`/start`, `/help`) to the guidance menu, and natural text inquiries to the Center Assistant.
- Media pipeline: Downloads submitted photos (JPEG, PNG, or WebP up to 10 MiB) via the Telegram Bot API and sends them to Gemini Vision.
- Grading engine: Calculates dynamic question counts, scores student work against provided rubrics or open worksheets, and produces proportional marks ($X / N$).
- Center inquiry engine: Gemini evaluates natural language inquiries using structured EduWise knowledge covering schedules, branch locations, fee structures, and makeup policies.
- Sub-workflow link: Calls the parental intervention alert workflow via native sub-workflow execution when testing guardian alert commands.

---

## Telegram bot commands and usage

Students and teachers interact with the bot through `@EduWiseBot`.

### Direct commands

| Command | Target | Action |
| :--- | :--- | :--- |
| `/start` | Student / Teacher | Displays service welcome message and available features. |
| `/help` | Student / Teacher | Shows usage instructions for homework grading and parent alerts. |
| `/parent_risk` | Teacher Demo | Simulates an academic risk alert for a student requiring academic support. |
| `/parent_absence` | Teacher Demo | Simulates a notification for a student with repeated absences (4 sessions). |
| `/parent_ok` | Teacher Demo | Demonstrates a stable student scenario where no intervention alert is required. |

### Conversational center inquiries

Students and parents can ask general inquiries at any time in natural or colloquial Egyptian Arabic:

- Schedules: Class times for 1st, 2nd, and 3rd secondary groups, including weekend intensive tracks.
- Locations and contacts: Addresses and phone numbers for the Nasr City and Dokki branches.
- Fees and subscriptions: Per-session fees, 8-session monthly packages, and booklet/worksheet prices.
- Absence and makeup: Excused absence notice policies (24 hours prior) and weekly makeup session slots.

### Homework evaluation workflow

Students submit homework directly in private chat:

1. Upload a clear photograph of the completed worksheet.
2. Optional rubric tag: Adding `#HW-01` in the image caption binds the grading to the official answer key and rubric criteria.
3. Open worksheet grading: Images submitted without a tag are dynamically evaluated. Gemini detects the total number of questions, checks each answer, and returns marks proportional to the detected question count.
4. Response formatting: Feedback includes total score, question breakdown, identified errors, and model solutions in Arabic.

---

## Backend API and persistence

FastAPI routes in `src/backend/api/v1/automation_endpoints.py` provide programmatic control and audit capabilities:

### Endpoints

- `POST /api/v1/alerts/trigger-risk-eval`: Accepts student features or precomputed risk scores. Verifies guardian contact data, records an idempotent event, and dispatches the alert via n8n webhook.
- `GET /api/v1/alerts/events/{event_id}`: Retrieves event status and delivery state.
- `POST /api/v1/alerts/claim`: Called by n8n to claim pending alert payloads using authorized workflow credentials.
- `POST /api/v1/alerts/audit-callback`: Confirms successful delivery to Telegram with the resulting Telegram message ID.
- `POST /api/v1/homework/context`: Validates student authorization and returns the active rubric configuration.
- `POST /api/v1/homework/submissions`: Ingests and stores provisional homework grades calculated by the vision pipeline.
- `POST /api/v1/homework/feedback-callback`: Confirms delivery of feedback messages to the student.

### Storage schema

SQLite tables in `var/academic_alerts.sqlite3` maintain audit records:

- `automation_alerts`: Stores `event_id`, SHA-256 fingerprint, `student_id`, status (`pending`, `sending`, `telegram_accepted`, `cancelled`), and Telegram message ID.
- `automation_homework`: Stores `submission_id`, serialized grade records, and `feedback_status`.

---

## Local verification and tests

The automation test suite verifies both the n8n workflow JavaScript logic and the FastAPI integration contracts:

```powershell
# 1. Run n8n workflow unit tests (fixtures and script nodes)
node --test tests/n8n_workflows.test.cjs

# 2. Run backend automation regression tests
python -m pytest -q --basetemp=.pytest_temp/automation tests/test_n8n_automation.py
```

Coverage includes:

- Conversational inquiry routing, FAQ knowledge base retrieval, and HTML response formatting (22 node tests).
- Token authentication and role separation for operator and workflow callers.
- Idempotent alert dispatching and deduplication via SHA-256 payload fingerprints.
- Rubric matching, score capping, unreadable image handling, and multi-part Telegram message splitting.
- BiDi text orientation and single-token slash command parsing.

---

## Environment configuration

Configure these variables in `.env` for local backend execution:

```ini
# n8n webhook settings
N8N_WEBHOOK_URL=https://yousseff7.app.n8n.cloud/webhook/student-eval
N8N_WEBHOOK_TOKEN=your_secure_n8n_token

# Automation service security tokens
EDUWISE_AUTOMATION_OPERATOR_TOKEN=your_operator_token
EDUWISE_AUTOMATION_CALLBACK_TOKEN=your_workflow_token

# Local storage and roster files
EDUWISE_AUTOMATION_DB=var/academic_alerts.sqlite3
EDUWISE_AUTOMATION_CONFIG=var/automation.json
```
