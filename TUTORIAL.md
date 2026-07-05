# JobApp AI Assistant Tutorial

## Why This App Exists

Job applications are rarely won by sending the same CV everywhere. Scientific and technical profiles are especially difficult to present because the same person may need to emphasize publications, software, grants, commercial experience, teaching, or consulting depending on the job.

JobApp AI Assistant was created to solve that problem locally:

- parse a structured CV into editable sections,
- remove export noise from platforms such as Ciencia Vitae,
- let the user choose exactly which CV items matter for a specific job,
- match that filtered profile against a job posting,
- generate an editable application package,
- keep private data on the user's own machine by default.

## Who It Helps Most

- Researchers applying outside academia.
- Bioinformaticians and omics specialists with publication-heavy CVs.
- PhD holders who need industry-ready CV versions.
- Scientific sales and biotech business-development profiles.
- Freelancers who tailor profiles for different client types.
- Career coaches who want a local BYOK workflow.

## What It Can Do

- Upload a CV from the computer as PDF, TXT, or XML.
- Parse Ciencia Vitae-style exports into structured English fields.
- Use AI parsing for better extraction, or local heuristic parsing without API credits.
- Edit parsed CV fields in the browser.
- Select or exclude individual publications, projects, jobs, skills, and other sections before matching a job.
- Fetch a job description from a URL when the site allows scraping.
- Generate a tailored CV, cover letter, and interview preparation.
- Export the parsed CV or final application as Markdown, DOCX, PDF, or JSON.
- Save local application history in SQLite.
- Connect Gemini, OpenAI, Claude, DeepSeek, GLM, Ollama, or another OpenAI-compatible API.

## How To Run On This PC

For ordinary users, use the packaged desktop app:

```text
Double-click JobApMaker.exe
```

It starts the local server and opens the browser automatically.
The API key is entered inside the local app, not on the PagBiOmicS website.

For development, open PowerShell:

```powershell
cd path\to\JobApp-AI-Assistant
python -m pip install -r requirements.txt
python -m uvicorn jobapp_ai_assistant:app --host 127.0.0.1 --port 8091
```

Open:

```text
http://127.0.0.1:8091/
```

Port `8091` is recommended on this workstation because `8080` may already be used by other local services.

Optional local file configuration:

```powershell
$env:JOBAPP_LOCAL_CV_PDF="C:\path\to\CV.pdf"
$env:JOBAPP_LOCAL_CV_TEXT="C:\path\to\CV_text.txt"
$env:JOBAPP_LOCAL_CV_XML="C:\path\to\CV.xml"
$env:JOBAPP_PROFILE_DOSSIER="C:\path\to\profile_brief.md"
```

Most users can skip this and simply upload a CV from the browser interface.

## Basic Workflow

1. Open the app.
2. Choose an AI provider in **AI Engine**.
3. Use **Choose CV from PC** or **Import CV from local drive** to upload a PDF/TXT/XML CV.
4. Choose **AI parser** when you have a configured API key or local LLM.
5. Choose **Heuristic parser** when you want a free local parse without spending API credits.
6. Use **Open last parsed CV** when you want to reuse the last imported profile.
7. In Step 2, select the role type and work mode, then filter the CV sections that should guide the AI.
8. Optionally download the full parsed CV or the filtered CV before matching.
9. Paste or fetch a job posting URL.
10. Click **Generate match**.
11. Export Markdown, DOCX, or PDF for later editing.

## Parsed CV Exports

The CV parsing step can export:

- full parsed CV as Markdown, DOCX, PDF,
- selected CV fields as Markdown,
- selected CV fields as JSON.

This is useful before running the AI match because the user can manually filter irrelevant details and give the model a cleaner, job-specific profile.

The detailed CV editor is placed after the application history. That keeps the main workflow visible even for very long academic CVs with many publications, events, supervision entries, and courses.

## Provider Setup

Use BYOK: bring your own key.

Helpful links:

- Gemini API key: <https://ai.google.dev/gemini-api/docs/api-key>
- Google AI Studio: <https://ai.google.dev/aistudio>
- OpenAI API keys: <https://platform.openai.com/api-keys>
- Claude API keys: <https://console.anthropic.com/settings/keys>
- Ollama local API: <https://docs.ollama.com/api>

Examples:

```text
Provider: Google Gemini
Model: gemini-3.5-flash
Base URL: https://generativelanguage.googleapis.com/v1beta
API key: your Gemini API key
```

```text
Provider: Ollama local
Model: llama3.1
Base URL: http://localhost:11434/v1
API key: leave empty
```

```text
Provider: Local OpenAI-compatible server
Model: local-model
Base URL: http://localhost:8081/v1
API key: leave empty unless your local server requires one
```

## Future PagBiOmicS Web Version

The localhost/desktop version should remain the private, safest workflow. A public PagBiOmicS web page should start as a landing/download page, not as a hosted BYOK app.

- Windows executable download,
- API-key tutorials,
- email capture for release notifications and newsletter signup,
- optional newsletter signup,
- sponsor placements from biotech, omics, scientific software, training providers, recruiters, or job boards,
- biotech/scientific-tool sponsorship placements.

For the web version, never ask users to paste API keys into the website unless there is a dedicated security model, privacy policy, and backend design. The safer product is: users enter API keys only inside the local desktop app.

The file `pagbiomics_embed.html` is a first embeddable prototype for the PagBiOmicS website. It points users to the downloadable app and official API-key guides. Hosted API, subscriptions, direct payments, and Cardano/Web3 options are future roadmap items tracked in `CHANGELOG.md`.

For non-technical users, the best first experience is:

1. Download `JobApMaker.exe`.
2. Double-click it.
3. Use the app in the browser window it opens.
4. Add a Gemini/OpenAI/Claude/Ollama key only inside the local app.
