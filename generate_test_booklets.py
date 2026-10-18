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

class UPSCNumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []
        self.doc_title = "COMBINED DEFENCE SERVICES EXAMINATION"
        self.doc_subject = "GENERAL ENGLISH"

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
        # Page 1 is the official cover page
        if self._pageNumber == 1:
            return

        # Running Header for Page 2+
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.drawString(36, h - 28, "UPSC CDS EXAMINATION")
        self.setFont("Helvetica", 8)
        self.drawString(160, h - 28, f"|  {self.doc_subject.upper()}  |  TEST BOOKLET SERIES [ A ]")
        self.drawRightString(w - 36, h - 28, f"T.B.C. : CDS-2024-A")
        
        self.setLineWidth(0.8)
        self.setStrokeColor(colors.black)
        self.line(36, h - 33, w - 36, h - 33)

        # Bottom Running Footer (Space for rough work + page number)
        rough_top = 58
        self.setStrokeColor(colors.HexColor("#64748b"))
        self.setDash([2, 2])
        self.setLineWidth(0.6)
        self.line(36, rough_top, w - 36, rough_top)
        
        self.setFont("Helvetica-Oblique", 7)
        self.setFillColor(colors.HexColor("#475569"))
        self.drawCentredString(w/2, rough_top - 10, "— SPACE FOR ROUGH WORK —")

        self.setFont("Helvetica", 8)
        self.setFillColor(colors.black)
        self.drawCentredString(w/2, 20, f"- {self._pageNumber} -")
        self.restoreState()


def create_cover_page(styles, subject_title, paper_code, total_questions, max_marks, tbc_code):
    story = []

    # Outer border table
    top_header_data = [
        [
            Paragraph(f"<b>T.B.C. : {tbc_code}</b><br/><font size=7.5>Serial No. <b>589201</b></font>", styles['CoverLeft']),
            Paragraph("<b>TEST BOOKLET<br/><font size=16 color='#b91c1c'>[ A ]</font></b><br/><font size=7.5>SERIES</font>", styles['CoverCenterBox']),
            Paragraph(f"<b>Time Allowed : Two Hours</b><br/><b>Maximum Marks : {max_marks}</b>", styles['CoverRight'])
        ]
    ]
    top_t = Table(top_header_data, colWidths=[175, 173, 175])
    top_t.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1.2, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.8, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(top_t)
    story.append(Spacer(1, 14))

    # Commission & Exam Titles
    story.append(Paragraph("<b>UNION PUBLIC SERVICE COMMISSION</b>", styles['CoverMainTitle']))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>COMBINED DEFENCE SERVICES (CDS) EXAMINATION</b>", styles['CoverSubTitle']))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"<b>TEST BOOKLET</b><br/><font size=12><b>{subject_title.upper()}</b></font>", styles['CoverExamBadge']))
    story.append(Spacer(1, 12))

    # Roll Number Input Box
    roll_cells = [["R", "O", "L", "L", "", "N", "O", "."]] + [["" for _ in range(7)]]
    roll_table_data = [
        [
            Paragraph("<b>ENTER ROLL NO. :</b>", styles['RollLabel']),
            Table([["" for _ in range(7)]], colWidths=[24]*7, rowHeights=[26])
        ]
    ]
    roll_t = Table(roll_table_data, colWidths=[180, 200])
    roll_t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (1,0), (1,0), 1.2, colors.black),
        ('INNERGRID', (1,0), (1,0), 1, colors.black),
    ]))
    story.append(roll_t)
    story.append(Spacer(1, 14))

    # Official Instructions
    story.append(Paragraph("<b>INSTRUCTIONS TO CANDIDATES</b>", styles['InstHead']))
    story.append(Spacer(1, 4))

    neg_text = "0.33 mark" if max_marks == 100 and total_questions == 100 else "0.28 mark (one-third)"

    instructions = [
        "<b>1.</b> IMMEDIATELY AFTER THE COMMENCEMENT OF THE EXAMINATION, YOU SHOULD CHECK THAT THIS TEST BOOKLET DOES NOT HAVE ANY UNPRINTED OR TORN OR MISSING PAGES OR ITEMS, ETC. IF SO, GET IT REPLACED BY A COMPLETE TEST BOOKLET.",
        "<b>2.</b> Please note that it is the candidate's responsibility to encode and fill in the <b>Roll Number</b> and <b>Test Booklet Series Code A, B, C or D</b> carefully and without any omission or discrepancy at the appropriate places in the OMR Answer Sheet. Any omission/discrepancy will render the Answer Sheet liable for rejection.",
        "<b>3.</b> You have to enter your Roll Number on the Test Booklet in the Box provided above. <b>DO NOT write anything else on the Test Booklet.</b>",
        f"<b>4.</b> This Test Booklet contains <b>{total_questions} items (questions)</b>. Each item comprises four responses (answers). You will select the response which you want to mark on the Answer Sheet. In case you feel that there is more than one correct response, mark the response which you consider the best. In any case, choose <b>ONLY ONE</b> response for each item.",
        "<b>5.</b> You have to mark all your responses <b>ONLY on the separate Answer Sheet provided</b>. See directions in the Answer Sheet.",
        "<b>6.</b> All items carry equal marks.",
        "<b>7.</b> Before you proceed to mark in the Answer Sheet the response to various items in the Test Booklet, you have to fill in some particulars in the Answer Sheet as per instructions sent to you with your Admission Certificate.",
        "<b>8.</b> After you have completed the examination, you should hand over to the Invigilator only the Answer Sheet. You are permitted to take away with you the Test Booklet.",
        "<b>9.</b> Sheets for rough work are appended in the Test Booklet at the end.",
        f"<b>10. PENALTY FOR WRONG ANSWERS :</b><br/>"
        f"THERE WILL BE PENALTY FOR WRONG ANSWERS MARKED BY A CANDIDATE IN THE OBJECTIVE TYPE QUESTION PAPERS.<br/>"
        f"(i) There are four alternatives for the answer to every question. For each question for which a wrong answer has been given by the candidate, <b>one-third ({neg_text})</b> of the marks assigned to that question will be deducted as penalty.<br/>"
        f"(ii) If a candidate gives more than one answer, it will be treated as a wrong answer even if one of the given answers happens to be correct and there will be same penalty as above to that question.<br/>"
        f"(iii) If a question is left blank, i.e., no answer is given by the candidate, there will be no penalty for that question."
    ]

    inst_table_data = [[Paragraph(txt, styles['InstBody'])] for txt in instructions]
    inst_t = Table(inst_table_data, colWidths=[520])
    inst_t.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(inst_t)
    story.append(Spacer(1, 14))

    # Bottom Warning
    story.append(Paragraph("<b>DO NOT OPEN THIS TEST BOOKLET UNTIL YOU ARE TOLD TO DO SO</b>", styles['CoverWarning']))
    story.append(PageBreak())

    return story


