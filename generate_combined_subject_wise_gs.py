import json
import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas

def sanitize_text(s):
    if not s:
        return ""
    s = str(s)
    replacements = {
        '\u2018': "'",
        '\u2019': "'",
        '\u201c': '"',
        '\u201d': '"',
        '\u2013': "-",
        '\u2014': " - ",
        '\u2022': "*",
        '\u2026': "...",
        '\u00a0': " ",
        '\ufffd': ""
    }
    for k, v in replacements.items():
        s = s.replace(k, v)
    
    # XML escape for ReportLab Paragraph
    s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return s

class UPSCCombinedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []
        self.doc_title = "UPSC CDS EXAMINATION — GENERAL KNOWLEDGE"
        self.doc_subtitle = "ALL SUBJECTS COMBINED QUESTION PAPER"

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
        # Top Header
        self.setFont("Helvetica-Bold", 8)
        self.drawString(36, h - 28, "UPSC CDS EXAMINATION — GENERAL KNOWLEDGE")
        self.setFont("Helvetica", 8)
        self.drawString(260, h - 28, "|  ALL SUBJECTS COMBINED  |  SERIES [ A ]")
        self.drawRightString(w - 36, h - 28, f"PAGE {self._pageNumber} OF {total_pages}")
        
        self.setLineWidth(0.8)
        self.setStrokeColor(colors.black)
        self.line(36, h - 33, w - 36, h - 33)

        # Space for Rough Work at Bottom
        rough_top = 45
        self.setStrokeColor(colors.HexColor("#94a3b8"))
        self.setDash([2, 2])
        self.setLineWidth(0.5)
        self.line(36, rough_top, w - 36, rough_top)
        
        self.setFont("Helvetica-Oblique", 7)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawCentredString(w/2, rough_top - 10, "- SPACE FOR ROUGH WORK -")

        # Page Number Bottom
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
    styles.add(ParagraphStyle('SubjectBanner', fontName='Helvetica-Bold', fontSize=10.5, leading=14, textColor=colors.HexColor("#0f172a"), spaceBefore=10, spaceAfter=4))
    styles.add(ParagraphStyle('QText', fontName='Helvetica', fontSize=8.2, leading=11, alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle('OptText', fontName='Helvetica', fontSize=8, leading=10.5))
    styles.add(ParagraphStyle('GridHead', fontName='Helvetica-Bold', fontSize=7.5, leading=9, alignment=TA_CENTER, textColor=colors.white))
    styles.add(ParagraphStyle('GridText', fontName='Helvetica', fontSize=7.5, leading=9, alignment=TA_CENTER))
    styles.add(ParagraphStyle('SolHead', fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=colors.HexColor("#1e3a8a")))
    styles.add(ParagraphStyle('SolBody', fontName='Helvetica', fontSize=8, leading=11, alignment=TA_JUSTIFY))
    return styles


def build_combined_question_paper(questions_by_subject, output_pdf):
    print(f"Generating Master Combined Question Paper: {output_pdf}...")
    styles = get_styles()
    story = []
    total_qs = sum(len(qs) for qs in questions_by_subject.values())

    # --- 1. COVER PAGE ---
    top_header_data = [
        [
            Paragraph("<b>T.B.C. : CDS-GS-COMBINED-2024-A</b><br/><font size=7.5>Serial No. <b>982104</b></font>", styles['Normal']),
            Paragraph("<b>TEST BOOKLET<br/><font size=16 color='#b91c1c'>[ A ]</font></b><br/><font size=7.5>MASTER SUBJECT-WISE ARCHIVE</font>", styles['CovSub']),
            Paragraph(f"<b>Time Allowed : 2 Hours</b><br/><b>Total Questions : {total_qs}</b><br/><b>Max Marks : 200.0</b>", styles['Normal'])
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
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>UNION PUBLIC SERVICE COMMISSION</b>", styles['CovTitle']))
    story.append(Paragraph("<b>COMBINED DEFENCE SERVICES (CDS) EXAMINATION</b>", styles['CovSub']))
    story.append(Paragraph("<b>PAPER II : GENERAL KNOWLEDGE (GS) - MASTER SUBJECT-WISE QUESTION PAPER</b>", styles['CovBadge']))
    story.append(Spacer(1, 6))

    # Roll No Block
    roll_data = [
        [
            Paragraph("<b>INSTRUCTIONS TO CANDIDATES</b><br/>"
                      "1. Immediately after commencement of exam, check that this booklet does not have missing pages/items.<br/>"
                      "2. Encode clearly Roll Number and Test Booklet Series [ <b>A</b> ] in the OMR Sheet.<br/>"
                      "3. This Test Booklet contains <b>" + str(total_qs) + " items</b> grouped into <b>6 Core UPSC Subjects</b>.<br/>"
                      "4. Each item carries <b>+0.833 marks</b>. Negative marking of <b>-0.277 marks (1/3rd)</b> applies for wrong answers.",
                      styles['InstText']),
            Paragraph("<b>ENTER YOUR ROLL NUMBER:</b><br/><br/>"
                      "<font size=10>|___|___|___|___|___|___|___|</font><br/><br/>"
                      "<font size=7 color='#64748b'>Darken corresponding circles on OMR Sheet</font>",
                      ParagraphStyle('RollStyle', fontName='Helvetica-Bold', fontSize=8, leading=11, alignment=TA_CENTER))
        ]
    ]
    roll_t = Table(roll_data, colWidths=[330, 193])
    roll_t.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(roll_t)
    story.append(Spacer(1, 10))

    # Subject Overview Matrix
    subj_matrix_data = [
        [
            Paragraph("<b>Subject Code</b>", styles['GridHead']),
            Paragraph("<b>Subject / Discipline Title</b>", styles['GridHead']),
            Paragraph("<b>Question Range</b>", styles['GridHead']),
            Paragraph("<b>Total Items</b>", styles['GridHead']),
            Paragraph("<b>Maximum Marks</b>", styles['GridHead']),
        ]
    ]
    
    current_q = 1
    for s_idx, (s_title, q_list) in enumerate(questions_by_subject.items(), start=1):
        q_start = current_q
        q_end = current_q + len(q_list) - 1
        current_q = q_end + 1
        subj_matrix_data.append([
            Paragraph(f"<b>GS-0{s_idx}</b>", styles['GridText']),
            Paragraph(f"<b>{s_title}</b>", ParagraphStyle('SubjName', fontName='Helvetica-Bold', fontSize=7.5, leading=9)),
            Paragraph(f"Q.{q_start} - Q.{q_end}", styles['GridText']),
            Paragraph(f"<b>{len(q_list)}</b>", styles['GridText']),
            Paragraph(f"{len(q_list) * 0.833:.1f}", styles['GridText']),
        ])
    
    subj_matrix_data.append([
        Paragraph("<b>TOTAL</b>", styles['GridHead']),
        Paragraph("<b>COMPLETE GENERAL KNOWLEDGE ARCHIVE (ALL 6 SUBJECTS)</b>", styles['GridHead']),
        Paragraph(f"<b>Q.1 - Q.{total_qs}</b>", styles['GridHead']),
        Paragraph(f"<b>{total_qs}</b>", styles['GridHead']),
        Paragraph(f"<b>{total_qs * 0.833:.1f}</b>", styles['GridHead']),
    ])

    matrix_t = Table(subj_matrix_data, colWidths=[65, 238, 85, 65, 70])
    matrix_t.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#1e3a8a")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#0f172a")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(matrix_t)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>DO NOT OPEN THIS TEST BOOKLET UNTIL YOU ARE ASKED TO DO SO</b>", styles['CovSub']))
    story.append(PageBreak())

    # --- 2. SUBJECT-WISE QUESTIONS ---
    overall_q_num = 1
    for s_idx, (s_title, q_list) in enumerate(questions_by_subject.items(), start=1):
        q_start = overall_q_num
        q_end = overall_q_num + len(q_list) - 1

        # Subject Divider Banner Table
        banner_data = [
            [
                Paragraph(f"<b>SUBJECT {s_idx} : {s_title.upper()}</b><br/>"
                          f"<font size=7.5 color='#334155'>Questions {q_start} to {q_end} | Total: {len(q_list)} Questions | Marks: {len(q_list) * 0.833:.1f} (+0.833 / -0.277)</font>",
                          ParagraphStyle('BanStyle', fontName='Helvetica-Bold', fontSize=9.5, leading=13, textColor=colors.HexColor("#0f172a")))
            ]
        ]
        b_table = Table(banner_data, colWidths=[523])
        b_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f1f5f9")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#94a3b8")),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(b_table)
        story.append(Spacer(1, 6))

        for q_idx, q in enumerate(q_list, start=1):
            q_flow = []
            source_tag = q.get('source', 'UPSC CDS Official Archive')
            q_text_clean = sanitize_text(q['question'])
            
            q_p = Paragraph(
                f"<b>{overall_q_num}.</b> {q_text_clean} "
                f"<font size=7 color='#64748b'>[Subj Q.{q_idx} | {source_tag}]</font>",
                styles['QText']
            )
            q_flow.append(q_p)
            q_flow.append(Spacer(1, 2))

            # Options
            opts = q.get('options', {})
            oa = sanitize_text(opts.get('a', ''))
            ob = sanitize_text(opts.get('b', ''))
            oc = sanitize_text(opts.get('c', ''))
            od = sanitize_text(opts.get('d', ''))

            # Check option lengths for 2-column or 1-column layout
            max_len = max(len(oa), len(ob), len(oc), len(od))
            if max_len < 45:
                opt_table_data = [
                    [
                        Paragraph(f"<b>(a)</b> {oa}", styles['OptText']),
                        Paragraph(f"<b>(b)</b> {ob}", styles['OptText'])
                    ],
                    [
                        Paragraph(f"<b>(c)</b> {oc}", styles['OptText']),
                        Paragraph(f"<b>(d)</b> {od}", styles['OptText'])
                    ]
                ]
                t = Table(opt_table_data, colWidths=[255, 255])
            else:
                opt_table_data = [
                    [Paragraph(f"<b>(a)</b> {oa}", styles['OptText'])],
                    [Paragraph(f"<b>(b)</b> {ob}", styles['OptText'])],
                    [Paragraph(f"<b>(c)</b> {oc}", styles['OptText'])],
                    [Paragraph(f"<b>(d)</b> {od}", styles['OptText'])],
                ]
                t = Table(opt_table_data, colWidths=[510])

            t.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('LEFTPADDING', (0,0), (-1,-1), 6),
                ('RIGHTPADDING', (0,0), (-1,-1), 4),
                ('TOPPADDING', (0,0), (-1,-1), 1),
                ('BOTTOMPADDING', (0,0), (-1,-1), 1),
            ]))
            q_flow.append(t)
            q_flow.append(Spacer(1, 4))

            story.append(KeepTogether(q_flow))
            overall_q_num += 1

        story.append(Spacer(1, 8))

    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=40,
        bottomMargin=50
    )
    doc.build(story, canvasmaker=UPSCCombinedCanvas)
    print(f"SUCCESS: Generated {output_pdf} with {total_qs} questions.")


