# JobApp AI Assistant

Local-first job application assistant for parsing structured CVs, tailoring applications to job postings, and exporting editable application packages.

Ciência Vitae exports are a strong reference use case because they are highly structured and widely used by researchers and institutions in Portugal, including academic evaluation, project submission, and funding workflows such as FCT calls. They can include education, professional experience, publications, projects, supervision, events, software, identifiers, and cross-references to research platforms such as ORCID, Scopus, ResearchGate, and Google Scholar.

For a complete practical guide, see [TUTORIAL.md](TUTORIAL.md).

This app can be presented under the broader [d'BiYOK Lab](docs/DBIYOK_LAB.md) idea, a PagBiOmicS initiative for Bring Your Own Key AI-assisted apps across professional productivity, biodiscovery, learning, entrepreneurship, and everyday workflows.

![JobApp AI Assistant mark](assets/jobapp_ai_assistant_mark.svg)

d'BiYOK page materials are kept separately:

- [d'BiYOK Lab concept](docs/DBIYOK_LAB.md)
- [PagBiOmicS page content](docs/PAGBIOMICS_DBIYOK_PAGE_CONTENT.md)
- [Blog post draft](docs/BLOG_POST_DBIYOK_JOBAPP.md)
- [Experimental Web App Lite page](docs/jobapp-web-lite.html)
- [Professional Web CV pipeline](docs/CV_WEB_EXPORT_PIPELINE.md)
- [Canonical CV JSON schema](schemas/cv_canonical.schema.json)
- [Validated CV golden-reference protocol](docs/CV_GOLDEN_REFERENCE.md)

## What It Does

- Parses a local or uploaded CV PDF/TXT into editable JSON-like sections.
- Accepts structured CV sources from the user's computer, including PDF, TXT, and XML.
- Includes a dedicated, credit-free heuristic parser for Ciência Vitae PDF exports: it removes layout noise and separates education, affiliations, projects, publications, chapters, conferences, datasets, teaching, distinctions, and languages into editable records.
- Lets the user include or exclude each CV item before matching a job.
- Places CV focusing before job matching so the AI receives only the evidence the user wants emphasized.
- Exports the parsed CV itself as Markdown, DOCX, PDF, or JSON.
- Exports only selected CV fields when the user wants to manually prepare a focused profile before calling the AI.
- Fetches a job posting URL and fills the job description automatically when the page allows scraping.
- Generates:
  - tailored CV bullets,
  - cover letter,
  - interview preparation,
  - ATS keywords and score estimate.
- Exports each generated application to `exports/` automatically as Markdown.
- Allows one-click export to Markdown, DOCX, and PDF.
- Keeps a local SQLite history of generated applications.

Parsed CV export is local and credit-free. The high-quality parser can use the configured AI provider, but the app also includes a local heuristic parser mode for free tests, structured Ciência Vitae XML/PDF workflows, and public web demos.

**Parser scope (be honest about what each mode does).** The robust heuristic parser is specific to Ciência Vitae exports. For generic PDFs, DOC/DOCX, or non–Ciência Vitae XML, the heuristic mode now returns a *neutral* result — it extracts only basic contact fields rather than a full structure. This is a deliberate, safer default (it never invents or reuses another person's data); for a rich structure from those formats, use the AI parser or edit the sections manually. Note also that **skills are populated only from the Ciência Vitae XML export**, because the PDF/RTF export does not contain the Knowledge-fields keywords (see `docs/CIENCIA_VITAE_EXPORT_BEHAVIOR.md`).

## AI Providers

The app is BYOK-friendly: users can bring their own API key.

Supported provider profiles:

- Google Gemini
- OpenAI / ChatGPT
- Anthropic Claude
- Custom OpenAI-compatible API
- Local OpenAI-compatible server
- Ollama local
- DeepSeek
- GLM / Zhipu AI

Local providers can run without an API key when they expose an OpenAI-compatible `/chat/completions` endpoint.

## Recommended Local Workflow

For non-technical users, the preferred distribution is the desktop executable: double-click `JobApp-AI-Assistant-Windows.exe`, the app starts a local server, and the browser opens automatically.

For development:

```powershell
cd path\to\JobApp-AI-Assistant
python -m pip install -r requirements.txt
python -m uvicorn jobapp_ai_assistant:app --host 127.0.0.1 --port 8091
```

Then open:

```text
http://127.0.0.1:8091/
```

The app may also run on `8080`, but that port can be occupied by other local services on the workstation.

## Desktop Distribution

Windows build:

```powershell
cd path\to\JobApp-AI-Assistant
powershell -ExecutionPolicy Bypass -File .\build_exe.ps1
```

Output:

```text
dist\JobApp-AI-Assistant-Windows.exe
```

For distribution, share only `dist\JobApp-AI-Assistant-Windows.exe`. Do not bundle local `data/`, `exports/`, `applications.db`, or API configuration files. On first run, the app creates its own local data folders next to the executable on the user's computer.

The launcher prefers `localhost:8080`; if that is busy, it tries `8090`, `8091`, `8000`, and then a free port from `8100+`.

macOS `.dmg` is a future release target. It should be built on macOS or through a GitHub Actions macOS runner, not from this Windows workstation.

To generate a local PDF guide next to the executable:

```powershell
powershell -ExecutionPolicy Bypass -File .\build_readme_pdf.ps1
```

Linux and macOS users can fork the repository or run it locally with Python:

```bash
git clone <repository-url>
cd JobApp-AI-Assistant
python -m pip install -r requirements.txt
python -m uvicorn jobapp_ai_assistant:app --host 127.0.0.1 --port 8091
```

## CV Parsing Workflow

1. Use **Choose CV from PC** or **Import CV from local drive** to upload a PDF/TXT/XML CV through the file explorer.
2. Select **AI parser** when a configured API key or local LLM is available.
3. Select **Heuristic parser** for a free local parse that avoids LLM/API credits.
4. Use **Open last parsed CV** to reuse the app's local CV memory instead of importing the same file repeatedly.
5. Use Step 2 to include or exclude publications, projects, experience, software, or other sections before matching.
6. Export either:
   - the full parsed CV,
   - only the selected fields,
   - or the final tailored application package after matching a job.

The parsed export intentionally uses structured data rather than raw Ciência Vitae PDF headers. It removes repeated page headers, footer noise, and Portuguese platform labels. Common labels and course names are normalised to English when this is deterministic; specialised titles should remain editable and be reviewed before publication.

The detailed parsed CV editor is intentionally placed after the main workflow so large academic CVs do not push job matching and final exports too far down the page.

## Professional Web CV Export

JobApp creates a source-aware `cv_canonical.json` whenever a CV is imported. This is a local, ignored data file that separates CV content from presentation. It is the foundation for a professional HTML export suitable for a Durable Custom Code block or a standalone web CV.

1. Import a CV. Prefer a Ciência Vitae XML export when available; PDF/TXT stay useful for narrative material and fallback parsing.
2. Review the parsed CV and use **Download professional HTML** in Step 2.
3. Contact details remain hidden by default. Enable them only when the selected fields are intended for a public page.
4. Open the resulting `.html` file to review it, then paste its content into Durable if desired.

The generated HTML is driven by `templates/durable_cv_template.html`; personal facts live in `data/cv_canonical.json`, not in the template. See [CV_WEB_EXPORT_PIPELINE.md](docs/CV_WEB_EXPORT_PIPELINE.md) for source priority, privacy safeguards, provenance, prompt versioning, and the golden-reference validation workflow. An export configuration example lives in [web_cv_export_config.example.json](docs/examples/web_cv_export_config.example.json).

## Provider Setup Tutorial

1. Open the app.
2. Go to **AI Engine**.
3. Select a provider.
4. Paste the API key if the provider requires one.
5. Set the model and base URL.
6. Click **Save engine**.
7. Click **Test connection**.

Direct provider help:

- Gemini API key: <https://ai.google.dev/gemini-api/docs/api-key>
- Google AI Studio: <https://ai.google.dev/aistudio>
- OpenAI API keys: <https://platform.openai.com/api-keys>
- Claude API keys: <https://console.anthropic.com/settings/keys>
- Ollama local API: <https://docs.ollama.com/api>

Security note: never commit `data/llm_providers.json` with a real API key. The file is ignored by Git, but local copies can still contain secrets; clear keys before packaging, screenshots, or support requests.

For local Ollama:

```text
Provider: Ollama local
Base URL: http://localhost:11434/v1
Model: llama3.1 or another installed Ollama model
API key: leave empty
```

For a local OpenAI-compatible server, such as the one used in Clean&Merge:

```text
Provider: Local OpenAI-compatible server
Base URL: http://localhost:8081/v1
Model: local-model
API key: leave empty unless your server requires one
```

## PagBiOmicS Web Roadmap

This repository is currently a localhost version. The safest PagBiOmicS web strategy is to offer two routes and explain the trade-offs clearly:

- **Run locally, recommended:** download the app, run it on localhost, and enter API keys only on the user's computer.
- **Run from the web, experimental:** possible for browser-based CV import, focused editing, and BYOK generation, but it must warn users that the API key is pasted into a browser page. Users should use a temporary or restricted key, test the workflow, clear the field, and revoke/delete the key after testing.

The initial public web page should explain both routes: a local desktop app and an experimental Web App Lite page. The Web App Lite warning focuses on API-key exposure in the browser.

- Downloadable Windows executable first.
- Mac `.dmg` later, ideally built on macOS or GitHub Actions.
- BYOK inside the local app for routine work; Web App Lite is for browser tests with temporary or restricted API keys.
- Free local tools: heuristic parsing and parsed-CV exports without AI credits.
- Email capture for updates, tutorials, and release notifications.
- Newsletter signup for job-search, bioinformatics, omics, and scientific-career resources.
- Optional sponsor placements from biotech, omics, scientific software, training providers, recruiters, or job boards.

The web version must be designed carefully around API-key handling: a browser-entered key can be exposed by shared devices, extensions, injected scripts, autofill, or careless reuse.

An embeddable HTML prototype is included in [pagbiomics_embed.html](pagbiomics_embed.html). It is a landing/download block with a link to the experimental Web App Lite page.

- It links users to the desktop release.
- It explains that browser-entered API keys should be temporary or restricted and removed/revoked after testing.
- It links directly to Gemini/AI Studio/Ollama setup pages.
- It links to Web App Lite as an experimental browser BYOK mode.

The Web App Lite page vendors the minimal PDF.js browser files under `docs/vendor/` so PDF parsing does not require loading a PDF parser from an external CDN on the same page where users enter an API key.

Future paid/API-hosted/Web3 ideas are tracked in [CHANGELOG.md](CHANGELOG.md), not exposed as current web options.

Near-term monetization without direct payments:

- email-gated release notifications and newsletter growth,
- sponsored placements from biotech, omics, scientific software, or training providers,
- job board partnerships,
- premium consulting/CV review services outside the automated app.

## Notes

- LinkedIn and some platforms may block scraping. In that case, paste the job text manually.
- Localhost mode is the safest default for private CV work.
- The generated outputs are starting points and should be reviewed before submission.
