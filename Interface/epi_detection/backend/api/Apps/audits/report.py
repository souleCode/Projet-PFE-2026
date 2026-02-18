from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, Image as RLImage, HRFlowable
)


# ── Palette ───────────────────────────────────────────────────────────────────
COLOR_PRIMARY  = colors.HexColor('#1e40af')
COLOR_DANGER   = colors.HexColor('#dc2626')
COLOR_WARNING  = colors.HexColor('#d97706')
COLOR_SUCCESS  = colors.HexColor('#16a34a')
COLOR_LIGHT    = colors.HexColor('#f1f5f9')
COLOR_BORDER   = colors.HexColor('#cbd5e1')

CRITICITY_COLORS = {
    'faible':  COLOR_SUCCESS,
    'moyenne': COLOR_WARNING,
    'elevee':  COLOR_DANGER,
}

EPI_LABELS = {
    'hardhat': 'Casque de sécurité',
    'vest':    'Gilet réfléchissant',
    'glass':   'Lunettes de protection',
}


def generate_audit_pdf(audit) -> BytesIO:
    """
    Génère un rapport PDF complet pour un audit.
    Retourne un BytesIO prêt à être envoyé en réponse HTTP.
    """
    buffer = BytesIO()
    doc    = SimpleDocTemplate(
        buffer,
        pagesize    = A4,
        rightMargin = 2 * cm,
        leftMargin  = 2 * cm,
        topMargin   = 2 * cm,
        bottomMargin= 2 * cm,
    )

    styles  = getSampleStyleSheet()
    story   = []

    # ── Styles personnalisés ──────────────────────────────────────────────────
    title_style = ParagraphStyle(
        'CustomTitle',
        parent    = styles['Title'],
        fontSize  = 22,
        textColor = COLOR_PRIMARY,
        spaceAfter= 6,
    )
    section_style = ParagraphStyle(
        'Section',
        parent     = styles['Heading2'],
        fontSize   = 13,
        textColor  = COLOR_PRIMARY,
        spaceBefore= 14,
        spaceAfter = 4,
        borderPad  = 4,
    )
    normal = styles['Normal']
    normal.fontSize  = 10
    normal.leading   = 14

    # ── En-tête ───────────────────────────────────────────────────────────────
    story.append(Paragraph("RAPPORT D'AUDIT EPI", title_style))
    story.append(Paragraph(audit.title, styles['Heading1']))
    story.append(HRFlowable(width='100%', thickness=2, color=COLOR_PRIMARY))
    story.append(Spacer(1, 0.4 * cm))

    # ── Infos générales ───────────────────────────────────────────────────────
    story.append(Paragraph("Informations générales", section_style))

    status_labels = {'ouvert': 'Ouvert', 'en_cours': 'En cours', 'clos': 'Clos'}
    info_data = [
        ['Caméra',        audit.camera.name if audit.camera else 'N/A'],
        ['Localisation',  audit.camera.location if audit.camera else 'N/A'],
        ['Créé par',      audit.created_by.full_name if audit.created_by else 'N/A'],
        ['Date création', audit.created_at.strftime('%d/%m/%Y %H:%M')],
        ['Statut',        status_labels.get(audit.status, audit.status)],
    ]
    info_table = Table(info_data, colWidths=[5 * cm, 12 * cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), COLOR_LIGHT),
        ('FONTNAME',   (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE',   (0, 0), (-1, -1), 10),
        ('GRID',       (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, COLOR_LIGHT]),
        ('VALIGN',     (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING',    (0, 0), (-1, -1), 6),
    ]))
    story.append(info_table)

    # ── Alerte liée ───────────────────────────────────────────────────────────
    if audit.alert:
        alert = audit.alert
        story.append(Paragraph("Alerte associée", section_style))

        crit_color = CRITICITY_COLORS.get(alert.criticity, COLOR_PRIMARY)
        missing    = ', '.join(EPI_LABELS.get(e, e) for e in alert.epi_missing) or 'Aucun'

        alert_data = [
            ['ID Alerte',      f"#{alert.id}"],
            ['Date',           alert.timestamp.strftime('%d/%m/%Y %H:%M')],
            ['Criticité',      alert.criticity.upper()],
            ['EPI manquants',  missing],
            ['Statut alerte',  alert.status],
        ]
        alert_table = Table(alert_data, colWidths=[5 * cm, 12 * cm])
        alert_table.setStyle(TableStyle([
            ('BACKGROUND',  (0, 0), (0, -1), COLOR_LIGHT),
            ('FONTNAME',    (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE',    (0, 0), (-1, -1), 10),
            ('GRID',        (0, 0), (-1, -1), 0.5, COLOR_BORDER),
            ('TEXTCOLOR',   (1, 2), (1, 2), crit_color),   # criticité colorée
            ('FONTNAME',    (1, 2), (1, 2), 'Helvetica-Bold'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, COLOR_LIGHT]),
            ('VALIGN',      (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING',     (0, 0), (-1, -1), 6),
        ]))
        story.append(alert_table)

    # ── Notes ─────────────────────────────────────────────────────────────────
    if audit.notes:
        story.append(Paragraph("Notes", section_style))
        story.append(Paragraph(audit.notes, normal))

    # ── Captures ──────────────────────────────────────────────────────────────
    captures = audit.captures.all()
    if captures.exists():
        story.append(Paragraph(f"Captures d'écran ({captures.count()})", section_style))
        story.append(Spacer(1, 0.3 * cm))

        for idx, capture in enumerate(captures, start=1):
            story.append(Paragraph(
                f"<b>Capture {idx}</b> — {capture.taken_at.strftime('%d/%m/%Y %H:%M')}"
                + (f" — {capture.description}" if capture.description else ""),
                normal
            ))
            story.append(Spacer(1, 0.2 * cm))

            try:
                img = RLImage(capture.image.path, width=14 * cm, height=8 * cm, kind='proportional')
                story.append(img)
            except Exception:
                story.append(Paragraph("<i>Image non disponible</i>", normal))

            story.append(Spacer(1, 0.4 * cm))

    # ── Pied de page ──────────────────────────────────────────────────────────
    story.append(Spacer(1, 1 * cm))
    story.append(HRFlowable(width='100%', thickness=1, color=COLOR_BORDER))
    story.append(Paragraph(
        f"Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')} — Système de surveillance EPI",
        ParagraphStyle('Footer', parent=normal, fontSize=8, textColor=colors.grey)
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer