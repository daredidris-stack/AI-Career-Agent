import pdfplumber

from resume_text_cleaner import clean_resume_text


def read_pdf_resume(filename):

    text = ""

    with pdfplumber.open(filename) as pdf:

        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return clean_resume_text(text)
