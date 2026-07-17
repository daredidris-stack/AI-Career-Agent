from html import escape
from io import BytesIO
import json
import re

from docx import Document
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


EXPORT_FORMATS = {"txt", "pdf", "docx"}


def export_document(document, export_format: str) -> tuple[bytes, str, str]:
    export_format = export_format.casefold()
    if export_format not in EXPORT_FORMATS:
        raise ValueError("Export format must be txt, pdf, or docx.")

    filename = _safe_filename(document.title)
    if export_format == "txt":
        return (
            _plain_content(document).encode("utf-8"),
            "text/plain; charset=utf-8",
            f"{filename}.txt",
        )
    if export_format == "docx":
        return _docx(document), (
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ), f"{filename}.docx"
    return _pdf(document), "application/pdf", f"{filename}.pdf"


def _docx(document) -> bytes:
    output = BytesIO()
    word_document = Document()
    word_document.add_heading(document.title, level=0)
    for heading, values in _sections(document):
        if heading:
            word_document.add_heading(heading, level=1)
        for value in values:
            word_document.add_paragraph(value)
    word_document.save(output)
    return output.getvalue()


def _pdf(document) -> bytes:
    output = BytesIO()
    styles = getSampleStyleSheet()
    story = [Paragraph(escape(document.title), styles["Title"]), Spacer(1, 18)]
    for heading, values in _sections(document):
        if heading:
            story.append(Paragraph(escape(heading), styles["Heading2"]))
            story.append(Spacer(1, 6))
        for value in values:
            story.append(Paragraph(escape(value) or "&nbsp;", styles["BodyText"]))
            story.append(Spacer(1, 6))
    SimpleDocTemplate(
        output,
        pagesize=LETTER,
        title=document.title,
        author="NextHire AI",
    ).build(story)
    return output.getvalue()


def _safe_filename(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "-", value).strip("-").lower() \
        or "document"


def _sections(document) -> list[tuple[str, list[str]]]:
    try:
        data = json.loads(document.content)
    except (TypeError, ValueError):
        return [("", document.content.split("\n"))]
    if not isinstance(data, dict) or "skills" not in data:
        return [("", document.content.split("\n"))]
    sections = []
    for key, label in (
        ("summary", "Professional Summary"),
        ("skills", "Skills"),
        ("experience", "Experience"),
        ("education", "Education"),
    ):
        value = data.get(key)
        values = [str(item) for item in value] if isinstance(value, list) \
            else [str(value)] if value else []
        if values:
            sections.append((label, values))
    return sections or [("", [""])]


def _plain_content(document) -> str:
    return "\n\n".join(
        "\n".join(([heading] if heading else []) + values)
        for heading, values in _sections(document)
    )
