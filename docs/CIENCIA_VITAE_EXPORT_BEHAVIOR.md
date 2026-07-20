# Ciência Vitae Export Behaviour — Background & Antecedents

*Reference notes underpinning JobApp AI Assistant's Ciência Vitae ingestion. Written 2026-07-19 from direct inspection of a real published record exported in all available formats.*

## Why this document exists

Ciência Vitae is the Portuguese national CV system (FCT). It is the primary
source of truth for this application: a researcher curates their record once and
exports it, and JobApp turns that export into tailored, job-specific
applications. The system offers several export formats, and — crucially — **they
are not equivalent**. Understanding exactly what each format carries is what lets
the parser be deterministic and honest instead of guessing or fabricating.

## What each export format actually contains

The same published record was exported as PDF, DOCX, RTF and XML and compared
field by field. The short version: the human-facing formats are lossy; only the
XML is complete.

| Data | PDF | DOCX | RTF | XML |
|---|---|---|---|---|
| Identity, contacts, identifiers (ORCID, Ciência ID) | Yes | Yes | Yes | Yes (with per-field privacy levels) |
| Education, Affiliations, Projects, Outputs, Distinctions | Yes | Yes | Yes | Yes (structured, with dates & DOIs) |
| Languages + proficiency levels | Yes (as a grid) | Yes | Yes | Yes (`language-competency`, per-skill levels) |
| **Knowledge fields — top-level domain** ("Natural sciences - Biological Sciences") | Yes | Yes | Yes | Yes |
| **Knowledge fields — subcategory + keywords** (the curated skill list) | **No** | **No** | **No** | **Yes** (`domain-activity` → `common:keyword`) |
| Per-field privacy (public / semi-public / private) | Not machine-readable | No | No | Yes (`privacy-level` attribute) |

### The key finding

The curated **Knowledge-fields keyword list** — the closest thing the record has
to a "skills" section — **is only present in the XML**. The PDF, DOCX and RTF
exports print the top-level science domain and silently drop the subcategory and
every keyword. Any pipeline that reads only the PDF therefore cannot recover the
user's skills; it must ingest the XML.

This single fact drives an architectural rule in the app: **skills come from the
XML path, never from the PDF path.** When only a PDF is available, the skills
section is legitimately empty rather than invented.

## Layout facts the parser relies on

- **Sections** appear as bare heading lines in a fixed order: Education →
  Affiliation → Projects → Outputs → Activities → Distinctions. The parser slices
  the text between consecutive headings.
- **Records** inside a section begin with a date token
  (`YYYY`, `YYYY/MM`, `YYYY/MM/DD`, optionally a range ending in `Current`).
- **Affiliations** frequently pack role and institution on one line:
  `Researcher (Research) Example Institute, Portugal`. The `(Category)` marker is
  the split point — which is why role/institution splitting must happen *before*
  English normalisation erases it.
- **Languages** render as `Language <level>` rows under a column header
  (`Language Speaking Reading Writing Listening Peer-review`). The real level must
  be read from the row; assuming a fixed level per language is wrong.
- **Outputs** list a quoted title followed by year and DOI. Year/DOI must be
  bound to the span between one title and the next, or a neighbouring record's DOI
  gets mis-attributed.
- **PDF text extraction order** (pypdf) roughly follows reading order, but the RTF
  stores every run as an absolutely-positioned shape, so RTF text order is *not*
  reliable for parsing — treat RTF as display-only.

## Consequences implemented in the app

1. **XML is the preferred import.** The PDF path is a fallback; the XML path
   (`cv_canonical.canonical_from_ciencia_vitae_xml`) is authoritative and is the
   only path that yields skills and per-field privacy.
2. **Privacy is honoured from the source.** Only `public` XML records are
   exported; semi-public and private fields (phone, address, etc.) are withheld
   by default.
3. **No fabrication.** Languages, DOIs, skills and roles are read from evidence or
   left empty — the parser never assumes them.

## Practical guidance for the user

- To get the **full CV including skills**, import the **XML** (`*.xml`), not just
  the PDF. The PDF alone will show empty skills — by design, because the data
  isn't in the PDF.
- Keep curating Knowledge-fields keywords in Ciência Vitae; they now flow through
  to the app's skills section via the XML.
