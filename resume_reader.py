import pdfplumber

from resume_text_cleaner import clean_resume_text


def read_pdf_resume(filename, max_characters=None):

    text_parts = []
    text_length = 0

    with pdfplumber.open(filename) as pdf:

        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text_length += len(page_text) + 1
                if (
                    max_characters is not None
                    and text_length > max_characters
                ):
                    raise ValueError(
                        "Extracted resume text exceeds the processing limit."
                    )
                text_parts.append(page_text)

    return clean_resume_text("\n".join(text_parts))
