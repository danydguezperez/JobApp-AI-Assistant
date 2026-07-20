"""Versioned, source-aware CV representation and web-CV renderer.

This module deliberately keeps extraction, editorial content, and presentation
separate.  It is used by JobApp AI Assistant, but has no FastAPI dependency so
the same canonical CV can later power desktop, web, DOCX, and Durable exports.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from html import escape
import json
import os
from pathlib import Path
import re
from typing import Any
from xml.etree import ElementTree as ET


SCHEMA_VERSION = "1.0.0"
SECTION_ORDER = [
    "experience",
    "education",
    "projects",
    "publications",
    "book_chapters",
    "conferences",
    "datasets",
    "teaching",
    "supervision",
    "service",
    "distinctions",
    "skills",
    "software",
    "languages",
]
SECTION_LABELS = {
    "experience": "Professional Experience",
    "education": "Education & Training",
    "projects": "Projects & Grants",
    "publications": "Peer-Reviewed Publications",
    "book_chapters": "Book Chapters",
    "conferences": "Conference Contributions",
    "datasets": "Datasets & Data Deposits",
    "teaching": "Teaching & Lecturing",
    "supervision": "Supervision & Academic Juries",
    "service": "Peer Review & Scientific Service",
    "distinctions": "Awards & Distinctions",
    "skills": "Core Expertise & Skills",
    "software": "Software Tools",
    "languages": "Languages",
}
PRIVATE_FIELD_NAMES = {
    "date_of_birth", "birth_date", "gender", "phone", "mobile", "street",
    "street_address", "postal_code", "address", "personal_address",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def local_name(value: str) -> str:
    return value.rsplit("}", 1)[-1]


def clean_text(value: Any, limit: int | None = None) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text[:limit].rstrip() if limit else text


def stable_id(prefix: str, *parts: Any) -> str:
    material = "|".join(clean_text(part).lower() for part in parts if clean_text(part))
    digest = sha256(material.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{digest}"


def normalise_visibility(value: str | None) -> str:
    label = clean_text(value).lower()
    if any(token in label for token in ("priv", "private")):
        return "private"
    if any(token in label for token in ("semi", "restricted")):
        return "restricted"
    return "public"


def make_provenance(
    source_type: str,
    source_name: str,
    *,
    source_id: str = "",
    locator: str = "",
    confidence: float = 1.0,
    method: str = "deterministic",
) -> dict[str, Any]:
    return {
        "source_type": source_type,
        "source_name": source_name,
        "source_id": source_id,
        "locator": locator,
        "method": method,
        "confidence": confidence,
    }


def make_item(
    section: str,
    data: dict[str, Any],
    provenance: dict[str, Any],
    *,
    visibility: str = "public",
    selected: bool = True,
) -> dict[str, Any]:
    title = clean_text(data.get("title") or data.get("name") or data.get("degree") or data.get("language"))
    identifier = provenance.get("source_id") or title or json.dumps(data, sort_keys=True, ensure_ascii=False)
    return {
        "id": stable_id(section, identifier),
        "selected": selected,
        "visibility": normalise_visibility(visibility),
        "data": {key: value for key, value in data.items() if value not in (None, "", [], {})},
        "provenance": [provenance],
    }


def empty_canonical(source_name: str = "") -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "document": {
            "kind": "professional_cv",
            "created_at": utc_now(),
            "updated_at": utc_now(),
            "sources": ([{"name": source_name}] if source_name else []),
        },
        "profile": {
            "full_name": "",
            "headline": "",
            "summary": "",
            "location": "",
            "contact": {},
            "links": [],
            "identifiers": [],
        },
        "sections": {section: [] for section in SECTION_ORDER},
        "display": {
            "section_order": SECTION_ORDER,
            "locale": "en",
            "public_contact_fields": ["email"],
            "theme": "pagbiomics-professional",
        },
    }


def source_fingerprint(raw: bytes | str) -> str:
    data = raw.encode("utf-8") if isinstance(raw, str) else raw
    return sha256(data).hexdigest()


def direct_or_descendant_text(element: ET.Element, *names: str) -> str:
    # Candidate order matters: a degree has both a generic type and its actual name.
    for wanted in names:
        for node in element.iter():
            if local_name(node.tag) == wanted:
                value = clean_text(" ".join(node.itertext()))
                if value:
                    return value
    return ""


def descendant_raw_text(element: ET.Element, *names: str) -> str:
    wanted = set(names)
    for node in element.iter():
        if local_name(node.tag) in wanted:
            return "".join(node.itertext())
    return ""


def first_date(element: ET.Element, *names: str) -> str:
    for wanted in names:
        for node in element.iter():
            if local_name(node.tag) != wanted:
                continue
            parts = [node.get(part) for part in ("year", "month", "day") if node.get(part)]
            if parts:
                return "-".join(parts)
            value = clean_text(" ".join(node.itertext()))
            if value:
                return value
    return ""


def compact_element_text(element: ET.Element, limit: int = 1600) -> str:
    chunks: list[str] = []
    for value in element.itertext():
        text = clean_text(value)
        if text and text not in chunks:
            chunks.append(text)
    return clean_text(". ".join(chunks), limit)


def xml_records(root: ET.Element, tag_name: str) -> list[ET.Element]:
    return [node for node in root.iter() if local_name(node.tag) == tag_name]


def xml_section_item(section: str, element: ET.Element, source_name: str) -> dict[str, Any] | None:
    visibility = normalise_visibility(element.get("privacy-level"))
    if visibility != "public":
        return None
    source_id = element.get("id", "")
    common = {
        "source_text": compact_element_text(element),
        "start_date": first_date(element, "start-date", "begin-date"),
        "end_date": first_date(element, "end-date", "finish-date"),
    }
    if section == "education":
        data = {
            "title": direct_or_descendant_text(element, "degree-name", "degree-type", "title"),
            "institution": direct_or_descendant_text(element, "institution-name"),
            "year": first_date(element, "end-date"),
            **common,
        }
    elif section == "experience":
        data = {
            "title": direct_or_descendant_text(element, "job-title", "employment-title", "position", "position-type", "role", "occupation"),
            "organization": direct_or_descendant_text(element, "institution-name", "organization-name", "employer-name"),
            **common,
        }
    elif section == "projects":
        data = {
            "title": direct_or_descendant_text(element, "funding-title", "project-title", "title", "acronym"),
            "organization": direct_or_descendant_text(element, "institution-name", "organization-name", "funder-name"),
            **common,
        }
    elif section == "distinctions":
        data = {
            "title": direct_or_descendant_text(element, "distinction-title", "title", "name"),
            "organization": direct_or_descendant_text(element, "institution-name", "organization-name"),
            "year": first_date(element, "date", "end-date", "award-date"),
            **common,
        }
    elif section == "service":
        data = {
            "title": direct_or_descendant_text(element, "service-title", "title", "journal-name", "name"),
            "organization": direct_or_descendant_text(element, "institution-name", "organization-name", "journal-name"),
            **common,
        }
    else:  # outputs / publications
        data = {
            "title": direct_or_descendant_text(
                element,
                "article-title", "chapter-title", "book-title", "dataset-title", "conference-title",
                "poster-title", "output-title", "publication-title", "title", "name",
            ),
            "journal": direct_or_descendant_text(element, "journal-title", "journal-name", "publisher", "publication-name"),
            "year": first_date(element, "publication-year", "publication-date", "date", "end-date"),
            "type": direct_or_descendant_text(element, "output-type", "output-category", "type"),
            "doi": direct_or_descendant_text(element, "doi"),
            **common,
        }
    if not clean_text(data.get("title")):
        data["title"] = common["source_text"][:180]
    return make_item(
        section,
        data,
        make_provenance("ciencia_vitae_xml", source_name, source_id=source_id, locator=section),
        visibility=visibility,
    )


def output_section(item: dict[str, Any]) -> str:
    output_type = clean_text((item.get("data") or {}).get("type")).lower()
    if "book chapter" in output_type or "book" in output_type:
        return "book_chapters"
    if any(token in output_type for token in ("conference", "poster", "presentation", "abstract")):
        return "conferences"
    if any(token in output_type for token in ("dataset", "data deposit", "repository")):
        return "datasets"
    return "publications"


def canonical_from_ciencia_vitae_xml(raw: bytes | str, source_name: str) -> dict[str, Any]:
    raw_bytes = raw.encode("utf-8") if isinstance(raw, str) else raw
    root = ET.fromstring(raw_bytes)
    canonical = empty_canonical(source_name)
    canonical["document"]["sources"] = [{
        "name": source_name,
        "type": "ciencia_vitae_xml",
        "sha256": source_fingerprint(raw_bytes),
        "imported_at": utc_now(),
    }]

    full_name = direct_or_descendant_text(root, "full-name", "displayName")
    raw_resume = descendant_raw_text(root, "resume")
    resume = clean_text(raw_resume)
    resume_lines = [line for line in str(raw_resume).splitlines() if clean_text(line)]
    canonical["profile"].update({
        "full_name": full_name,
        "headline": clean_text(resume_lines[0] if resume_lines else ""),
        "summary": clean_text(resume, 2400),
    })

    # Only public contacts are retained, and they are still hidden in web output by default.
    for element in xml_records(root, "email"):
        if normalise_visibility(element.get("privacy-level")) == "public":
            value = direct_or_descendant_text(element, "email-address")
            if value:
                canonical["profile"]["contact"]["email"] = value
                break
    for element in xml_records(root, "author-identifier"):
        if normalise_visibility(element.get("privacy-level")) != "public":
            continue
        label = direct_or_descendant_text(element, "identifier-type")
        value = direct_or_descendant_text(element, "identifier")
        if value:
            canonical["profile"]["identifiers"].append({"label": label or "Identifier", "value": value})
    for element in xml_records(root, "web-address"):
        if normalise_visibility(element.get("privacy-level")) != "public":
            continue
        value = direct_or_descendant_text(element, "url")
        if value:
            canonical["profile"]["links"].append(value)
    for element in xml_records(root, "language-competency"):
        if normalise_visibility(element.get("privacy-level")) != "public":
            continue
        language = direct_or_descendant_text(element, "language")
        level = direct_or_descendant_text(element, "read", "write", "speak", "understand-spoken")
        if language:
            canonical["sections"]["languages"].append(make_item(
                "languages", {"language": language, "level": level},
                make_provenance("ciencia_vitae_xml", source_name, source_id=element.get("id", ""), locator="language"),
                visibility=element.get("privacy-level", "public"),
            ))
    # Knowledge fields: the PDF/RTF export only prints the top-level science
    # domain, but the XML keeps the full keyword list under domain-activity.
    # Map those keywords to skills so the user's curated expertise is preserved.
    skill_seen: set[str] = set()
    for domain in xml_records(root, "domain-activity"):
        if normalise_visibility(domain.get("privacy-level")) == "private":
            continue
        for node in domain.iter():
            if local_name(node.tag) != "keyword":
                continue
            keyword = clean_text(" ".join(node.itertext()))
            if not keyword or keyword.lower() in skill_seen:
                continue
            skill_seen.add(keyword.lower())
            canonical["sections"]["skills"].append(make_item(
                "skills", {"title": keyword},
                make_provenance("ciencia_vitae_xml", source_name, source_id=domain.get("id", ""), locator="domain-activity/keyword"),
                visibility=domain.get("privacy-level", "public"),
            ))

    for xml_tag, section in {
        "degree": "education",
        "employment": "experience",
        "funding": "projects",
        "output": "publications",
        "distinction": "distinctions",
        "service": "service",
    }.items():
        for element in xml_records(root, xml_tag):
            item = xml_section_item(section, element, source_name)
            if item:
                target_section = output_section(item) if xml_tag == "output" else section
                item["id"] = stable_id(target_section, item.get("provenance", [{}])[0].get("source_id"), item_key(item))
                canonical["sections"][target_section].append(item)
    return canonical


def profile_value_items(section: str, value: Any, source_name: str) -> list[dict[str, Any]]:
    values = value if isinstance(value, list) else [value]
    items: list[dict[str, Any]] = []
    for index, entry in enumerate(values):
        if isinstance(entry, dict):
            data = {key: value for key, value in entry.items() if value not in (None, "", [], {})}
        else:
            data = {"title": clean_text(entry)}
        if not data:
            continue
        if section == "skills" and "title" in data:
            data = {"title": data["title"]}
        items.append(make_item(
            section,
            data,
            make_provenance("jobapp_profile", source_name, source_id=f"{section}:{index}", locator=section, confidence=0.8),
        ))
    return items


def canonical_from_jobapp_profile(profile: dict[str, Any], source_name: str = "parsed_cv.json") -> dict[str, Any]:
    canonical = empty_canonical(source_name)
    personal = profile.get("personal_info") or {}
    canonical["profile"].update({
        "full_name": clean_text(personal.get("full_name") or personal.get("name")),
        "headline": clean_text(personal.get("headline")),
        "summary": clean_text(personal.get("summary"), 2400),
        "location": clean_text(personal.get("location")),
        "links": [clean_text(link) for link in personal.get("links", []) if clean_text(link)],
    })
    if clean_text(personal.get("email")):
        canonical["profile"]["contact"]["email"] = clean_text(personal["email"])
    if clean_text(personal.get("phone")):
        canonical["profile"]["contact"]["phone"] = clean_text(personal["phone"])
    section_map = {
        "experience": "experience",
        "education": "education",
        "projects": "projects",
        "publications": "publications",
        "book_chapters": "book_chapters",
        "datasets": "datasets",
        "languages": "languages",
        "skills": "skills",
        "software": "software",
        "supervision": "supervision",
        "events": "conferences",
        "teaching": "teaching",
        "service": "service",
        "awards": "distinctions",
    }
    for source_key, section in section_map.items():
        canonical["sections"][section].extend(profile_value_items(section, profile.get(source_key, []), source_name))
    return canonical


def item_key(item: dict[str, Any]) -> str:
    data = item.get("data") or {}
    return clean_text(data.get("doi") or data.get("title") or data.get("name") or data.get("source_text")).lower()


def merge_canonical(primary: dict[str, Any], supplemental: dict[str, Any]) -> dict[str, Any]:
    """Retain source-rich records while filling editorial gaps from JobApp parsing."""
    merged = deepcopy(primary)
    merged["document"]["updated_at"] = utc_now()
    merged["document"]["sources"].extend(supplemental.get("document", {}).get("sources", []))
    for field in ("full_name", "headline", "summary", "location"):
        if not clean_text(merged["profile"].get(field)) and clean_text(supplemental.get("profile", {}).get(field)):
            merged["profile"][field] = supplemental["profile"][field]
    for field in ("contact", "links", "identifiers"):
        if not merged["profile"].get(field):
            merged["profile"][field] = deepcopy(supplemental.get("profile", {}).get(field, {} if field == "contact" else []))
    for section in SECTION_ORDER:
        existing = {item_key(item) for item in merged["sections"].get(section, []) if item_key(item)}
        for item in supplemental.get("sections", {}).get(section, []):
            if section == "experience":
                supplement_company = clean_text((item.get("data") or {}).get("company") or (item.get("data") or {}).get("organization")).lower()
                matched = next(
                    (
                        candidate for candidate in merged["sections"].get(section, [])
                        if supplement_company
                        and (candidate_org := clean_text((candidate.get("data") or {}).get("organization") or (candidate.get("data") or {}).get("company")).lower())
                        and (supplement_company in candidate_org or candidate_org in supplement_company)
                    ),
                    None,
                )
                if matched:
                    for field, value in (item.get("data") or {}).items():
                        if value and (not matched.get("data", {}).get(field) or field in {"title", "description", "company", "years"}):
                            matched.setdefault("data", {})[field] = value
                    matched.setdefault("provenance", []).extend(deepcopy(item.get("provenance", [])))
                    continue
            if item_key(item) not in existing:
                merged["sections"].setdefault(section, []).append(deepcopy(item))
                existing.add(item_key(item))
    return merged


def canonical_from_import(
    parsed_profile: dict[str, Any],
    *,
    source_name: str,
    xml_raw: bytes | str | None = None,
) -> dict[str, Any]:
    fallback = canonical_from_jobapp_profile(parsed_profile, source_name)
    if not xml_raw:
        return fallback
    try:
        return merge_canonical(canonical_from_ciencia_vitae_xml(xml_raw, source_name), fallback)
    except ET.ParseError:
        return fallback


def privacy_findings(canonical: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    contact = canonical.get("profile", {}).get("contact", {}) or {}
    for name in PRIVATE_FIELD_NAMES:
        if clean_text(contact.get(name)):
            findings.append(f"Profile contact contains '{name}'.")
    for section, items in (canonical.get("sections") or {}).items():
        for item in items or []:
            if item.get("visibility") != "public":
                findings.append(f"{section}:{item.get('id', 'unknown')} is not public.")
    return findings


def validate_canonical(canonical: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if canonical.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"Unsupported schema version: {canonical.get('schema_version')!r}.")
    if not clean_text((canonical.get("profile") or {}).get("full_name")):
        errors.append("profile.full_name is required.")
    if not isinstance(canonical.get("sections"), dict):
        errors.append("sections must be an object.")
    return errors


def record_meta(data: dict[str, Any]) -> str:
    fields = ("organization", "institution", "company", "journal", "year", "years", "start_date", "end_date", "role", "level", "type")
    parts: list[str] = []
    for field in fields:
        value = clean_text(data.get(field))
        if value and value not in parts:
            parts.append(value)
    return " · ".join(parts)


def record_description(data: dict[str, Any]) -> str:
    # source_text is retained for human traceability, not shown in the public layout.
    for field in ("description", "summary"):
        value = clean_text(data.get(field))
        if value:
            return value
    return ""


def render_records(items: list[dict[str, Any]]) -> str:
    cards: list[str] = []
    for item in items:
        if not item.get("selected", True) or item.get("visibility") != "public":
            continue
        data = item.get("data") or {}
        title = clean_text(data.get("title") or data.get("name") or data.get("degree") or data.get("language"))
        if not title:
            continue
        meta = record_meta(data)
        description = record_description(data)
        # Precompute the optional fragments so the f-strings below contain no
        # backslashes inside their expressions (keeps Python 3.10 compatibility).
        meta_html = f'<p class="cv-meta">{escape(meta)}</p>' if meta else ""
        desc_html = f"<p>{escape(description)}</p>" if description else ""
        cards.append(
            "<article class=\"cv-record\">"
            f"<h3>{escape(title)}</h3>"
            f"{meta_html}"
            f"{desc_html}"
            "</article>"
        )
    return "\n".join(cards)


def render_section(section: str, items: list[dict[str, Any]]) -> str:
    records = render_records(items)
    if not records:
        return ""
    label = SECTION_LABELS.get(section, section.replace("_", " ").title())
    return f"<section class=\"cv-section\" id=\"cv-{escape(section)}\"><h2>{escape(label)}</h2>{records}</section>"


def consulting_cta_html(config: dict[str, Any] | None = None) -> str:
    """Optional 'work with me' call-to-action for the public web CV.

    Nothing is hardcoded: it renders only when an email or URL is supplied via
    ``config['cta']`` or the JOBAPP_CTA_* environment variables, and stays empty
    otherwise so the template remains generic and reusable.
    """
    cta = (config or {}).get("cta") or {}
    email = clean_text(cta.get("email") or os.getenv("JOBAPP_CTA_EMAIL", ""))
    url = clean_text(cta.get("url") or os.getenv("JOBAPP_CTA_URL", ""))
    if not email and not url:
        return ""
    headline = clean_text(cta.get("headline") or os.getenv("JOBAPP_CTA_HEADLINE", "")) or "Available for freelance & consulting"
    text = clean_text(cta.get("text") or os.getenv("JOBAPP_CTA_TEXT", "")) or "Have a project that needs bioinformatics support? Let's talk."
    button = clean_text(cta.get("button") or os.getenv("JOBAPP_CTA_BUTTON", "")) or "Get in touch"
    buttons = []
    if email:
        subject = escape("Consulting enquiry via web CV", quote=True)
        buttons.append(
            f'<a class="cv-cta-btn cv-cta-primary" href="mailto:{escape(email, quote=True)}?subject={subject}"'
            f' data-cta="contact" onclick="window.plausible&&window.plausible(\'cta_contact\')">{escape(button)}</a>'
        )
    if url.startswith(("https://", "http://")):
        buttons.append(
            f'<a class="cv-cta-btn cv-cta-secondary" href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer"'
            f' data-cta="services" onclick="window.plausible&&window.plausible(\'cta_services\')">View services</a>'
        )
    if not buttons:
        return ""
    return (
        '<aside class="cv-cta" aria-label="Work with me">'
        f'<div class="cv-cta-copy"><p class="cv-cta-kicker">{escape(headline)}</p>'
        f'<p class="cv-cta-text">{escape(text)}</p></div>'
        f'<div class="cv-cta-actions">{"".join(buttons)}</div></aside>'
    )


def render_durable_html(canonical: dict[str, Any], template_path: Path, config: dict[str, Any] | None = None) -> str:
    errors = validate_canonical(canonical)
    if errors:
        raise ValueError(" ".join(errors))
    config = config or {}
    profile = canonical.get("profile") or {}
    include_sections = config.get("include_sections") or canonical.get("display", {}).get("section_order") or SECTION_ORDER
    include_contact = bool(config.get("include_contact", False))
    title = clean_text(config.get("page_title") or profile.get("full_name") or "Professional CV")
    summary = clean_text(profile.get("summary"))
    headline = clean_text(profile.get("headline"))
    location = clean_text(profile.get("location"))
    contact = profile.get("contact") or {}
    public_contact = []
    if include_contact:
        for field in canonical.get("display", {}).get("public_contact_fields", []):
            value = clean_text(contact.get(field))
            if value:
                public_contact.append(value)
    links = [clean_text(value) for value in profile.get("links", []) if clean_text(value).startswith(("https://", "http://"))]
    meta_parts = [part for part in [location, *public_contact] if part]
    sections_html = "\n".join(render_section(section, canonical.get("sections", {}).get(section, [])) for section in include_sections)
    identifiers = profile.get("identifiers") or []
    identifiers_html = "".join(
        f"<li><strong>{escape(clean_text(item.get('label')))}:</strong> {escape(clean_text(item.get('value')))}</li>"
        for item in identifiers if clean_text(item.get("value"))
    )
    if identifiers_html:
        sections_html += f"\n<section class=\"cv-section cv-identifiers\"><h2>Academic Identifiers</h2><ul>{identifiers_html}</ul></section>"
    links_html = "".join(
        f"<a href=\"{escape(link, quote=True)}\" target=\"_blank\" rel=\"noopener noreferrer\">{escape(link.replace('https://', '').replace('http://', ''))}</a>"
        for link in links
    )
    replacements = {
        "{{CTA}}": consulting_cta_html(config),
        "{{PAGE_TITLE}}": escape(title),
        "{{FULL_NAME}}": escape(clean_text(profile.get("full_name"))),
        "{{HEADLINE}}": escape(headline),
        "{{SUMMARY}}": escape(summary),
        "{{META}}": escape(" · ".join(meta_parts)),
        "{{LINKS}}": links_html,
        "{{SECTIONS}}": sections_html,
        "{{SCHEMA_VERSION}}": escape(SCHEMA_VERSION),
        "{{GENERATED_AT}}": escape(utc_now()),
    }
    template = template_path.read_text(encoding="utf-8")
    for marker, value in replacements.items():
        template = template.replace(marker, value)
    return template