def build_test_booklet_pdf(data_file, output_filename, subject_title, total_questions, max_marks, tbc_code):
    with open(data_file, 'r', encoding='utf-8') as f:
        questions = json.load(f)

    # Styles
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle('CoverLeft', fontName='Helvetica', fontSize=8.5, leading=11, alignment=TA_LEFT))
    styles.add(ParagraphStyle('CoverCenterBox', fontName='Helvetica', fontSize=9, leading=12, alignment=TA_CENTER))
    styles.add(ParagraphStyle('CoverRight', fontName='Helvetica', fontSize=8.5, leading=11, alignment=TA_RIGHT))
    styles.add(ParagraphStyle('CoverMainTitle', fontName='Helvetica-Bold', fontSize=14, leading=17, alignment=TA_CENTER))
    styles.add(ParagraphStyle('CoverSubTitle', fontName='Helvetica-Bold', fontSize=11, leading=14, alignment=TA_CENTER))
    styles.add(ParagraphStyle('CoverExamBadge', fontName='Helvetica-Bold', fontSize=13, leading=17, alignment=TA_CENTER))
    styles.add(ParagraphStyle('RollLabel', fontName='Helvetica-Bold', fontSize=9.5, leading=12, alignment=TA_LEFT))
    styles.add(ParagraphStyle('InstHead', fontName='Helvetica-Bold', fontSize=10, leading=13, alignment=TA_CENTER))
    styles.add(ParagraphStyle('InstBody', fontName='Helvetica', fontSize=7.5, leading=10, alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle('CoverWarning', fontName='Helvetica-Bold', fontSize=10, leading=13, alignment=TA_CENTER))

    styles.add(ParagraphStyle('SectionBanner', fontName='Helvetica-Bold', fontSize=10, leading=13, textColor=colors.HexColor("#0f172a"), spaceBefore=10, spaceAfter=6))
    styles.add(ParagraphStyle('QNum', fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=colors.black))
    styles.add(ParagraphStyle('QText', fontName='Helvetica', fontSize=8.5, leading=11.5, alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle('QSource', fontName='Helvetica-Oblique', fontSize=7, leading=9, textColor=colors.HexColor("#475569")))
    styles.add(ParagraphStyle('OptionText', fontName='Helvetica', fontSize=8.2, leading=11))

    doc = SimpleDocTemplate(
        output_filename,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=42,
        bottomMargin=70
    )

    story = []
    # 1. Add Cover Page
    story.extend(create_cover_page(styles, subject_title, "CDS", total_questions, max_marks, tbc_code))

    # 2. Add Questions
    current_section = None
    for idx, q in enumerate(questions):
        sec = q.get('section', '')
        if sec != current_section:
            current_section = sec
            sec_table = Table([[
                Paragraph(f"<b>SECTION : {sec.upper()}</b>", styles['SectionBanner'])
            ]], colWidths=[523])
            sec_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f1f5f9")),
                ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor("#94a3b8")),
                ('TOPPADDING', (0,0), (-1,-1), 4),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                ('LEFTPADDING', (0,0), (-1,-1), 8),
            ]))
            story.append(sec_table)
            story.append(Spacer(1, 6))

        # Format Options: check length to decide horizontal or 2x2 grid
        opts = q.get('options', {})
        oa = escape_xml(opts.get('a', ''))
        ob = escape_xml(opts.get('b', ''))
        oc = escape_xml(opts.get('c', ''))
        od = escape_xml(opts.get('d', ''))

        max_opt_len = max(len(oa), len(ob), len(oc), len(od))
        
        q_rows = []
        # Question stem row
        q_stem_text = escape_xml(q.get('question', ''))
        q_src_text = escape_xml(q.get('source', ''))
        q_stem_html = f"<b>{q['id']}.</b> {q_stem_text} <font size=7 color='#64748b'>[{q_src_text}]</font>"
        q_rows.append([Paragraph(q_stem_html, styles['QText'])])

        if max_opt_len <= 28:
            # 1 row with 4 options
            opt_table_data = [[
                Paragraph(f"(a) {oa}", styles['OptionText']),
                Paragraph(f"(b) {ob}", styles['OptionText']),
                Paragraph(f"(c) {oc}", styles['OptionText']),
                Paragraph(f"(d) {od}", styles['OptionText']),
            ]]
            opt_t = Table(opt_table_data, colWidths=[128, 128, 128, 128])
            opt_t.setStyle(TableStyle([
                ('TOPPADDING', (0,0), (-1,-1), 2),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                ('LEFTPADDING', (0,0), (-1,-1), 4),
            ]))
            q_rows.append([opt_t])
        elif max_opt_len <= 65:
            # 2 rows with 2 options
            opt_table_data = [
                [Paragraph(f"(a) {oa}", styles['OptionText']), Paragraph(f"(b) {ob}", styles['OptionText'])],
                [Paragraph(f"(c) {oc}", styles['OptionText']), Paragraph(f"(d) {od}", styles['OptionText'])],
            ]
            opt_t = Table(opt_table_data, colWidths=[256, 256])
            opt_t.setStyle(TableStyle([
                ('TOPPADDING', (0,0), (-1,-1), 2),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                ('LEFTPADDING', (0,0), (-1,-1), 4),
            ]))
            q_rows.append([opt_t])
        else:
            # 4 stacked rows
            opt_table_data = [
                [Paragraph(f"(a) {oa}", styles['OptionText'])],
                [Paragraph(f"(b) {ob}", styles['OptionText'])],
                [Paragraph(f"(c) {oc}", styles['OptionText'])],
                [Paragraph(f"(d) {od}", styles['OptionText'])],
            ]
            opt_t = Table(opt_table_data, colWidths=[512])
            opt_t.setStyle(TableStyle([
                ('TOPPADDING', (0,0), (-1,-1), 2),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                ('LEFTPADDING', (0,0), (-1,-1), 4),
            ]))
            q_rows.append([opt_t])

        q_table = Table(q_rows, colWidths=[523])
        q_table.setStyle(TableStyle([
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ('LINEBELOW', (0,-1), (-1,-1), 0.4, colors.HexColor("#e2e8f0")),
        ]))
        story.append(KeepTogether([q_table, Spacer(1, 4)]))

    # Dedicated Rough Work Page at end
    story.append(PageBreak())
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>SPACE FOR ROUGH WORK</b>", styles['CoverMainTitle']))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceAfter=20))

    # Custom Canvas Setup
    def make_canvas(*args, **kwargs):
        c = UPSCNumberedCanvas(*args, **kwargs)
        c.doc_subject = subject_title
        return c

    doc.build(story, canvasmaker=make_canvas)
    print(f"Generated Test Booklet: {output_filename}")


