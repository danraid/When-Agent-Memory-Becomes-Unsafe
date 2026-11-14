"""Optional neutral PDF proof via reportlab. Not a journal-specific certified PDF."""
from __future__ import annotations
from pathlib import Path
from xml.sax.saxutils import escape


def render_draft_pdf(title, authors, abstract, sections, output):
    try:
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_LEFT
    except ImportError as exc:
        raise RuntimeError('PDF export needs optional reportlab>=4 dependency') from exc
    output=Path(output)
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='PaperTitle', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=17,
                              leading=21, spaceAfter=14, textColor=colors.HexColor('#172b44')))
    styles.add(ParagraphStyle(name='PaperHeading', parent=styles['Heading2'], fontName='Helvetica-Bold',
                              fontSize=11.5, leading=15, spaceBefore=15, spaceAfter=8))
    styles.add(ParagraphStyle(name='PaperBody', parent=styles['BodyText'], fontName='Helvetica', fontSize=9.7,
                              leading=14.5, spaceAfter=8, alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='PaperWarning', parent=styles['BodyText'], fontName='Helvetica-Bold', fontSize=9.5,
                              leading=13, textColor=colors.HexColor('#8f372c'), spaceAfter=13))
    doc=SimpleDocTemplate(str(output),pagesize=(595.28,841.89),rightMargin=54,leftMargin=54,topMargin=55,bottomMargin=58)
    story=[Paragraph(escape(title),styles['PaperTitle']),
           Paragraph('DRAFT - NOT APPROVED FOR SUBMISSION',styles['PaperWarning']),
           Paragraph(escape(', '.join(authors) if authors else 'AUTHOR METADATA REQUIRED'),styles['PaperBody']),
           Spacer(1,12),Paragraph('Abstract',styles['PaperHeading']),Paragraph(escape(abstract),styles['PaperBody'])]
    for heading, blocks in sections.items():
        story.append(Paragraph(escape(heading),styles['PaperHeading']))
        for text in blocks:
            story.append(Paragraph(escape(text),styles['PaperBody']))
    def footer(canvas, doc):
        canvas.setFont('Helvetica',8)
        canvas.setFillColor(colors.HexColor('#617184'))
        canvas.drawString(54,35,'Agentic Research Hub - unreviewed editorial proof')
        canvas.drawRightString(541,35,f'Page {doc.page}')
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    return output
