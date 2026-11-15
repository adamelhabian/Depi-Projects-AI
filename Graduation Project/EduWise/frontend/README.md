# EduFlow AI frontend

A bilingual React/Vite/Tailwind workspace for an Egyptian education center. The EduFlow identity uses educational blue, apricot, IBM Plex Sans Arabic, and Material 3 roles. Local imagery and eight hash destinations are retained. This is an explicit **local demo**, not authenticated production software.

## Brand identity

Open `/brand/` for the visual guide, logo variants, palette, typography and application templates. [BRAND.md](public/brand/BRAND.md) records positioning, voice, usage and the demo naming decision. [DESIGN.md](DESIGN.md) owns interface rules; `src/material-theme.css` owns runtime color roles. The brand kit and board PNG/PDF are available under `public/brand/`.

To regenerate downloadable assets, run `node scripts/export-brand.mjs --prepare`, `npm run build`, start the preview, run `npm run brand:export`, then `npm run build` again. Exporting uses the installed Edge browser on Windows and Playwright Chromium elsewhere. Font licenses are included in the downloadable kit.

## Run

Use Node 22.12+ (verified here with Node 24.20) and npm:

```powershell
npm ci
npm run dev
```

Open [development](http://127.0.0.1:5173). `npm run build` creates `dist`; `npm run preview` serves [production preview](http://127.0.0.1:4173). Scripts call Vite through Node so Windows paths containing `&` work.

```powershell
npm test
npm run test:smoke
npm run test:exports
```

The browser suite uses installed Microsoft Edge on Windows, otherwise Playwright Chromium. Start the dev server first. Set `DEMO_URL`, or run `npm run test:smoke -- http://127.0.0.1:4173`, to test another origin (including the production preview). Run `test:exports` after the browser suite; it inspects the downloaded Word, PowerPoint and CSV samples. Tests create isolated browser contexts; they do not erase your browser data. Screenshots, traces on failure, and export samples are written to ignored `test-results/`.

## Local capabilities

- Role-aware overview, grouped navigation, explicit administrator/teacher/secretary **preview**. Old links (`#overview`, `#students`, `#attendance`, `#payments`, `#studio`, `#materials`, `#automations`, `#analytics`) still work. Detail filters use hash query parameters.
- Student creation/editing, center-unique codes, multi-group dated enrollment, groups and audited archiving without deleting references.
- Session creation and per-session attendance (present/late/absent/excused). Unrecorded is separate; corrections require a reason and retain actor/time/history.
- Integer-piastre EGP charges, discounts, partial allocated receipts, reference deduplication, reasoned refund/void adjustments and derived balances. Financial records remain available for archived students.
- Asynchronous demo Interface, serialized mutations, revision conflicts, idempotent retries, disabled repeated submits, inline errors and preserved inputs on failure. Settings can deliberately fail the next save once.
- Version-3 atomic snapshots, graph validation, migration from existing v1 keys, recoverable backups and read-only protection for future versions. Settings downloads all workspace/legacy/recovery data. Browser storage is neither encrypted nor suitable for production PII.
- Ready built-in physics material fixtures; 15 MB PDF extension/header validation. Uploaded entries are explicitly **metadata-only / indexing failed**, never ready. No original PDF bytes persist.
- Material/subject/grade/topic/difficulty/type/count exam configuration, explicit failed generation jobs, editable saved drafts and a separate teacher-review step. MCQ only in the fixed demo bank; unsupported requests are not silently truncated.
- A/B/C reuse questions: B/C reverse their order and rotate options. Stable choice IDs preserve answer mapping. Separate student and answer-key Word/PowerPoint/print documents; student projection excludes answers and explanations. Print PDF means the browser's “Save as PDF”, not a server-generated PDF download.
- Worksheet/slide preparation from the same reviewed exam flow, source-linked lesson time-allocation templates, clearly illustrative concept notes, keyword-only essay rubric suggestions and independently stored teacher overrides. No final student grades are awarded.
- Manual demo automation configuration/activation/run history/event deduplication/edit/review/approval. No scheduling or message delivery. Reports derive attendance and collection summaries from operational demo records and expose missing evidence instead of risk predictions.
- Arabic/English, localized Cairo dates/EGP, RTL, isolated mixed-direction codes/phones, keyboard-operable Base UI dialogs and confirmation dialogs, scrollable tables, reduced-motion support, formula-safe UTF-8 CSV.

## Where things live

```text
src/App.jsx                    small entry / compatibility export
src/WorkspaceApp.jsx           shell, hash navigation, preview/settings
src/data/WorkspaceProvider.jsx async React orchestration and form action state
src/data/service.js            asynchronous read/execute Interface and atomic commit
src/data/persistence.js        versioning, migration, validation recovery
src/domain/workspace.js        entities, permissions, operational rules/calculations
src/domain/content.js          generation, review, variants, rubric and automation rules
src/features/Operations.jsx    students/groups, sessions/attendance, ledger
src/features/Teaching.jsx      materials, preparation, exam/essay review
src/features/Management.jsx    role overview, automations, evidence-based reports
src/components/                accessible shared UI and form/table helpers
src/i18n.js                    errors, status terminology, date/money formatting
src/exports.js                 audience-safe export projections and generators
tests/workspace.test.mjs       domain, persistence and asynchronous Interface checks
scripts/workflows.mjs          isolated browser workflows
```

Arabic UI uses locally bundled Cairo weights 400/500/600/700, replacing Noto Sans Arabic; English retains DM Sans and Plus Jakarta Sans. The old root page modules are compatibility re-exports rather than separate competing implementations. Domain tests and UI call the same operations. See [data rules](docs/DATA_MODEL.md), [proposed integration contract](docs/INTEGRATION.md) and [verification record](docs/VERIFICATION.md).

## External dependencies / deliberate backlog

There are **no confirmed HTTP endpoints, auth sessions, storage/indexing service, model integration, scheduler or delivery provider in this repository**. There is consequently no invented live adapter or automatic live-to-demo fallback. Those systems require server-side authorization, tenant isolation, validation, transactional uniqueness/idempotency, durable jobs and source provenance. See integration documentation before wiring them.

OCR receipt extraction, OMR/bubble-sheet scanning, voice commands, Tauri/desktop packaging, external messaging, real predictive learning-gap models and additional integrations remain deferred. Real Office/LibreOffice visual rendering and a full WCAG/screen-reader/cross-browser audit require separate manual validation; structural export tests do not claim those results.
