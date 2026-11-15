# EduFlow AI UX Contract

This contract records shared interface behavior. Domain policy remains in [DATA_MODEL.md](docs/DATA_MODEL.md), and proposed service behavior remains in [INTEGRATION.md](docs/INTEGRATION.md). The approved visual rules live in [DESIGN.md](DESIGN.md).

## Product context

- Audience: center administrators, teachers, and secretaries.
- Primary jobs: administer students and groups, record attendance and payments, prepare/review exams, and inspect operations.
- The AI studio exposes exam drafting and teacher review only. Legacy worksheet, lesson and essay drafts remain stored for snapshot compatibility without a UI entry point.
- Market: Egyptian learning centers, based on the project brief and repository domain rules.
- Locales: Arabic and English. Dates use Africa/Cairo; currency is EGP.
- Accessibility target: visible keyboard focus, semantic controls, accessible labels, and keyboard-operable Base UI dialogs. A full WCAG audit has not been completed.

## Business-context sources

| Scope | Source of truth |
| --- | --- |
| Local records, roles, attendance, money, archival and migration | [docs/DATA_MODEL.md](docs/DATA_MODEL.md) |
| Confirmed vs proposed services, errors, retries and integration requirements | [docs/INTEGRATION.md](docs/INTEGRATION.md) |
| Product scope and operational workflows | [README.md](README.md) and the supplied EduFlow project brief |

These are local-demo contracts; client-side role presentation is not backend authorization.

## Visual and component ownership

- Visual source: [DESIGN.md](DESIGN.md).
- Runtime tokens: hand-maintained semantic CSS variables in `src/material-theme.css`.
- Adapter: Tailwind v4 `@theme inline` aliases and the shared CSS component layer.
- Button, field feedback, status, table and dialog owners: `src/components/ui.jsx`, `src/components/feature-ui.jsx`, and `src/material-theme.css`.
- Dialog and alert-dialog primitives: Base UI.
- Themes: light only. Arabic/English direction and copy follow the active locale.

## Canonical UI Map

| Capability | Canonical owner | Source of truth | Allowed variants | Verification |
| --- | --- | --- | --- | --- |
| Tables | Shared semantic table in `feature-ui.jsx` | This contract | Read-oriented; horizontal scroll on narrow screens | Rendered narrow-screen review |
| Select/Listbox | Native `<select>` | This contract; platform popup accepted | Native platform popup and keyboard behavior | Existing browser workflows; no new test suite run for this update |
| Date | Native date/time inputs | This contract; platform popup accepted | Native date/time; active browser locale | Existing browser workflows; unchanged ownership |
| Form | Shared `Field`, `Feedback`, `Submit` | This contract and `docs/DATA_MODEL.md` | `noValidate`, localized errors, retained input after failed save | Existing browser workflows; build and rendered review for this update |
| Dialogs | Base UI `Dialog` and `AlertDialog` | This contract | Modal focus, dismissal and restoration | Rendered keyboard review |
| Roles | Workspace shell and domain permission map | `docs/DATA_MODEL.md` | Demo preview only; server must enforce real permissions | Existing permission workflows; no permission policy change |
| Workspace search | `WorkspaceSearch.jsx` with shared `Modal` / `SearchField` | This contract | Button and Ctrl/Meta+K; projected local data only | Rendered keyboard and narrow-screen review |
| Search fields | `SearchField` in `feature-ui.jsx` | This contract | Clear button restores input focus; immediate local results | Rendered clear/no-results review |
| Source preview | `Materials` with shared `Modal` | This contract and `docs/DATA_MODEL.md` | Metadata only; illustrative cover, not PDF bytes | Rendered preview and navigation review |

## Navigation and operation feedback

The eight established hash destinations remain available. Sidebar, role preview and page actions use semantic links/buttons. Successful CRUD dialogs close and the updated shared data appears on the owning page; failures remain next to the form and preserve entries. Repeated submission is blocked by the shared action lock and idempotency key. Conflicts offer refresh and re-entry review. The responsive menu uses the existing app-owned modal navigation pattern.

## Form and state behavior

- Workspace search is transient and does not persist typed names. It offers native links, visible keyboard hints, Arrow keys/Enter, Escape dismissal and an explicit no-results state. Student destinations filter by code and include archived records. The same role permission map owns every result category.
- Material filtering combines title search with all/ready/needs-attention states, an announced result count and a clear-filter recovery action. Preview does not mutate records; its preparation action opens the existing source-selected studio route.
- Overview shortcuts navigate to existing permission-gated workflows. Preparation steps describe the selected sources and currently displayed saved draft; they do not claim remote model progress.
- `Submit` uses `aria-busy`, an inline spinner and a preserved label footprint during saves.
- The brand guide is a separate marketing/design surface: clipboard feedback has a manual-copy recovery path, logo/font controls have real state, and product previews are labelled screenshots with links to the live local demo.

- Labels are associated with native controls through the shared `Field` primitive.
- Forms use `noValidate`; the domain layer provides localized validation messages.
- Pending save disables the submit action. Failure leaves entered values available for retry.
- Destructive archive and financial adjustment use app-owned confirmation surfaces with a reason.
- Status is textual and paired with semantic color. A missing attendance record stays distinct from absence.
- PDF metadata retry keeps the selected `File` only in component memory. It does not upload or index bytes; navigating away requires reselection.
- Reports communicate their sample, period and calculation source; unsupported learning-evidence claims remain unavailable.

## Async, permission and recovery behavior

The local service serializes writes, validates before snapshot commit, and rejects stale revisions. Storage failure commits no partial mutation. Reads are canceled/ignored when their request or role is obsolete. There is no live authentication, server synchronization, guaranteed cross-tab transaction, document processing, AI provider, job scheduler, or message delivery in this demo. Proposed live behavior is documented in `docs/INTEGRATION.md`.

## Verification boundary

### Operational feedback update — 2026-10-23

- `domain/reports.js` owns report selectors. Attendance percentages use present + late divided by present + late + absent; excused and unrecorded are excluded. No denominator displays an em dash. Period and group filters apply before aggregation. No fixture values substitute for zero.
- Learning-risk, quiz mastery, syllabus coverage and comparative trend claims are not displayed without supporting records. Follow-up lists show actual recorded absence and open student profiles directly.
- Student detail uses `#students?studentId=...&status=all`. Guardian details, grade and notes are optional fields saved through the existing validated student command. Enrollment, attendance and finance histories link to existing workflows; teacher projections continue to exclude finance.
- Shared tables paginate at 10/25/50 rows, offer header sorting, clamp/reset pages after dataset changes, and keep the first column sticky on phones. Sort and page are transient component state in this local demo; profile return currently opens the directory defaults.
- Receipt filters apply to receipt/adjustment event dates in Cairo. Net period collections subtract adjustments occurring in the period, including adjustments to earlier receipts. Charges remain a separate balance view. Receipt preview shows original values and adjustments, and prints only the receipt.
- Current evidence: 23 domain/report tests, production build, `scripts/check-feedback.mjs`, and `test-results/feedback-audit.json`. Existing historical verification entries below do not replace current test output.

The project maintains unit/domain tests, isolated Playwright browser workflows, export-package checks, and a production build. Refer to [docs/VERIFICATION.md](docs/VERIFICATION.md) for the last recorded full suite. For this design-system change, the implementation check is the Vite production build and direct rendered-screen review; no behavioral contract is changed.
