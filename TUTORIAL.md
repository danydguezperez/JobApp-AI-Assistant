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

Open PowerShell:

```powershell
cd "G:\O meu disco\JobApMaker"
python -m pip install -r requirements.txt
python -m uvicorn jobapp_ai_assistant:app --host 127.0.0.1 --port 8091
```

Open:

```text
http://127.0.0.1:8091/
```

Port `8091` is recommended on this workstation because `8080` may already be used by other local services.

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

The localhost version should remain the private, safest workflow. A public PagBiOmicS web version can later add:

- BYOK free mode,
- limited free tests,
- hosted paid API mode,
- email capture before downloading files,
- anti-bot validation,
- optional newsletter signup,
- discreet export-time ads,
- subscriptions,
- ADA/Cardano native-token payments after server-side verification.

For the web version, never expose hosted API keys or payment secrets in browser HTML.

The file `pagbiomics_embed.html` is a first embeddable prototype for the PagBiOmicS website. It includes Free, BYOK, and Hosted API beta modes. The suggested beta price, EUR 1.99 for 20 applications, is reasonable as a low-friction test offer. If usage becomes serious, consider a monthly tier around EUR 4.99-9.99 plus BYOK free mode.
