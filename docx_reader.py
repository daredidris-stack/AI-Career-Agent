from docx import Document

from resume_text_cleaner import clean_resume_text


def read_docx_resume(filename, max_characters=None):

    doc = Document(filename)

    text_parts = []
    text_length = 0

    for paragraph in doc.paragraphs:
        text_length += len(paragraph.text) + 1
        if (
            max_characters is not None
            and text_length > max_characters
        ):
            raise ValueError(
                "Extracted resume text exceeds the processing limit."
            )
        text_parts.append(paragraph.text)

    return clean_resume_text("\n".join(text_parts))
