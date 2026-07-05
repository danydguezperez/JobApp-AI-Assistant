# JobApp AI Assistant

Local-first job application assistant for parsing structured CVs, tailoring applications to job postings, and exporting editable application packages.

Ciencia Vitae exports are a strong reference use case because they are highly structured and include education, professional experience, publications, projects, supervision, events, software, identifiers, and cross-references to research platforms such as ORCID, Scopus, ResearchGate, and Google Scholar.

For a complete practical guide, see [TUTORIAL.md](TUTORIAL.md).

## What It Does

- Parses a local or uploaded CV PDF/TXT into editable JSON-like sections.
- Accepts structured CV sources from the user's computer, including PDF, TXT, and XML.
- Works especially well with structured Ciencia Vitae exports.
- Lets the user include or exclude each CV item before matching a job.
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

Parsed CV export is local and credit-free. The high-quality parser can use the configured AI provider, but the app also includes a local heuristic parser mode for free tests, structured Ciencia Vitae XML/PDF workflows, and public web demos.

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

```powershell
cd "G:\O meu disco\JobApMaker"
python -m pip install -r requirements.txt
python -m uvicorn jobapp_ai_assistant:app --host 127.0.0.1 --port 8091
```

Then open:

```text
http://127.0.0.1:8091/
```

The app may also run on `8080`, but that port can be occupied by other local services on the workstation.

## CV Parsing Workflow

1. Use **Choose CV from PC** to upload a PDF/TXT/XML CV through the file explorer.
2. Keep **AI parser** enabled for the best structured English extraction.
3. Turn **AI parser** off for a free local parse that avoids LLM/API credits.
4. Edit the parsed fields directly in the browser.
5. Use the toggles to include or exclude publications, projects, experience, software, or other sections.
6. Export either:
   - the full parsed CV,
   - only the selected fields,
   - or the final tailored application package after matching a job.

The parsed export intentionally uses the structured data, not the raw Ciencia Vitae PDF headers. This removes repeated page headers, footer noise, and Portuguese platform labels where the parser has already translated the content into English.

## Provider Setup Tutorial

1. Open the app.
2. Go to **AI Engine**.
3. Select a provider.
4. Paste the API key if the provider requires one.
5. Set the model and base URL.
6. Click **Save engine**.
7. Click **Test connection**.

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

This repository is currently a localhost version. A future PagBiOmicS web version could follow the visual identity of `pagbiomics.com` and offer:

- Free trial with a limited number of test generations.
- BYOK free mode, where users add their own API keys.
- Paid hosted mode using a managed Gemini/OpenAI/Claude provider.
- Browser-visible results with download gated by email capture and a lightweight anti-bot check.
- Email delivery of generated application packages.
- Newsletter signup for job-search, bioinformatics, omics, and scientific-career resources.
- Optional unobtrusive ad placement at export time, never inside the editing or matching workflow.
- Optional subscription tier for recurring CV tailoring and application tracking.
- Future Web3 payment option for ADA and Cardano native tokens, with wallet connection handled in the web frontend and payment verification handled server-side.

The web version must be designed carefully around privacy: CVs, job postings, and API keys are sensitive data.

Suggested Web3 path:

- Start with conventional payments and BYOK first.
- Add a Cardano wallet-connect layer only in the hosted PagBiOmicS web version.
- Use a server-side payment-verification service before unlocking downloads or subscriptions.
- Do not put hosted API keys, payment verification secrets, or entitlement logic in client-side HTML.
- Evaluate Cardano Developer Portal payment guidance, MeshJS for wallet integration, and Blockfrost or a similar provider for blockchain reads/submission.

## Notes

- LinkedIn and some platforms may block scraping. In that case, paste the job text manually.
- Localhost mode is the safest default for private CV work.
- The generated outputs are starting points and should be reviewed before submission.