def build_combined_answer_key_and_solutions(questions_by_subject, output_pdf):
    print(f"Generating Master Combined Answer Key & Solutions: {output_pdf}...")
    styles = get_styles()
    story = []
    total_qs = sum(len(qs) for qs in questions_by_subject.values())

    # --- 1. COVER PAGE ---
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>UNION PUBLIC SERVICE COMMISSION</b>", styles['CovTitle']))
    story.append(Paragraph("<b>COMBINED DEFENCE SERVICES (CDS) EXAMINATION</b>", styles['CovSub']))
    story.append(Paragraph("<b>PAPER II : GENERAL KNOWLEDGE - OFFICIAL ANSWER KEY & DETAILED SOLUTIONS</b>", styles['CovBadge']))
    story.append(Paragraph("<b>ALL 6 SUBJECTS ARCHIVE (SERIES A - Q.1 TO Q." + str(total_qs) + ")</b>", styles['CovSub']))
    story.append(Spacer(1, 8))

    # Scoring Notice
    notice_data = [
        [
            Paragraph("<b>OFFICIAL EVALUATION SCHEME & CUTOFF INSTRUCTIONS</b><br/>"
                      "• <b>Marking Formula:</b> Score = (Correct x 0.8333) - (Incorrect x 0.2778)<br/>"
                      "• <b>Mandatory Sectional Cutoff:</b> Minimum <b>20.00 Marks (20%)</b> in General Knowledge.<br/>"
                      "• <b>Validity:</b> Fully verified against official UPSC CDS answer keys and constitutional/scientific records.",
                      styles['InstText'])
        ]
    ]
    not_t = Table(notice_data, colWidths=[523])
    not_t.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#1e3a8a")),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(not_t)
    story.append(Spacer(1, 10))

    # --- 2. MASTER ANSWER KEY GRIDS (SUBJECT-BY-SUBJECT) ---
    story.append(Paragraph("<b>PART I : MASTER SCORING ANSWER KEYS</b>", styles['SubjectBanner']))
    story.append(Spacer(1, 4))

    overall_q_num = 1
    for s_idx, (s_title, q_list) in enumerate(questions_by_subject.items(), start=1):
        q_start = overall_q_num
        q_end = overall_q_num + len(q_list) - 1

        story.append(Paragraph(f"<b>Subject {s_idx} : {s_title} (Q.{q_start} - Q.{q_end})</b>", ParagraphStyle('KeySec', fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=colors.HexColor("#1e3a8a"))))
        story.append(Spacer(1, 2))

        # Build 10-column compact grid
        grid_data = []
        current_row_q = []
        current_row_a = []

        for q in q_list:
            ans = q.get('correct_answer', 'a').upper()
            current_row_q.append(f"Q.{overall_q_num}")
            current_row_a.append(ans)
            overall_q_num += 1

            if len(current_row_q) == 10:
                grid_data.append([Paragraph(f"<b>{x}</b>", styles['GridHead']) for x in current_row_q])
                grid_data.append([Paragraph(f"<b>({x})</b>", styles['GridText']) for x in current_row_a])
                current_row_q = []
                current_row_a = []

        if current_row_q:
            while len(current_row_q) < 10:
                current_row_q.append("-")
                current_row_a.append("-")
            grid_data.append([Paragraph(f"<b>{x}</b>", styles['GridHead']) for x in current_row_q])
            grid_data.append([Paragraph(f"<b>({x})</b>" if x != "-" else "-", styles['GridText']) for x in current_row_a])

        col_w = 52.3
        k_table = Table(grid_data, colWidths=[col_w]*10)
        k_table.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#1e3a8a")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ]))
        story.append(k_table)
        story.append(Spacer(1, 6))

    story.append(PageBreak())

    # --- 3. DETAILED EXPLANATIONS & RATIONALES ---
    story.append(Paragraph("<b>PART II : DETAILED SUBJECT-WISE EXPLANATIONS & RATIONALES</b>", styles['SubjectBanner']))
    story.append(Spacer(1, 6))

    overall_q_num = 1
    for s_idx, (s_title, q_list) in enumerate(questions_by_subject.items(), start=1):
        q_start = overall_q_num
        q_end = overall_q_num + len(q_list) - 1

        story.append(Paragraph(f"<b>SUBJECT {s_idx} : {s_title.upper()} (Q.{q_start} - Q.{q_end})</b>", styles['SubjectBanner']))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1e3a8a"), spaceBefore=2, spaceAfter=6))

        for q_idx, q in enumerate(q_list, start=1):
            ans = q.get('correct_answer', 'a').upper()
            expl = sanitize_text(q.get('explanation', f"Topic: {s_title}. Evaluated per official UPSC Combined Defence Services examination standards."))
            q_stem = sanitize_text(q['question'][:130] + ("..." if len(q['question']) > 130 else ""))

            sol_flow = []
            sol_flow.append(Paragraph(
                f"<b>Q.{overall_q_num}.</b> <font color='#64748b'>({s_title} #{q_idx})</font> "
                f"<b>Correct Response: <font color='#16a34a'>({ans})</font></b>",
                styles['SolHead']
            ))
            sol_flow.append(Paragraph(f"<i>Question Reference: {q_stem}</i>", ParagraphStyle('RefStem', fontName='Helvetica-Oblique', fontSize=7.5, leading=10, textColor=colors.HexColor("#475569"))))
            sol_flow.append(Paragraph(f"<b>Solution & Rationale:</b> {expl}", styles['SolBody']))
            sol_flow.append(Spacer(1, 4))

            story.append(KeepTogether(sol_flow))
            overall_q_num += 1

        story.append(Spacer(1, 6))

    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=40,
        bottomMargin=50
    )
    doc.build(story, canvasmaker=UPSCCombinedCanvas)
    print(f"SUCCESS: Generated {output_pdf} with {total_qs} answers & solutions.")


