import pdfplumber


def read_pdf_resume(filename):

    text = ""

    with pdfplumber.open(filename) as pdf:

        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text