from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "database", "resumes")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Theme colours
PRIMARY = HexColor("#1a1a2e")
ACCENT = HexColor("#0f3460")
TEXT_COLOR = HexColor("#333333")
LIGHT_GRAY = HexColor("#666666")


def _styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="CVName", fontSize=22, leading=26, textColor=PRIMARY,
        fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="CVContact", fontSize=9, leading=12, textColor=LIGHT_GRAY,
        fontName="Helvetica", alignment=TA_CENTER, spaceAfter=12,
    ))
    styles.add(ParagraphStyle(
        name="CVSection", fontSize=12, leading=16, textColor=ACCENT,
        fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="CVBody", fontSize=10, leading=13, textColor=TEXT_COLOR,
        fontName="Helvetica", alignment=TA_JUSTIFY, spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="CVJobTitle", fontSize=10, leading=13, textColor=PRIMARY,
        fontName="Helvetica-Bold", spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        name="CVCompany", fontSize=9, leading=12, textColor=LIGHT_GRAY,
        fontName="Helvetica-Oblique", spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="CVBullet", fontSize=9, leading=12, textColor=TEXT_COLOR,
        fontName="Helvetica", leftIndent=15, spaceAfter=2,
    ))
    return styles


def generate_cv_pdf(cv_data: dict, page_count: int, user_id: int) -> tuple:
    """Build a professional PDF and return (filepath, filename)."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c if c.isalnum() or c in " _-" else "" for c in cv_data.get("name", "resume"))
    safe_name = safe_name.strip().replace(" ", "_") or "resume"
    filename = f"CV_{safe_name}_{timestamp}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)

    doc = SimpleDocTemplate(
        filepath, pagesize=A4,
        rightMargin=0.6 * inch, leftMargin=0.6 * inch,
        topMargin=0.5 * inch, bottomMargin=0.5 * inch,
    )

    s = _styles()
    story = []

    # --- Header ---
    story.append(Paragraph(cv_data.get("name", "Your Name"), s["CVName"]))

    contact_parts = [
        v for v in [
            cv_data.get("email"), cv_data.get("phone"),
            cv_data.get("location"), cv_data.get("linkedin"),
        ] if v
    ]
    if contact_parts:
        story.append(Paragraph(" &nbsp;|&nbsp; ".join(contact_parts), s["CVContact"]))

    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=10))

    # --- Professional Summary ---
    summary = cv_data.get("summary", "")
    if summary:
        story.append(Paragraph("PROFESSIONAL SUMMARY", s["CVSection"]))
        story.append(HRFlowable(width="100%", thickness=0.5, color=LIGHT_GRAY, spaceAfter=6))
        story.append(Paragraph(summary, s["CVBody"]))

    # --- Work Experience ---
    experience = cv_data.get("experience", [])
    if experience:
        story.append(Paragraph("WORK EXPERIENCE", s["CVSection"]))
        story.append(HRFlowable(width="100%", thickness=0.5, color=LIGHT_GRAY, spaceAfter=6))
        limit = len(experience) if page_count >= 2 else min(len(experience), 4)
        for exp in experience[:limit]:
            story.append(Paragraph(exp.get("title", ""), s["CVJobTitle"]))
            story.append(Paragraph(
                f"{exp.get('company', '')} | {exp.get('duration', '')}", s["CVCompany"]
            ))
            achv = exp.get("achievements", [])
            achv_limit = len(achv) if page_count >= 2 else min(len(achv), 3)
            for a in achv[:achv_limit]:
                story.append(Paragraph(f"&bull; {a}", s["CVBullet"]))
            story.append(Spacer(1, 4))

    # --- Education ---
    education = cv_data.get("education", [])
    if education:
        story.append(Paragraph("EDUCATION", s["CVSection"]))
        story.append(HRFlowable(width="100%", thickness=0.5, color=LIGHT_GRAY, spaceAfter=6))
        for edu in education:
            story.append(Paragraph(edu.get("degree", ""), s["CVJobTitle"]))
            story.append(Paragraph(
                f"{edu.get('institution', '')} | {edu.get('year', '')}", s["CVCompany"]
            ))
            story.append(Spacer(1, 4))

    # --- Skills ---
    skills = cv_data.get("skills", [])
    if skills:
        story.append(Paragraph("SKILLS", s["CVSection"]))
        story.append(HRFlowable(width="100%", thickness=0.5, color=LIGHT_GRAY, spaceAfter=6))
        limit = len(skills) if page_count >= 2 else min(len(skills), 15)
        story.append(Paragraph(" &bull; ".join(skills[:limit]), s["CVBody"]))

    # --- Certifications ---
    certs = cv_data.get("certifications", [])
    if certs:
        story.append(Paragraph("CERTIFICATIONS", s["CVSection"]))
        story.append(HRFlowable(width="100%", thickness=0.5, color=LIGHT_GRAY, spaceAfter=6))
        for c in certs:
            story.append(Paragraph(f"&bull; {c}", s["CVBullet"]))

    # --- Projects ---
    projects = cv_data.get("projects", [])
    if projects:
        story.append(Paragraph("PROJECTS", s["CVSection"]))
        story.append(HRFlowable(width="100%", thickness=0.5, color=LIGHT_GRAY, spaceAfter=6))
        limit = len(projects) if page_count >= 2 else min(len(projects), 3)
        for p in projects[:limit]:
            story.append(Paragraph(f"<b>{p.get('name', '')}</b>", s["CVBody"]))
            desc = p.get("description", "")
            if desc:
                story.append(Paragraph(desc, s["CVBullet"]))
            story.append(Spacer(1, 4))

    doc.build(story)
    return filepath, filename
