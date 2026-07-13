from docx import Document


def save_cover_letter(text, filename):

    doc = Document()

    for line in text.split("\n"):

        if line.strip():
            doc.add_paragraph(line)

    doc.save(filename)