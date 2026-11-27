# EduFlow AI brand deployment

- Brand guide: https://eduflow-ai-brand.vercel.app/brand/
- Linked application demo: https://eduflow-ai-brand.vercel.app/
- Vercel team: `youssef-mms-projects`
- Project: `eduflow-ai-brand` (`prj_JTyAs6fTlI5jHiJ7uyTzBhSjXrvM`)
- Initial production deployment: `dpl_GL5AyEoxkn3LLfFqjaCbAeXojQym`
- Published: 2026-10-21
- Source: locally built Vite snapshot, deployed with Build Output API v3.
- Local snapshot: `.deploy/eduflow-ai-brand/.vercel/output/`

The snapshot contains the built application and public assets. It includes the approved option 05 logo, 4096px PNG exports, fonts, interactive brand guide and download archives. The application remains a local-data demo; this deployment adds static hosting.

## Publish the authenticated application

Run from `frontend`. The existing `eduflow-ai-brand` project builds the Vite app and the functions in `api/`. The `/brand/` guide and browser-local demo at `/?mode=demo` are included in the same build.

- Connect a private Blob store to this project for preview and production with OIDC. Vercel supplies `BLOB_STORE_ID`.
- Set the sensitive `EDUFLOW_AUTH` environment variable in each target to a JSON object with `accounts` (the hashed entries produced by `npm run accounts:setup`) and a random 32-byte hex `sessionSecret`. Keep passwords, hashes, and secrets outside the Git checkout and deployment upload.
- Deploy and verify sign-in, workspace reads and writes, and the brand page in preview before deploying to production. Preview and production store their records separately.

```powershell
vercel deploy --project eduflow-ai-brand --scope youssef-mms-projects --yes --non-interactive
vercel deploy --prod --project eduflow-ai-brand --scope youssef-mms-projects --yes --non-interactive
```

The initial prebuilt snapshot remains recorded above. Authenticated deployments require a source build so Vercel can build the API functions.
