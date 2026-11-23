# EduWise graduation-project prototype

The prototype runs in the two original n8n Cloud workflows with the existing Telegram Bot and Google Gemini credentials. The workflows run without FastAPI, HTTP Request nodes, or an external database.

- [Smart Parental Intervention Alert](https://yousseff7.app.n8n.cloud/workflow/C04gl8dLAMCxy4Zm)
- [Vision AI Homework and Quiz Assistant](https://yousseff7.app.n8n.cloud/workflow/U0KUH311xbf2GLmZ)

## Run the demo

Open a private chat with the bot attached to **Telegram Message Trigger** and send one of the following.

| Input | Expected result |
| --- | --- |
| /help | Short Arabic instructions. |
| /parent | A notification about four missed classes for a fictional student. |
| /parent risk | A notification about the fictional student's academic risk. |
| /parent ok | A message explaining why the fictional student did not trigger an alert. |
| One clear photo, no caption | A practice grade and Arabic explanations for the visible questions. |
| The bundled math worksheet with #HW-01 in the caption | A grade out of four using the example teacher rubric. |

Use [sample_math_homework.jpg](../../data/sample_math_homework.jpg) for the four-question demo. The circle-area answer in that file is intentionally incorrect. The expected result is 3 out of 4. A correct answer is 154 cm² when π is taken as 22/7. The bot accepts JPEG, PNG, and WebP images up to 10 MiB in private chats. Analyze Image sends the homework photo to Gemini through the [Gemini Files API](https://aistudio.google.com/docs/files).

The parent command calls the original alert workflow through a native n8n sub-workflow. It uses fictional scenarios and sends the result to the same private chat. The model sees only a general support category and selects an approved coaching tip. Use the **From Preview Demo Manually** trigger to preview the text inside n8n.

The original POST /webhook/student-eval returns a generic preview for the supplied missed_sessions_count and is_at_risk, with preview_only set to true. It does not use caller-supplied names or chat IDs. Use the bot commands to exercise Telegram sending.

## Import on another n8n instance

1. Import [the parent prototype](../../data/n8n/eduflow_student_alert_workflow.json) and [the Telegram homework prototype](../../data/n8n/eduflow_vision_homework_grader.json).
2. Select the same Telegram credential in Telegram Photo Trigger, Download Homework Image, Send Student Telegram Feedback, and Send Parent Telegram Alert.
3. Select the Google Gemini credential in both Gemini nodes. Both use Gemini 3.5 Flash-Lite.
4. In Run Parent Demo, select the imported parent workflow by ID. The export contains the ID for the current EduWise Cloud project. Keep both workflows in the same project.
5. Publish the parent workflow and then the Telegram workflow. Use one active Telegram trigger per bot. [n8n Telegram Trigger documentation](https://docs.n8n.io/integrations/builtin/trigger-nodes/n8n-nodes-base.telegramtrigger/common-issues/)

The bot returns provisional demo feedback. It does not store grades, connect to the school system, read actual attendance, or notify real guardians. Make sure the test photos omit personal details. Existing FastAPI integration code is outside the prototype execution path.

## Local verification

~~~powershell
node --test tests/n8n_workflows.test.cjs
.\.venv\Scripts\python.exe -m pytest -q
~~~

The Node tests run the embedded workflow scripts against Telegram and Gemini fixtures. They cover routing, the shipped math rubric, malformed grades, unreadable input, and the synthetic guardian scenarios.