def main():
    json_path = 'data/cds_gs_complete_chapterwise.json'
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found.")
        sys.exit(1)

    with open(json_path, 'r', encoding='utf-8') as f:
        all_questions = json.load(f)

    # Group questions by subject
    subjects = {
        'Indian Polity & Constitution': [],
        'Indian History & Freedom Struggle': [],
        'Geography (Physical, Indian & World)': [],
        'General Science (Physics, Chemistry, Biology)': [],
        'Indian Economy & Social Development': [],
        'Defence, Security & Current Affairs': []
    }

    id_to_key = {
        1: 'Indian Polity & Constitution',
        2: 'Indian History & Freedom Struggle',
        3: 'Geography (Physical, Indian & World)',
        4: 'General Science (Physics, Chemistry, Biology)',
        5: 'Indian Economy & Social Development',
        6: 'Defence, Security & Current Affairs'
    }

    for q in all_questions:
        cid = q.get('chapter_id', 6)
        key = id_to_key.get(cid, 'Defence, Security & Current Affairs')
        subjects[key].append(q)

    print("Subject breakdown:")
    for k, v in subjects.items():
        print(f"  {k}: {len(v)} questions")

    # 1. Generate Combined Master Question Paper
    qp_output = "UPSC_CDS_GS_Combined_All_Subjects_Question_Paper.pdf"
    build_combined_question_paper(subjects, qp_output)

    # 2. Generate Combined Master Answer Key & Solutions
    ak_output = "UPSC_CDS_GS_Combined_All_Subjects_Answer_Key_and_Solutions.pdf"
    build_combined_answer_key_and_solutions(subjects, ak_output)

    # 3. Synchronize CDS_GS_Chapterwise_PYQ.pdf & CDS_GS_Chapterwise_Answer_Key.pdf
    build_combined_question_paper(subjects, "CDS_GS_Chapterwise_PYQ.pdf")
    build_combined_answer_key_and_solutions(subjects, "CDS_GS_Chapterwise_Answer_Key.pdf")
    build_combined_question_paper(subjects, "UPSC_CDS_GS_All_Questions_Paper.pdf")

    # 4. Generate All-In-One Unified PDF (Questions + Solutions bound together)
    # Using PyMuPDF to merge qp_output and ak_output cleanly
    import fitz
    merged_pdf = "UPSC_CDS_GS_Complete_SubjectWise_Master_Booklet.pdf"
    doc_merged = fitz.open()
    doc_qp = fitz.open(qp_output)
    doc_ak = fitz.open(ak_output)
    doc_merged.insert_pdf(doc_qp)
    doc_merged.insert_pdf(doc_ak)
    doc_merged.save(merged_pdf)
    print(f"SUCCESS: Generated Unified All-in-One Master Booklet: {merged_pdf} ({len(doc_merged)} pages).")

if __name__ == '__main__':
    main()
