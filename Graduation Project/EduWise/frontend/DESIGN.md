---
version: alpha
name: EduFlow AI
description: Bilingual learning-center operations and teaching workspace, using Material 3 roles with educational blue and restrained apricot accents.
colors:
  primary: "#315da8"
  on-primary: "#ffffff"
  primary-container: "#d8e2ff"
  on-primary-container: "#001a41"
  secondary: "#555f74"
  secondary-container: "#dce2f9"
  on-secondary-container: "#141c2b"
  tertiary: "#805334"
  tertiary-container: "#ffdcc3"
  on-tertiary-container: "#301400"
  accent: "#f2b880"
  success: "#276443"
  success-container: "#d5eddd"
  on-success-container: "#123723"
  background: "#f8f9ff"
  surface: "#f8f9ff"
  surface-container-low: "#f2f3fa"
  surface-container: "#eceef5"
  surface-container-high: "#e6e8ef"
  on-surface: "#1a1c22"
  on-surface-variant: "#44474f"
  outline: "#747780"
  outline-variant: "#c4c6d0"
  error: "#ba1a1a"
  error-container: "#ffdad6"
typography:
  sans:
    fontFamily: "DM Sans, IBM Plex Sans Arabic, sans-serif"
  display:
    fontFamily: "Plus Jakarta Sans, IBM Plex Sans Arabic, sans-serif"
  arabic:
    fontFamily: "IBM Plex Sans Arabic, DM Sans, sans-serif"
  mono:
    fontFamily: "ui-monospace, SFMono-Regular, monospace"
rounded:
  DEFAULT: "12px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "28px"
  full: "999px"
spacing:
  control-height: "40px"
  field-height: "48px"
  page-gutter: "32px"
components:
  button:
    rounded: "999px"
    height: "40px"
  input:
    rounded: "4px"
    height: "48px"
  card:
    rounded: "16px"
  dialog:
    rounded: "28px"
  navigation-item:
    rounded: "999px"
---

## Overview

### Creative North Star

Material Design 3's adaptable component roles give the operations workspace familiar, accessible structure. Educational blue, restrained apricot accents, and education imagery define EduFlow's Egyptian center product identity.

### Product context and register

- **Audience and primary job:** Center administrators, teachers, and secretaries managing daily learning-center operations in one bilingual workspace.
- **Target market(s) and evidence:** Egyptian education-center demo; product brief and existing Cairo/Egyptian-pound domain rules are in `docs/DATA_MODEL.md` and `docs/INTEGRATION.md`.
- **Locale(s) and language policy:** Arabic and English; Cairo timezone and EGP. IBM Plex Sans Arabic is the Arabic UI font; DM Sans and Plus Jakarta Sans provide the Latin interface hierarchy.
- **Usage scene:** Frequent desktop administration with responsive phone access for attendance, student records, and review.
- **Register:** Product UI. Action clarity, legible data, and reliable state cues lead.
- **Memorable signature:** Educational blue paired with cool tonal containers, small apricot highlights, and blue/apricot educator and preparation photography. Green-dominant photography is not used in the active identity.
- **Restraint:** Routine records stay quiet; primary actions and selected navigation use the primary/secondary roles. Do not use decorative gradients, heavy shadows, or color as the only state cue.
- **Anti-references:** Generic analytics templates, saturated multi-color dashboards, and direct copies of Google's app branding.
- **Token ownership/runtime mapping:** Existing CSS remains canonical. This file mirrors the approved values; `src/material-theme.css` maps Material 3 semantic roles into Tailwind v4 and shared CSS consumers. The stylesheet is the single runtime adapter.

## Colors

The educational-blue seed identifies primary actions and selected content; secondary roles give navigation and supporting states a softer container. Apricot accents and warm tertiary containers highlight creative teaching content. Surface roles separate the page, cards, and table headers without outlining every region. `outline` is reserved for controls and boundaries. Green success roles identify attendance and completed work independently of the brand color; error roles identify failures. Text and icons accompany color. Focus uses the primary role with a visible outline. The current product ships a light theme; dark mode is not implied.

Exact runtime values are in `src/material-theme.css` and mirrored above. Tailwind utilities consume `--color-primary`, `--color-surface-container`, and related `@theme inline` aliases. Shared controls and page surfaces consume `--md-sys-color-*` directly. No separate Material UI theme or duplicate component library is installed.

