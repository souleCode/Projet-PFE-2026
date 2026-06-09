"""
Présentation Technique — Validation de Stage
Projet EPI Detection — Plateforme HSE Intelligente
Exécuter : python generate_validation_stage.py
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Cm
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.oxml.ns import qn
from lxml import etree

# ── Palette de couleurs ──────────────────────────────────────────────────────
NAVY        = RGBColor(15,  23,  42)
NAVY_CARD   = RGBColor(30,  41,  59)
NAVY_LIGHT  = RGBColor(51,  65,  85)
ORANGE      = RGBColor(249, 115, 22)
ORANGE_DARK = RGBColor(194, 65,  12)
BLUE_ELEC   = RGBColor(59,  130, 246)
WHITE       = RGBColor(255, 255, 255)
LIGHT_BG    = RGBColor(248, 250, 252)
TEXT_DARK   = RGBColor(15,  23,  42)
TEXT_MUTED  = RGBColor(100, 116, 139)
GREEN_OK    = RGBColor(16,  185, 129)
RED_KO      = RGBColor(239, 68,  68)
YELLOW      = RGBColor(234, 179, 8)
BORDER      = RGBColor(226, 232, 240)

# ── Infos à personnaliser ────────────────────────────────────────────────────
STAGIAIRE   = "Souleymane Traoré"
ENTREPRISE  = "[NOM DE L'ENTREPRISE]"
DUREE_STAGE = "[Durée du stage, ex. 4 mois]"
PERIODE     = "[Période, ex. Fév – Juin 2025]"
ENCADRANT   = "[Nom de votre encadrant entreprise]"
NB_COMMITS  = "[XX]"   # git log --oneline | wc -l
DATE_PRES   = "Juin 2025"


# ── Dimensions slide 16:9 ────────────────────────────────────────────────────
SLIDE_W = Cm(33.87)
SLIDE_H = Cm(19.05)


# ── Utilitaires ──────────────────────────────────────────────────────────────

def _rgb(color: RGBColor):
    return color.r, color.g, color.b


def set_bg(slide, prs, color: RGBColor):
    """Remplit le fond du slide avec une couleur unie."""
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_rect(slide, left, top, width, height,
             fill_color=None, line_color=None, line_width=Pt(0)):
    """Ajoute un rectangle simple."""
    shape = slide.shapes.add_shape(
        1,  # MSO_SHAPE.RECTANGLE
        left, top, width, height
    )
    if fill_color:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_color
    else:
        shape.fill.background()
    if line_color:
        shape.line.color.rgb = line_color
        shape.line.width = line_width
    else:
        shape.line.fill.background()
    return shape


def add_rounded_rect(slide, left, top, width, height,
                     fill_color=None, line_color=None, line_width=Pt(0),
                     corner_radius=30000):
    """Ajoute un rectangle arrondi.

    corner_radius : valeur OOXML 0–50000 (50000 = demi-cercle).
    Les anciennes valeurs >50000 sont ramenées dans la plage valide.
    """
    shape = slide.shapes.add_shape(
        5,  # MSO_SHAPE.ROUNDED_RECTANGLE
        left, top, width, height
    )
    # Réglage du rayon via l'XML OOXML (a:prstGeom/a:avLst/a:gd)
    radius = min(max(int(corner_radius), 0), 50000)
    sp = shape.element
    prstGeom = sp.spPr.find(qn('a:prstGeom'))
    if prstGeom is not None:
        avLst = prstGeom.find(qn('a:avLst'))
        if avLst is None:
            avLst = etree.SubElement(prstGeom, qn('a:avLst'))
        gd_list = avLst.findall(qn('a:gd'))
        if gd_list:
            gd_list[0].set('fmla', f'val {radius}')
        else:
            gd = etree.SubElement(avLst, qn('a:gd'))
            gd.set('name', 'adj')
            gd.set('fmla', f'val {radius}')
    if fill_color:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_color
    else:
        shape.fill.background()
    if line_color:
        shape.line.color.rgb = line_color
        shape.line.width = line_width
    else:
        shape.line.fill.background()
    return shape


def add_textbox(slide, left, top, width, height, text,
                font_color=TEXT_DARK, font_size=14, bold=False,
                italic=False, align=PP_ALIGN.LEFT, wrap=True):
    """Ajoute une zone de texte."""
    txb = slide.shapes.add_textbox(left, top, width, height)
    tf = txb.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = font_size
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = font_color
    run.font.name = "Calibri"
    return txb


def add_header(slide, title, slide_num=None, dark_bg=False):
    """Ajoute la barre header NAVY en haut avec titre."""
    # Barre de fond header
    add_rect(slide,
             left=Cm(0), top=Cm(0),
             width=SLIDE_W, height=Cm(2.2),
             fill_color=NAVY)
    # Accent orange à gauche
    add_rect(slide,
             left=Cm(0), top=Cm(0),
             width=Cm(0.5), height=Cm(2.2),
             fill_color=ORANGE)
    # Titre dans le header
    add_textbox(slide,
                left=Cm(1), top=Cm(0.35),
                width=Cm(29), height=Cm(1.5),
                text=title,
                font_color=WHITE, font_size=Pt(22), bold=True,
                align=PP_ALIGN.LEFT)
    # Numéro de slide
    if slide_num:
        add_textbox(slide,
                    left=Cm(31.5), top=Cm(0.6),
                    width=Cm(2), height=Cm(1),
                    text=str(slide_num),
                    font_color=ORANGE, font_size=Pt(13), bold=True,
                    align=PP_ALIGN.RIGHT)


def add_bullet_card(slide, left, top, width, height,
                    title, items, title_color=ORANGE,
                    bg_color=None, text_color=TEXT_DARK,
                    bullet_char="▸", bullet_color=ORANGE, font_size=Pt(14)):
    """Ajoute une carte avec titre et liste de bullets."""
    if bg_color:
        add_rounded_rect(slide, left, top, width, height,
                         fill_color=bg_color, corner_radius=120000)
    # Titre de la carte
    add_textbox(slide, left + Cm(0.3), top + Cm(0.2),
                width - Cm(0.6), Cm(0.8),
                text=title,
                font_color=title_color, font_size=Pt(13), bold=True)
    # Bullets
    y_offset = top + Cm(1.1)
    line_h = Cm(0.7)
    for item in items:
        add_textbox(slide, left + Cm(0.3), y_offset,
                    width - Cm(0.6), line_h,
                    text=f"{bullet_char}  {item}",
                    font_color=text_color, font_size=font_size)
        y_offset += line_h


def add_stat_card(slide, left, top, width, height,
                  value, label, val_color=ORANGE, bg_color=NAVY_CARD):
    """Carte statistique : grande valeur + label."""
    add_rounded_rect(slide, left, top, width, height,
                     fill_color=bg_color, corner_radius=150000)
    # Valeur
    add_textbox(slide, left, top + Cm(0.5),
                width, Cm(1.4),
                text=value,
                font_color=val_color, font_size=Pt(28), bold=True,
                align=PP_ALIGN.CENTER)
    # Label
    add_textbox(slide, left + Cm(0.2), top + Cm(2.0),
                width - Cm(0.4), Cm(0.7),
                text=label,
                font_color=WHITE, font_size=Pt(11),
                align=PP_ALIGN.CENTER)


def add_flow_step(slide, left, top, width, height,
                  num, title, subtitle="",
                  num_color=ORANGE, box_color=NAVY_CARD):
    """Étape numérotée pour un diagramme de flux."""
    add_rounded_rect(slide, left, top, width, height,
                     fill_color=box_color, corner_radius=100000)
    # Numéro
    add_textbox(slide, left, top + Cm(0.2),
                width, Cm(0.8),
                text=num,
                font_color=num_color, font_size=Pt(16), bold=True,
                align=PP_ALIGN.CENTER)
    # Titre
    add_textbox(slide, left + Cm(0.2), top + Cm(0.9),
                width - Cm(0.4), Cm(0.7),
                text=title,
                font_color=WHITE, font_size=Pt(11), bold=True,
                align=PP_ALIGN.CENTER)
    if subtitle:
        add_textbox(slide, left + Cm(0.2), top + Cm(1.55),
                    width - Cm(0.4), Cm(0.6),
                    text=subtitle,
                    font_color=TEXT_MUTED, font_size=Pt(9),
                    align=PP_ALIGN.CENTER)


def add_arrow_right(slide, left, top, width=Cm(0.8), height=Cm(0.5)):
    """Ajoute une flèche droite (shape)."""
    shape = slide.shapes.add_shape(
        13,  # MSO_SHAPE.RIGHT_ARROW
        left, top, width, height
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = ORANGE
    shape.line.fill.background()
    return shape


def add_tag(slide, left, top, text,
            bg=NAVY_CARD, fg=WHITE, font_size=Pt(12)):
    """Badge/tag compact."""
    w, h = Cm(3.5), Cm(0.7)
    add_rounded_rect(slide, left, top, w, h,
                     fill_color=bg, corner_radius=80000)
    add_textbox(slide, left + Cm(0.1), top + Cm(0.05),
                w - Cm(0.2), h,
                text=text,
                font_color=fg, font_size=font_size, bold=True,
                align=PP_ALIGN.CENTER)


# ── SLIDES ───────────────────────────────────────────────────────────────────

def slide_01_titre(prs):
    """Slide 1 — Titre"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, prs, NAVY)

    # Barre orange pleine largeur en haut
    add_rect(slide, Cm(0), Cm(0), SLIDE_W, Cm(1.0), fill_color=ORANGE)

    # Badge "VALIDATION DE STAGE" centré en haut
    add_textbox(slide, Cm(0), Cm(0.1), SLIDE_W, Cm(0.8),
                text="PRÉSENTATION TECHNIQUE — VALIDATION DE STAGE",
                font_color=WHITE, font_size=Pt(11), bold=True,
                align=PP_ALIGN.CENTER)

    # Titre principal — ligne 1
    add_textbox(slide, Cm(2), Cm(2.0), Cm(30), Cm(1.8),
                text="Plateforme Intelligente de Détection EPI",
                font_color=WHITE, font_size=Pt(34), bold=True,
                align=PP_ALIGN.CENTER)

    # Titre principal — ligne 2
    add_textbox(slide, Cm(2), Cm(3.6), Cm(30), Cm(1.4),
                text="Gestion des Alertes & Audits HSE",
                font_color=ORANGE, font_size=Pt(28), bold=True,
                align=PP_ALIGN.CENTER)

    # Séparateur
    add_rect(slide, Cm(8), Cm(5.3), Cm(18), Cm(0.08),
             fill_color=ORANGE)

    # Sous-titre
    add_textbox(slide, Cm(2), Cm(5.6), Cm(30), Cm(0.8),
                text=f"Stage réalisé au sein de {ENTREPRISE}",
                font_color=WHITE, font_size=Pt(16),
                align=PP_ALIGN.CENTER)

    add_textbox(slide, Cm(2), Cm(6.4), Cm(30), Cm(0.7),
                text=f"{PERIODE} — {DUREE_STAGE}",
                font_color=TEXT_MUTED, font_size=Pt(14),
                align=PP_ALIGN.CENTER)

    # Infos stagiaire / encadrant
    add_textbox(slide, Cm(2), Cm(8.0), Cm(14), Cm(0.7),
                text=f"Stagiaire : {STAGIAIRE}",
                font_color=WHITE, font_size=Pt(13), bold=True,
                align=PP_ALIGN.LEFT)
    add_textbox(slide, Cm(18), Cm(8.0), Cm(14), Cm(0.7),
                text=f"Encadrant : {ENCADRANT}",
                font_color=WHITE, font_size=Pt(13),
                align=PP_ALIGN.RIGHT)

    # Barre orange en bas
    add_rect(slide, Cm(0), Cm(18.55), SLIDE_W, Cm(0.5),
             fill_color=ORANGE)

    add_textbox(slide, Cm(0), Cm(18.6), SLIDE_W, Cm(0.4),
                text=DATE_PRES,
                font_color=WHITE, font_size=Pt(9),
                align=PP_ALIGN.CENTER)


