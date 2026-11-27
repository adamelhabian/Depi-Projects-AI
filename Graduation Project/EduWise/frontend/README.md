# EduFlow AI frontend

A bilingual React/Vite/Tailwind workspace for an Egyptian education center, with account sign-in and a local JSON API.

## Brand identity

Open `/brand/` for the visual guide, logo variants, palette, typography and application templates. [BRAND.md](public/brand/BRAND.md) records positioning, voice, usage and the demo naming decision. [DESIGN.md](DESIGN.md) owns interface rules; `src/material-theme.css` owns runtime color roles. The brand kit and board PNG/PDF are available under `public/brand/`.

To regenerate downloadable assets, run `node scripts/export-brand.mjs --prepare`, `npm run build`, start the preview, run `npm run brand:export`, then `npm run build` again. Exporting uses the installed Edge browser on Windows and Playwright Chromium elsewhere. Font licenses are included in the downloadable kit.

## Run

Use Node 22.12+ (verified here with Node 24.20) and npm:

```powershell
npm ci
npm run accounts:setup
npm run api
```

The setup command prints generated passwords once for `admin@eduflow.test`, `teacher@eduflow.test` and `secretary@eduflow.test`. Save the credentials for the accounts you need. Start Vite in a second terminal from this directory.

```powershell
npm run dev
```

Open [the sign-in page](http://127.0.0.1:5173/). The API listens on loopback port 8787 by default and the Vite proxy forwards same-origin `/api` requests. The API stores account hashes and workspace records under the ignored `server/.data/` directory. An absolute `EDUFLOW_DATA_DIR` overrides that directory for both setup and the API. Set `EDUFLOW_API_PORT` for a different API port and set `EDUFLOW_API_TARGET` to the matching origin when running Vite.

`npm run build` creates `dist`. `npm run preview` serves [the build preview](http://127.0.0.1:4173/) with the same API proxy. Open [the sample workspace](http://127.0.0.1:5173/?mode=demo) to use browser-local sample records without running the API. A static host can serve this demo at `/?mode=demo`. Account mode needs a same-origin `/api` route.

```powershell
npm test
npm run test:smoke
npm run test:exports
```

The browser suite uses installed Microsoft Edge on Windows, otherwise Playwright Chromium. Start the dev server first. Set `DEMO_URL`, or run `npm run test:smoke -- http://127.0.0.1:4173`, to test another origin (including the production preview). Run `test:exports` after the browser suite; it inspects the downloaded Word, PowerPoint and CSV samples. Tests create isolated browser contexts; they do not erase your browser data. Screenshots, traces on failure, and export samples are written to ignored `test-results/`.

## Local capabilities

- The API assigns the account role and filters records accordingly. The sample workspace includes a role preview. Section links and detail filters use hash URLs.
- Student creation/editing, center-unique codes, multi-group dated enrollment, groups and audited archiving without deleting references.
- Session creation and per-session attendance (present/late/absent/excused). Unrecorded is separate; corrections require a reason and retain actor/time/history.
- Integer-piastre EGP charges, discounts, partial allocated receipts, reference deduplication, reasoned refund/void adjustments and derived balances. Financial records remain available for archived students.
- Serialized mutations, revision conflicts, idempotent retries, inline errors and preserved inputs on failure. In demo mode, Settings can deliberately fail the next save once.
- Account mode starts with a fresh workspace and stores records server-side. Demo mode keeps its existing browser snapshots, v1 migration, recovery downloads and read-only protection for future schema versions.
- Ready built-in physics material fixtures; 15 MB PDF extension/header validation. Uploaded entries are explicitly **metadata-only / indexing failed**, never ready. No original PDF bytes persist.
- Material/subject/grade/topic/difficulty/type/count exam configuration, explicit failed generation jobs, editable saved drafts and a separate teacher-review step. MCQ only in the fixed demo bank; unsupported requests are not silently truncated.
- A/B/C reuse questions: B/C reverse their order and rotate options. Stable choice IDs preserve answer mapping. Separate student and answer-key Word/PowerPoint/print documents; student projection excludes answers and explanations. Print PDF means the browser's “Save as PDF”, not a server-generated PDF download.
- The active AI studio exposes exam drafts and teacher review only. Worksheets, lesson plans, concept notes, essay rubrics, and slide-deck creation are excluded from the current project scope. Student marks/results named in the project README are not implemented in this local demo yet. Legacy draft types remain readable for existing snapshots.
- Manual demo automation configuration/activation/run history/event deduplication/edit/review/approval. No scheduling or message delivery. Reports derive attendance and collection summaries from operational demo records and expose missing evidence instead of risk predictions.
- Arabic/English, localized Cairo dates/EGP, RTL, isolated mixed-direction codes/phones, keyboard-operable Base UI dialogs and confirmation dialogs, scrollable tables, reduced-motion support, formula-safe UTF-8 CSV.

## Where things live

```text
src/App.jsx                    small entry / compatibility export
src/WorkspaceApp.jsx           shell, hash navigation, login gate and settings
src/data/WorkspaceProvider.jsx async React orchestration and form action state
src/data/api.js                Axios client for session and workspace requests
src/data/service.js            browser-local demo service
server/                        local Node API, account setup and JSON persistence
src/data/persistence.js        versioning, migration, validation recovery
src/domain/workspace.js        entities, permissions, operational rules/calculations
src/domain/content.js          exam and legacy content rules; automation rules
src/features/Operations.jsx    students/groups, sessions/attendance, ledger
src/features/Teaching.jsx      materials, exam preparation and review
src/features/Management.jsx    role overview, automations, evidence-based reports
src/components/                accessible shared UI and form/table helpers
src/i18n.js                    errors, status terminology, date/money formatting
src/exports.js                 audience-safe export projections and generators
tests/workspace.test.mjs       domain, persistence and asynchronous Interface checks
scripts/workflows.mjs          isolated browser workflows
```

Arabic UI uses locally bundled Cairo weights 400/500/600/700, replacing Noto Sans Arabic; English retains DM Sans and Plus Jakarta Sans. The old root page modules are compatibility re-exports rather than separate competing implementations. Domain tests and UI call the same operations. See [data rules](docs/DATA_MODEL.md), [proposed integration contract](docs/INTEGRATION.md) and [verification record](docs/VERIFICATION.md).

## External dependencies / deliberate backlog

The account API targets a single local center with three provisioned accounts and an in-memory session store. The document storage/indexing service, model provider, scheduler and delivery provider remain future integrations. See [the integration contract](docs/INTEGRATION.md) for the available endpoints and deployment boundaries.

OCR receipt extraction, OMR/bubble-sheet scanning, voice commands, Tauri/desktop packaging, external messaging, real predictive learning-gap models and additional integrations remain deferred. Real Office/LibreOffice visual rendering and a full WCAG/screen-reader/cross-browser audit require separate manual validation; structural export tests do not claim those results.
