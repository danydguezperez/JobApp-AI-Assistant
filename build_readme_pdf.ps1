# build_readme_pdf.ps1 - creates the local PDF guide next to JobApMaker.exe
# Run from the project root: .\build_readme_pdf.ps1

$ErrorActionPreference = "Stop"

@'
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from xml.sax.saxutils import escape
import re

root = Path.cwd()
out = root / "dist" / "JobApp_AI_Assistant_README.pdf"
out.parent.mkdir(exist_ok=True)

files = [
    ("README", root / "README.md"),
    ("Tutorial", root / "TUTORIAL.md"),
    ("Security", root / "SECURITY.md"),
    ("d'BiYOK Lab", root / "docs" / "DBIYOK_LAB.md"),
]

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CodeBlock", parent=styles["BodyText"], fontName="Courier", fontSize=8, leading=10, leftIndent=10, backColor="#F3F5F4"))
styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8, leading=10, textColor="#58635f"))

def inline_md(text: str) -> str:
    text = escape(text)
    text = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", text)
    return re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)

story = [
    Paragraph("JobApp AI Assistant", styles["Title"]),
    Paragraph("Local README pack for the desktop executable", styles["Small"]),
    Spacer(1, 0.4 * cm),
]

for doc_title, path in files:
    if not path.exists():
        continue
    story.append(Paragraph(doc_title, styles["Heading1"]))
    in_code = False
    code_lines = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.rstrip()
        if line.startswith("```"):
            if in_code:
                story.append(Paragraph(escape("<br/>".join(code_lines)) or " ", styles["CodeBlock"]))
                story.append(Spacer(1, 0.2 * cm))
                code_lines = []
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_lines.append(line)
            continue
        if not line.strip():
            story.append(Spacer(1, 0.16 * cm))
        elif line.startswith("# "):
            story.append(Paragraph(inline_md(line[2:]), styles["Heading1"]))
        elif line.startswith("## "):
            story.append(Paragraph(inline_md(line[3:]), styles["Heading2"]))
        elif line.startswith("### "):
            story.append(Paragraph(inline_md(line[4:]), styles["Heading3"]))
        elif line.startswith("- "):
            story.append(Paragraph("• " + inline_md(line[2:]), styles["BodyText"]))
        elif re.match(r"^\d+\.\s+", line):
            story.append(Paragraph(inline_md(line), styles["BodyText"]))
        elif line.startswith("!["):
            continue
        else:
            story.append(Paragraph(inline_md(line), styles["BodyText"]))
    if in_code and code_lines:
        story.append(Paragraph(escape("<br/>".join(code_lines)), styles["CodeBlock"]))
    story.append(PageBreak())

if story and isinstance(story[-1], PageBreak):
    story.pop()

SimpleDocTemplate(
    str(out),
    pagesize=A4,
    rightMargin=1.6 * cm,
    leftMargin=1.6 * cm,
    topMargin=1.4 * cm,
    bottomMargin=1.4 * cm,
).build(story)

print(out)
'@ | python -

Write-Host "LISTO: dist\JobApp_AI_Assistant_README.pdf" -ForegroundColor Green
