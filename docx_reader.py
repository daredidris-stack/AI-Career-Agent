from docx import Document

from resume_text_cleaner import clean_resume_text


def read_docx_resume(filename):

    doc = Document(filename)

    text = ""

    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"

    return clean_resume_text(text)
