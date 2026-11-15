# Verification record

## Visual and UX update — 2026-10-21

- Production build passed after the blue/apricot photography, shared workspace search, quick actions, source filtering/metadata previews and preparation guidance were added.
- Premium UI static audit: `audit_project.py . --mode strict --output test-results/ux-audit.json` returned 0 findings after existing native-control ownership was recorded and textarea sizing was made explicit. This is static evidence, not a full accessibility audit.
- Rendered review used isolated browser contexts. Captures: `test-results/ux-overview-desktop.png`, `ux-search-desktop.png`, `ux-library-desktop.png`, `ux-material-preview.png`, `ux-library-mobile.png`, and `ux-brand-mobile.png`.
- Search input received initial focus, Escape returned focus to the search trigger, both the library and brand guide fit a 390px viewport, and the reviewed pages reported no page errors.
- The brand export regenerated the board PNG/PDF, product screenshot previews and ZIP; its color-pair and mobile-width checks completed successfully. Photos are delivered as 80 KB and 143 KB WebP files, with provenance in `public/images/ASSETS.md`.
- No new automated test file was added. Automatic approval review rejected both adding a new test script and running `npm test` as outside the current request. Historical suite results below were not rerun for this update.

The main interface uses native links/buttons, Base UI modal focus management and localized copy. No real AI generation, document indexing or messaging capability was added by this UX update.

Date: 2026-10-21. Local Windows workspace, Node 24.20.0, Playwright with installed Microsoft Edge. Browser checks ran against the built application at `http://127.0.0.1:4173`, in isolated contexts. The workspace has no Git repository, so this record identifies the working files rather than a commit.

## Final results

| Command | Actual result |
| --- | --- |
| `npm test` | 20 passed, 0 failed |
| `npm run build` | Passed; Vite production output generated |
| `npm run test:smoke -- http://127.0.0.1:4173` | 10 workflow checks passed, 0 page errors |
| `npm run test:exports` | 6 output checks passed, 0 failed |

The original baseline build and 11 earlier smoke checks passed before implementation; those are historical results, not the final suite count. During final verification, a repeated selection of the same preview role exposed a loading-state bug. The role setter now ignores unchanged values; the final browser run passed including that case and a future teacher lesson.

## Covered behavior

- Stable student identities, unique display codes, multiple group enrollments and retained archived references.
- Enrollment eligibility; duplicate attendance within a session; two sessions on one day; correction reasons, actor and history; reload persistence.
- Exact minor-unit money, partial receipts, derived balances, discounts, reference deduplication and traceable refund/void adjustments.
- Failed requests preserving entered payment data, repeated submit protection, idempotent retries, revision conflicts and storage failures leaving committed data intact.
- Legacy data preservation and migration notices after reopening; malformed snapshots backed up before recovery; future schemas protected from writes.
- Role-specific pages, actions and forbidden deep links; assigned groups and future teacher sessions; unchanged role selection remaining usable.
- Invalid PDF signatures; transient metadata-save failure followed by retry without reselection; exactly one saved entry; honest failed/unindexed metadata state and no fabricated progress.
- Unsupported generation requests, editable drafts, invalidation of review after edits, correct answer mappings across shuffled variants and independent student/key export projections.
- Keyword rubric suggestions and separately retained teacher overrides.
- Automation activation, explicit recorded absence, event deduplication, draft editing, review, approval and unavailable delivery.
- Report denominators, missing observations and explicit evidence boundaries.
- Arabic RTL, all eight routes at 320/390-pixel widths without page overflow, localized validation with preserved inputs, keyboard dialog opening/focus containment/Escape/focus restoration and mobile navigation.
- Actual browser downloads of English/Arabic Word and PowerPoint files; separate teacher key; UTF-8 Arabic CSV with formula-like input escaped as text.

## Export and visual inspection

The export checker opens Office packages and inspects their content/relationships, Arabic text, direction metadata and audience separation. Student packages exclude correct-answer fields and explanations; the teacher Word package contains them. CSV checks verify the BOM, Arabic names and formula escaping.

Browser screenshots were inspected for the dashboard, Arabic mobile layout and Arabic student print view. The print view has right-aligned Arabic questions/choices and no answer section. Export libraries load on demand; the final main application bundle is approximately 443.38 kB minified / 140.07 kB gzip.

Artifacts are in ignored `test-results/`, including `workspace-desktop.png`, `workspace-ar-mobile.png`, `student-print.png`, `student-ar-print.png`, `reports.png`, `.docx`/`.pptx` samples and `students-safe.csv`. Failure traces from intermediate runs may also remain there; the final results above supersede those runs.

## Not run / external dependencies

- No live backend, authenticated session, tenant isolation, real PDF storage/indexing, model provider, scheduler or message delivery is implemented in this repository. No live integration was tested.
- Office package checks do not establish visual rendering in Microsoft Word, PowerPoint or LibreOffice. Those applications were not opened for rendering checks.
- The browser print page was checked; the operating-system print dialog, a saved PDF's pagination and physical printing were not tested.
- No Firefox/WebKit matrix, screen-reader session or full WCAG audit was run.
- Local snapshot validation and revision checks do not establish transactional correctness for simultaneous cross-tab writes. Server transactions and uniqueness/idempotency constraints remain required for live operation.

See [setup and capabilities](../README.md), [local data rules](DATA_MODEL.md) and [confirmed versus proposed integrations](INTEGRATION.md).
