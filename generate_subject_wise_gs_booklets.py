import json, os, sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas

def escape_xml(s):
    if not s:
        return ""
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

class UPSCSubjectCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []
        self.doc_subject = "GENERAL KNOWLEDGE"
        self.doc_code = "CDS-GS-2024-A"

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, total_pages):
        w, h = A4
        if self._pageNumber == 1:
            return

        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.drawString(36, h - 28, "UPSC CDS EXAMINATION — SUBJECT-WISE QUESTION PAPER")
        self.setFont("Helvetica", 8)
        self.drawString(290, h - 28, f"|  {self.doc_subject.upper()}  |  SERIES [ A ]")
        self.drawRightString(w - 36, h - 28, f"PAGE {self._pageNumber} OF {total_pages}")
        
        self.setLineWidth(0.8)
        self.setStrokeColor(colors.black)
        self.line(36, h - 33, w - 36, h - 33)

        rough_top = 45
        self.setStrokeColor(colors.HexColor("#94a3b8"))
        self.setDash([2, 2])
        self.setLineWidth(0.5)
        self.line(36, rough_top, w - 36, rough_top)
        
        self.setFont("Helvetica-Oblique", 7)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawCentredString(w/2, rough_top - 10, "— SPACE FOR ROUGH WORK —")

        self.setFont("Helvetica", 8)
        self.setFillColor(colors.black)
        self.drawCentredString(w/2, 16, f"- {self._pageNumber} -")
        self.restoreState()


