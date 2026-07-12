from docx import Document


def read_docx_resume(filename):

    doc = Document(filename)

    text = ""

    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"

    return text


if __name__ == "__main__":

    text = read_docx_resume("resume.docx")

    print(text)