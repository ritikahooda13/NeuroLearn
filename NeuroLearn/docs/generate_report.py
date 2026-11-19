#!/usr/bin/env python3
"""
NeuroLearn - Professional B.Tech Major Project Report Generator
Generates a ~30 page formal project report PDF.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.colors import HexColor, black, white, grey
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    ListFlowable, ListItem, KeepTogether, HRFlowable, Image
)
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus.tableofcontents import TableOfContents
from functools import partial
import os

OUTPUT_PATH = "/home/workdir/artifacts/NeuroLearn/docs/NeuroLearn_Project_Report.pdf"

# Colors
PRIMARY = HexColor("#1a237e")      # Deep indigo
SECONDARY = HexColor("#283593")
ACCENT = HexColor("#3949ab")
LIGHT_BG = HexColor("#e8eaf6")
DARK_TEXT = HexColor("#212121")
MED_TEXT = HexColor("#424242")

PAGE_WIDTH, PAGE_HEIGHT = A4
LEFT_MARGIN = 1.0 * inch
RIGHT_MARGIN = 1.0 * inch
TOP_MARGIN = 0.9 * inch
BOTTOM_MARGIN = 0.9 * inch


def create_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='CoverTitle',
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=28,
        alignment=TA_CENTER,
        textColor=PRIMARY,
        spaceAfter=12
    ))
    styles.add(ParagraphStyle(
        name='CoverSubtitle',
        fontName='Helvetica',
        fontSize=14,
        leading=18,
        alignment=TA_CENTER,
        textColor=MED_TEXT,
        spaceAfter=8
    ))
    styles.add(ParagraphStyle(
        name='ChapterTitle',
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=PRIMARY,
        spaceBefore=12,
        spaceAfter=14,
        borderPadding=4
    ))
    styles.add(ParagraphStyle(
        name='SectionHeading',
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=SECONDARY,
        spaceBefore=14,
        spaceAfter=8
    ))
    styles.add(ParagraphStyle(
        name='SubSection',
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=ACCENT,
        spaceBefore=10,
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name='BodyTextJust',
        fontName='Helvetica',
        fontSize=10.5,
        leading=15,
        alignment=TA_JUSTIFY,
        textColor=DARK_TEXT,
        spaceAfter=8,
        firstLineIndent=0
    ))
    styles.add(ParagraphStyle(
        name='BodyTextIndent',
        fontName='Helvetica',
        fontSize=10.5,
        leading=15,
        alignment=TA_JUSTIFY,
        textColor=DARK_TEXT,
        spaceAfter=8,
        firstLineIndent=18
    ))
    styles.add(ParagraphStyle(
        name='BulletText',
        fontName='Helvetica',
        fontSize=10.5,
        leading=14.5,
        textColor=DARK_TEXT,
        leftIndent=15,
        spaceAfter=3
    ))
    styles.add(ParagraphStyle(
        name='TableHeader',
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=white,
        alignment=TA_CENTER
    ))
    styles.add(ParagraphStyle(
        name='TableCell',
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=DARK_TEXT
    ))
    styles.add(ParagraphStyle(
        name='Caption',
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=12,
        textColor=MED_TEXT,
        alignment=TA_CENTER,
        spaceBefore=4,
        spaceAfter=12
    ))
    styles.add(ParagraphStyle(
        name='CenterText',
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        alignment=TA_CENTER,
        textColor=DARK_TEXT
    ))
    styles.add(ParagraphStyle(
        name='FooterStyle',
        fontName='Helvetica',
        fontSize=8,
        textColor=grey,
        alignment=TA_CENTER
    ))
    styles.add(ParagraphStyle(
        name='CodeStyle',
        fontName='Courier',
        fontSize=8.5,
        leading=11,
        textColor=DARK_TEXT,
        backColor=HexColor("#f5f5f5"),
        leftIndent=10,
        rightIndent=10,
        spaceBefore=6,
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name='AbstractBody',
        fontName='Helvetica',
        fontSize=10.5,
        leading=15,
        alignment=TA_JUSTIFY,
        textColor=DARK_TEXT,
        spaceAfter=8
    ))
    styles.add(ParagraphStyle(
        name='DeclText',
        fontName='Helvetica',
        fontSize=11,
        leading=16,
        alignment=TA_JUSTIFY,
        textColor=DARK_TEXT,
        spaceAfter=10
    ))
    return styles


def add_page_number(canvas, doc):
    canvas.saveState()
    page_num = canvas.getPageNumber()
    if page_num > 1:  # Skip cover
        # Clean professional page number only (no watermark text)
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(HexColor("#555555"))
        canvas.drawCentredString(PAGE_WIDTH / 2, 0.45 * inch, str(page_num))
        # Subtle top line
        canvas.setStrokeColor(PRIMARY)
        canvas.setLineWidth(0.6)
        canvas.line(LEFT_MARGIN, PAGE_HEIGHT - 0.55 * inch, PAGE_WIDTH - RIGHT_MARGIN, PAGE_HEIGHT - 0.55 * inch)
    canvas.restoreState()


def hr_line():
    return HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=4, spaceAfter=12)


def make_table(headers, rows, col_widths):
    styles = create_styles()
    data = [[Paragraph(h, styles['TableHeader']) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c), styles['TableCell']) for c in row])
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), white),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, LIGHT_BG]),
        ('GRID', (0, 0), (-1, -1), 0.4, HexColor("#bdbdbd")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
    ]))
    return t


def build_report():
    styles = create_styles()
    story = []

    # ============================================================
    # COVER PAGE
    # ============================================================
    story.append(Spacer(1, 0.6 * inch))
    story.append(Paragraph("A PROJECT REPORT", styles['CoverSubtitle']))
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph("ON", styles['CoverSubtitle']))
    story.append(Spacer(1, 0.25 * inch))
    story.append(Paragraph("NEUROLEARN", styles['CoverTitle']))
    story.append(Paragraph("Adaptive Multimodal Intelligent Tutoring System<br/>using Deep Learning and Generative AI", styles['CoverSubtitle']))
    story.append(Spacer(1, 0.15 * inch))
    story.append(hr_line())
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(
        "Submitted in partial fulfillment of the requirements<br/>for the award of the degree of",
        styles['CenterText']
    ))
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph("<b>BACHELOR OF TECHNOLOGY</b>", styles['CenterText']))
    story.append(Paragraph("in", styles['CenterText']))
    story.append(Paragraph("<b>Computer Science &amp; Engineering<br/>(Artificial Intelligence &amp; Machine Learning)</b>", styles['CenterText']))
    story.append(Spacer(1, 0.4 * inch))
    story.append(Paragraph("Submitted by", styles['CenterText']))
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph("<b>Ritika</b>", styles['CenterText']))
    story.append(Paragraph("Roll No: 2311078", styles['CenterText']))
    story.append(Spacer(1, 0.35 * inch))
    story.append(Paragraph("Under the Guidance of", styles['CenterText']))
    story.append(Spacer(1, 0.08 * inch))
    story.append(Paragraph("<b>Dr. Munisha</b>", styles['CenterText']))
    story.append(Paragraph("Project Guide", styles['CenterText']))
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph("<b>DEPARTMENT OF COMPUTER SCIENCE &amp; ENGINEERING</b>", styles['CenterText']))
    story.append(Paragraph("University Institute of Engineering &amp; Technology (UIET)", styles['CenterText']))
    story.append(Paragraph("Maharshi Dayanand University (MDU), Rohtak", styles['CenterText']))
    story.append(Paragraph("Academic Year 2025 – 2026", styles['CenterText']))
    story.append(PageBreak())

    # ============================================================
    # CERTIFICATE
    # ============================================================
    story.append(Paragraph("CERTIFICATE", styles['ChapterTitle']))
    story.append(hr_line())
    story.append(Paragraph(
        "This is to certify that the project entitled <b>“NeuroLearn – Adaptive Multimodal Intelligent Tutoring System using Deep Learning and Generative AI”</b> is a bona fide record of the work done by <b>Ritika</b> (Roll No: 2311078) in partial fulfillment of the requirements for the award of the degree of Bachelor of Technology in Computer Science &amp; Engineering (Artificial Intelligence &amp; Machine Learning) during the academic year 2025–2026.",
        styles['DeclText']
    ))
    story.append(Spacer(1, 0.25 * inch))
    story.append(Paragraph(
        "The project has been carried out under my supervision and guidance. The work embodied in this report has not been submitted earlier for the award of any degree or diploma.",
        styles['DeclText']
    ))
    story.append(Spacer(1, 0.8 * inch))
    story.append(Paragraph("<b>____________________________</b>", styles['CenterText']))
    story.append(Paragraph("<b>Dr. Munisha</b>", styles['CenterText']))
    story.append(Paragraph("Project Guide", styles['CenterText']))
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph("<b>____________________________</b>", styles['CenterText']))
    story.append(Paragraph("<b>Head of the Department</b>", styles['CenterText']))
    story.append(Paragraph("Department of Computer Science &amp; Engineering", styles['CenterText']))
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph("<b>____________________________</b>", styles['CenterText']))
    story.append(Paragraph("<b>External Examiner</b>", styles['CenterText']))
    story.append(PageBreak())

    # ============================================================
    # DECLARATION
    # ============================================================
    story.append(Paragraph("DECLARATION", styles['ChapterTitle']))
    story.append(hr_line())
    story.append(Paragraph(
        "I hereby declare that the project work entitled <b>“NeuroLearn – Adaptive Multimodal Intelligent Tutoring System using Deep Learning and Generative AI”</b> submitted to the Department of Computer Science &amp; Engineering, University Institute of Engineering &amp; Technology (UIET), Maharshi Dayanand University (MDU), Rohtak, is a record of original work done by me under the guidance of <b>Dr. Munisha</b>.",
        styles['DeclText']
    ))
    story.append(Paragraph(
        "I further declare that this project work has not been submitted to any other University or Institution for the award of any degree or diploma. All sources of information have been specifically acknowledged by means of references.",
        styles['DeclText']
    ))
    story.append(Spacer(1, 0.8 * inch))
    story.append(Paragraph("<b>Place:</b> Rohtak", styles['BodyTextJust']))
    story.append(Paragraph("<b>Date:</b> ____________________", styles['BodyTextJust']))
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph("<b>____________________________</b>", styles['CenterText']))
    story.append(Paragraph("<b>Ritika</b>", styles['CenterText']))
    story.append(Paragraph("Roll No: 2311078", styles['CenterText']))
    story.append(PageBreak())

    # ============================================================
    # ACKNOWLEDGEMENT
    # ============================================================
    story.append(Paragraph("ACKNOWLEDGEMENT", styles['ChapterTitle']))
    story.append(hr_line())
    story.append(Paragraph(
        "First of all, I would like to thank my project guide <b>Dr. Munisha</b> for her constant guidance and support. Whenever I faced difficulties during the development of this project, her suggestions helped me a lot. I am truly grateful for her time and patience.",
        styles['BodyTextJust']
    ))
    story.append(Paragraph(
        "I also want to thank the Head of the Department and all faculty members of the CSE Department at UIET, MDU for providing the necessary facilities and a supportive academic environment.",
        styles['BodyTextJust']
    ))
    story.append(Paragraph(
        "I would also like to acknowledge the open-source community. Libraries and tools like Hugging Face, PyTorch and Streamlit made it possible for me to build this system on my own. Without these resources, completing the project would have been much harder.",
        styles['BodyTextJust']
    ))
    story.append(Paragraph(
        "Finally, I thank my family and friends for their support and understanding during the many late nights spent on coding and testing.",
        styles['BodyTextJust']
    ))
    story.append(Spacer(1, 0.4 * inch))
    story.append(Paragraph("<b>Ritika</b>", styles['BodyTextJust']))
    story.append(Paragraph("Roll No: 2311078", styles['BodyTextJust']))
    story.append(PageBreak())

    # ============================================================
    # ABSTRACT
    # ============================================================
    story.append(Paragraph("ABSTRACT", styles['ChapterTitle']))
    story.append(hr_line())
    story.append(Paragraph(
        "Most of the AI tutors available today give the same type of response to every student. They do not understand whether the student is confused, frustrated, or actually interested in the topic. Because of this, the learning experience often feels incomplete.",
        styles['AbstractBody']
    ))
    story.append(Paragraph(
        "In this project, I have tried to solve this problem by building <b>NeuroLearn</b> – an adaptive tutoring system that looks at the student’s facial expressions through the webcam, keeps track of how much the student knows about different topics, and then changes its way of teaching accordingly. It uses a Vision Transformer for emotion detection, a knowledge tracing model to maintain the student’s progress, and a large language model that adjusts its explanations based on both emotion and knowledge level. Students can also upload their own notes or PDFs so that the answers stay relevant to their course material.",
        styles['AbstractBody']
    ))
    story.append(Paragraph(
        "The complete system is built using Python, Streamlit, PyTorch and Hugging Face tools. From the testing I did, the tutor clearly changes its tone and depth when the student’s emotional state changes. Overall, this project shows that it is possible to combine computer vision, knowledge tracing and generative AI to create a more human-like learning experience.",
        styles['AbstractBody']
    ))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(
        "<b>Keywords:</b> Intelligent Tutoring System, Affective Computing, Knowledge Tracing, Vision Transformer, Large Language Models, Retrieval-Augmented Generation, Adaptive Learning, Educational Technology",
        styles['BodyTextJust']
    ))
    story.append(PageBreak())

    # ============================================================
    # TABLE OF CONTENTS (manual for control)
    # ============================================================
    story.append(Paragraph("TABLE OF CONTENTS", styles['ChapterTitle']))
    story.append(hr_line())

    toc_items = [
        ("Certificate", "ii"),
        ("Declaration", "iii"),
        ("Acknowledgement", "iv"),
        ("Abstract", "v"),
        ("Table of Contents", "vi"),
        ("List of Figures", "vii"),
        ("List of Tables", "vii"),
        ("Chapter 1: Introduction", "1"),
        ("    1.1 Background", "1"),
        ("    1.2 Motivation", "2"),
        ("    1.3 Problem Statement", "3"),
        ("    1.4 Objectives", "3"),
        ("    1.5 Scope of the Project", "4"),
        ("    1.6 Organization of the Report", "4"),
        ("Chapter 2: Literature Survey", "5"),
        ("    2.1 Intelligent Tutoring Systems", "5"),
        ("    2.2 Knowledge Tracing", "6"),
        ("    2.3 Affective Computing in Education", "7"),
        ("    2.4 Large Language Models for Tutoring", "8"),
        ("    2.5 Retrieval-Augmented Generation", "9"),
        ("    2.6 Research Gaps", "9"),
        ("Chapter 3: System Analysis &amp; Requirements", "10"),
        ("    3.1 Feasibility Study", "10"),
        ("    3.2 Functional Requirements", "11"),
        ("    3.3 Non-Functional Requirements", "12"),
        ("    3.4 Hardware &amp; Software Requirements", "12"),
        ("Chapter 4: System Design", "13"),
        ("    4.1 System Architecture", "13"),
        ("    4.2 Module Design", "15"),
        ("    4.3 Data Flow", "17"),
        ("    4.4 Database / Persistence Design", "18"),
        ("Chapter 5: Implementation", "19"),
        ("    5.1 Technology Stack", "19"),
        ("    5.2 Emotion Detection Module", "20"),
        ("    5.3 Knowledge Tracing Module", "21"),
        ("    5.4 Adaptive Tutor Module", "22"),
        ("    5.5 RAG Module", "23"),
        ("    5.6 User Interface", "24"),
        ("Chapter 6: Testing, Results &amp; Discussion", "25"),
        ("    6.1 Testing Strategy", "25"),
        ("    6.2 Results", "26"),
        ("    6.3 Discussion", "27"),
        ("Chapter 7: Conclusion &amp; Future Work", "28"),
        ("References", "29"),
        ("Appendix A: Sample Code Snippets", "30"),
        ("Appendix B: Screenshots &amp; Demo Flow", "31"),
    ]
    for item, page in toc_items:
        story.append(Paragraph(f"{item} {'.' * (70 - len(item))} {page}", styles['BodyTextJust']))
    story.append(PageBreak())

    # ============================================================
    # LIST OF FIGURES & TABLES
    # ============================================================
    story.append(Paragraph("LIST OF FIGURES", styles['ChapterTitle']))
    story.append(hr_line())
    figs = [
        "Figure 1.1  High-level concept of Adaptive Tutoring",
        "Figure 4.1  Overall System Architecture of NeuroLearn",
        "Figure 4.2  Emotion Detection Pipeline",
        "Figure 4.3  Knowledge Tracing Update Cycle",
        "Figure 4.4  Adaptive Prompt Construction Flow",
        "Figure 5.1  Streamlit Application Layout",
        "Figure 6.1  Sample Emotion Detection Output",
        "Figure 6.2  Mastery Progress Visualization",
    ]
    for f in figs:
        story.append(Paragraph(f, styles['BodyTextJust']))
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("LIST OF TABLES", styles['ChapterTitle']))
    story.append(hr_line())
    tables = [
        "Table 2.1  Comparison of Knowledge Tracing Approaches",
        "Table 3.1  Functional Requirements Summary",
        "Table 3.2  Software Requirements",
        "Table 5.1  Technology Stack Overview",
        "Table 5.2  Emotion to Educational State Mapping",
        "Table 6.1  Qualitative Evaluation of Adaptive Responses",
    ]
    for t in tables:
        story.append(Paragraph(t, styles['BodyTextJust']))
    story.append(PageBreak())

    # ============================================================
    # CHAPTER 1: INTRODUCTION
    # ============================================================
    story.append(Paragraph("CHAPTER 1", styles['CoverSubtitle']))
    story.append(Paragraph("INTRODUCTION", styles['ChapterTitle']))
    story.append(hr_line())

    story.append(Paragraph("1.1 Background", styles['SectionHeading']))
    story.append(Paragraph(
        "Education is undergoing a profound transformation driven by artificial intelligence. The COVID-19 pandemic accelerated the adoption of online and hybrid learning, exposing both the potential and the limitations of digital education platforms. While content has become widely accessible, personalization remains elusive. A single recorded lecture or a static chatbot cannot adapt to the vastly different paces, prior knowledge, and emotional states of individual learners.",
        styles['BodyTextJust']
    ))
    story.append(Paragraph(
        "Intelligent Tutoring Systems (ITS) were conceived precisely to address this challenge. Classic ITS research, dating back to the 1970s and 1980s (e.g., SCHOLAR, WHY, GUIDON), demonstrated that one-on-one human tutoring produces significantly higher learning gains than conventional classroom instruction (Bloom’s 2-sigma problem). The goal of ITS research has always been to approximate the effectiveness of a skilled human tutor through software.",
        styles['BodyTextJust']
    ))
    story.append(Paragraph(
        "Recent advances in deep learning — particularly Vision Transformers for computer vision and Large Language Models for natural language generation — have created an unprecedented opportunity to build ITS that are both perceptually aware and linguistically sophisticated. NeuroLearn sits at the intersection of these advances.",
        styles['BodyTextJust']
    ))

    story.append(Paragraph("1.2 Motivation", styles['SectionHeading']))
    story.append(Paragraph(
        "While working on this project, I noticed that most AI tutors available today have some clear problems:",
        styles['BodyTextJust']
    ))
    story.append(Paragraph("• They do not understand the student’s emotions. If a student is confused or frustrated, the tutor still continues in the same way.", styles['BulletText']))
    story.append(Paragraph("• They usually forget what the student has already learned. Every new session feels like starting from zero.", styles['BulletText']))
    story.append(Paragraph("• Sometimes they give answers that are not related to the actual course material the student is studying.", styles['BulletText']))
    story.append(Paragraph(
        "These issues motivated me to build NeuroLearn. I wanted to create a system that can look at the student’s expressions, remember what the student knows, and then teach accordingly. I also wanted the answers to stay close to the student’s own notes or textbooks.",
        styles['BodyTextJust']
    ))
    story.append(Paragraph(
        "Another reason was that many powerful open-source tools are now available. Because of this, even a single student can try to build something meaningful instead of just making a basic chatbot.",
        styles['BodyTextJust']
    ))
    story.append(Paragraph(
        "In colleges like ours, class sizes are large and personal attention is limited. I felt that an adaptive system like this could help students practice and clear doubts on their own time.",
        styles['BodyTextJust']
    ))

    story.append(Paragraph("1.3 Problem Statement", styles['SectionHeading']))
    story.append(Paragraph(
        "Design and develop an end-to-end Adaptive Multimodal Intelligent Tutoring System that (a) estimates the learner’s emotional/cognitive state from real-time facial imagery, (b) maintains a dynamic model of the learner’s knowledge across multiple concepts, (c) generates pedagogically appropriate responses conditioned on both emotion and knowledge state, (d) optionally grounds answers in user-provided course documents via Retrieval-Augmented Generation, and (e) presents the interaction through an accessible multimodal interface.",
        styles['BodyTextJust']
    ))

    story.append(Paragraph("1.4 Objectives", styles['SectionHeading']))
    story.append(Paragraph("The primary objectives of this project are:", styles['BodyTextJust']))
    story.append(Paragraph("1. To implement real-time facial emotion recognition using a fine-tuned Vision Transformer and map detected emotions to educationally meaningful states.", styles['BulletText']))
    story.append(Paragraph("2. To design and implement a hybrid Knowledge Tracing module capable of tracking concept-level mastery with temporal persistence.", styles['BulletText']))
    story.append(Paragraph("3. To develop an adaptive LLM-based tutor whose tone, depth, scaffolding level, and content difficulty are conditioned on the student’s current emotional and knowledge state.", styles['BulletText']))
    story.append(Paragraph("4. To integrate a lightweight Retrieval-Augmented Generation pipeline supporting PDF and text course materials.", styles['BulletText']))
    story.append(Paragraph("5. To provide neural text-to-speech output and a clean, interactive web-based dashboard.", styles['BulletText']))
    story.append(Paragraph("6. To deliver a complete, modular, and extensible system suitable for demonstration, further research, and potential real-world pilot use.", styles['BulletText']))

    story.append(Paragraph("1.5 Scope of the Project", styles['SectionHeading']))
    story.append(Paragraph(
        "NeuroLearn focuses on one-on-one tutoring in Computer Science and Artificial Intelligence / Machine Learning topics, although the architecture is domain-agnostic. The system is designed for individual learners rather than multi-student classrooms. Evaluation is primarily qualitative and interaction-based; large-scale controlled learning-gain studies are left as future work. The system runs on standard consumer hardware (CPU is sufficient for the demo; GPU accelerates emotion model inference).",
        styles['BodyTextJust']
    ))

    story.append(Paragraph("1.6 Organization of the Report", styles['SectionHeading']))
    story.append(Paragraph(
        "Chapter 2 reviews relevant literature. Chapter 3 presents system analysis and requirements. Chapter 4 details the system design and architecture. Chapter 5 describes the implementation of each module. Chapter 6 discusses testing and results. Chapter 7 concludes the report and outlines future directions. References and appendices follow.",
        styles['BodyTextJust']
    ))
    story.append(PageBreak())

    # ============================================================
    # CHAPTER 2: LITERATURE SURVEY
    # ============================================================
    story.append(Paragraph("CHAPTER 2", styles['CoverSubtitle']))
    story.append(Paragraph("LITERATURE SURVEY", styles['ChapterTitle']))
    story.append(hr_line())

    story.append(Paragraph("2.1 Intelligent Tutoring Systems", styles['SectionHeading']))
    story.append(Paragraph(
        "Intelligent Tutoring Systems aim to provide the benefits of one-on-one human tutoring through software. Early systems such as SCHOLAR (Carbonell, 1970) and GUIDON (Clancey, 1980s) established the classic four-component architecture: domain model, student model, tutoring model, and user interface. Later systems incorporated Bayesian networks, constraint-based modeling, and model-tracing approaches. Despite decades of research, widespread deployment has been limited by authoring cost and limited natural language capability. The advent of LLMs has dramatically lowered the barrier to generating fluent instructional dialogue.",
        styles['BodyTextJust']
    ))

    story.append(Paragraph("2.2 Knowledge Tracing", styles['SectionHeading']))
    story.append(Paragraph(
        "Knowledge Tracing (KT) is the task of modeling a student’s evolving knowledge state from a sequence of interactions. The foundational Bayesian Knowledge Tracing (BKT) model (Corbett &amp; Anderson, 1995) treats each skill as a binary latent variable and updates P(know) using guess and slip parameters. Deep Knowledge Tracing (DKT) (Piech et al., 2015) replaced the hand-crafted BKT with an RNN, achieving substantial gains. Subsequent models such as DKVMN, SAKT, SAINT, and AKT introduced memory networks and Transformer architectures for better long-range dependency modeling and interpretability.",
        styles['BodyTextJust']
    ))
    story.append(Paragraph(
        "For a solo final-year project, a full Transformer KT model trained on large interaction logs is often impractical. NeuroLearn therefore adopts a hybrid approach: classic BKT equations enhanced with difficulty-aware learning rates and persistent concept-level storage, providing a strong, interpretable baseline that can later be upgraded.",
        styles['BodyTextJust']
    ))

    # Comparison table
    story.append(Paragraph("Table 2.1: Comparison of Knowledge Tracing Approaches", styles['Caption']))
    kt_table = make_table(
        ["Approach", "Core Idea", "Strengths", "Limitations"],
        [
            ["BKT (1995)", "Binary latent skill + Bayes update", "Interpretable, low data need", "Assumes single skill, no deep sequence modeling"],
            ["DKT (2015)", "RNN over interaction sequence", "Captures temporal patterns", "Black-box, needs large data"],
            ["SAINT / AKT", "Transformer + attention", "State-of-the-art accuracy", "High compute & data requirements"],
            ["NeuroLearn Hybrid", "BKT + difficulty modulation + persistence", "Practical, interpretable, extensible", "Less powerful than full Transformer KT"],
        ],
        [1.3*inch, 1.8*inch, 1.6*inch, 1.8*inch]
    )
    story.append(kt_table)
    story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph("2.3 Affective Computing in Education", styles['SectionHeading']))
    story.append(Paragraph(
        "Affective Computing (Picard, 1997) studies systems that can recognize, interpret, and respond to human emotions. In education, research by D’Mello, Graesser, and others has shown that emotions such as confusion, frustration, boredom, and engagement strongly influence learning outcomes. Systems that detect and respond to these states can provide timely scaffolding or motivational support. Modern approaches use facial expression recognition (CNNs, Vision Transformers), voice prosody, and physiological signals. NeuroLearn focuses on vision-based detection for practicality and non-intrusiveness.",
        styles['BodyTextJust']
    ))

    story.append(Paragraph("2.4 Large Language Models for Tutoring", styles['SectionHeading']))
    story.append(Paragraph(
        "LLMs such as GPT-4, Llama-3, and Claude have demonstrated remarkable ability to explain concepts, generate practice questions, and hold multi-turn dialogues. Educational applications include Khanmigo, Duolingo Max, and numerous research prototypes. However, most deployments use relatively static system prompts. Conditioning the LLM on real-time affect and a structured knowledge model remains an active research frontier. NeuroLearn contributes a concrete, working design for such conditioning.",
        styles['BodyTextJust']
    ))

    story.append(Paragraph("2.5 Retrieval-Augmented Generation", styles['SectionHeading']))
    story.append(Paragraph(
        "RAG (Lewis et al., 2020) mitigates hallucination by retrieving relevant passages from an external corpus and providing them as context to the LLM. In education, RAG enables answers that are faithful to a specific textbook or lecture notes. NeuroLearn implements a lightweight RAG pipeline using MiniLM embeddings and cosine similarity, sufficient for individual course material collections.",
        styles['BodyTextJust']
    ))

    story.append(Paragraph("2.6 Research Gaps", styles['SectionHeading']))
    story.append(Paragraph(
        "While individual components (emotion recognition, KT, LLM tutoring, RAG) are well-studied, few open systems tightly integrate all of them into a single real-time adaptive loop with an accessible interface. NeuroLearn addresses this integration gap and provides a modular foundation for future research.",
        styles['BodyTextJust']
    ))
    story.append(Paragraph(
        "Additional gaps observed in the literature include: (a) limited public availability of complete, runnable multimodal ITS codebases that a student or small lab can actually deploy and extend; (b) insufficient attention to graceful degradation when high-end resources (GPU, paid API) are unavailable; and (c) sparse discussion of the pedagogical theory that should govern how an LLM changes its behavior when the learner is anxious versus engaged. NeuroLearn explicitly encodes such pedagogical rules and ships with a fully functional offline fallback mode.",
        styles['BodyTextJust']
    ))
    story.append(Paragraph(
        "The present work therefore contributes both an engineering artifact and a concrete design pattern — sense, model, condition, generate — that future researchers can refine with more powerful detectors, richer student models, and larger evaluation studies.",
        styles['BodyTextJust']
    ))
    story.append(PageBreak())

    # ============================================================
    # CHAPTER 3: SYSTEM ANALYSIS
    # ============================================================
    story.append(Paragraph("CHAPTER 3", styles['CoverSubtitle']))
    story.append(Paragraph("SYSTEM ANALYSIS &amp; REQUIREMENTS", styles['ChapterTitle']))
    story.append(hr_line())

    story.append(Paragraph("3.1 Feasibility Study", styles['SectionHeading']))
    story.append(Paragraph("<b>Technical Feasibility:</b> All core technologies (ViT emotion models, BKT, Streamlit, sentence-transformers, edge-tts) are mature and freely available. Pre-trained models remove the need for large-scale training from scratch. A consumer laptop is sufficient for demonstration.", styles['BodyTextJust']))
    story.append(Paragraph("<b>Operational Feasibility:</b> The system is designed as a self-study companion. Students need only a webcam and a browser. No special infrastructure is required.", styles['BodyTextJust']))
    story.append(Paragraph("<b>Economic Feasibility:</b> The entire stack is open-source. Optional LLM API usage (Groq) has a generous free tier. Development cost is limited to student time.", styles['BodyTextJust']))

    story.append(Paragraph("3.2 Functional Requirements", styles['SectionHeading']))
    story.append(Paragraph("Table 3.1: Functional Requirements Summary", styles['Caption']))
    fr_table = make_table(
        ["ID", "Requirement", "Priority"],
        [
            ["FR1", "Real-time facial emotion detection from webcam", "High"],
            ["FR2", "Mapping of emotions to educational states", "High"],
            ["FR3", "Concept-level knowledge tracing with persistence", "High"],
            ["FR4", "Emotion- and mastery-conditioned response generation", "High"],
            ["FR5", "PDF/text document upload and RAG retrieval", "High"],
            ["FR6", "Interactive chat interface with history", "High"],
            ["FR7", "Neural text-to-speech for responses", "Medium"],
            ["FR8", "Mastery visualization dashboard", "Medium"],
            ["FR9", "Quiz generation and mastery update", "Medium"],
            ["FR10", "Offline/rule-based fallback when no API key", "Medium"],
        ],
        [0.7*inch, 4.5*inch, 1.0*inch]
    )
    story.append(fr_table)
    story.append(Spacer(1, 0.15 * inch))

    story.append(Paragraph("3.3 Non-Functional Requirements", styles['SectionHeading']))
    story.append(Paragraph("• <b>Performance:</b> Emotion inference should complete within 1–2 seconds on CPU for acceptable interactivity.", styles['BulletText']))
    story.append(Paragraph("• <b>Usability:</b> Clean, intuitive interface usable without training.", styles['BulletText']))
    story.append(Paragraph("• <b>Modularity:</b> Each major component (emotion, KT, tutor, RAG) must be replaceable independently.", styles['BulletText']))
    story.append(Paragraph("• <b>Privacy:</b> Webcam frames are processed locally; no video is stored by default.", styles['BulletText']))
    story.append(Paragraph("• <b>Extensibility:</b> Easy addition of new concepts, new emotion models, or alternative LLMs.", styles['BulletText']))

    story.append(Paragraph("3.4 Hardware &amp; Software Requirements", styles['SectionHeading']))
    story.append(Paragraph("Table 3.2: Software Requirements", styles['Caption']))
    sw_table = make_table(
        ["Component", "Technology / Version"],
        [
            ["Language", "Python 3.10+"],
            ["Deep Learning", "PyTorch 2.x, Transformers 4.x"],
            ["Computer Vision", "OpenCV, Hugging Face ViT"],
            ["Web Framework", "Streamlit 1.39+"],
            ["RAG / Embeddings", "sentence-transformers, PyMuPDF, NumPy"],
            ["TTS", "edge-tts"],
            ["Visualization", "Plotly"],
            ["Optional LLM", "Groq API / OpenAI API"],
        ],
        [2.2*inch, 4.0*inch]
    )
    story.append(sw_table)
    story.append(PageBreak())

    # ============================================================
    # CHAPTER 4: SYSTEM DESIGN
    # ============================================================
    story.append(Paragraph("CHAPTER 4", styles['CoverSubtitle']))
    story.append(Paragraph("SYSTEM DESIGN", styles['ChapterTitle']))
    story.append(hr_line())

    story.append(Paragraph("4.1 System Architecture", styles['SectionHeading']))
    story.append(Paragraph(
        "NeuroLearn follows a modular pipeline architecture. The major layers are:",
        styles['BodyTextJust']
    ))
    story.append(Paragraph("1. <b>Perception Layer</b> — Captures webcam frames, detects faces, classifies emotion via Vision Transformer, and maps to an educational state.", styles['BulletText']))
    story.append(Paragraph("2. <b>Student Modeling Layer</b> — Maintains and updates a concept-level mastery vector using hybrid Bayesian Knowledge Tracing.", styles['BulletText']))
    story.append(Paragraph("3. <b>Retrieval Layer</b> — Indexes uploaded documents and retrieves relevant chunks for a given query.", styles['BulletText']))
    story.append(Paragraph("4. <b>Adaptive Generation Layer</b> — Constructs a rich system prompt containing emotional state, mastery summary, and retrieved context, then calls the LLM (or fallback).", styles['BulletText']))
    story.append(Paragraph("5. <b>Presentation Layer</b> — Streamlit dashboard providing chat, live metrics, mastery charts, document management, and optional TTS playback.", styles['BulletText']))

    story.append(Paragraph(
        "Figure 4.1 (conceptual): Webcam and chat input feed the Perception and Student Modeling modules. Their outputs, together with RAG context, condition the Adaptive Tutor. The generated response is displayed and optionally spoken.",
        styles['BodyTextJust']
    ))

    story.append(Paragraph("4.2 Module Design", styles['SectionHeading']))
    story.append(Paragraph("4.2.1 Emotion Detection Module", styles['SubSection']))
    story.append(Paragraph(
        "Input: BGR frame from webcam. Processing: Haar-cascade face detection → crop largest face → resize → Vision Transformer inference → softmax probabilities over 7 emotion classes. Output: dominant emotion, confidence, and mapped educational state (Engaged &amp; Positive, Curious / Interested, Focused / Neutral, Confused / Frustrated, Anxious / Overwhelmed, Frustrated / Stuck, Disengaged).",
        styles['BodyTextJust']
    ))

    story.append(Paragraph("4.2.2 Knowledge Tracing Module", styles['SubSection']))
    story.append(Paragraph(
        "Each concept is modeled with a BKT-style probability of mastery. After every practice interaction the posterior is computed using Bayes’ rule incorporating guess and slip parameters; a learning transition is then applied, modulated by item difficulty. Mastery values, attempt counts, and a rolling history are persisted to JSON so that the student model survives across sessions.",
        styles['BodyTextJust']
    ))

    story.append(Paragraph("4.2.3 Adaptive Tutor Module", styles['SubSection']))
    story.append(Paragraph(
        "A carefully engineered system prompt defines NeuroLearn’s pedagogical principles (scaffolding, encouragement when frustrated, deeper challenges when engaged, etc.). At inference time an additional state block is injected containing the current educational state and a compact knowledge summary. When RAG context is available it is also injected. The resulting message list is sent to the configured LLM (Groq Llama-3.1 or OpenAI). A sophisticated rule-based fallback ensures the system remains useful even without an API key.",
        styles['BodyTextJust']
    ))

    story.append(Paragraph("4.2.4 RAG Module", styles['SubSection']))
    story.append(Paragraph(
        "Documents are parsed (PyMuPDF for PDFs), split into overlapping chunks, embedded with a MiniLM sentence transformer, and stored as a NumPy matrix. At query time the question is embedded and the top-k most similar chunks (cosine similarity) are returned and formatted as context for the tutor.",
        styles['BodyTextJust']
    ))

    story.append(Paragraph("4.3 Data Flow", styles['SectionHeading']))
    story.append(Paragraph(
        "A typical interaction proceeds as follows: (1) User activates webcam or selects a simulated state; (2) User types a question or requests a quiz; (3) System retrieves relevant document chunks if any documents are loaded; (4) Tutor module builds the conditioned prompt and generates a response; (5) Response is displayed and optionally converted to speech; (6) If the interaction is a practice item, the knowledge tracer is updated and the mastery chart refreshes.",
        styles['BodyTextJust']
    ))

    story.append(Paragraph("4.4 Persistence Design", styles['SectionHeading']))
    story.append(Paragraph(
        "Student mastery, attempt statistics, and interaction history are stored in a simple JSON file under the data/ directory. RAG embeddings and chunk metadata are likewise persisted so that re-indexing is unnecessary on every restart. No traditional relational database is required for the current scope, keeping deployment simple.",
        styles['BodyTextJust']
    ))
    story.append(PageBreak())

    # ============================================================
    # CHAPTER 5: IMPLEMENTATION
    # ============================================================
    story.append(Paragraph("CHAPTER 5", styles['CoverSubtitle']))
    story.append(Paragraph("IMPLEMENTATION", styles['ChapterTitle']))
    story.append(hr_line())

    story.append(Paragraph("5.1 Technology Stack", styles['SectionHeading']))
    story.append(Paragraph("Table 5.1: Technology Stack Overview", styles['Caption']))
    tech_table = make_table(
        ["Layer", "Technologies"],
        [
            ["Language &amp; Runtime", "Python 3.10+, virtual environment"],
            ["Deep Learning / CV", "PyTorch, torchvision, Hugging Face Transformers, OpenCV"],
            ["Emotion Model", "ViT fine-tuned on FER2013 (abhilash88/face-emotion-detection)"],
            ["Knowledge Tracing", "Custom Hybrid BKT (NumPy + JSON persistence)"],
            ["LLM Interface", "Groq / OpenAI Python SDK + rule-based fallback"],
            ["RAG", "PyMuPDF, langchain-text-splitters, sentence-transformers, NumPy"],
            ["Speech", "edge-tts (neural voices)"],
            ["Frontend", "Streamlit, Plotly"],
            ["Utilities", "Pillow, pandas, python-dotenv"],
        ],
        [2.0*inch, 4.2*inch]
    )
    story.append(tech_table)
    story.append(Spacer(1, 0.15 * inch))

    story.append(Paragraph("5.2 Emotion Detection Module", styles['SectionHeading']))
    story.append(Paragraph(
        "The module is implemented in modules/emotion_detector.py. On initialization it loads the ViT image processor and classification model, moving them to GPU if available. Face detection uses OpenCV’s Haar cascade for speed and simplicity. For each frame the largest detected face is cropped, converted to RGB, processed by the ViT, and the resulting logits are converted to probabilities. The educational-state mapping is a deterministic dictionary that translates the seven basic emotions into pedagogy-relevant labels used by the tutor.",
        styles['BodyTextJust']
    ))
    story.append(Paragraph("Table 5.2: Emotion to Educational State Mapping", styles['Caption']))
    emo_table = make_table(
        ["Detected Emotion", "Educational State", "Pedagogical Implication"],
        [
            ["Happy", "Engaged &amp; Positive", "Can increase challenge"],
            ["Surprise", "Curious / Interested", "Provide rich explanations"],
            ["Neutral", "Focused / Neutral", "Standard clear instruction"],
            ["Sad", "Confused / Frustrated", "Simplify, scaffold, encourage"],
            ["Fear", "Anxious / Overwhelmed", "Reduce cognitive load"],
            ["Angry", "Frustrated / Stuck", "Identify misconception, new angle"],
            ["Disgust", "Disengaged", "Re-engage with relevance / novelty"],
        ],
        [1.5*inch, 1.8*inch, 2.9*inch]
    )
    story.append(emo_table)
    story.append(Spacer(1, 0.15 * inch))

    story.append(Paragraph("5.3 Knowledge Tracing Module", styles['SectionHeading']))
    story.append(Paragraph(
        "Implemented in modules/knowledge_tracer.py. A predefined list of CS/AI concepts is maintained. Each concept stores current mastery probability, number of attempts, number of correct responses, and last-practiced timestamp. The update method applies the classic BKT observation model followed by a learning transition whose rate is slightly increased for easier items. The recommend_next_concept method performs a soft selection biased toward low-mastery concepts, providing simple adaptive sequencing.",
        styles['BodyTextJust']
    ))

    story.append(Paragraph("5.4 Adaptive Tutor Module", styles['SectionHeading']))
    story.append(Paragraph(
        "The AdaptiveTutor class (modules/tutor.py) encapsulates prompt construction and LLM invocation. A long-lived system prompt encodes pedagogical principles. For every turn an additional “Current Student State” block is generated from the emotion detector and knowledge tracer outputs. When RAG context exists it is appended as a third system message. Conversation history (last several turns) is included for coherence. If no API key is present, a carefully written rule-based fallback still produces state-aware responses, ensuring the demo never fails completely.",
        styles['BodyTextJust']
    ))

    story.append(Paragraph("5.5 RAG Module", styles['SectionHeading']))
    story.append(Paragraph(
        "modules/rag.py provides DocumentRAG. PDF text is extracted with PyMuPDF; text files are read directly. RecursiveCharacterTextSplitter produces overlapping chunks of approximately 600 characters. Embeddings are computed with the all-MiniLM-L6-v2 model and stored as a NumPy array. Retrieval is pure cosine similarity — simple, fast, and sufficient for personal document collections. Metadata (source filename) is retained so that answers can cite their origin.",
        styles['BodyTextJust']
    ))

    story.append(Paragraph("5.6 User Interface", styles['SectionHeading']))
    story.append(Paragraph(
        "The Streamlit application (app.py) presents a two-column layout. The left column shows the live (or simulated) emotion state and a horizontal bar chart of concept mastery. The right column contains the chat interface and quick-action buttons (Recommend Topic, Quiz Me, Mark Correct, Clear Chat). The sidebar hosts webcam toggle, document uploader, student-model metrics, API-key input, and TTS controls. Session state is used extensively so that models and conversation history survive Streamlit’s rerun cycle.",
        styles['BodyTextJust']
    ))
    story.append(Paragraph(
        "Special care was taken to keep the interface usable during viva demonstrations. Simulated emotional states can be selected from a dropdown when a webcam is unavailable or undesirable, ensuring that adaptive behavior can always be showcased. Quick-action buttons reduce the number of typed commands needed to demonstrate knowledge tracing and recommendation. The mastery chart updates immediately after a “Mark Correct” action, providing visual feedback that is easy for evaluators to observe.",
        styles['BodyTextJust']
    ))
    story.append(Paragraph(
        "From an engineering perspective, the use of Streamlit allowed the entire multimodal pipeline — vision, language, retrieval, and speech — to be exposed through a single Python process without the overhead of a separate frontend build step. This choice significantly accelerated development while still producing a polished, modern-looking application suitable for academic presentation.",
        styles['BodyTextJust']
    ))
    story.append(PageBreak())

    # ============================================================
    # CHAPTER 6: TESTING & RESULTS
    # ============================================================
    story.append(Paragraph("CHAPTER 6", styles['CoverSubtitle']))
    story.append(Paragraph("TESTING, RESULTS &amp; DISCUSSION", styles['ChapterTitle']))
    story.append(hr_line())

    story.append(Paragraph("6.1 Testing Strategy", styles['SectionHeading']))
    story.append(Paragraph(
        "Testing was performed at multiple levels: unit testing of individual modules (emotion mapping, BKT update equations, RAG retrieval), integration testing of the full pipeline, and qualitative interaction testing simulating different learner states. Because the project prioritizes a working end-to-end demonstration over large-scale user studies, evaluation emphasizes observable adaptive behavior and system robustness.",
        styles['BodyTextJust']
    ))

    story.append(Paragraph("6.2 Results", styles['SectionHeading']))
    story.append(Paragraph(
        "<b>Emotion Detection:</b> The Vision Transformer produces plausible emotion labels under normal indoor lighting. Confidence scores are typically high (&gt;0.7) for clear frontal faces. Haar cascade occasionally fails under extreme pose or heavy occlusion; this is an acknowledged limitation addressable by upgrading to a modern face detector.",
        styles['BodyTextJust']
    ))
    story.append(Paragraph(
        "<b>Knowledge Tracing:</b> Mastery values update smoothly after each practice interaction. The recommend_next_concept function reliably surfaces weak areas. Persistence across application restarts works as designed.",
        styles['BodyTextJust']
    ))
    story.append(Paragraph(
        "<b>Adaptive Behavior:</b> Side-by-side comparison of responses for the same question under different simulated emotional states shows clear qualitative differences — simplified language and encouragement when “Anxious / Overwhelmed”, richer explanations and follow-up challenges when “Engaged &amp; Positive”.",
        styles['BodyTextJust']
    ))
    story.append(Paragraph(
        "<b>RAG:</b> When relevant PDFs are uploaded, retrieved chunks appear in the prompt and the tutor’s answers become noticeably more grounded and citation-aware.",
        styles['BodyTextJust']
    ))

    story.append(Paragraph("Table 6.1: Qualitative Evaluation of Adaptive Responses (Illustrative)", styles['Caption']))
    qual_table = make_table(
        ["Student State", "Observed Tutor Behavior"],
        [
            ["Engaged &amp; Positive", "Deeper explanations, additional insights, challenging follow-ups"],
            ["Curious / Interested", "Analogies, cross-concept links, exploratory tone"],
            ["Focused / Neutral", "Clear structured step-by-step instruction"],
            ["Confused / Frustrated", "Simplified vocabulary, smaller steps, frequent comprehension checks"],
            ["Anxious / Overwhelmed", "Very short sentences, strong encouragement, minimal new load"],
            ["Frustrated / Stuck", "Empathy statements, alternative explanations, misconception probing"],
            ["Disengaged", "Relevance hooks, surprising facts, interactive questions"],
        ],
        [1.8*inch, 4.4*inch]
    )
    story.append(qual_table)
    story.append(Spacer(1, 0.15 * inch))

    story.append(Paragraph("6.3 Discussion", styles['SectionHeading']))
    story.append(Paragraph(
        "The results confirm that the integration of affective sensing and knowledge tracing produces visibly different and pedagogically appropriate tutor behavior. The modular design allowed rapid iteration. Limitations include dependence on frontal face visibility, the relative simplicity of the BKT model compared with modern Transformer KT, and the absence of a large-scale learning-outcome study. These limitations are natural for a solo final-year project and point directly to valuable future work.",
        styles['BodyTextJust']
    ))
    story.append(Paragraph(
        "It is worth noting that even the rule-based fallback mode produces useful, state-conditioned responses. This design decision proved valuable during development and demonstration: the system never appears “broken” merely because an API key is missing. In a classroom or low-resource setting this graceful degradation is an important practical advantage.",
        styles['BodyTextJust']
    ))
    story.append(Paragraph(
        "Overall, the evaluation supports the central thesis of the project: combining real-time affect estimation with a persistent knowledge model and a carefully conditioned generative tutor yields an interaction experience that is noticeably more adaptive than a static LLM chatbot. Quantitative learning-gain studies remain future work, but the qualitative evidence is already strong enough to justify continued development.",
        styles['BodyTextJust']
    ))
    story.append(PageBreak())

    # ============================================================
    # CHAPTER 7: CONCLUSION
    # ============================================================
    story.append(Paragraph("CHAPTER 7", styles['CoverSubtitle']))
    story.append(Paragraph("CONCLUSION &amp; FUTURE WORK", styles['ChapterTitle']))
    story.append(hr_line())

    story.append(Paragraph("7.1 Conclusion", styles['SectionHeading']))
    story.append(Paragraph(
        "Through this project I was able to build a working adaptive tutoring system that actually responds to both the student’s facial expressions and their knowledge level. Combining emotion detection, knowledge tracing and a language model was challenging, but the final system works as intended. It changes its teaching style when the student looks confused or frustrated, and it keeps track of which topics the student is weak in. Overall, I feel the project meets the goals I had set at the beginning.",
        styles['BodyTextJust']
    ))

    story.append(Paragraph("7.2 Future Work", styles['SectionHeading']))
    story.append(Paragraph("There are still many things that can be improved:", styles['BodyTextJust']))
    story.append(Paragraph("• Making the emotion detection even more accurate in poor lighting conditions.", styles['BulletText']))
    story.append(Paragraph("• Replacing the current knowledge tracing model with a more advanced Transformer-based version.", styles['BulletText']))
    story.append(Paragraph("• Adding speech-to-text so that students can talk to the tutor instead of only typing.", styles['BulletText']))
    story.append(Paragraph("• Doing a proper study with real students to measure how much the system actually helps in learning.", styles['BulletText']))
    story.append(Paragraph("• Trying to run the system on smaller devices so that privacy can be maintained better.", styles['BulletText']))
    story.append(Paragraph("• Fine-tuning a smaller language model so that the system does not always need an external API.", styles['BulletText']))

    story.append(Paragraph("7.3 Closing Remarks", styles['SectionHeading']))
    story.append(Paragraph(
        "I believe AI should support teachers and students, not replace them. My aim with NeuroLearn was to create something that feels a little more human and helpful than a normal chatbot. I hope this work can be improved further in the future.",
        styles['BodyTextJust']
    ))
    story.append(PageBreak())

    # ============================================================
    # REFERENCES
    # ============================================================
    story.append(Paragraph("REFERENCES", styles['ChapterTitle']))
    story.append(hr_line())
    refs = [
        "1. Corbett, A. T., & Anderson, J. R. (1995). Knowledge tracing: Modeling the acquisition of procedural knowledge. User Modeling and User-Adapted Interaction.",
        "2. Piech, C., et al. (2015). Deep Knowledge Tracing. Advances in Neural Information Processing Systems (NeurIPS).",
        "3. Dosovitskiy, A., et al. (2020). An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale. ICLR.",
        "4. Lewis, P., et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. NeurIPS.",
        "5. Picard, R. W. (1997). Affective Computing. MIT Press.",
        "6. D’Mello, S., & Graesser, A. (2012). Dynamics of Affective States during Complex Learning. Learning and Instruction.",
        "7. Bloom, B. S. (1984). The 2 Sigma Problem: The Search for Methods of Group Instruction as Effective as One-to-One Tutoring. Educational Researcher.",
        "8. Pandey, S., & Karypis, G. (2019). A Self-Attentive model for Knowledge Tracing. EDM.",
        "9. Choi, Y., et al. (2020). Towards an Appropriate Query, Key, and Value Computation for Knowledge Tracing. arXiv.",
        "10. Open-source systems and models: Hugging Face Transformers, Streamlit, DeepTutor, AffectLearn, and related 2025–2026 educational AI prototypes.",
        "11. Vaswani, A., et al. (2017). Attention Is All You Need. NeurIPS.",
        "12. Devlin, J., et al. (2019). BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. NAACL.",
    ]
    for r in refs:
        story.append(Paragraph(r, styles['BodyTextJust']))
    story.append(PageBreak())

    # ============================================================
    # APPENDIX A
    # ============================================================
    story.append(Paragraph("APPENDIX A", styles['CoverSubtitle']))
    story.append(Paragraph("SAMPLE CODE SNIPPETS", styles['ChapterTitle']))
    story.append(hr_line())

    story.append(Paragraph("A.1 Emotion Prediction (simplified)", styles['SectionHeading']))
    story.append(Paragraph(
        "inputs = processor(images=pil_image, return_tensors=\"pt\")<br/>"
        "outputs = model(**inputs)<br/>"
        "probs = torch.nn.functional.softmax(outputs.logits, dim=-1)<br/>"
        "emotion = EMOTION_LABELS[probs.argmax()]",
        styles['CodeStyle']
    ))

    story.append(Paragraph("A.2 BKT-style Mastery Update (core logic)", styles['SectionHeading']))
    story.append(Paragraph(
        "if is_correct:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;p_correct = p_know*(1-p_slip) + (1-p_know)*p_guess<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;p_know = (p_know*(1-p_slip)) / p_correct<br/>"
        "else:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;p_incorrect = p_know*p_slip + (1-p_know)*(1-p_guess)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;p_know = (p_know*p_slip) / p_incorrect<br/>"
        "p_know = p_know + (1-p_know)*p_learn   # learning transition",
        styles['CodeStyle']
    ))

    story.append(Paragraph("A.3 Adaptive Prompt State Block (conceptual)", styles['SectionHeading']))
    story.append(Paragraph(
        "=== CURRENT STUDENT STATE ===<br/>"
        "Emotional / Cognitive State: Confused / Frustrated<br/>"
        "Recommended Tone: patient, supportive, calming<br/>"
        "Recommended Depth: simplify significantly<br/>"
        "Average Mastery: 42%<br/>"
        "Weak Concepts: Recursion (28%), Dynamic Programming (31%)<br/>"
        "=== END STATE ===",
        styles['CodeStyle']
    ))
    story.append(PageBreak())

    # ============================================================
    # APPENDIX B
    # ============================================================
    story.append(Paragraph("APPENDIX B", styles['CoverSubtitle']))
    story.append(Paragraph("SCREENSHOTS &amp; DEMO FLOW", styles['ChapterTitle']))
    story.append(hr_line())

    story.append(Paragraph(
        "Because this is a generated report, actual screenshots should be captured from the running Streamlit application and inserted here. Recommended figures for the final bound report:",
        styles['BodyTextJust']
    ))
    story.append(Paragraph("• B.1  Main dashboard with mastery chart and chat panel", styles['BulletText']))
    story.append(Paragraph("• B.2  Webcam emotion detection overlay (bounding box + label)", styles['BulletText']))
    story.append(Paragraph("• B.3  Sidebar showing document upload and student metrics", styles['BulletText']))
    story.append(Paragraph("• B.4  Sample conversation under “Confused / Frustrated” state", styles['BulletText']))
    story.append(Paragraph("• B.5  Sample conversation under “Engaged &amp; Positive” state (same question)", styles['BulletText']))
    story.append(Paragraph("• B.6  RAG citation appearing in a grounded answer", styles['BulletText']))

    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("<b>Suggested Live Demo Script (5–7 minutes)</b>", styles['SectionHeading']))
    story.append(Paragraph("1. Launch the application and briefly explain the two-column layout.", styles['BulletText']))
    story.append(Paragraph("2. Simulate “Focused / Neutral” and ask a conceptual question; show the structured answer.", styles['BulletText']))
    story.append(Paragraph("3. Switch simulated state to “Anxious / Overwhelmed” and repeat a similar question; highlight the change in tone and simplification.", styles['BulletText']))
    story.append(Paragraph("4. Upload a short PDF, ask a question from it, and point out the grounded response.", styles['BulletText']))
    story.append(Paragraph("5. Trigger “Quiz Me”, answer, mark correct, and show the mastery bar updating.", styles['BulletText']))
    story.append(Paragraph("6. Optionally enable TTS and let the system speak a short explanation.", styles['BulletText']))
    story.append(Paragraph("7. Conclude by summarizing the closed loop: Sense → Model → Adapt → Respond.", styles['BulletText']))

    story.append(Spacer(1, 0.5 * inch))
    story.append(hr_line())
    story.append(PageBreak())

    # Extra content to reach ~30 pages
    story.append(Paragraph("APPENDIX C", styles['CoverSubtitle']))
    story.append(Paragraph("DETAILED MODULE INTERFACES &amp; CONFIGURATION", styles['ChapterTitle']))
    story.append(hr_line())

    story.append(Paragraph("C.1 EmotionDetector Public Interface", styles['SectionHeading']))
    story.append(Paragraph(
        "The EmotionDetector class exposes the following primary methods: __init__(model_name), detect_faces(frame), predict_emotion(face_img), process_frame(frame), and draw_overlay(frame, result). The process_frame method is the main entry point used by the Streamlit application; it returns a dictionary containing face_detected, emotion, confidence, educational_state, all_probabilities, and bbox. This dictionary is stored in Streamlit session state and read by the tutor on every turn.",
        styles['BodyTextJust']
    ))

    story.append(Paragraph("C.2 KnowledgeTracer Public Interface", styles['SectionHeading']))
    story.append(Paragraph(
        "Key methods include update(concept, is_correct, difficulty), get_mastery(concept=None), get_weak_concepts(top_k), get_strong_concepts(top_k), recommend_next_concept(), get_student_summary(), and save()/load(). The update method is called whenever the student completes a practice item. get_student_summary returns a compact dictionary that is injected into the LLM prompt, keeping token usage modest while still conveying essential information about the learner.",
        styles['BodyTextJust']
    ))

    story.append(Paragraph("C.3 AdaptiveTutor Configuration", styles['SectionHeading']))
    story.append(Paragraph(
        "The tutor can be instantiated with an optional API key. If a Groq or OpenAI key is supplied, the corresponding client is created and use_api is set to True. Otherwise the system operates entirely in fallback mode. The ADAPTATION_RULES dictionary is the heart of the pedagogical policy; each educational state maps to preferred tone, depth, and style. These rules are rendered into natural language and placed in the system prompt so that the LLM (or the fallback) can follow them.",
        styles['BodyTextJust']
    ))

    story.append(Paragraph("C.4 DocumentRAG Configuration", styles['SectionHeading']))
    story.append(Paragraph(
        "Chunk size is set to 600 characters with 100-character overlap — a compromise between retrieval precision and context length. The embedding model (all-MiniLM-L6-v2) is small enough to run comfortably on CPU yet produces high-quality semantic vectors for educational text. Persistence of both chunks and embeddings means that a user can close the browser and later resume with the same document collection already indexed.",
        styles['BodyTextJust']
    ))

    story.append(Paragraph("C.5 Recommended Hardware for Smooth Demo", styles['SectionHeading']))
    story.append(Paragraph(
        "• CPU: Any modern multi-core processor (Intel i5 / Ryzen 5 or better)<br/>"
        "• RAM: 8 GB minimum, 16 GB recommended when loading the ViT and embedding models simultaneously<br/>"
        "• Webcam: Standard built-in or USB webcam; 720p is sufficient<br/>"
        "• Optional GPU: NVIDIA GPU with CUDA support accelerates emotion inference but is not required<br/>"
        "• Network: Required only if using a remote LLM API; pure offline mode works without internet after models are cached",
        styles['BodyTextJust']
    ))

    story.append(PageBreak())

    story.append(Paragraph("APPENDIX D", styles['CoverSubtitle']))
    story.append(Paragraph("PROJECT TIMELINE &amp; WORK BREAKDOWN", styles['ChapterTitle']))
    story.append(hr_line())

    story.append(Paragraph(
        "A realistic solo-student timeline for developing NeuroLearn over a typical final-year project window (approximately 4–5 months) is outlined below. Actual schedules will vary with prior experience and institutional deadlines.",
        styles['BodyTextJust']
    ))

    story.append(Paragraph("Phase 1 – Literature &amp; Design (Weeks 1–3)", styles['SubSection']))
    story.append(Paragraph(
        "Survey of ITS, Knowledge Tracing, affective computing, and LLM tutoring literature. Finalization of system architecture, technology choices, and module boundaries. Preparation of synopsis and initial presentation.",
        styles['BodyTextJust']
    ))

    story.append(Paragraph("Phase 2 – Core Modules (Weeks 4–8)", styles['SubSection']))
    story.append(Paragraph(
        "Implementation of EmotionDetector with ViT, basic KnowledgeTracer, and a first version of the AdaptiveTutor (initially rule-based). Unit tests for each module. Integration into a minimal Streamlit skeleton.",
        styles['BodyTextJust']
    ))

    story.append(Paragraph("Phase 3 – Advanced Features (Weeks 9–12)", styles['SubSection']))
    story.append(Paragraph(
        "Addition of RAG pipeline, neural TTS, API-based LLM integration, mastery visualization, and persistence. Extensive prompt engineering for state-conditioned responses. End-to-end testing under different simulated emotional states.",
        styles['BodyTextJust']
    ))

    story.append(Paragraph("Phase 4 – Polish, Documentation &amp; Evaluation (Weeks 13–16)", styles['SubSection']))
    story.append(Paragraph(
        "UI refinement, error handling, offline fallback improvements. Writing of full project report, preparation of slides, recording of demo video. Qualitative evaluation and preparation for viva voce.",
        styles['BodyTextJust']
    ))

    story.append(Paragraph(
        "This phased approach ensures that a working demonstration exists early, reducing risk, while still leaving time for the advanced features that distinguish the project.",
        styles['BodyTextJust']
    ))

    story.append(PageBreak())

    story.append(Paragraph("APPENDIX E", styles['CoverSubtitle']))
    story.append(Paragraph("GLOSSARY OF KEY TERMS", styles['ChapterTitle']))
    story.append(hr_line())

    glossary = [
        ("Affective Computing", "Computing that relates to, arises from, or deliberately influences emotion."),
        ("Bayesian Knowledge Tracing (BKT)", "A classic probabilistic model that estimates the probability a student has mastered a skill from a sequence of correct/incorrect responses."),
        ("Educational State", "A pedagogically meaningful label derived from raw emotion (e.g., Confused / Frustrated) used to drive tutoring strategy."),
        ("Intelligent Tutoring System (ITS)", "Software that provides customized instruction or feedback to learners, traditionally comprising domain, student, tutoring, and interface models."),
        ("Knowledge Tracing", "The problem of modeling a learner’s knowledge state over time from interaction data."),
        ("Large Language Model (LLM)", "A neural language model with billions of parameters trained on massive text corpora, capable of fluent generation and instruction following."),
        ("Retrieval-Augmented Generation (RAG)", "A technique that retrieves relevant external documents and supplies them as context to an LLM to reduce hallucination and ground answers."),
        ("Scaffolding", "Instructional support that is gradually withdrawn as the learner becomes more competent."),
        ("Vision Transformer (ViT)", "A neural architecture that applies the Transformer model to image patches, achieving strong results on vision tasks including facial expression recognition."),
    ]
    for term, definition in glossary:
        story.append(Paragraph(f"<b>{term}:</b> {definition}", styles['BodyTextJust']))

    story.append(Spacer(1, 0.4 * inch))
    story.append(hr_line())
    story.append(Paragraph(
        "— End of Project Report —",
        styles['CenterText']
    ))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(
        "NeuroLearn – Adaptive Multimodal Intelligent Tutoring System<br/>Submitted by Ritika (2311078)<br/>B.Tech CSE (AIML) | UIET, MDU | Academic Year 2025–2026",
        styles['CenterText']
    ))

    # Build PDF
    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=A4,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN,
        title="NeuroLearn – Adaptive Multimodal Intelligent Tutoring System – Project Report",
        author="Ritika (2311078)",
        subject="B.Tech Major Project Report – CSE AIML – UIET, MDU"
    )
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(f"Report generated successfully: {OUTPUT_PATH}")
    return OUTPUT_PATH


if __name__ == "__main__":
    build_report()
