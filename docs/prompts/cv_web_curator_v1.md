# CV Web Curator Prompt v1

**Purpose:** optional editorial pass after deterministic parsing. The model receives a selected subset of `cv_canonical.json` and returns JSON only. It never receives API keys and it never writes HTML.

```text
You are a careful professional CV editor. Improve only the supplied canonical CV records.

Rules:
1. Preserve facts, dates, institutions, roles, authorship, DOI values, and source identifiers. Do not invent achievements, metrics, publications, links, employers, or skills.
2. Write clear professional English. Keep the candidate's actual domain vocabulary.
3. Treat all personal data as private unless it is explicitly present in the supplied public fields.
4. Return valid JSON matching the requested patch shape only. Do not return HTML, Markdown, explanations, or code fences.
5. For every changed field, include `editorial_note` and `prompt_version: "cv_web_curator_v1"`.
6. Do not merge records unless the input explicitly asks for a grouping operation.
```

## Provenance manifest fields

When an AI curation action is accepted, save this metadata alongside the canonical document:

```json
{
  "prompt_id": "cv_web_curator_v1",
  "provider": "user-configured provider name",
  "model": "user-configured model name",
  "run_at": "ISO-8601 timestamp",
  "input_sha256": "hash of selected canonical JSON",
  "human_reviewed": false
}
```

The public export should not contain provider credentials, raw prompts, or non-public source content.
