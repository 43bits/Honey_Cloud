# ai_agents/pdf_generator.py
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import (
    HexColor, white, black
)
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from datetime import datetime
import io
import re
# ── Colour palette ─────────────────────────────────
DARK_BG    = HexColor('#0a0e1a')
CYAN       = HexColor('#00ffe7')
CYAN_DIM   = HexColor('#00b3a0')
RED        = HexColor('#ff2d2d')
ORANGE     = HexColor('#ff6b00')
YELLOW     = HexColor('#ffe600')
GREEN      = HexColor('#00ff88')
SLATE      = HexColor('#1a2035')
SLATE_MID  = HexColor('#243050')
TEXT_MAIN  = HexColor('#e2f0ff')
TEXT_DIM   = HexColor('#8899bb')
WHITE      = white


def build_styles():
    styles = getSampleStyleSheet()

    return {
        'cover_title': ParagraphStyle(
            'cover_title',
            fontName='Helvetica-Bold',
            fontSize=28,
            textColor=CYAN,
            alignment=TA_CENTER,
            spaceAfter=8,
            leading=34,
        ),
        'cover_sub': ParagraphStyle(
            'cover_sub',
            fontName='Helvetica',
            fontSize=11,
            textColor=TEXT_DIM,
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        'section_heading': ParagraphStyle(
            'section_heading',
            fontName='Helvetica-Bold',
            fontSize=13,
            textColor=CYAN,
            spaceBefore=18,
            spaceAfter=6,
            leading=16,
            borderPadding=(0, 0, 4, 0),
        ),
        'body': ParagraphStyle(
            'body',
            fontName='Helvetica',
            fontSize=9.5,
            textColor=TEXT_MAIN,
            leading=15,
            spaceAfter=8,
            alignment=TA_JUSTIFY,
        ),
        'bullet_item': ParagraphStyle(
            'bullet_item',
            fontName='Helvetica',
            fontSize=9.5,
            textColor=TEXT_MAIN,
            leading=15,
            leftIndent=16,
            spaceAfter=4,
        ),
        'label': ParagraphStyle(
            'label',
            fontName='Helvetica-Bold',
            fontSize=8,
            textColor=CYAN_DIM,
            spaceAfter=2,
        ),
        'caption': ParagraphStyle(
            'caption',
            fontName='Helvetica-Oblique',
            fontSize=8,
            textColor=TEXT_DIM,
            alignment=TA_CENTER,
        ),
        'footer': ParagraphStyle(
            'footer',
            fontName='Helvetica',
            fontSize=7.5,
            textColor=TEXT_DIM,
            alignment=TA_CENTER,
        ),
        'ioc': ParagraphStyle(
            'ioc',
            fontName='Courier',
            fontSize=8.5,
            textColor=GREEN,
            leading=13,
            leftIndent=12,
            spaceAfter=2,
        ),
    }


def risk_color(level: str):
    return {
        'CRITICAL': RED,
        'HIGH':     ORANGE,
        'MEDIUM':   YELLOW,
        'LOW':      CYAN,
    }.get(level, CYAN_DIM)


def parse_report_sections(report_text: str) -> dict:
    """Split LLM output into named sections."""
    section_names = [
        'EXECUTIVE SUMMARY',
        'THREAT ANALYSIS',
        'ANOMALY DETECTION FINDINGS',
        'CAMPAIGN ATTRIBUTION',
        'RISK ASSESSMENT',
        'IMMEDIATE RECOMMENDATIONS',
        'INDICATORS OF COMPROMISE',
    ]
    sections = {}
    current  = 'PREAMBLE'
    lines    = report_text.split('\n')
    buf      = []

    for line in lines:
        matched = False
        for name in section_names:
            if name in line.upper():
                if buf:
                    sections[current] = '\n'.join(buf).strip()
                current = name
                buf     = []
                matched = True
                break
        if not matched:
            buf.append(line)

    if buf:
        sections[current] = '\n'.join(buf).strip()

    return sections


def make_stat_table(stats: dict) -> Table:
    """Colourful risk stat table for the cover page."""
    by_risk = stats.get('by_risk', {})
    total   = stats.get('total_attacks', 0)

    data = [
        ['RISK LEVEL', 'COUNT', '% OF TOTAL'],
        ['CRITICAL',   str(by_risk.get('CRITICAL', 0)),
         f"{round(by_risk.get('CRITICAL',0)/max(total,1)*100,1)}%"],
        ['HIGH',       str(by_risk.get('HIGH', 0)),
         f"{round(by_risk.get('HIGH',0)/max(total,1)*100,1)}%"],
        ['MEDIUM',     str(by_risk.get('MEDIUM', 0)),
         f"{round(by_risk.get('MEDIUM',0)/max(total,1)*100,1)}%"],
        ['LOW',        str(by_risk.get('LOW', 0)),
         f"{round(by_risk.get('LOW',0)/max(total,1)*100,1)}%"],
        ['TOTAL',      str(total), '100%'],
    ]

    row_colors = [SLATE_MID, RED, ORANGE, YELLOW, CYAN_DIM, SLATE_MID]
    text_colors = [CYAN, WHITE, WHITE, DARK_BG, DARK_BG, CYAN]

    style = TableStyle([
        ('BACKGROUND',  (0,0), (-1,0),  SLATE_MID),
        ('TEXTCOLOR',   (0,0), (-1,0),  CYAN),
        ('FONTNAME',    (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTSIZE',    (0,0), (-1,-1), 9),
        ('ALIGN',       (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',      (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-2),
         [HexColor('#1a0505'), HexColor('#1a0e05'),
          HexColor('#1a1a05'), HexColor('#051a18')]),
        ('BACKGROUND',  (0,-1), (-1,-1), SLATE_MID),
        ('TEXTCOLOR',   (0,1), (-1,-2),  TEXT_MAIN),
        ('TEXTCOLOR',   (0,-1), (-1,-1), CYAN),
        ('FONTNAME',    (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('GRID',        (0,0),  (-1,-1), 0.5, HexColor('#1e3a4a')),
        ('TOPPADDING',  (0,0),  (-1,-1), 6),
        ('BOTTOMPADDING',(0,0), (-1,-1), 6),
    ])

    return Table(data, colWidths=[2.2*inch, 1.5*inch, 1.5*inch],
                 style=style)


def generate_pdf(report_text: str, stats: dict, attacks: list) -> bytes:
    """Generate full PDF and return as bytes."""

    buf    = io.BytesIO()
    doc    = SimpleDocTemplate(
        buf,
        pagesize=letter,
        leftMargin=0.75*inch,  rightMargin=0.75*inch,
        topMargin=0.75*inch,   bottomMargin=0.75*inch,
    )
    styles   = build_styles()
    sections = parse_report_sections(report_text)
    story    = []
    now      = datetime.now()

    # ── PAGE BACKGROUND via canvas callback ──────────
    def dark_page(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(DARK_BG)
        canvas.rect(0, 0, letter[0], letter[1], fill=1, stroke=0)
        # top accent bar
        canvas.setFillColor(CYAN)
        canvas.rect(0, letter[1]-3, letter[0], 3, fill=1, stroke=0)
        # bottom accent bar
        canvas.setFillColor(SLATE)
        canvas.rect(0, 0, letter[0], 18, fill=1, stroke=0)
        # footer text
        canvas.setFillColor(TEXT_DIM)
        canvas.setFont('Helvetica', 7)
        canvas.drawString(
            0.75*inch, 6,
            f"HONEYCLOUD SENTINEL  |  CONFIDENTIAL  |  "
            f"Generated {now.strftime('%Y-%m-%d %H:%M UTC')}"
        )
        canvas.drawRightString(
            letter[0]-0.75*inch, 6,
            f"Page {doc.page}"
        )
        canvas.restoreState()

    # ── COVER ─────────────────────────────────────────
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("HONEYCLOUD SENTINEL", styles['cover_title']))
    story.append(Paragraph(
        "THREAT INTELLIGENCE REPORT", styles['cover_sub']))
    story.append(Paragraph(
        f"Generated: {now.strftime('%B %d, %Y  %H:%M UTC')}",
        styles['cover_sub']))
    story.append(Spacer(1, 0.3*inch))

    # Cyan divider
    story.append(HRFlowable(
        width="100%", thickness=1,
        color=CYAN, spaceAfter=16
    ))

    # Stat table
    story.append(make_stat_table(stats))
    story.append(Spacer(1, 0.2*inch))

    story.append(HRFlowable(
        width="100%", thickness=1,
        color=SLATE_MID, spaceAfter=24
    ))

    # ── REPORT SECTIONS ───────────────────────────────
    section_order = [
        ('EXECUTIVE SUMMARY',           '01'),
        ('THREAT ANALYSIS',             '02'),
        ('ANOMALY DETECTION FINDINGS',  '03'),
        ('CAMPAIGN ATTRIBUTION',        '04'),
        ('RISK ASSESSMENT',             '05'),
        ('IMMEDIATE RECOMMENDATIONS',   '06'),
        ('INDICATORS OF COMPROMISE',    '07'),
    ]

    for section_name, num in section_order:
        content = sections.get(section_name, '').strip()
        if not content:
            continue

        # Section header
        story.append(KeepTogether([
            Paragraph(
                f"<font color='#00b3a0'>{num} ·</font>  {section_name}",
                styles['section_heading']
            ),
            HRFlowable(
                width="100%", thickness=0.5,
                color=SLATE_MID, spaceAfter=8
            ),
        ]))

        # IoC section — monospace green
        if 'INDICATOR' in section_name:
            for line in content.split('\n'):
                line = line.strip()
                if not line:
                    story.append(Spacer(1, 4))
                    continue
                story.append(Paragraph(f"▸  {line}", styles['ioc']))

        # Recommendations — numbered list styling
        elif 'RECOMMENDATION' in section_name:
            for line in content.split('\n'):
                line = line.strip()
                if not line:
                    story.append(Spacer(1, 4))
                    continue
                # bold the number prefix if present
                line = re.sub(
                    r'^(\d+\.)\s*',
                    r'<font color="#00ffe7"><b>\1</b></font> ',
                    line
                )
                story.append(Paragraph(line, styles['bullet_item']))

        # All other sections — body paragraphs
        else:
            for para_text in content.split('\n\n'):
                para_text = para_text.strip().replace('\n', ' ')
                if para_text:
                    story.append(Paragraph(para_text, styles['body']))

        story.append(Spacer(1, 8))

    # ── RECENT ATTACKS TABLE ──────────────────────────
    story.append(Paragraph(
        "<font color='#00b3a0'>08 ·</font>  RECENT ATTACK LOG",
        styles['section_heading']
    ))
    story.append(HRFlowable(
        width="100%", thickness=0.5,
        color=SLATE_MID, spaceAfter=8
    ))

    table_data = [['TIME', 'SOURCE IP', 'TYPE', 'PORT', 'COUNTRY', 'RISK']]
    for a in attacks[:15]:
        ts = a.get('timestamp', '')[:16]
        table_data.append([
            ts,
            a.get('source_ip', '?'),
            a.get('attack_type', '?')[:22],
            str(a.get('port_targeted', '?')),
            a.get('country', '?')[:14],
            a.get('risk_level', '?'),
        ])

    attack_table_style = TableStyle([
        ('BACKGROUND',   (0,0), (-1,0),  SLATE_MID),
        ('TEXTCOLOR',    (0,0), (-1,0),  CYAN),
        ('FONTNAME',     (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTSIZE',     (0,0), (-1,-1), 7.5),
        ('ALIGN',        (0,0), (-1,-1), 'LEFT'),
        ('VALIGN',       (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),
         [HexColor('#0d1220'), HexColor('#101828')]),
        ('TEXTCOLOR',    (0,1), (-1,-1), TEXT_MAIN),
        ('GRID',         (0,0), (-1,-1), 0.4, HexColor('#1e2a3a')),
        ('TOPPADDING',   (0,0), (-1,-1), 5),
        ('BOTTOMPADDING',(0,0), (-1,-1), 5),
        ('LEFTPADDING',  (0,0), (-1,-1), 6),
    ])

    # Colour the risk column
    risk_col = 5
    risk_map = {'CRITICAL': RED, 'HIGH': ORANGE, 'MEDIUM': YELLOW, 'LOW': CYAN}
    for i, row in enumerate(table_data[1:], start=1):
        clr = risk_map.get(row[risk_col], CYAN_DIM)
        attack_table_style.add('TEXTCOLOR', (risk_col,i), (risk_col,i), clr)
        attack_table_style.add('FONTNAME',  (risk_col,i), (risk_col,i), 'Helvetica-Bold')

    col_widths = [1.1*inch, 1.1*inch, 1.8*inch,
                  0.5*inch, 1.1*inch, 0.7*inch]
    story.append(Table(
        table_data,
        colWidths=col_widths,
        style=attack_table_style,
        repeatRows=1,
    ))

    # ── BUILD PDF ─────────────────────────────────────
    doc.build(story, onFirstPage=dark_page, onLaterPages=dark_page)
    return buf.getvalue()