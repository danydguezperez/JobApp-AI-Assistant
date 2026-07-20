# Changelog

## v0.2.0 - July 2026

### Fixes

- Updated the OpenAI default model string to `gpt-5.6-terra` while keeping `gemini-3.5-flash` and `claude-sonnet-5` as current defaults.
- Removed the local hardcoded Gemini API key from `data/llm_providers.json`.
- Avoid sending non-default `temperature` values to `claude-sonnet-5`, which rejects sampling parameters in the Anthropic Messages API.
- Replaced version-pinned download links with GitHub `/releases/latest/` links in public-facing HTML.

### Features

- Added a monetization layer to web-facing pages: email capture, provider links, sponsor placeholder, consulting CTA, and Pro waitlist CTA.
- Updated `pagbiomics_embed.html` with release-download flow, provider links, and newsletter/consulting sections for the PagBiOmicS d'BiYOK Lab page.
- Updated `docs/jobapp-web-lite.html` with BYOK guidance, release links, provider setup links, sponsor slot, newsletter capture, and Pro waitlist.
- Added a GitHub Actions workflow for automatic Windows `.exe` builds on tag push.

## Unreleased

### Professional Web CV pipeline

- Added the versioned `cv_canonical.json` representation and public JSON Schema.
- Added Ciência Vitae XML canonicalization with per-record source metadata, selection state, and visibility.
- Added a standalone, Durable-oriented professional HTML template that is separated from CV content.
- Added local professional HTML export and privacy-first defaults: public contact details stay hidden unless explicitly selected.
- Added reproducibility documentation, a versioned AI-curation prompt, and a generic export configuration example.

### Ciência Vitae heuristic parser

- Replaced the PDF fallback-first behaviour with a dedicated deterministic parser for official Ciência Vitae PDF exports.
- Added separate editable records for education, affiliations, projects, publications, book chapters, conferences, datasets, teaching, distinctions, and languages.
- Added a browser-side section-first counterpart for Web Lite, with local Markdown and JSON exports that do not require an API key.
- Added automated parser coverage with a representative Ciência Vitae fixture and validated the desktop executable against the 22-page reference PDF.

- Validated the local heuristic parser against a 22-page Ciência Vitae PDF and a curated PagBiOmicS HTML CV reference.
- Fixed local heuristic phone extraction so labelled `Mobile phone` values are preferred over date ranges.
- Improved local heuristic distinction extraction to use the formal Ciência Vitae distinction section rather than the page-1 summary.
- Web prototype changed again after product/security review:
  - no hosted free LLM tests paid by PagBiOmicS,
  - no API-key entry in the website,
  - website becomes a download/education page,
  - BYOK happens inside the local desktop app.
- Hosted API, subscriptions, crypto, Cardano native tokens, and direct paid credits are moved to future roadmap.
- Added direct API key help links for Gemini, OpenAI, Claude, and Ollama.
- Expanded the experimental Web App Lite page with browser-side CV import, PDF/TXT/Markdown/JSON parsing, editable section toggles, focused CV export, job URL fetch attempts, and Gemini BYOK generation.
- Renamed public distribution references from JobApMaker to JobApp AI Assistant.
- Clarified Web App Lite warnings around browser-entered API keys: use a temporary or restricted key, test, clear the field, and revoke/delete the key after testing.
- Future monetization ideas to evaluate:
  - sponsored biotech/scientific software placements,
  - newsletter sponsorships,
  - job board partnerships,
  - affiliate links for training/cloud/dev tools where allowed,
  - paid consulting or CV/application review services,
  - unobtrusive export-time ads.