def build_answer_keys_pdf(output_filename="UPSC_CDS_Official_Answer_Keys_and_Solutions.pdf"):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle('AKTitle', fontName='Helvetica-Bold', fontSize=15, leading=19, alignment=TA_CENTER))
    styles.add(ParagraphStyle('Sub', fontName='Helvetica-Bold', fontSize=11, leading=14, alignment=TA_CENTER))
    styles.add(ParagraphStyle('H2', fontName='Helvetica-Bold', fontSize=11, leading=14, textColor=colors.HexColor("#1e3a8a"), spaceBefore=12, spaceAfter=6))
    styles.add(ParagraphStyle('GridText', fontName='Helvetica', fontSize=8, leading=10, alignment=TA_CENTER))
    styles.add(ParagraphStyle('GridHead', fontName='Helvetica-Bold', fontSize=8, leading=10, alignment=TA_CENTER, textColor=colors.white))
    styles.add(ParagraphStyle('SolHead', fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=colors.HexColor("#0f172a")))
    styles.add(ParagraphStyle('SolBody', fontName='Helvetica', fontSize=8, leading=11, alignment=TA_JUSTIFY))

    doc = SimpleDocTemplate(
        output_filename,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=40,
        bottomMargin=40
    )

    story = []
    story.append(Paragraph("<b>UNION PUBLIC SERVICE COMMISSION (UPSC)</b>", styles['AKTitle']))
    story.append(Spacer(1, 3))
    story.append(Paragraph("<b>COMBINED DEFENCE SERVICES (CDS) EXAMINATION</b>", styles['Sub']))
    story.append(Spacer(1, 2))
    story.append(Paragraph("<b>OFFICIAL ANSWER KEYS & DETAILED SOLUTIONS GUIDE</b>", styles['Sub']))
    story.append(Spacer(1, 10))

    # Scoring Benchmark Table
    bench_data = [
        [Paragraph("<b>Paper / Subject</b>", styles['GridHead']), Paragraph("<b>Items</b>", styles['GridHead']), Paragraph("<b>Max Marks</b>", styles['GridHead']), Paragraph("<b>Scoring Formula</b>", styles['GridHead']), Paragraph("<b>Qualifying Cutoff</b>", styles['GridHead'])],
        [Paragraph("Paper I : General English", styles['GridText']), Paragraph("120", styles['GridText']), Paragraph("100", styles['GridText']), Paragraph("+0.833 / -0.277 (1/3rd)", styles['GridText']), Paragraph("20.00 Marks (20%)", styles['GridText'])],
        [Paragraph("Paper II : General Knowledge", styles['GridText']), Paragraph("120", styles['GridText']), Paragraph("100", styles['GridText']), Paragraph("+0.833 / -0.277 (1/3rd)", styles['GridText']), Paragraph("20.00 Marks (20%)", styles['GridText'])],
        [Paragraph("Paper III : Elementary Maths", styles['GridText']), Paragraph("100", styles['GridText']), Paragraph("100", styles['GridText']), Paragraph("+1.000 / -0.333 (1/3rd)", styles['GridText']), Paragraph("20.00 Marks (20%)", styles['GridText'])],
    ]
    bt = Table(bench_data, colWidths=[140, 50, 65, 145, 120])
    bt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e293b")),
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(bt)
    story.append(Spacer(1, 14))

    # Helper function to render a 10-column compact Answer Key Table
    def render_key_grid(q_list, title):
        story.append(Paragraph(f"<b>{title.upper()} - OFFICIAL SCORING GRID (SERIES A)</b>", styles['H2']))
        rows = []
        # Header row
        header = []
        for i in range(10):
            header.extend([Paragraph("<b>Q#</b>", styles['GridHead']), Paragraph("<b>Ans</b>", styles['GridHead'])])
        rows.append(header)

        # 10 columns of Q#/Ans
        num_cols = 10
        total_items = len(q_list)
        num_rows = (total_items + num_cols - 1) // num_cols

        for r in range(num_rows):
            row_data = []
            for c in range(num_cols):
                idx = c * num_rows + r
                if idx < total_items:
                    q = q_list[idx]
                    row_data.append(Paragraph(f"<b>{q['id']}</b>", styles['GridText']))
                    row_data.append(Paragraph(f"<b>({q['correct_answer'].upper()})</b>", styles['GridText']))
                else:
                    row_data.extend(["", ""])
            rows.append(row_data)

        col_widths = [26, 26] * 10
        kt = Table(rows, colWidths=col_widths)
        kt.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
            ('BOX', (0,0), (-1,-1), 1, colors.black),
            ('INNERGRID', (0,0), (-1,-1), 0.4, colors.HexColor("#cbd5e1")),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ]))
        story.append(kt)
        story.append(Spacer(1, 12))

    # English Keys
    with open('data/cds_mock_english_120.json', 'r', encoding='utf-8') as f:
        eng_qs = json.load(f)
    render_key_grid(eng_qs, "Paper I : General English (120 Questions)")

    # GS Keys
    with open('data/cds_mock_gs_120.json', 'r', encoding='utf-8') as f:
        gs_qs = json.load(f)
    render_key_grid(gs_qs, "Paper II : General Knowledge (120 Questions)")

    # Math Keys
    with open('data/cds_mock_math_100.json', 'r', encoding='utf-8') as f:
        math_qs = json.load(f)
    render_key_grid(math_qs, "Paper III : Elementary Mathematics (100 Questions)")

    # GS Explanations Section
    story.append(PageBreak())
    story.append(Paragraph("<b>GENERAL KNOWLEDGE (GS) — IN-DEPTH OFFICIAL EXPLANATIONS & RATIONALES</b>", styles['H2']))
    story.append(Spacer(1, 6))

    for q in gs_qs:
        exp_text = escape_xml(q.get('explanation', ''))
        q_text = escape_xml(q.get('question', ''))
        sec_text = escape_xml(q.get('section', ''))
        q_sol_data = [
            [
                Paragraph(f"<b>Q.{q['id']} [{sec_text}] — Correct Answer: ({q['correct_answer'].upper()})</b>", styles['SolHead'])
            ],
            [
                Paragraph(f"<b>Question:</b> {q_text}<br/><b>Explanation:</b> {exp_text}", styles['SolBody'])
            ]
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

    doc.build(story)
    print(f"Generated Official Answer Keys & Explanations: {output_filename}")


if __name__ == "__main__":
    print("Generating UPSC CDS Real Test Booklets...")
    build_test_booklet_pdf(
        "data/cds_mock_english_120.json",
        "UPSC_CDS_Paper_I_English_Real_Test_Paper.pdf",
        "GENERAL ENGLISH",
        120,
        100,
        "CDS-ENG-24-A"
    )

    build_test_booklet_pdf(
        "data/cds_mock_gs_120.json",
        "UPSC_CDS_Paper_II_General_Knowledge_Real_Test_Paper.pdf",
        "GENERAL KNOWLEDGE",
        120,
        100,
        "CDS-GS-24-A"
    )

    build_test_booklet_pdf(
        "data/cds_mock_math_100.json",
        "UPSC_CDS_Paper_III_Elementary_Mathematics_Real_Test_Paper.pdf",
        "ELEMENTARY MATHEMATICS",
        100,
        100,
        "CDS-MATH-24-A"
    )

    build_answer_keys_pdf("UPSC_CDS_Official_Answer_Keys_and_Solutions.pdf")
    print("ALL UPSC TEST BOOKLETS & KEYS GENERATED SUCCESSFULLY!")