def get_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle('CovTitle', fontName='Helvetica-Bold', fontSize=14, leading=18, alignment=TA_CENTER))
    styles.add(ParagraphStyle('CovSub', fontName='Helvetica-Bold', fontSize=10.5, leading=14, alignment=TA_CENTER))
    styles.add(ParagraphStyle('CovBadge', fontName='Helvetica-Bold', fontSize=12, leading=16, alignment=TA_CENTER, textColor=colors.HexColor("#1e3a8a")))
    styles.add(ParagraphStyle('InstText', fontName='Helvetica', fontSize=8, leading=11, alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle('ChapBanner', fontName='Helvetica-Bold', fontSize=10, leading=13, textColor=colors.HexColor("#0f172a"), spaceBefore=8, spaceAfter=4))
    styles.add(ParagraphStyle('QText', fontName='Helvetica', fontSize=8.2, leading=11, alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle('OptText', fontName='Helvetica', fontSize=8, leading=10.5))
    styles.add(ParagraphStyle('GridHead', fontName='Helvetica-Bold', fontSize=7.5, leading=9, alignment=TA_CENTER, textColor=colors.white))
    styles.add(ParagraphStyle('GridText', fontName='Helvetica', fontSize=7.5, leading=9, alignment=TA_CENTER))
    styles.add(ParagraphStyle('SolHead', fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=colors.HexColor("#1e3a8a")))
    styles.add(ParagraphStyle('SolBody', fontName='Helvetica', fontSize=8, leading=11, alignment=TA_JUSTIFY))
    return styles


def build_subject_question_paper(subject_id, subject_title, questions, output_pdf, tbc_code):
    print(f"Generating Question Paper for Subject {subject_id}: {subject_title} ({len(questions)} Qs)...")
    styles = get_styles()
    story = []

    # 1. Official Cover Page
    top_header_data = [
        [
            Paragraph(f"<b>T.B.C. : {tbc_code}</b><br/><font size=7.5>Serial No. <b>{840000 + subject_id * 1423}</b></font>", styles['Normal']),
            Paragraph(f"<b>TEST BOOKLET<br/><font size=16 color='#b91c1c'>[ A ]</font></b><br/><font size=7.5>SUBJECT ARCHIVE</font>", styles['CovSub']),
            Paragraph(f"<b>Time Allowed : {max(30, int(len(questions) * 1.0))} Mins</b><br/><b>Max. Marks : {len(questions) * 0.833:.1f}</b>", styles['Normal'])
        ]
    ]
    top_t = Table(top_header_data, colWidths=[175, 173, 175])
    top_t.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1.2, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.8, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('ALIGN', (0,0), (-1,-1), 'CENTER')
    ]))
    story.append(top_t)
    story.append(Spacer(1, 14))

    story.append(Paragraph("<b>UNION PUBLIC SERVICE COMMISSION</b>", styles['CovTitle']))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>COMBINED DEFENCE SERVICES (CDS) EXAMINATION</b>", styles['CovSub']))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"<b>SUBJECT {subject_id} : {subject_title.upper()}</b>", styles['CovBadge']))
    story.append(Spacer(1, 10))

    instructions = [
        f"<b>1.</b> This question paper contains <b>ALL {len(questions)} authentic questions</b> for <b>{subject_title}</b> extracted directly from official UPSC Combined Defence Services examination archives.",
        f"<b>2.</b> Immediately after commencement of the examination, check that this booklet does not have any unprinted, torn, or missing pages.",
        f"<b>3. SCORING STANDARD:</b> Each question carries <b>+0.833 marks</b> for a correct response. Penalty for each incorrect response is <b>-0.277 marks</b> (1/3rd penalty).",
        "<b>4.</b> Candidates must encode their Roll Number and Test Booklet Series [ A ] strictly according to the UPSC OMR Answer Sheet guidelines.",
        "<b>5. DO NOT OPEN THIS TEST BOOKLET UNTIL YOU ARE TOLD TO DO SO.</b>"
    ]
    inst_t = Table([[Paragraph(txt, styles['InstText'])] for txt in instructions], colWidths=[523])
    inst_t.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(inst_t)
    story.append(PageBreak())

    # 2. Section Header
    sec_header = Table([[
        Paragraph(f"<b>SECTION : {subject_title.upper()} ({len(questions)} QUESTIONS)</b>", styles['ChapBanner'])
    ]], colWidths=[523])
    sec_header.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#fef3c7")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#d97706")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(sec_header)
    story.append(Spacer(1, 4))

    # 3. Question Items
    for idx, q in enumerate(questions):
        item_no = idx + 1
        stem_safe = escape_xml(q['question'])
        src_safe = escape_xml(q.get('source', 'UPSC CDS Official Archive'))
        oa = escape_xml(q['options'].get('a', ''))
        ob = escape_xml(q['options'].get('b', ''))
        oc = escape_xml(q['options'].get('c', ''))
        od = escape_xml(q['options'].get('d', ''))

        max_len = max(len(oa), len(ob), len(oc), len(od))
        q_flowables = [Paragraph(f"<b>{item_no}.</b> {stem_safe} <font size=6.5 color='#64748b'>[{src_safe}]</font>", styles['QText'])]

        if max_len <= 26:
            opt_row = Table([[
                Paragraph(f"(a) {oa}", styles['OptText']),
                Paragraph(f"(b) {ob}", styles['OptText']),
                Paragraph(f"(c) {oc}", styles['OptText']),
                Paragraph(f"(d) {od}", styles['OptText']),
            ]], colWidths=[128, 128, 128, 128])
        elif max_len <= 65:
            opt_row = Table([
                [Paragraph(f"(a) {oa}", styles['OptText']), Paragraph(f"(b) {ob}", styles['OptText'])],
                [Paragraph(f"(c) {oc}", styles['OptText']), Paragraph(f"(d) {od}", styles['OptText'])],
            ], colWidths=[256, 256])
        else:
            opt_row = Table([
                [Paragraph(f"(a) {oa}", styles['OptText'])],
                [Paragraph(f"(b) {ob}", styles['OptText'])],
                [Paragraph(f"(c) {oc}", styles['OptText'])],
                [Paragraph(f"(d) {od}", styles['OptText'])],
            ], colWidths=[512])

        opt_row.setStyle(TableStyle([
            ('TOPPADDING', (0,0), (-1,-1), 1),
            ('BOTTOMPADDING', (0,0), (-1,-1), 1),
            ('LEFTPADDING', (0,0), (-1,-1), 2),
        ]))
        q_flowables.append(opt_row)

        q_box = Table([[q_flowables]], colWidths=[523])
        q_box.setStyle(TableStyle([
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
            ('RIGHTPADDING', (0,0), (-1,-1), 4),
            ('LINEBELOW', (0,0), (-1,-1), 0.3, colors.HexColor("#e2e8f0")),
        ]))
        story.append(KeepTogether([q_box, Spacer(1, 2)]))

    # Canvas setup
    def make_canvas(*args, **kwargs):
        c = UPSCSubjectCanvas(*args, **kwargs)
        c.doc_subject = subject_title
        c.doc_code = tbc_code
        return c

    doc_out = SimpleDocTemplate(output_pdf, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=40, bottomMargin=55)
    doc_out.build(story, canvasmaker=make_canvas)
    print(f"  -> Generated Question Paper: {output_pdf}")


