# Golden Reference: Ciência Vitae to Professional Web CV

## Role

The curated Ciência Vitae-to-Durable CV is the first validated reference for JobApp's professional web-CV export. It establishes the expected standard: structured factual data, editorially useful English, deliberate public/private separation, responsive presentation, and human review before publication.

## Historical workflow record

The original reference was produced through these stages, as reported by its author:

1. Export PDF and XML from Ciência Vitae after authenticated access to the portal.
2. Use the PDF as text/narrative input and the XML as a structured factual source.
3. Build a first HTML interpretation with Claude Sonnet 4.6.
4. Use that HTML as input to a ChatGPT Sol editorial/design pass, producing the refined Durable-oriented version.
5. Manually review section order, strategic profile text, public identifiers, software, teaching, publications, and responsive behaviour.

The precise historical prompts, provider request ids, and model build identifiers were not preserved. They must therefore be treated as unavailable rather than reconstructed from memory. This reference is valid as an accepted output and design target, not as a bit-for-bit reproducible historical AI run.

## Reproducibility from this version forward

Every new run should record:

- source file names and SHA-256 hashes;
- canonical schema version;
- parser/JobApp version and template path;
- optional AI provider, model, prompt id, run time, and input hash;
- human reviewer and approval date;
- exported HTML filename and visual QA result.

Use [cv_web_curator_v1.md](prompts/cv_web_curator_v1.md) for optional AI editorial work and [cv_generation_manifest.example.json](examples/cv_generation_manifest.example.json) as the run record.

## Acceptance criteria

- All visible factual items trace back to a source record or an explicitly approved editorial field.
- Restricted/private Ciência Vitae fields never enter the HTML automatically.
- The design template contains no personal facts.
- The generated page renders without horizontal overflow at desktop and mobile widths.
- The reviewer checks names, dates, titles, publications, links, and intended public contact information before publishing.
