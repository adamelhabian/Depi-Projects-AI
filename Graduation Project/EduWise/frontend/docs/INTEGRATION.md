# Integration readiness

## Confirmed versus proposed

**Confirmed from repository inspection:** React frontend, local assets/fonts, installed export libraries, local demo storage. No implemented backend, API schema, auth session, model provider, file storage/indexing endpoint, scheduler or delivery provider was found. No HTTP path below is confirmed or called by the app.

**Implemented local Interface:** `createDemoService({storage, now, uuid, contentOperation})`; `await read(role, {signal})` returns `{data, notice, readOnly}`; `await execute(command, input, {role, idempotencyKey, expectedRevision})` returns that same envelope after an atomic validated commit. `failNextMutation()` is an explicitly labelled diagnostic. Injected time/identity/storage make tests deterministic. The command vocabulary and data shapes are in `domain/workspace.js`, `domain/content.js` and DATA_MODEL.md.

**Proposed HTTP design for agreement:** implement a live adapter only after server responses and policies are confirmed. The adapter must map validated responses to these same entities rather than importing network calls into pages. Demo/live mode must be explicit in the shell. Never catch live errors by returning demo records. A switch into demo must be a deliberate user action using a separate data namespace.

## Proposed read resources

```text
GET /v1/session                         user, roles, center and expiry
GET /v1/students?status=&q=&groupId=&cursor=&limit=
GET /v1/groups?status=&teacherId=&cursor=&limit=
GET /v1/enrollments?studentId=&groupId=&onDate=&cursor=&limit=
GET /v1/sessions?groupId=&from=&to=&cursor=&limit=
GET /v1/attendance?sessionId=&status=&cursor=&limit=
GET /v1/charges?studentId=&outstanding=&cursor=&limit=
GET /v1/payments?studentId=&from=&to=&cursor=&limit=
GET /v1/materials?status=&subject=&grade=&cursor=&limit=
GET /v1/generation-jobs/{id}
GET /v1/drafts?kind=&status=&cursor=&limit=
GET /v1/automation-runs?workflowId=&sessionId=&cursor=&limit=
GET /v1/reports/operations?from=&to=
```

Proposed list envelope: `{data: Entity[], page: {nextCursor: string|null, limit: number}, meta: {requestId, generatedAt}}`. Default limit 50, server-capped 100; stable sorting `(createdAt,id)` or an explicitly documented resource order. Cursors opaque, scoped to filters/tenant; do not confuse “page loaded” with totals. Dashboard totals/report denominators must be computed server-side over the same filters, not over a page of data. The current demo loads its small workspace at once and **does not claim live pagination**.

Center scope comes from the authenticated session, not a trusted arbitrary client `centerId`. Dates, query normalization, archived visibility, inclusive date boundaries and finance permissions must match the local rules or trigger an explicit contract revision.

## Proposed mutation resources

```text
POST/PATCH /v1/students[/{id}]
POST /v1/students/{id}/archive           reason, expectedVersion
POST /v1/groups; POST /v1/groups/{id}/archive
POST /v1/enrollments; POST /v1/sessions
PUT /v1/sessions/{sessionId}/attendance/{studentId}
POST /v1/charges
POST /v1/payments                       amountMinor,currency,reference,allocations[]
POST /v1/payments/{id}/adjustments      type,amountMinor,reason
POST /v1/material-uploads              validated metadata -> signed upload handle
POST /v1/materials/{id}/process
POST /v1/generation-jobs
PATCH /v1/drafts/{id}; POST /v1/drafts/{id}/review
PATCH /v1/workflows/{id}
POST /v1/automation-runs
POST /v1/drafts/{id}/approve
```

All financial/attendance/generation/automation mutations require `Idempotency-Key` scoped to authenticated center+user+operation. Replay of the same key+canonical body returns the original result; key+different body returns 409. Agree retention (at least 24h is a proposal, **not a guarantee**), canonical hashing, transaction isolation, receipt reference normalization, event uniqueness and reconciliation after timeout. `If-Match` / entity version is preferable to a whole-workspace revision for production. Atomic payment+allocation+audit commits, ledger balance checks and unique `(centerId,normalizedReference)` and `(centerId,studentId,sessionId)` constraints must be server-side. UI locks are not sufficient.

Proposed error:

```json
{"error":{"code":"DUPLICATE_REFERENCE","message":"Reference already used","fieldErrors":{"reference":"DUPLICATE_REFERENCE"},"requestId":"...","retryable":false}}
```

Localize stable error codes in the frontend, not arbitrary server/provider prose. 400/422 validation keeps forms, 401 invalid/expired session clears sensitive cached projections and requests sign-in, 403 forbidden renders unavailable state, 409 revision/idempotency/duplicate conflict needs review, 413 file too large, 429 honors Retry-After, 5xx shows visible failure. Abort stale reads on navigation/role/session changes; ignore late completions. Retry safe reads with bounded backoff. Do not automatically replay a possibly committed payment without its original idempotency key and checking the original result.

## Materials and generation

- Uploading = real byte transfer, processing = accepted ingestion job, ready = stored validated document with version/checksum and completed indexing. Failed carries actionable error code. UI must not invent progress percentages. Only report measurable transfer progress when the transport exposes byte counts.
- Server revalidates size (15 MB limit), MIME/magic and actual PDF parsing; sanitize filenames, scan malicious content, authorize every download, enforce storage ACLs/tenant isolation and retain original versions/checksums. The local header check is not server validation.
- A metadata-only demo registration cannot resume indexing: the original file must be selected again after integration. The current UI therefore offers reselection, not a fake successful retry. No upload cancellation is offered because no real upload exists.
- A transient failure to save metadata can be retried while the material-library screen retains the selected File in memory. That retry only saves metadata; it does not upload bytes or index the document. Leaving or reloading the screen requires reselection.
- Proposed generation request: `{materialIds, materialVersions, subject, grade, topic, difficulty, questionType, count, purpose, locale}`. Material IDs must be ready and authorized. Refuse unsupported source coverage rather than returning fewer questions without agreement.
- Proposed job: `{id,status:"queued|running|succeeded|failed|cancelled",createdAt,startedAt,completedAt,resultDraftId,error,cancelSupported}`. Poll with AbortSignal or consume an authenticated event stream; cancellation only when `cancelSupported`, with server-confirmed cancellation state. The demo returns terminal jobs immediately; it simulates neither tokens nor OCR progress.
- Proposed citation: `{materialId,materialVersion,page,excerptHash,verification:"verified"}`; actual indexed page numbers and authorized source viewer are required. Current `page:null,demoPage:N,verification:"demo-only"` are **not verified citations**.
- Source-document text is untrusted **data**, never application instructions. Server generation must keep system/application instructions separate from retrieved passages, identify retrieval provenance, resist prompt injection and never expose credentials or let source content authorize tool use.
- Persist/edit drafts separately from jobs, version edits, invalidate review after changes, record reviewer/time. Stable choice IDs survive variants. Server and frontend must enforce separate student/key projections, including attachments, previews, APIs and download authorization. Do not generate the student file by hiding an answer section with CSS.
- Rubric suggestions and teacher overrides are separate records; approved final grades require a distinct authenticated assessment/student linkage and approval policy. Keyword presence is not scientific assessment.

## Automation/report requirements

Configuration, activation, manual/scheduled trigger, execution, editable draft, teacher review, approval and actual delivery are separate states. Add durable scheduler/event bus, recipient consent/authorization, delivery provider, signed callbacks and delivery audit before displaying “sent”. A successful local event key `workflow:session` prevents repeated follow-up; actual corrected-attendance events need a versioned event/retraction policy agreed before integrating. Failed runs may retry, successful runs are not rerun for that session. Approval is not delivery.

Reports must disclose calendar range, timezone, population/denominator, sample size, update freshness and source provenance. Attendance excludes excused from the rate denominator, missing records stay missing; financial collections are receipts minus adjustments in the period, not revenue/profit. Real learning-gap/risk claims require approved assessment evidence, model/version validation, minimum sample/coverage and explainable source links. None are invented in this demo.

## Security / deferred work

Keep provider/API keys and credentials on the server. Agree session renewal/logout, CSRF protection where cookie auth is used, CORS allowlists, access scopes, PII retention/encryption, audit retention, backup/recovery and observability before production. The role switcher must be removed/replaced for authenticated use. No production deployment or external messages were authorized in this task.

Deferred: OCR receipts, OMR scans, voice commands, desktop/Tauri packaging, real provider inference, predictive models, external messaging/scheduling and additional external integrations. Multi-charge receipt allocation, enrollment editing/transfer and production-grade accounting policies need contract/product agreement.