def build_subject_answer_key(subject_id, subject_title, questions, output_pdf, tbc_code):
    print(f"Generating Companion Answer Key & Solutions for Subject {subject_id}: {subject_title}...")
    styles = get_styles()
    story = []

    story.append(Paragraph("<b>UNION PUBLIC SERVICE COMMISSION (UPSC)</b>", styles['CovTitle']))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>CDS GENERAL KNOWLEDGE — SUBJECT {subject_id}: {subject_title.upper()}</b>", styles['CovSub']))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>OFFICIAL MASTER ANSWER KEY & COMPREHENSIVE EXPLANATIONS</b>", styles['CovBadge']))
    story.append(Spacer(1, 10))

    # 1. Scoring Grid
    rows = []
    num_cols = min(10, max(5, len(questions) // 5))
    total_items = len(questions)
    num_rows = (total_items + num_cols - 1) // num_cols

    header = []
    for _ in range(num_cols):
        header.extend([Paragraph("<b>Q#</b>", styles['GridHead']), Paragraph("<b>Ans</b>", styles['GridHead'])])
    rows.append(header)

    for r in range(num_rows):
        row_data = []
        for c in range(num_cols):
            idx = c * num_rows + r
            if idx < total_items:
                q = questions[idx]
                row_data.append(Paragraph(f"<b>{idx + 1}</b>", styles['GridText']))
                row_data.append(Paragraph(f"<b>({q['correct_answer'].upper()})</b>", styles['GridText']))
            else:
                row_data.extend(["", ""])
        rows.append(row_data)

    col_w = 520 / (num_cols * 2)
    kt = Table(rows, colWidths=[col_w, col_w] * num_cols)
    kt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.4, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(kt)
    story.append(Spacer(1, 14))

    # 2. Detailed Explanations
    story.append(Paragraph("<b>COMPREHENSIVE CONCEPTUAL SOLUTIONS & RATIONALES:</b>", styles['ChapBanner']))
    for idx, q in enumerate(questions):
        item_no = idx + 1
        exp = escape_xml(q.get('explanation', f"Standard UPSC CDS rationale assessing {subject_title}."))
        q_text = escape_xml(q['question'])
        ans_letter = q['correct_answer'].upper()
        correct_opt_text = escape_xml(q['options'].get(q['correct_answer'].lower(), ''))

        q_sol_data = [
            [Paragraph(f"<b>Q.{item_no} — Official Correct Answer: ({ans_letter}) {correct_opt_text}</b>", styles['SolHead'])],
            [Paragraph(f"<b>Question:</b> {q_text}<br/><b>Solution Rationale:</b> {exp}", styles['SolBody'])]
        ]
        q_sol_t = Table(q_sol_data, colWidths=[520])
        q_sol_t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f8fafc")),
            ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor("#94a3b8")),
            ('LINEBELOW', (0,0), (-1,0), 0.6, colors.HexColor("#cbd5e1")),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(KeepTogether([q_sol_t, Spacer(1, 4)]))

    doc_key_out = SimpleDocTemplate(output_pdf, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=40, bottomMargin=40)
    doc_key_out.build(story)
    print(f"  -> Generated Companion Answer Key: {output_pdf}")


def generate_all_subject_pdfs():
    with open('data/cds_gs_complete_chapterwise.json', 'r', encoding='utf-8') as f:
        all_qs = json.load(f)

    subject_configs = [
        {
            "id": 1,
            "title": "Indian Polity & Constitution",
            "file_q": "UPSC_CDS_GS_Subject_1_Indian_Polity_and_Constitution.pdf",
            "file_k": "UPSC_CDS_GS_Subject_1_Indian_Polity_Answer_Key.pdf",
            "tbc": "CDS-GS-POL-24-A"
        },
        {
            "id": 2,
            "title": "Indian History & Freedom Struggle",
            "file_q": "UPSC_CDS_GS_Subject_2_Indian_History_and_Freedom_Struggle.pdf",
            "file_k": "UPSC_CDS_GS_Subject_2_Indian_History_Answer_Key.pdf",
            "tbc": "CDS-GS-HIS-24-A"
        },
        {
            "id": 3,
            "title": "Geography (Physical, Indian & World)",
            "file_q": "UPSC_CDS_GS_Subject_3_Geography_Physical_Indian_World.pdf",
            "file_k": "UPSC_CDS_GS_Subject_3_Geography_Answer_Key.pdf",
            "tbc": "CDS-GS-GEO-24-A"
        },
        {
            "id": 4,
            "title": "General Science (Physics, Chemistry, Biology)",
            "file_q": "UPSC_CDS_GS_Subject_4_General_Science_Physics_Chemistry_Biology.pdf",
            "file_k": "UPSC_CDS_GS_Subject_4_General_Science_Answer_Key.pdf",
            "tbc": "CDS-GS-SCI-24-A"
        },
        {
            "id": 5,
            "title": "Indian Economy & Social Development",
            "file_q": "UPSC_CDS_GS_Subject_5_Indian_Economy_and_Social_Development.pdf",
            "file_k": "UPSC_CDS_GS_Subject_5_Indian_Economy_Answer_Key.pdf",
            "tbc": "CDS-GS-ECO-24-A"
        },
        {
            "id": 6,
            "title": "Defence, Security & Current Affairs",
            "file_q": "UPSC_CDS_GS_Subject_6_Defence_Security_and_Current_Affairs.pdf",
            "file_k": "UPSC_CDS_GS_Subject_6_Defence_Security_Answer_Key.pdf",
            "tbc": "CDS-GS-DEF-24-A"
        }
    ]

    print("=== GENERATING ALL 6 SUBJECT-WISE QUESTION PAPERS & ANSWER KEYS ===")
    manifest = []
    for cfg in subject_configs:
        subj_qs = [q for q in all_qs if q['chapter_id'] == cfg['id']]
        print(f"\nProcessing Subject {cfg['id']}: {cfg['title']} ({len(subj_qs)} Questions)...")
        build_subject_question_paper(cfg['id'], cfg['title'], subj_qs, cfg['file_q'], cfg['tbc'])
        build_subject_answer_key(cfg['id'], cfg['title'], subj_qs, cfg['file_k'], cfg['tbc'])
        manifest.append({
            "subject_id": cfg['id'],
            "title": cfg['title'],
            "questions_count": len(subj_qs),
            "question_pdf": cfg['file_q'],
            "answer_key_pdf": cfg['file_k']
        })

    with open('data/subject_wise_manifest.json', 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    print("\nSUCCESS: All 6 Subject-Wise Question Papers and Answer Keys Generated!")

if __name__ == '__main__':
    generate_all_subject_pdfs()
