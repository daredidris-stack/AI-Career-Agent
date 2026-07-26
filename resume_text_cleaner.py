import re


_TEMPLATE_NOTE_MARKERS = (
    "include relevant projects if applicable",
    "add certifications like",
    "this resume emphasizes",
    "ats-friendly keywords",
)
_OPTIONAL_HEADINGS = {
    "projects (optional)",
    "certifications (optional)",
}


def clean_resume_text(resume_text: str) -> str:
    """Remove literal Markdown and generator instructions from resume text."""
    cleaned_lines = []
    for raw_line in str(resume_text or "").splitlines():
        line = _clean_line(raw_line)
        if line:
            cleaned_lines.append(line)

    return "\n".join(
        line
        for line in cleaned_lines
        if line.casefold() not in _OPTIONAL_HEADINGS
    )


def _clean_line(raw_line: str) -> str:
    line = raw_line.strip()
    if not line or re.fullmatch(r"```(?:markdown)?", line, re.IGNORECASE):
        return ""
    if re.fullmatch(r"[-*_]{2,}", line):
        return ""

    line = re.sub(
        r"\[([^\]]+)]\((https?://[^)]+)\)",
        r"\1: \2",
        line,
    )
    line = re.sub(r"\*\*([^*]+)\*\*", r"\1", line)
    line = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", line)
    line = re.sub(r"^#{1,6}\s+", "", line)
    line = line.replace("```", "").strip()

    folded = line.casefold()
    if folded.startswith("note:") and any(
        marker in folded for marker in _TEMPLATE_NOTE_MARKERS
    ):
        return ""
    return line