def slide_02_contexte(prs):
    """Slide 2 — Contexte & Problématique"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, prs, LIGHT_BG)
    add_header(slide, "Contexte & Problématique Métier", slide_num=2)

    # Colonne gauche — Contexte
    add_textbox(slide, Cm(1), Cm(2.6), Cm(15), Cm(0.6),
                text="CONTEXTE", font_color=ORANGE, font_size=Pt(12), bold=True)
    add_rect(slide, Cm(1), Cm(3.2), Cm(15), Cm(0.05),
             fill_color=ORANGE)

    bullets_contexte = [
        "Environnements industriels à risque",
        "Port des EPI = obligation réglementaire",
        "Contrôles manuels = ponctuels & incomplets",
        "Aucune traçabilité des non-conformités",
        "Réaction après accident plutôt que prévention",
    ]
    y = Cm(3.4)
    for b in bullets_contexte:
        add_textbox(slide, Cm(1.3), y, Cm(14.5), Cm(0.65),
                    text=f"▸  {b}", font_color=TEXT_DARK, font_size=Pt(14))
        y += Cm(0.7)

    # Colonne droite — Problématique
    add_rounded_rect(slide, Cm(17.5), Cm(2.6), Cm(15.5), Cm(6.5),
                     fill_color=NAVY_CARD, corner_radius=150000)

    add_textbox(slide, Cm(18), Cm(3.0), Cm(14.5), Cm(0.7),
                text="PROBLÉMATIQUE", font_color=ORANGE,
                font_size=Pt(13), bold=True)

    add_textbox(slide, Cm(18), Cm(3.8), Cm(14.2), Cm(3.5),
                text=('"Comment détecter automatiquement les '
                      'non-conformités EPI, centraliser les incidents '
                      'et garantir un suivi jusqu\'à la résolution ?"'),
                font_color=WHITE, font_size=Pt(14), italic=True)

    add_textbox(slide, Cm(18), Cm(7.2), Cm(14.2), Cm(0.6),
                text="Réponse → Plateforme HSE intelligente full-stack",
                font_color=GREEN_OK, font_size=Pt(12), bold=True)

    # Barre bas
    add_rect(slide, Cm(0), Cm(18.55), SLIDE_W, Cm(0.5),
             fill_color=NAVY)


def slide_03_architecture(prs):
    """Slide 3 — Architecture Globale"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, prs, LIGHT_BG)
    add_header(slide, "Architecture Globale de la Solution", slide_num=3)

    # 3 couches verticales
    layers = [
        ("FRONTEND",  "React · TypeScript · Vite · Tailwind",  BLUE_ELEC,  RGBColor(219,234,254)),
        ("BACKEND",   "Django 4.2 · DRF · YOLOv8 · ReportLab", NAVY,       RGBColor(226,232,240)),
        ("CLOUD",     "AWS EC2 · S3 · RDS · Cloudflare CDN",   ORANGE,     RGBColor(255,237,213)),
    ]

    box_h = Cm(2.8)
    box_w = Cm(22)
    left  = Cm(5.5)
    y_start = Cm(2.6)
    gap = Cm(3.1)

    for i, (layer_name, tech, accent, bg) in enumerate(layers):
        top = y_start + i * gap
        add_rounded_rect(slide, left, top, box_w, box_h,
                         fill_color=bg,
                         line_color=accent, line_width=Pt(2),
                         corner_radius=120000)
        # Label couche à gauche
        add_textbox(slide, left + Cm(0.5), top + Cm(0.3),
                    Cm(4), Cm(0.8),
                    text=layer_name,
                    font_color=accent, font_size=Pt(14), bold=True)
        # Technologies
        add_textbox(slide, left + Cm(0.5), top + Cm(1.2),
                    box_w - Cm(1), Cm(0.9),
                    text=tech,
                    font_color=TEXT_DARK, font_size=Pt(13))
        # Flèche entre couches
        if i < len(layers) - 1:
            add_textbox(slide,
                        left + box_w / 2 - Cm(3), top + box_h + Cm(0.1),
                        Cm(6), Cm(0.6),
                        text="API REST + JWT Cookies",
                        font_color=TEXT_MUTED, font_size=Pt(10),
                        align=PP_ALIGN.CENTER)
            add_rect(slide,
                     left + box_w / 2 - Cm(0.05),
                     top + box_h + Cm(0.6),
                     Cm(0.1), Cm(0.8),
                     fill_color=ORANGE)

    # Note architecture côté droit
    add_rounded_rect(slide, Cm(28.5), Cm(2.6), Cm(4.8), Cm(10.5),
                     fill_color=NAVY_CARD, corner_radius=120000)
    add_textbox(slide, Cm(28.7), Cm(2.9), Cm(4.4), Cm(0.7),
                text="Points clés", font_color=ORANGE,
                font_size=Pt(11), bold=True)
    notes = [
        "Auth JWT HttpOnly",
        "CORS sécurisé",
        "S3 pour médias",
        "Nginx + Gunicorn",
        "CI/CD CodeDeploy",
        "CDN Cloudflare",
    ]
    y = Cm(3.7)
    for n in notes:
        add_textbox(slide, Cm(28.7), y, Cm(4.2), Cm(0.6),
                    text=f"• {n}", font_color=WHITE, font_size=Pt(10))
        y += Cm(0.7)

    add_rect(slide, Cm(0), Cm(18.55), SLIDE_W, Cm(0.5), fill_color=NAVY)


def slide_04_stack(prs):
    """Slide 4 — Stack Technologique"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, prs, LIGHT_BG)
    add_header(slide, "Stack Technologique", slide_num=4)

    # 4 cartes : IA / Frontend / Backend / Infra
    categories = [
        ("IA & Vision",    ORANGE,     NAVY_CARD, ["YOLOv8 (ultralytics)", "OpenCV", "Python 3.11", "best.pt (custom)"]),
        ("Frontend",       BLUE_ELEC,  RGBColor(30,58,138), ["React 18 + TypeScript", "Vite + Tailwind CSS", "Recharts (KPIs)", "React Router v6"]),
        ("Backend",        GREEN_OK,   RGBColor(6,78,59),   ["Django 4.2 + DRF", "JWT HttpOnly cookies", "PostgreSQL / SQLite", "ReportLab (PDF)"]),
        ("Infra & Cloud",  YELLOW,     RGBColor(78,60,6),   ["AWS EC2 + CodeDeploy", "AWS S3 + RDS", "Cloudflare CDN", "Nginx + Gunicorn"]),
    ]

    card_w = Cm(7.8)
    card_h = Cm(8.0)
    y_top  = Cm(2.6)
    x_start= Cm(0.8)

    for i, (cat, accent, bg, techs) in enumerate(categories):
        left = x_start + i * (card_w + Cm(0.5))
        add_rounded_rect(slide, left, y_top, card_w, card_h,
                         fill_color=bg, corner_radius=150000)
        # Ligne accent
        add_rect(slide, left, y_top, card_w, Cm(0.22),
                 fill_color=accent)
        # Titre
        add_textbox(slide, left + Cm(0.3), y_top + Cm(0.4),
                    card_w - Cm(0.6), Cm(0.8),
                    text=cat, font_color=accent,
                    font_size=Pt(14), bold=True)
        # Tech list
        y_item = y_top + Cm(1.4)
        for t in techs:
            add_textbox(slide, left + Cm(0.5), y_item,
                        card_w - Cm(0.7), Cm(1.2),
                        text=t, font_color=WHITE, font_size=Pt(13))
            y_item += Cm(1.35)

    add_rect(slide, Cm(0), Cm(18.55), SLIDE_W, Cm(0.5), fill_color=NAVY)


def slide_05_yolo(prs):
    """Slide 5 — Dataset & Modèle YOLO"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, prs, LIGHT_BG)
    add_header(slide, "Dataset & Entraînement du Modèle YOLOv8", slide_num=5)

    # Colonne gauche — Dataset
    add_textbox(slide, Cm(1), Cm(2.6), Cm(15), Cm(0.6),
                text="DATASET", font_color=ORANGE, font_size=Pt(12), bold=True)
    add_rect(slide, Cm(1), Cm(3.2), Cm(14), Cm(0.06), fill_color=ORANGE)

    dataset_items = [
        ("Classes détectées",     "Casque · Gilet · Gants · Lunettes"),
        ("Source des données",    "[Dataset public + annotations custom]"),
        ("Annotation",            "LabelImg / Roboflow — format YOLO"),
        ("Split",                 "Train 70% / Val 20% / Test 10%"),
        ("Prétraitement",         "Redimensionnement 640×640 px"),
    ]
    y = Cm(3.4)
    for label, val in dataset_items:
        add_textbox(slide, Cm(1.3), y, Cm(5), Cm(0.7),
                    text=label, font_color=TEXT_MUTED, font_size=Pt(12))
        add_textbox(slide, Cm(6.5), y, Cm(9.5), Cm(0.7),
                    text=val, font_color=TEXT_DARK,
                    font_size=Pt(12), bold=True)
        y += Cm(0.8)

    # Colonne droite — Entraînement
    add_textbox(slide, Cm(17.5), Cm(2.6), Cm(15), Cm(0.6),
                text="ENTRAÎNEMENT", font_color=BLUE_ELEC,
                font_size=Pt(12), bold=True)
    add_rect(slide, Cm(17.5), Cm(3.2), Cm(14), Cm(0.06), fill_color=BLUE_ELEC)

    train_items = [
        ("Modèle base",     "YOLOv8n / YOLOv8s"),
        ("Epochs",          "[XX] epochs"),
        ("Batch size",      "[XX]"),
        ("Image size",      "640"),
        ("Optimizer",       "SGD / Adam"),
        ("Hardware",        "[GPU / CPU]"),
    ]
    y = Cm(3.4)
    for label, val in train_items:
        add_textbox(slide, Cm(17.8), y, Cm(6), Cm(0.7),
                    text=label, font_color=TEXT_MUTED, font_size=Pt(12))
        add_textbox(slide, Cm(24), y, Cm(7), Cm(0.7),
                    text=val, font_color=TEXT_DARK,
                    font_size=Pt(12), bold=True)
        y += Cm(0.8)

    # Métriques en bas — 4 cartes
    metrics = [
        ("[XX%]",  "Precision"),
        ("[XX%]",  "Recall"),
        ("[XX%]",  "mAP@0.5"),
        ("[Xs]",   "Inférence / image"),
    ]
    card_w = Cm(7.5)
    x = Cm(1)
    for val, label in metrics:
        add_stat_card(slide, x, Cm(12.0), card_w, Cm(3.5),
                      value=val, label=label)
        x += card_w + Cm(0.7)

    add_rect(slide, Cm(0), Cm(18.55), SLIDE_W, Cm(0.5), fill_color=NAVY)


def slide_06_detection(prs):
    """Slide 6 — Pipeline de Détection (live)"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, prs, NAVY)
    add_header(slide, "Pipeline de Détection — Flux Complet", slide_num=6)

    # Étapes du pipeline
    steps = [
        ("01", "Capture\nimage",  "Webcam / URL"),
        ("02", "POST API",        "/detect/"),
        ("03", "YOLOv8",          "best.pt"),
        ("04", "Log",             "DetectionLog"),
        ("05", "Alerte",          "Si non-conforme"),
    ]

    box_w  = Cm(5.2)
    box_h  = Cm(2.8)
    y_box  = Cm(5.5)
    x_start = Cm(1.0)
    gap = Cm(1.05)

    for i, (num, title, sub) in enumerate(steps):
        left = x_start + i * (box_w + gap)
        add_flow_step(slide, left, y_box, box_w, box_h,
                      num, title, sub)
        if i < len(steps) - 1:
            arrow_left = left + box_w + Cm(0.15)
            arrow_top  = y_box + box_h / 2 - Cm(0.25)
            add_arrow_right(slide, arrow_left, arrow_top,
                            Cm(0.8), Cm(0.5))

    # Résultat en bas
    add_rounded_rect(slide, Cm(7), Cm(9.5), Cm(8.5), Cm(1.5),
                     fill_color=GREEN_OK, corner_radius=100000)
    add_textbox(slide, Cm(7), Cm(9.7), Cm(8.5), Cm(1),
                text="✓  Conforme — Log enregistré",
                font_color=WHITE, font_size=Pt(15), bold=True,
                align=PP_ALIGN.CENTER)

    add_rounded_rect(slide, Cm(17), Cm(9.5), Cm(10), Cm(1.5),
                     fill_color=RED_KO, corner_radius=100000)
    add_textbox(slide, Cm(17), Cm(9.7), Cm(10), Cm(1),
                text="✗  Non-conforme → Alerte créée automatiquement",
                font_color=WHITE, font_size=Pt(14), bold=True,
                align=PP_ALIGN.CENTER)

    # Commande de démo
    add_rounded_rect(slide, Cm(1), Cm(12.2), Cm(32), Cm(2.0),
                     fill_color=NAVY_CARD, corner_radius=100000)
    add_textbox(slide, Cm(1.5), Cm(12.4), Cm(31), Cm(0.7),
                text="DEMO LIVE :", font_color=ORANGE,
                font_size=Pt(12), bold=True)
    add_textbox(slide, Cm(6), Cm(12.4), Cm(25), Cm(1.2),
                text="POST http://localhost:8000/api/detection/detect/   {file: image.jpg, camera_id: 1}",
                font_color=GREEN_OK, font_size=Pt(12))

    add_rect(slide, Cm(0), Cm(18.55), SLIDE_W, Cm(0.5), fill_color=ORANGE)


def slide_07_plateforme(prs):
    """Slide 7 — Plateforme Web"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, prs, LIGHT_BG)
    add_header(slide, "Plateforme Web — Fonctionnalités Clés", slide_num=7)

    # 6 modules en 2 colonnes × 3 lignes
    modules = [
        ("Dashboard",      "KPIs temps réel · Statistiques",            BLUE_ELEC),
        ("Détection Live", "Webcam · Upload · Résultats YOLO",          ORANGE),
        ("Alertes",        "Cycle complet · Criticité · Historique",     RED_KO),
        ("Règles HSE",     "EPI par zone · Seuils de criticité",         GREEN_OK),
        ("Audits",         "Captures · Notes · Export PDF",              YELLOW),
        ("Administration", "Utilisateurs · Rôles · Permissions",         NAVY_LIGHT),
    ]

    card_w = Cm(15.5)
    card_h = Cm(2.2)
    cols = [Cm(0.8), Cm(17.3)]
    y_positions = [Cm(2.8), Cm(5.3), Cm(7.8)]

    for i, (name, desc, color) in enumerate(modules):
        col_idx = i % 2
        row_idx = i // 2
        left = cols[col_idx]
        top  = y_positions[row_idx]

        add_rounded_rect(slide, left, top, card_w, card_h,
                         fill_color=WHITE,
                         line_color=BORDER, line_width=Pt(1.5),
                         corner_radius=100000)
        # Bande couleur gauche
        add_rounded_rect(slide, left, top, Cm(0.5), card_h,
                         fill_color=color, corner_radius=100000)
        add_textbox(slide, left + Cm(0.8), top + Cm(0.2),
                    Cm(8), Cm(0.7),
                    text=name, font_color=TEXT_DARK,
                    font_size=Pt(14), bold=True)
        add_textbox(slide, left + Cm(0.8), top + Cm(1.0),
                    Cm(14), Cm(0.7),
                    text=desc, font_color=TEXT_MUTED, font_size=Pt(12))

    # Endpoints API en bas
    add_rounded_rect(slide, Cm(0.8), Cm(10.6), Cm(32), Cm(1.8),
                     fill_color=NAVY_CARD, corner_radius=100000)
    add_textbox(slide, Cm(1.3), Cm(10.8), Cm(5), Cm(0.6),
                text="API REST :", font_color=ORANGE,
                font_size=Pt(11), bold=True)
    apis = "/users/  ·  /cameras/  ·  /detection/  ·  /alerts/  ·  /rules/  ·  /audits/"
    add_textbox(slide, Cm(6.5), Cm(10.8), Cm(25), Cm(1.2),
                text=apis, font_color=WHITE, font_size=Pt(12))

    add_rect(slide, Cm(0), Cm(18.55), SLIDE_W, Cm(0.5), fill_color=NAVY)


def slide_08_workflow(prs):
    """Slide 8 — Workflow Métier Central"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, prs, NAVY)
    add_header(slide, "Workflow Métier — De la Détection à la Résolution", slide_num=8)

    # Pipeline horizontal 6 étapes
    steps = [
        ("01", "Capture",     "Image / Frame"),
        ("02", "Détection",   "YOLO → Log"),
        ("03", "Alerte",      "Auto-générée"),
        ("04", "Audit",       "Ouvert si grave"),
        ("05", "Suivi",       "Notes + captures"),
        ("06", "Clôture",     "PDF exporté"),
    ]

    box_w = Cm(4.5)
    box_h = Cm(3.0)
    y_box = Cm(4.5)
    x_start = Cm(0.7)
    gap = Cm(0.8)

    for i, (num, title, sub) in enumerate(steps):
        left = x_start + i * (box_w + gap)
        add_flow_step(slide, left, y_box, box_w, box_h,
                      num, title, sub)
        if i < len(steps) - 1:
            add_arrow_right(slide,
                            left + box_w + Cm(0.1),
                            y_box + box_h / 2 - Cm(0.25),
                            Cm(0.7), Cm(0.5))

    # Statuts alertes en bas
    add_textbox(slide, Cm(1), Cm(9.0), Cm(15), Cm(0.6),
                text="Cycle de vie des alertes :",
                font_color=TEXT_MUTED, font_size=Pt(11))

    statuts = [
        ("NOUVEAU",    ORANGE),
        ("EN COURS",   BLUE_ELEC),
        ("RÉSOLU",     GREEN_OK),
        ("IGNORÉ",     NAVY_LIGHT),
    ]
    x = Cm(1)
    for label, color in statuts:
        add_rounded_rect(slide, x, Cm(9.7), Cm(4.5), Cm(0.9),
                         fill_color=color, corner_radius=80000)
        add_textbox(slide, x, Cm(9.75), Cm(4.5), Cm(0.7),
                    text=label, font_color=WHITE,
                    font_size=Pt(11), bold=True,
                    align=PP_ALIGN.CENTER)
        if label != "IGNORÉ":
            add_arrow_right(slide, x + Cm(4.6), Cm(10.05),
                            Cm(0.5), Cm(0.4))
        x += Cm(5.2)

    # Règle anti-doublon audit
    add_rounded_rect(slide, Cm(1), Cm(11.5), Cm(32), Cm(1.3),
                     fill_color=RGBColor(30, 58, 138), corner_radius=100000)
    add_textbox(slide, Cm(1.5), Cm(11.6), Cm(31), Cm(1),
                text="⚠  Règle métier : une alerte ne peut pas avoir deux audits actifs simultanément",
                font_color=WHITE, font_size=Pt(13))

    add_rect(slide, Cm(0), Cm(18.55), SLIDE_W, Cm(0.5), fill_color=ORANGE)


def slide_09_contribution(prs):
    """Slide 9 — Contribution Personnelle"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, prs, LIGHT_BG)
    add_header(slide, "Ce que J'ai Personnellement Développé", slide_num=9)

    # Titre fort
    add_textbox(slide, Cm(1), Cm(2.6), Cm(32), Cm(0.7),
                text=f"Contributions de {STAGIAIRE} — {NB_COMMITS} commits Git",
                font_color=TEXT_MUTED, font_size=Pt(13))

    contributions = [
        ("Backend API",       GREEN_OK,  [
            "6 apps Django (Users, Cameras, Detection, Alertes, Audits, RegleSHE)",
            "Authentification JWT — cookies HttpOnly sécurisés",
            "Intégration YOLOv8 : pipeline detect → log → alerte",
            "Génération PDF (ReportLab) et export CSV",
        ]),
        ("Frontend React",    BLUE_ELEC, [
            "Dashboard KPIs avec Recharts",
            "Page Détection — webcam + flux temps réel",
            "Pages Alertes, Audits, Règles HSE, Administration",
            "Contexte d'authentification global (AuthContext)",
        ]),
        ("IA & Données",      ORANGE,    [
            "Pipeline complet : dataset → annotation → entraînement YOLO",
            "Script de prétraitement et augmentation de données",
            "Validation du modèle (metrics mAP, Precision, Recall)",
        ]),
        ("Déploiement",       YELLOW,    [
            "Configuration AWS CodeBuild + CodeDeploy (CI/CD)",
            "Nginx + Gunicorn en production sur EC2",
            "Frontend sur Cloudflare CDN avec HTTPS",
        ]),
    ]

    card_w = Cm(15.5)
    card_h = Cm(3.8)
    cols = [Cm(0.8), Cm(17.2)]
    rows = [Cm(3.4), Cm(7.6)]

    for i, (title, color, items) in enumerate(contributions):
        col = i % 2
        row = i // 2
        left = cols[col]
        top  = rows[row]

        add_rounded_rect(slide, left, top, card_w, card_h,
                         fill_color=WHITE,
                         line_color=color, line_width=Pt(2),
                         corner_radius=120000)
        add_rect(slide, left, top, card_w, Cm(0.25),
                 fill_color=color)
        add_textbox(slide, left + Cm(0.4), top + Cm(0.35),
                    Cm(14), Cm(0.6),
                    text=title, font_color=color,
                    font_size=Pt(13), bold=True)
        y_item = top + Cm(1.0)
        for item in items:
            add_textbox(slide, left + Cm(0.6), y_item,
                        Cm(14.5), Cm(0.65),
                        text=f"✓  {item}",
                        font_color=TEXT_DARK, font_size=Pt(11))
            y_item += Cm(0.7)

    add_rect(slide, Cm(0), Cm(18.55), SLIDE_W, Cm(0.5), fill_color=NAVY)


def slide_10_difficultes(prs):
    """Slide 10 — Difficultés & Solutions"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, prs, LIGHT_BG)
    add_header(slide, "Difficultés Rencontrées & Solutions Apportées", slide_num=10)

    challenges = [
        (
            "Qualité et volume des données",
            RED_KO,
            "Manque d'images annotées pour l'entraînement YOLO",
            "Augmentation de données (flip, rotation, bruit) + Roboflow"
        ),
        (
            "Intégration IA ↔ Backend",
            ORANGE,
            "Appel YOLO synchrone = latence sur l'API Django",
            "Optimisation via réduction résolution + mise en cache du modèle"
        ),
        (
            "Auth sécurisée full-stack",
            BLUE_ELEC,
            "Cookies HttpOnly + CORS = complexité de configuration",
            "Custom CookieJWTAuthentication + CORS_ALLOW_CREDENTIALS"
        ),
        (
            "Synchronisation Alerte ↔ Audit",
            GREEN_OK,
            "Doublons d'audits actifs sur une même alerte",
            "Vérification côté backend avant création d'audit"
        ),
    ]

    card_w = Cm(15.5)
    card_h = Cm(3.2)
    cols = [Cm(0.8), Cm(17.2)]
    rows = [Cm(2.8), Cm(6.4)]

    for i, (title, color, problem, solution) in enumerate(challenges):
        col = i % 2
        row = i // 2
        left = cols[col]
        top  = rows[row]

        add_rounded_rect(slide, left, top, card_w, card_h,
                         fill_color=WHITE,
                         line_color=color, line_width=Pt(1.5),
                         corner_radius=120000)
        add_textbox(slide, left + Cm(0.4), top + Cm(0.2),
                    Cm(14.5), Cm(0.6),
                    text=title, font_color=color,
                    font_size=Pt(12), bold=True)
        add_textbox(slide, left + Cm(0.4), top + Cm(0.9),
                    Cm(14.5), Cm(0.75),
                    text=f"🔴  {problem}",
                    font_color=TEXT_DARK, font_size=Pt(11))
        add_textbox(slide, left + Cm(0.4), top + Cm(1.8),
                    Cm(14.5), Cm(0.9),
                    text=f"🟢  {solution}",
                    font_color=GREEN_OK, font_size=Pt(11))

    # Bilan
    add_rounded_rect(slide, Cm(0.8), Cm(10.5), Cm(32), Cm(1.5),
                     fill_color=NAVY_CARD, corner_radius=100000)
    add_textbox(slide, Cm(1.3), Cm(10.7), Cm(31), Cm(1),
                text=("Ces difficultés ont renforcé ma maîtrise de l'architecture full-stack "
                      "et de l'intégration de modèles IA dans un système de production."),
                font_color=WHITE, font_size=Pt(13), italic=True)

    add_rect(slide, Cm(0), Cm(18.55), SLIDE_W, Cm(0.5), fill_color=NAVY)


def slide_11_preuves(prs):
    """Slide 11 — Preuves & Livrables"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, prs, LIGHT_BG)
    add_header(slide, "Preuves de Travail & Livrables", slide_num=11)

    # Git log info
    add_rounded_rect(slide, Cm(0.8), Cm(2.6), Cm(32), Cm(2.2),
                     fill_color=NAVY_CARD, corner_radius=120000)
    add_textbox(slide, Cm(1.3), Cm(2.8), Cm(15), Cm(0.7),
                text="git log --author=\"Souleymane\"",
                font_color=GREEN_OK, font_size=Pt(13), bold=True)
    add_textbox(slide, Cm(1.3), Cm(3.6), Cm(30), Cm(0.7),
                text=(f"{NB_COMMITS} commits · "
                      f"Backend (Django) · Frontend (React) · Modèle YOLO · CI/CD AWS"),
                font_color=WHITE, font_size=Pt(12))

    # Dossier de preuves
    dossier = [
        ("Présentation",  ORANGE,    "Presentation.pptx"),
        ("Code source",   BLUE_ELEC, "Dépôt Git complet"),
        ("Captures",      GREEN_OK,  "Screenshots fonctionnalités"),
        ("Vidéo démo",    YELLOW,    "Démo enregistrée 5–10 min"),
        ("Rapport",       NAVY_LIGHT,"Documentation technique"),
        ("Dataset sample",RED_KO,    "Exemples d'images annotées"),
    ]

    card_w = Cm(9.8)
    card_h = Cm(2.0)
    cols   = [Cm(0.8), Cm(11.4), Cm(22.0)]
    rows   = [Cm(5.3), Cm(7.6)]

    for i, (name, color, desc) in enumerate(dossier):
        col = i % 3
        row = i // 3
        left = cols[col]
        top  = rows[row]

        add_rounded_rect(slide, left, top, card_w, card_h,
                         fill_color=WHITE,
                         line_color=BORDER, line_width=Pt(1.2),
                         corner_radius=100000)
        add_rect(slide, left, top, Cm(0.4), card_h, fill_color=color)
        add_textbox(slide, left + Cm(0.6), top + Cm(0.15),
                    Cm(8.5), Cm(0.65),
                    text=name, font_color=color,
                    font_size=Pt(12), bold=True)
        add_textbox(slide, left + Cm(0.6), top + Cm(0.9),
                    Cm(8.5), Cm(0.6),
                    text=desc, font_color=TEXT_MUTED, font_size=Pt(11))

    # Structure dossier
    add_rounded_rect(slide, Cm(0.8), Cm(10.2), Cm(32), Cm(2.5),
                     fill_color=NAVY_CARD, corner_radius=100000)
    add_textbox(slide, Cm(1.3), Cm(10.4), Cm(10), Cm(0.6),
                text="Validation_Stage/", font_color=ORANGE,
                font_size=Pt(12), bold=True)
    content = ("Presentation.pptx  ·  Rapport.pdf  ·  Code_Source/  ·  "
               "Captures/  ·  Videos_Demo/  ·  Git_Logs.pdf")
    add_textbox(slide, Cm(1.3), Cm(11.1), Cm(31), Cm(1),
                text=content, font_color=WHITE, font_size=Pt(11))

    add_rect(slide, Cm(0), Cm(18.55), SLIDE_W, Cm(0.5), fill_color=NAVY)


def slide_12_conclusion(prs):
    """Slide 12 — Conclusion & Perspectives"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, prs, NAVY)

    # Barre orange en haut
    add_rect(slide, Cm(0), Cm(0), SLIDE_W, Cm(0.8), fill_color=ORANGE)
    add_textbox(slide, Cm(0), Cm(0.05), SLIDE_W, Cm(0.7),
                text="CONCLUSION", font_color=WHITE,
                font_size=Pt(12), bold=True, align=PP_ALIGN.CENTER)

    add_textbox(slide, Cm(2), Cm(1.2), Cm(30), Cm(1.4),
                text="Ce qui a été livré",
                font_color=ORANGE, font_size=Pt(26), bold=True,
                align=PP_ALIGN.CENTER)

    # 3 points forts
    points = [
        ("Plateforme IA opérationnelle",
         "Détection YOLOv8 intégrée dans un backend Django en production"),
        ("Workflow métier complet",
         "De la détection brute jusqu'à l'audit clôturé avec PDF"),
        ("Infrastructure cloud robuste",
         "AWS EC2 + CodeDeploy + Cloudflare CDN — déploiement CI/CD automatisé"),
    ]

    y = Cm(3.0)
    for i, (title, desc) in enumerate(points):
        add_rounded_rect(slide, Cm(1.5), y, Cm(31), Cm(1.8),
                         fill_color=NAVY_CARD, corner_radius=120000)
        add_rect(slide, Cm(1.5), y, Cm(0.4), Cm(1.8),
                 fill_color=ORANGE)
        add_textbox(slide, Cm(2.2), y + Cm(0.15),
                    Cm(29), Cm(0.65),
                    text=title, font_color=ORANGE,
                    font_size=Pt(13), bold=True)
        add_textbox(slide, Cm(2.2), y + Cm(0.85),
                    Cm(29), Cm(0.65),
                    text=desc, font_color=WHITE, font_size=Pt(12))
        y += Cm(2.1)

    # Séparateur
    add_rect(slide, Cm(5), y + Cm(0.3), Cm(24), Cm(0.06),
             fill_color=ORANGE)

    # Perspectives
    persp = [
        "Flux vidéo RTSP / HLS en streaming",
        "Application mobile technicien terrain",
        "Entraînement continu du modèle (MLOps)",
        "Notifications temps réel (Slack, email)",
    ]
    y_p = y + Cm(0.6)
    for p in persp:
        add_textbox(slide, Cm(5), y_p, Cm(24), Cm(0.65),
                    text=f"→  {p}", font_color=WHITE, font_size=Pt(13))
        y_p += Cm(0.7)

    # Call to action
    add_rounded_rect(slide, Cm(10), Cm(15.5), Cm(14), Cm(1.8),
                     fill_color=ORANGE, corner_radius=150000)
    add_textbox(slide, Cm(10), Cm(15.8), Cm(14), Cm(1.2),
                text="Questions ?",
                font_color=WHITE, font_size=Pt(24), bold=True,
                align=PP_ALIGN.CENTER)

    add_textbox(slide, Cm(1), Cm(17.8), Cm(32), Cm(0.6),
                text=f"{STAGIAIRE}  —  {ENTREPRISE}  —  {PERIODE}",
                font_color=TEXT_MUTED, font_size=Pt(10),
                align=PP_ALIGN.CENTER)

    add_rect(slide, Cm(0), Cm(18.55), SLIDE_W, Cm(0.5), fill_color=ORANGE)


# ── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    prs = Presentation()
    prs.slide_width  = SLIDE_W
    prs.slide_height = SLIDE_H

    # Création des 12 slides dans l'ordre
    slide_01_titre(prs)
    slide_02_contexte(prs)
    slide_03_architecture(prs)
    slide_04_stack(prs)
    slide_05_yolo(prs)
    slide_06_detection(prs)
    slide_07_plateforme(prs)
    slide_08_workflow(prs)
    slide_09_contribution(prs)
    slide_10_difficultes(prs)
    slide_11_preuves(prs)
    slide_12_conclusion(prs)

    output = "validation_stage_EPI_Detection.pptx"
    prs.save(output)
    import sys
    out = sys.stdout
    print(f"[OK] Fichier genere : {output}", file=out)
    print(f"     {len(prs.slides)} slides creees", file=out)
    print(file=out)
    print("  Placeholders a remplacer dans le script :", file=out)
    print("    ENTREPRISE, DUREE_STAGE, PERIODE, ENCADRANT", file=out)
    print("    NB_COMMITS, metriques YOLO [XX%]", file=out)


if __name__ == "__main__":
    main()


# === NOTES DE PRÉSENTATION ===
#
# TIMING (20–25 min + questions) :
#  Slide 01 Titre           :  0:30 — Accueil et présentation rapide
#  Slide 02 Contexte        :  1:30 — Poser le problème métier clairement
#  Slide 03 Architecture    :  2:00 — Vue d'ensemble, montrer la maturité
#  Slide 04 Stack           :  1:00 — Justifier chaque choix technologique
#  Slide 05 YOLO/Dataset    :  2:30 — Cœur de la partie IA
#  Slide 06 Détection Live  :  2:00 — MONTRER la démo ici (commande POST)
#  Slide 07 Plateforme Web  :  2:00 — Screenshots ou démo navigateur
#  Slide 08 Workflow        :  2:00 — Montrer la logique métier complète
#  Slide 09 Contribution    :  2:00 — Crucial — prouver votre travail
#  Slide 10 Difficultés     :  1:30 — Honnêteté = crédibilité
#  Slide 11 Preuves         :  1:00 — Git log, dossier de preuves
#  Slide 12 Conclusion      :  1:00 — Synthèse + questions
#
# QUESTIONS PROBABLES :
#  Q: "Pourquoi YOLOv8 ?"
#     → Meilleur compromis vitesse/précision pour la détection temps réel.
#        Supporte le fine-tuning sur dataset custom facilement.
#  Q: "Pourquoi Django et pas FastAPI ?"
#     → Richesse de l'écosystème (ORM, permissions, admin). YOLO appelé
#        en synchrone, les perf Django DRF sont suffisantes pour le besoin.
#  Q: "Comment avez-vous annoté les données ?"
#     → LabelImg ou Roboflow pour annoter en format YOLO (.txt bounding boxes).
#  Q: "Quelle est la précision du modèle ?"
#     → Citer vos métriques réelles. Si modèle insuffisant : nommer les pistes
#        d'amélioration (plus de données, augmentation, modèle plus grand).
#  Q: "Comment gère-t-on les faux positifs ?"
#     → Statut "ignoré" dans les alertes. Prévu : boucle de feedback
#        pour réentraînement.
#  Q: "Le système est-il déployé ?"
#     → Backend AWS EC2, frontend Cloudflare. Montrer l'URL live si disponible.
