# Ciência Vitae Parser Validation

Validation date: 2026-07-17

## Reference Files

- Source PDF: `0A12-DF56-155A.pdf`
- Curated reference HTML: `CV_DDP_PagBiOMICs_2026.html`

The reference HTML appears to be a curated, presentation-ready CV generated from the Ciência Vitae PDF. It is not just a raw parser output: it reorganizes the CV into polished sections, cards, badges, and selected entries.

## Reference HTML Coverage

The curated HTML contains these visible section/card counts:

- Profile: 1
- Professional experience: 6
- Education/training: 9
- Projects/grants: 5
- Peer-reviewed journal articles: 23
- Book chapters: 2
- Conference contributions: 10
- Datasets/data deposits: 6
- Teaching: 4
- Supervision/juries: 1 grouped section
- Peer review/scientific service: 1 grouped section
- Distinctions: 1 grouped section
- Skills/software/languages/identifiers: grouped sections

## Current Local Heuristic Parser Coverage

Running the dedicated deterministic parser over the same 22-page PDF gives:

- Experience: 4 affiliations
- Education/training: 19 entries
- Projects/grants: 5 entries
- Peer-reviewed publications: 26 entries
- Book chapters: 2 entries
- Conference contributions: 4 entries
- Datasets/data deposits: 25 entries
- Teaching: 3 entries
- Awards/distinctions: 6 entries
- Languages: 4 entries

The parser reads the 22-page PDF with page markers, removes Ciência Vitae layout noise, separates output families, and builds editable records without an API key. Personal street address and phone remain hidden in the professional HTML export by default.

## Validation Conclusion

The local desktop parser is suitable for the first, credit-free extraction pass and can recover important Ciência Vitae fields without AI credits. However, it is not equivalent to the curated HTML generated through several AI/manual iterations:

- The curated HTML has richer summaries, visual design, editorial grouping, supervision, and service organization.
- The parser preserves specialised course titles and source evidence where deterministic translation would be unsafe; users should review those fields before publication.
- The Web Lite parser follows the same section-first philosophy but is intentionally a lighter, browser-only implementation.

## Product Positioning

Public copy should say:

- Desktop/local app: recommended for real Ciência Vitae parsing, sensitive CVs, long workflows, local exports, and repeated applications.
- Web Lite: experimental browser version for quick tests, BYOK learning, and a first heuristic pass over PDF/TXT/Markdown/JSON/XML CVs.
- Curated publication-ready CV pages, like the reference HTML, still require a higher-quality AI/manual curation layer.

This supports the current d'BiYOK Lab messaging: practical, transparent, local-first, and honest about what each mode can and cannot do.
