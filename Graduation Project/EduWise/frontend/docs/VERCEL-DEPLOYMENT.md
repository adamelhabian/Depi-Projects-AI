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

## Publish a later version

Run these from the frontend directory. Choose a new release directory name for every snapshot so old release files remain recoverable.

```powershell
npm run build
node scripts/prepare-vercel-brand.mjs eduflow-ai-brand-r2
vercel project inspect eduflow-ai-brand --scope youssef-mms-projects --non-interactive
vercel deploy --cwd .deploy/eduflow-ai-brand-r2 --prebuilt --prod --project eduflow-ai-brand --scope youssef-mms-projects --yes --non-interactive
node scripts/check-vercel-brand.mjs https://eduflow-ai-brand.vercel.app
```

The prepare script verifies relative links, image loading, logo variants, product previews, the mobile layout and the linked demo. The live check opens a fresh browser without a Vercel login and verifies public page access, downloads and the approved SVG checksum. Reports are saved to `test-results/vercel-brand-live-check.json` and screenshots to `test-results/vercel-brand-*.png`.

`.deploy/` and `.vercel/` are ignored. This is a snapshot deployment; saving local source changes does not update the public website until a new deployment is made.
