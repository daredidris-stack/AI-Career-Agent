from html import escape
from io import BytesIO
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
            document.content.encode("utf-8"),
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
    for block in document.content.split("\n"):
        word_document.add_paragraph(block)
    word_document.save(output)
    return output.getvalue()


def _pdf(document) -> bytes:
    output = BytesIO()
    styles = getSampleStyleSheet()
    story = [Paragraph(escape(document.title), styles["Title"]), Spacer(1, 18)]
    for block in document.content.split("\n"):
        story.append(Paragraph(escape(block) or "&nbsp;", styles["BodyText"]))
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