## Typography

Arabic uses locally bundled IBM Plex Sans Arabic weights 400, 500, 600, and 700. English body text uses DM Sans; Latin display headings and numeric metrics use Plus Jakarta Sans. Arabic headings use IBM Plex Sans Arabic. Body copy is readable at 14px or larger on the new workspace surfaces; compact metadata keeps a clear text hierarchy. Student codes, IDs, and phone numbers preserve their own direction with `<bdi>`/LTR isolation. Financial figures use tabular numerals.

## Layout

Keep the established grouped sidebar, top app bar, main page heading, and focused page content. Desktop content retains its readable max width; the sidebar becomes the existing mobile navigation surface on narrow screens. Page content uses 32px desktop and 18px mobile gutters. Dense read-only data remains in semantic, horizontally scrollable tables; forms keep document scrolling. Controls retain visible focus and stable dimensions while saving.

## Elevation & Depth

Hierarchy comes primarily from `surface-container` tonal steps and spacing. Ordinary cards use low surfaces with no shadow. Reserve the single low elevation token for a floating caption or overlay where separation is needed. Dialog backdrops and modals remain above the app surface. Do not use blur or shadow as a substitute for contrast.

## Shapes

Inputs use a restrained 4px corner; small support elements use 8px; fields and dense panels use 12px; cards use 16px; dialogs and hero surfaces use 28px. Buttons, navigation selection, and segmented selection use full rounding. Tables use row dividers, not rounded individual cells.

## Components

### Foundational visual states

Base UI owns dialog and switch interaction semantics; native fields keep browser keyboard behavior. Shared controls define hover, pressed, focus-visible, disabled, and busy visuals. Selected navigation and segmented controls use a tonal container. Success, warning, error, ready, and failed states retain readable labels; error surfaces use error-container roles. Subtle interaction transitions and the submit spinner follow the reduced-motion policy below.

### Buttons and actions

The primary filled pill is for a page's main action. Secondary is a tonal filled pill; ghost is a low-emphasis action. Keep dangerous archive and financial adjustment flows inside their existing confirmation behavior. Icon-only actions retain their accessible names.

### Navigation and data display

The fixed sidebar and responsive drawer share the same nav tokens. Selected destinations use a tonal pill. Data tables keep their horizontal scroll surface, semantic headers, tabular figures, and visible row boundaries. Metrics remain quiet tonal cards, not standalone visualizations.

### Forms and overlays

Fields use a real label, 48px minimum height, neutral outline, and primary focus. Native date/time and select popups remain operating-system controls. Inline errors use error-container colors and text. Existing Base UI dialogs retain focus management and a large container radius.

### Iconography

Lucide remains the icon family. Use its existing 16–24px stroke icons beside action labels; keep text on non-universal actions.

### Motion

Interaction motion uses the `--ux-motion` and `--ux-motion-ease` tokens in `src/experience.css`: 160ms color/border feedback and restrained image hover transitions. Movement helps identify actionable surfaces; it does not delay navigation or hide content. All transitions and nonessential animation are disabled for `prefers-reduced-motion`.

### Contextual photography

Use `/images/educator-blue.webp` for teaching context and `/images/materials-blue.webp` for sources/preparation. Images reserve their aspect ratio, below-fold imagery is lazy-loaded, and source cards explicitly label photos as illustrative covers. Asset prompts and provenance live in `public/images/ASSETS.md`. Do not imply a photograph is the actual PDF or a real customer.

### Content and data visualization

Use direct bilingual action language, Cairo-localized dates, EGP amounts, explicit demo/source states, and labeled status. Charts and reports distinguish measured demo records from unavailable evidence.

## Do's and Don'ts

- **Do:** Use semantic Material 3 color roles and the runtime aliases in `src/material-theme.css`.
- **Do:** Use educational blue for brand actions, apricot for restrained accents, green for success, and keep IBM Plex Sans Arabic typography, bilingual behavior, and functional Base UI components.
- **Don't:** Add MUI alongside Base UI for the same interaction surfaces.
- **Don't:** Introduce dark-mode, animation, or a component redesign beyond the approved shared visual language without a product decision.
