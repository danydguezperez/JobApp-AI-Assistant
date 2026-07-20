# Professional Web CV Pipeline

## Purpose

This pipeline turns a structured CV export into a professional, editable web CV without coupling the source data to a particular HTML design. The current validated reference is the 22-page Ciência Vitae export and its curated PagBiOmicS/Durable presentation.

## Reproducible stages

1. **Import**: upload Ciência Vitae XML whenever available; PDF/TXT remain useful fallbacks for narrative sections.
2. **Canonicalize**: create `cv_canonical.json` using schema version `1.0.0`. Every record carries a source, source id, extraction method, confidence, selection state, and visibility.
3. **Review**: edit the canonical data in JobApp. Select records for a public CV independently from the records selected for a job application.
4. **Optional AI curation**: request wording, translation, grouping, or a profile summary as structured JSON. AI must not write the final HTML directly.
5. **Render**: apply `templates/durable_cv_template.html` to the approved canonical document. The template is design only; it contains no personal CV facts.
6. **Validate**: check schema, required profile fields, source counts, links, and privacy findings before exporting.
7. **Export**: produce a standalone HTML file for Durable or another site. The same canonical document can later feed DOCX, PDF, and job-tailored variants.

## Source priority

| Need | Preferred source | Reason |
| --- | --- | --- |
| Degrees, employments, outputs, grants, identifiers | Ciência Vitae XML | Structured fields and source identifiers survive import. |
| Narrative biography, teaching prose, layout-only PDF material | Ciência Vitae PDF/TXT | Some content is easier to recover from the printable export. |
| Strategic profile and public positioning | Human review, optionally AI-assisted | This is editorial content, not a factual source record. |

## Privacy rule

The XML may include public, restricted, and private information. Canonical records preserve visibility. The HTML renderer exports only records marked `public`; contact details are hidden unless the export configuration explicitly allows named fields. Date of birth, gender, phone numbers, and postal addresses must never be promoted automatically into a public export.

## Golden reference protocol

For each validated CV, retain:

- the original XML/PDF outside Git;
- the generated `cv_canonical.json` outside Git unless explicitly anonymised;
- a small manifest containing source hashes, parser version, template version, prompt version, and human review date;
- the final HTML output and a visual screenshot for regression comparison.

This lets a later version of JobApp show exactly what changed: source data, editorial choices, or design.

## What is deterministic vs optional AI

XML parsing, source provenance, privacy filtering, selection, HTML rendering, and file export are deterministic and do not consume AI credits. AI is optional for English polishing, summaries, section grouping, and role-oriented versions. When AI is used, store model/provider/prompt identifiers in the export manifest, never API keys.
