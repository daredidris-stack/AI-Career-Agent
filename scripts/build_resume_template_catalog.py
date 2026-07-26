from argparse import ArgumentParser
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

from build_tailored_resume_template import build_template


VARIANTS = {
    "ats-professional": {
        "font": "Calibri",
        "primary": RGBColor(11, 37, 69),
        "accent": RGBColor(46, 116, 181),
        "muted": RGBColor(82, 93, 108),
        "margins": (1.0, 1.0),
    },
    "ats-modern": {
        "font": "Arial",
        "primary": RGBColor(15, 76, 69),
        "accent": RGBColor(15, 118, 110),
        "muted": RGBColor(71, 85, 105),
        "margins": (0.82, 0.9),
    },
    "ats-classic": {
        "font": "Georgia",
        "primary": RGBColor(23, 23, 23),
        "accent": RGBColor(64, 64, 64),
        "muted": RGBColor(82, 82, 82),
        "margins": (0.9, 0.95),
    },
}


def _set_style_font(style, name, color):
    style.font.name = name
    style.font.color.rgb = color
    fonts = style.element.get_or_add_rPr().get_or_add_rFonts()
    fonts.set(qn("w:ascii"), name)
    fonts.set(qn("w:hAnsi"), name)


def apply_variant(path: Path, variant: str) -> None:
    settings = VARIANTS[variant]
    document = Document(path)
    for style_name in (
        "Normal",
        "Resume Name",
        "Resume Target Role",
        "Resume Contact",
        "Resume Section",
        "Resume Body",
        "Resume Experience Header",
        "Resume Bullet",
    ):
        style = document.styles[style_name]
        color = settings["primary"]
        if style_name == "Resume Target Role":
            color = settings["accent"]
        elif style_name == "Resume Contact":
            color = settings["muted"]
        _set_style_font(style, settings["font"], color)

    top_bottom, left_right = settings["margins"]
    section = document.sections[0]
    section.top_margin = Inches(top_bottom)
    section.bottom_margin = Inches(top_bottom)
    section.left_margin = Inches(left_right)
    section.right_margin = Inches(left_right)

    if variant == "ats-classic":
        document.styles["Resume Name"].font.size = Pt(22)
        document.styles["Resume Section"].font.all_caps = True

    document.save(path)


def build_catalog(directory: Path) -> None:
    filenames = {
        "ats-professional": "ats_tailored_resume_template.docx",
        "ats-modern": "ats_modern_resume_template.docx",
        "ats-classic": "ats_classic_resume_template.docx",
    }
    directory.mkdir(parents=True, exist_ok=True)
    for variant, filename in filenames.items():
        destination = directory / filename
        build_template(destination)
        apply_variant(destination, variant)


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--directory", required=True, type=Path)
    arguments = parser.parse_args()
    build_catalog(arguments.directory)


if __name__ == "__main__":
    main()
