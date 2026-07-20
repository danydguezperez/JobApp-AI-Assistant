"""Deterministic parser for text exported from the Portuguese Ciencia Vitae CV.

The parser deliberately keeps the source evidence in editable records.  It does
not invent experience or translate factual content with an LLM.  Common CV
labels are normalised to English so the resulting profile is useful before an
optional AI tailoring step.
"""
from __future__ import annotations

import re
from typing import Any


SECTION_BOUNDARIES = {
    "education": (r"^Education\s*$", r"^Affiliation\s*$"),
    "affiliations": (r"^Affiliation\s*$", r"^Projects\s*$"),
    "projects": (r"^Projects\s*$", r"^Outputs\s*$"),
    "outputs": (r"^Outputs\s*$", r"^Activities\s*$"),
    "activities": (r"^Activities\s*$", r"^Distinctions\s*$"),
    "distinctions": (r"^Distinctions\s*$", r"\Z"),
}

DATE_LINE = re.compile(
    r"(?m)^(?P<date>(?:19|20)\d{2}(?:/\d{2}(?:/\d{2})?)?(?:\s*-\s*(?:(?:19|20)\d{2}(?:/\d{2}(?:/\d{2})?)?|Current))?)\s*"
)
YEAR = re.compile(r"\b(?:19|20)\d{2}\b")
URL = re.compile(r"https?://[^\s)]+", re.IGNORECASE)
DOI = re.compile(r"\b10\.\d{4,9}/[^\s,;]+", re.IGNORECASE)

TRANSLATIONS = {
    "Concluded": "Completed",
    "Current": "Present",
    "Researcher (Research)": "Researcher",
    "Auxiliary Researcher (Research)": "Assistant Researcher",
    "Research Assistant (Research)": "Research Assistant",
    "Lecturer (University Teacher)": "Lecturer",
    "Tutor (University Teacher)": "Tutor",
    "Teaching in Higher Education": "Higher Education Teaching",
    "Science and Technology Management": "Science and Technology Management",
    "FundaÃ§Ã£o para a CiÃªncia e a Tecnologia": "Foundation for Science and Technology (FCT)",
    "Fundação para a Ciência e a Tecnologia": "Foundation for Science and Technology (FCT)",
    "GestÃ£o de Recursos Humanos": "Human Resources Management",
    "Gestão de Recursos Humanos": "Human Resources Management",
    "Criar e Desenvolver Ideias de NegÃ³cio": "Create and Develop Business Ideas",
    "Criar e Desenvolver Ideias de Negócio": "Create and Develop Business Ideas",
    "Implementar Processos de ComunicaÃ§Ã£o Criativos": "Implement Creative Communication Processes",
    "Implementar Processos de Comunicação Criativos": "Implement Creative Communication Processes",
    "Conceber, Implementar e Avaliar AÃ§Ãµes de RelaÃ§Ãµes PÃºblicas": "Design, Implement and Evaluate Public Relations Actions",
    "Conceber, Implementar e Avaliar Ações de Relações Públicas": "Design, Implement and Evaluate Public Relations Actions",
}


