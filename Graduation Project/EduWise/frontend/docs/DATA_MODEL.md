# Local entity and business-rule contract (schema 3)

This is the implemented frontend/demo contract, **not an agreed backend contract**. Every demo record belongs to center `nile`, timezone `Africa/Cairo`, currency `EGP`. No real person or financial event is represented by the sample seeds.

## Entities

| Entity | Identity / relationships | Relevant state |
| --- | --- | --- |
| Center | `id`; owns users/students/groups/financial data | timezone, currency |
| User / Role | stable `id`, `centerId`, `role`, `groupIds` | admin, teacher, secretary; preview only |
| Student | stable opaque `id`, separate `code`, bilingual `name`, phone | active / archived; codes normalized NFKC+trim+uppercase, unique including archived |
| Group | stable `id`, `centerId`, subject, grade, optional teacher | active / archived; new groups unassigned |
| Enrollment | `studentId`, `groupId`, inclusive `startDate`, optional inclusive `endDate` | active / ended; same-group overlapping intervals rejected; different groups allowed |
| Session | `id`, `groupId`, calendar `date`, local `startTime`, title | scheduled; group/date/time duplicates rejected |
| AttendanceRecord | `id`, unique student/session pair | present / late / absent / excused; actorId, updatedAt, reason, prior states |
| Charge | `studentId`, description, dueDate | grossMinor − discountMinor; reason required for discount |
| Payment | immutable receipt, student, reference, method, amountMinor | original receipt never overwritten; references reserved even after void |
| PaymentAllocation | receipt → charge | local UI allocates one receipt to one charge; multiple receipts may cover one charge |
| Financial adjustment | paymentId, type, amountMinor | refund / void, reason, actor/time; cannot exceed unreversed amount |
| Material | stable id, title, subject, grade, topic, storage | uploading / processing / ready / failed schema; demo has ready bank fixtures or failed metadata-only entries |
| GenerationJob | request/config, createdBy, timestamps, provenance | queued / running / succeeded / failed / cancelled vocabulary; demo produces terminal succeeded/failed jobs immediately |
| Draft | exam / worksheet via purpose / essay / lesson / automation | draft → reviewed; edits invalidate exam review; automation additionally approved; teacher essay review is not a final grade |
| AutomationRun | workflow, session, eventKey, actor/time, draftIds | failed / succeeded; one successful follow-up per workflow/session |

`audit` stores mutation command, actor, time, target, and reasons. Idempotency entries retain command/input fingerprints and commit timestamps. These are demo-local, not tamper-evident audit logs.

## Attendance and time

Optional student metadata added 2026-10-23: `guardianName` (100 chars), `guardianPhone` (same phone syntax as student), `grade` (100 chars), `notes` (2000 chars). Existing snapshots need no migration because these are optional. These fields are illustrative local data, with the same role projection and retention as the owning student record.

- Eligibility comes from enrollment covering the **session's calendar date**, not a payment flag. Current student/group archive status blocks new attendance; existing records can still be corrected with an explanation.
- Not recorded is the absence of a record, never an absent state. Two sessions on the same day have independent registers.
- Corrections require `expectedUpdatedAt` plus a reason. Prior status, actor, time and reason remain; the global audit also preserves correction reasons.
- Archiving ends currently open enrollments on the Cairo archive date and keeps all references. There is no delete. Re-enrollment / reassignment policy beyond the current add-enrollment UI must be agreed before production.
- Calendar values are `YYYY-MM-DD`; session time is center-local `HH:mm`. Event timestamps are ISO instants. Cairo formatting uses IANA timezone rules, not a fixed UTC offset. The backend must resolve schedule instants / DST and ambiguous times itself.

## Money

All new amounts use integer EGP minor units (100 piastres = EGP 1); decimal text is parsed exactly, at most two decimal places. No floating point currency arithmetic. Local maximum is EGP 10,000,000 per amount.

Outstanding charge = gross − explicit discount − allocations + linked refund/void amounts. Refunds reopen the same charge; void reverses the remaining unreversed receipt value. This demo does not support customer credits, overpayments, charge deletion, tax accounting or multi-charge allocation in one receipt. Splitting a receipt across charges is a proposed backend extension, not silently implemented.

Receipt references are unique for the **entire center**, case/whitespace normalized, including seed/imported/voided receipts. A correction uses a new receipt/reference plus a reasoned reversal. Receipt `createdAt` is its event instant, not a backdated accounting date. Enrollment eligibility is intentionally independent from balance; fee-gated admission needs a separately agreed policy.

## Migration and recovery

- Existing `eduflow.{students,materials,flows,drafts,payments,exams}.v1` keys are never removed.
- Student display codes map to new stable IDs; all old fields remain verbatim in `legacy.data`. Old unscoped presence, risk, attendance percentages, paid/due flags and AI drafts are **not promoted to verified new events**. A visible migration banner explains this; settings exports the archive.
- Valid legacy receipts are converted to minor units (legacy decimal amounts rounded to nearest piastre) and matched to their student code. Each receives a clearly marked *receipt-backed opening reconciliation charge*, not a newly invented subscription. Original references are retained; a unique `IMPORT-{index}-...` reference prevents old duplicate references losing receipts. Unmatched/invalid entries remain in `legacy.data` for reconciliation.
- Uploaded metadata cannot be recovered into document content. It becomes failed/indexing unavailable; built-in sample sources remain demo fixtures.
- Version 3 snapshots validate graph references, duplicate identities/attendance/reference keys and financial limits before reading/committing. Invalid snapshots are copied into `eduflow.recovery.{timestamp}` before opening a fresh sample workspace. Failure to create that backup prevents writing. Future versions are read-only and never overwritten.
- Every mutation commits one complete snapshot only after validation/storage success. A storage error preserves the preceding committed state. The local service serializes writes and rejects stale revisions. Simultaneous cross-tab storage still cannot offer server-grade transactions: last-millisecond races are a documented browser-demo limitation. Production requires transactional constraints.

## Permissions

| Capability | Admin | Teacher | Secretary |
| --- | --- | --- | --- |
| Directory read | all | assigned groups | all |
| Student/group/enrollment mutation | yes | no | yes |
| Sessions / attendance | all | assigned groups | all |
| Charges / receipts / financial adjustments | yes | no | yes |
| Materials / exam / essay / lesson | yes | own drafts, shared center sources | no |
| Automation configuration / run / review | yes | assigned sessions / own drafts | no |
| Reports | full | assigned attendance; no money | no |

Navigation, unavailable pages, commands and demo read projections share this policy. A preview is not security: anyone controlling browser JavaScript/storage controls this sample data. Backend permissions must supersede every client check.
