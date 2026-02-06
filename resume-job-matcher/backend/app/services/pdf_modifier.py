import os
import copy
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT

from app.models.schemas import ResumeRecommendation


def apply_recommendations_to_pdf(
    original_pdf_path: str,
    recommendations: list[ResumeRecommendation],
    output_path: str,
) -> str:
    """
    Create a modified resume PDF with recommendations applied.
    Since directly editing PDF text is unreliable, we generate a new
    clean PDF with the modified content.
    """
    import pdfplumber

    # Extract original text
    original_text = ""
    with pdfplumber.open(original_pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                original_text += page_text + "\n"

    # Apply text replacements
    modified_text = original_text
    for rec in recommendations:
        if rec.original_text and rec.original_text != "(No summary section found)" \
                and rec.original_text != "(ATS optimization)" \
                and rec.original_text != "(Resume length)":
            modified_text = modified_text.replace(rec.original_text, rec.recommended_text)

    # Generate new PDF
    _generate_pdf(modified_text, output_path)
    return output_path


def _generate_pdf(text: str, output_path: str):
    """Generate a clean PDF from text content."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()

    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=13,
        spaceAfter=6,
        spaceBefore=12,
        textColor="#1a1a2e",
        fontName="Helvetica-Bold",
    )

    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        spaceAfter=4,
        alignment=TA_LEFT,
        fontName="Helvetica",
    )

    name_style = ParagraphStyle(
        "NameStyle",
        parent=styles["Title"],
        fontSize=18,
        spaceAfter=4,
        textColor="#1a1a2e",
        fontName="Helvetica-Bold",
    )

    elements = []
    lines = text.split("\n")

    section_headers = {
        "summary", "objective", "professional summary", "profile",
        "experience", "work experience", "professional experience",
        "education", "skills", "technical skills", "core competencies",
        "projects", "certifications", "awards", "publications",
        "volunteer", "interests", "references", "contact",
    }

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            elements.append(Spacer(1, 6))
            continue

        # Escape XML special characters for reportlab
        safe_text = (
            stripped.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

        # First non-empty line is likely the name
        if i < 3 and len(stripped) < 50 and not any(c in stripped for c in ["@", "|", "•"]):
            elements.append(Paragraph(safe_text, name_style))
        elif stripped.lower().rstrip(":") in section_headers or (
            stripped.upper() == stripped and len(stripped) < 40 and len(stripped) > 2
        ):
            elements.append(Spacer(1, 8))
            elements.append(Paragraph(safe_text, heading_style))
        elif stripped.startswith(("•", "-", "–", "▪", "○")):
            bullet_text = "• " + safe_text.lstrip("•-–▪○● ")
            elements.append(Paragraph(bullet_text, body_style))
        else:
            elements.append(Paragraph(safe_text, body_style))

    doc.build(elements)