def clean_text(value: str) -> str:
    text = (value or "").replace("\r", "\n")
    text = re.sub(r"(?m)^--- Page \d+ ---\s*$", "", text)
    text = re.sub(r"(?mi)^.*(?:CI[\u00ca\u00ca]NCIAVITAE|CIÊNCIA VITAE).*?(?:Page|Página)\s*\d+\s*$", "", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def english_text(value: str) -> str:
    text = re.sub(r"\s+", " ", value or "").strip()
    for source, target in TRANSLATIONS.items():
        text = text.replace(source, target)
    return text


def is_ciencia_vitae_text(text: str) -> bool:
    probe = (text or "").lower()
    signals = ("ciência vitae", "ciÊncia vitae", "ciênciavitae", "ciência id", "author identifiers")
    return sum(signal in probe for signal in signals) >= 1 and ("outputs" in probe or "affiliation" in probe or "education" in probe)


def section(text: str, name: str) -> str:
    start_pattern, end_pattern = SECTION_BOUNDARIES[name]
    match = re.search(start_pattern, text, flags=re.IGNORECASE | re.MULTILINE)
    if not match:
        return ""
    tail = text[match.end():]
    end = re.search(end_pattern, tail, flags=re.IGNORECASE | re.MULTILINE)
    return tail[: end.start() if end else len(tail)].strip()


def blocks_by_date(text: str) -> list[tuple[str, str]]:
    matches = list(DATE_LINE.finditer(text))
    blocks: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[match.end():end].strip()
        if body:
            blocks.append((match.group("date"), body))
    return blocks


def take_title(lines: list[str]) -> str:
    ignored = re.compile(r"^(Completed|Concluded|Published|Ongoing|Classification|Degree|Grant|Contract|Designation|Funders|EmployerCategory|Host institution|Major in|Aprovado)$", re.I)
    for line in lines:
        candidate = english_text(line)
        if candidate and not ignored.match(candidate) and len(candidate) > 3:
            return candidate
    return ""


INSTITUTION_KEYWORDS = r"\b(University|Universidade|Institute|Instituto|School|Escola|Faculty|Faculdade|College|Centro|Center|Centre|Stazione|Foundation|Fundação|Hospital|Laboratory|Laboratório|PagBiOMICs|PROQUINORTE|CIIMAR|EMBRC)\b"


def take_institution(lines: list[str]) -> str:
    candidates = [english_text(line) for line in lines if re.search(INSTITUTION_KEYWORDS, line, re.I)]
    return candidates[-1] if candidates else ""


def extract_role_and_institution(raw_lines: list[str]) -> tuple[str, str]:
    """Split a role from its institution.

    Ciencia Vitae frequently packs an affiliation onto a single line such as
    ``Researcher (Research) Example Institute, Portugal``.  Translating the whole
    line first would erase the ``(Category)`` marker used to split it, so the
    split is attempted on the raw text before English normalisation.
    """
    for line in raw_lines:
        match = re.match(r"^(?P<role>.*?\))\s+(?P<inst>.+)$", line)
        if match and re.search(INSTITUTION_KEYWORDS, match.group("inst"), re.I):
            return english_text(match.group("role")), english_text(match.group("inst"))
    english_lines = [english_text(line) for line in raw_lines]
    title = take_title(english_lines)
    company = take_institution(english_lines)
    # When role and institution collapse into one string, drop the institution
    # substring from the title so the two fields stay distinct.
    if title and company and company in title and title != company:
        trimmed = title.replace(company, "").strip(" ,-–")
        if trimmed:
            title = trimmed
    return title, company


def parse_personal(text: str) -> dict[str, Any]:
    heading = re.search(r"^Education\s*$", text, re.I | re.M)
    before_education = text[: heading.start()] if heading else text[:8000]
    full_name = ""
    full = re.search(r"Full name\s*\n\s*([^\n]+)", before_education, re.I)
    if full:
        full_name = full.group(1).strip()
    if not full_name:
        first = re.search(r"(?m)^([A-Z][^\n]{3,80})\s*$", before_education)
        full_name = first.group(1).strip() if first else ""
    email = re.search(r"[\w.\-+]+@[\w.\-]+\.\w+", before_education)
    phone = re.search(r"(?:Mobile phone|Telephones?)\s*\n?\s*(\+?\d[\d\s().-]{7,}\d)", before_education, re.I)
    links = []
    for link in URL.findall(before_education):
        if any(token in link.lower() for token in ("facebook.com", "twitter.com", "x.com")):
            continue
        if link not in links:
            links.append(link)
    identifiers = []
    for label, pattern in (("Ciência ID", r"Ci[êe]ncia ID\s*\n\s*([^\n]+)"), ("ORCID", r"ORCID iD\s*\n\s*([^\n]+)"), ("Scopus Author ID", r"Scopus Author Id\s*\n\s*([^\n]+)")):
        match = re.search(pattern, before_education, re.I)
        if match:
            identifiers.append({"label": label, "value": match.group(1).strip()})
    return {
        "full_name": full_name,
        "email": email.group(0) if email else "",
        "phone": phone.group(1).strip() if phone else "",
        "location": "Porto, Portugal" if "Porto" in before_education else "",
        "links": links,
        "identifiers": identifiers,
    }


LANGUAGE_LEVEL = re.compile(
    r"(Native speaker|Native|Mother tongue|Proficient|Fluent|Advanced|"
    r"Upper[\s-]?intermediate|Intermediate|Elementary|Beginner|Basic)"
    r"(?:\s*\(?\s*([ABC][12])\s*\)?)?|\(?\s*([ABC][12])\s*\)?",
    re.I,
)
_LANGUAGE_HEADER_TOKENS = ("speaking", "reading", "writing", "listening", "peer-review", "spoken", "comprehension", "interaction", "production")


def parse_languages(text: str) -> list[dict[str, str]]:
    """Read the real proficiency levels from the CV instead of assuming them."""
    block = re.search(r"(?is)\bLanguages\b(.*?)(?=\bEducation\b)", text)
    if not block:
        return []

    # pypdf can flatten the Ciência Vitae language grid into several lines per
    # row: ``Spanish; Castilian`` then ``(Mother tongue)``, or ``English
    # Advanced`` then ``(C1)`` repeated for the remaining columns. Reassemble
    # those fragments before extracting a single representative level.
    fragments: list[str] = []
    current = ""
    level_words = {
        "native", "mother", "tongue", "proficient", "fluent", "advanced",
        "upper", "intermediate", "elementary", "beginner", "basic", "mother tongue",
    }

    def starts_language_row(value: str) -> bool:
        low_value = value.lower().strip().strip("()")
        if not low_value or low_value in level_words or re.fullmatch(r"\(?[abc][12]\)?", low_value):
            return False
        direct = re.match(
            r"^[A-Za-zÀ-ÿ'’;().\- ]+?\s+"
            r"(?:Native|Mother|Proficient|Fluent|Advanced|Upper|Intermediate|Elementary|Beginner|Basic|\(?[ABC][12]\)?)\b",
            value,
            re.I,
        )
        if direct:
            return True
        return bool(re.fullmatch(r"[A-Za-zÀ-ÿ'’;().\- ]{2,60}", value))

    for raw_line in block.group(1).splitlines():
        line = raw_line.strip()
        if not line:
            continue
        low = line.lower()
        if low.startswith("language ") or sum(token in low for token in _LANGUAGE_HEADER_TOKENS) >= 2:
            continue
        if current and current.rstrip().endswith(";"):
            current = f"{current} {line}"
            continue
        if starts_language_row(line):
            if current:
                fragments.append(current)
            current = line
        elif current:
            current = f"{current} {line}"
    if current:
        fragments.append(current)

    results: list[dict[str, str]] = []
    seen: set[str] = set()
    for line in fragments:
        # Some exports put a descriptor such as ``(Mother tongue)`` in its own
        # visual cell. It belongs to the preceding language, not its name.
        normalized_line = re.sub(
            r"\((Native speaker|Native|Mother tongue|Proficient|Fluent|Advanced|Upper[\s-]?intermediate|Intermediate|Elementary|Beginner|Basic)\)",
            r"\1",
            line,
            flags=re.I,
        )
        match = re.match(
            r"([A-Za-zÀ-ÿ'’;().\- ]+?)\s+"
            r"((?:Native|Mother|Proficient|Fluent|Advanced|Upper|Intermediate|Elementary|Beginner|Basic|\(?[ABC][12]\)?)\b.*)$",
            normalized_line,
        )
        if match:
            language = match.group(1).strip()
            rest = match.group(2).strip()
        else:
            language, rest = line.strip(), ""
        language = re.sub(r"\s+", " ", language).strip(" .").title()
        if not language or language.lower() in {"language", "languages"} or language.lower() in seen:
            continue
        level_match = LANGUAGE_LEVEL.search(rest)
        if level_match:
            descriptor = (level_match.group(1) or "").strip()
            cefr = level_match.group(2) or level_match.group(3)
            descriptor = "Native" if descriptor.lower() in {"native", "native speaker", "mother tongue"} else descriptor.title()
            if descriptor and cefr:
                level = f"{descriptor} ({cefr.upper()})"
            elif descriptor:
                level = descriptor
            else:
                level = f"({cefr.upper()})" if cefr else ""
        else:
            level = re.sub(r"\s{2,}.*$", "", rest).strip()
        seen.add(language.lower())
        results.append({"language": language, "level": level})
    return results


def parse_education(text: str) -> list[dict[str, str]]:
    records = []
    for date, body in blocks_by_date(section(text, "education")):
        lines = [line.strip() for line in body.splitlines() if line.strip()]
        title = take_title(lines)
        if not title:
            continue
        institution = take_institution(lines)
        description = " ".join(english_text(line) for line in lines[1:] if line not in {institution, "Completed", "Concluded"})
        records.append({"degree": title, "institution": institution, "year": YEAR.search(date).group(0) if YEAR.search(date) else "", "description": description[:900]})
    return records


def parse_experience(text: str) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    experience, teaching = [], []
    for date, body in blocks_by_date(section(text, "affiliations")):
        raw_lines = [line.strip() for line in body.splitlines() if line.strip()]
        if not raw_lines:
            continue
        title, company = extract_role_and_institution(raw_lines)
        years = date.replace("Current", "Present")
        if re.search(r"Lecturer|Tutor|Teaching", body, re.I):
            teaching.append({"title": title, "institution": company, "year": YEAR.search(date).group(0) if YEAR.search(date) else "", "description": ""})
        else:
            experience.append({"title": title, "company": company, "years": years, "description": ""})
    return experience, teaching


def parse_projects(text: str) -> list[dict[str, str]]:
    projects = []
    for date, body in blocks_by_date(section(text, "projects")):
        lines = [english_text(line) for line in body.splitlines() if line.strip()]
        title = take_title(lines)
        if not title:
            continue
        role = next((line for line in lines[1:] if re.fullmatch(r"(?:Researcher|Research Fellow|Research Technician Fellow|Contract|Grant)", line, re.I)), "")
        projects.append({"name": title, "role": role, "years": date.replace("Current", "Present"), "description": ""})
    return projects


def parse_outputs(text: str) -> dict[str, list[dict[str, str]]]:
    raw = section(text, "outputs")
    result = {"publications": [], "book_chapters": [], "events": [], "datasets": []}
    category = "publications"
    category_marks = ((r"Book chapter", "book_chapters"), (r"Journal article", "publications"), (r"Conference\s+(?:abstract|poster)", "events"), (r"Dataset", "datasets"))
    marks = sorted((match.start(), value) for pattern, value in category_marks for match in re.finditer(pattern, raw, re.I))
    seen: set[tuple[str, str]] = set()
    quotes = list(re.finditer(r'["“]([^"”]{12,850})["”]', raw))
    for index, quote in enumerate(quotes):
        for position, value in marks:
            if position <= quote.start():
                category = value
            else:
                break
        title = english_text(quote.group(1).replace("\n", " ").strip(" ."))
        key = (category, title.lower())
        if key in seen:
            continue
        seen.add(key)
        # Bind year/DOI to THIS record only: the span from the end of its title
        # to the start of the next quoted title. A fixed character window would
        # reach into a neighbouring record and mis-attribute its DOI or year.
        segment_end = quotes[index + 1].start() if index + 1 < len(quotes) else len(raw)
        segment = raw[quote.end():segment_end]
        year_values = YEAR.findall(segment)
        doi = DOI.search(segment)
        item = {"title": title, "year": year_values[0] if year_values else "", "doi": doi.group(0).rstrip(".") if doi else ""}
        if category == "datasets":
            item["url"] = next(iter(URL.findall(segment)), "")
        result[category].append(item)
    # Ciencia Vitae keeps data deposits as a numbered run. They are often not
    # quoted, so recover the full run independently from publication records.
    first_dataset = re.search(r"(?im)^\s*Dataset\s*1\b", raw)
    if first_dataset:
        dataset_tail = raw[first_dataset.start():]
        other_output = re.search(r"(?im)^Other output\b", dataset_tail)
        if other_output:
            dataset_tail = dataset_tail[:other_output.start()]
        dataset_rows = re.split(r"(?m)^\s*(?=\d{1,2}\s+|Dataset\s+1\b)", dataset_tail)
        for row in dataset_rows:
            compact = english_text(row.replace("\n", " "))
            if not re.match(r"(?:Dataset\s+1|\d{1,2})\s+", compact):
                continue
            title = re.sub(r"^(?:Dataset\s+1|\d{1,2})\s+", "", compact).strip()
            if len(title) < 16:
                continue
            key = ("datasets", title.lower())
            if key not in seen:
                seen.add(key)
                doi = DOI.search(title)
                result["datasets"].append({
                    "title": title[:1200],
                    "year": YEAR.search(title).group(0) if YEAR.search(title) else "",
                    "doi": doi.group(0).rstrip(".") if doi else "",
                })
    return result


def parse_distinctions(text: str) -> list[dict[str, str]]:
    raw = section(text, "distinctions")
    records = []
    for date, body in blocks_by_date(raw):
        title = take_title([line.strip() for line in body.splitlines() if line.strip()])
        if title:
            records.append({"title": title, "year": YEAR.search(date).group(0) if YEAR.search(date) else "", "description": ""})
    return records


def parse_ciencia_vitae(text: str) -> dict[str, Any]:
    """Parse a PDF-text export into a factual JobApp profile without an LLM."""
    cleaned = clean_text(text)
    personal = parse_personal(cleaned)
    outputs = parse_outputs(cleaned)
    experience, teaching = parse_experience(cleaned)
    return {
        "personal_info": {
            **personal,
            "headline": "",
            "summary": "",
        },
        "education": parse_education(cleaned),
        "experience": experience,
        "projects": parse_projects(cleaned),
        "publications": outputs["publications"],
        "book_chapters": outputs["book_chapters"],
        "events": outputs["events"],
        "datasets": outputs["datasets"],
        "teaching": teaching,
        "awards": parse_distinctions(cleaned),
        "supervision": [],
        "service": [],
        "skills": [],
        "software": [],
        "languages": parse_languages(cleaned),
        "source_notes": {
            "mode": "ciencia_vitae_heuristic",
            "source_chars": len(cleaned),
            "translation": "Deterministic label and common-course translation only; review specialised source titles before publishing.",
        },
    }
