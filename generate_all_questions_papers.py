import json, os, sys, fitz, re
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
        if self._pageNumber == 1:
            return

        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.drawString(36, h - 28, "UPSC CDS EXAMINATION — ALL QUESTIONS QUESTION PAPER")
        self.setFont("Helvetica", 8)
        self.drawString(320, h - 28, f"|  {self.doc_subject.upper()}  |  SERIES [ A ]")
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


def build_all_questions_paper(input_pdf_path, key_pdf_path, output_pdf_path, subject_title, pos_mark, neg_mark):
    print(f"Building Complete All-Questions Paper for {subject_title}...")
    doc_in = fitz.open(input_pdf_path)
    full_text = '\n'.join([p.get_text() for p in doc_in])
    
    # Parse keys if key_pdf exists
    keys = {}
    if key_pdf_path and os.path.exists(key_pdf_path):
        doc_key = fitz.open(key_pdf_path)
        key_text = '\n'.join([p.get_text() for p in doc_key])
        parts = re.split(r'CHAPTER\s+(\d+)', key_text)
        for i in range(1, len(parts), 2):
            c_num = int(parts[i])
            c_text = parts[i+1]
            matches = re.findall(r'(?:^|\n)\s*(\d+)\s*\n\s*\(?([a-dA-D])\)?', c_text)
            keys[c_num] = dict([(int(q), ans.lower()) for q, ans in matches])

    chap_splits = re.split(r'CHAPTER\s+(\d+)', full_text)
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle('CovTitle', fontName='Helvetica-Bold', fontSize=15, leading=19, alignment=TA_CENTER))
    styles.add(ParagraphStyle('CovSub', fontName='Helvetica-Bold', fontSize=11, leading=14, alignment=TA_CENTER))
    styles.add(ParagraphStyle('CovBadge', fontName='Helvetica-Bold', fontSize=13, leading=17, alignment=TA_CENTER, textColor=colors.HexColor("#1e3a8a")))
    styles.add(ParagraphStyle('InstText', fontName='Helvetica', fontSize=8, leading=11, alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle('ChapBanner', fontName='Helvetica-Bold', fontSize=10.5, leading=14, textColor=colors.HexColor("#0f172a"), spaceBefore=10, spaceAfter=4))
    styles.add(ParagraphStyle('QText', fontName='Helvetica', fontSize=8.2, leading=11, alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle('OptText', fontName='Helvetica', fontSize=8, leading=10.5))
    styles.add(ParagraphStyle('TOCItem', fontName='Helvetica', fontSize=8.5, leading=12))
    styles.add(ParagraphStyle('TOCBold', fontName='Helvetica-Bold', fontSize=8.5, leading=12))

    story = []

    # 1. Official Cover Page
    top_header_data = [
        [
            Paragraph(f"<b>T.B.C. : CDS-ALL-{subject_title[:4].upper()}-A</b><br/><font size=7.5>Serial No. <b>940281</b></font>", styles['Normal']),
            Paragraph("<b>TEST BOOKLET<br/><font size=16 color='#b91c1c'>[ A ]</font></b><br/><font size=7.5>COMPLETE REPOSITORY</font>", styles['CovSub']),
            Paragraph(f"<b>Comprehensive Archive</b><br/><b>Marks Scheme: +{pos_mark} / -{neg_mark}</b>", styles['Normal'])
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
    story.append(Spacer(1, 8))
    story.append(Paragraph(f"<b>OFFICIAL QUESTION PAPER — ALL QUESTIONS COMPLETE ARCHIVE</b><br/><font size=12><b>{subject_title.upper()}</b></font>", styles['CovBadge']))
    story.append(Spacer(1, 12))

    # Instructions box
    instructions = [
        "<b>1.</b> This comprehensive question paper contains <b>ALL Previous Year Questions</b> extracted directly from official UPSC Combined Defence Services examination archives across all chapters.",
        "<b>2.</b> Candidates are advised to practice these questions under authentic timed conditions using the companion UPSC CDS OMR Sheet.",
        f"<b>3. SCORING FORMULA:</b> Each correct response awards <b>+{pos_mark} marks</b>. Each incorrect response incurs a penalty deduction of <b>-{neg_mark} marks (one-third)</b>. Unattempted items carry 0 marks.",
        "<b>4.</b> Official chapter-wise answer keys and scoring guides are provided in the companion evaluation guide.",
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
    story.append(Spacer(1, 14))

    # 2. Extract and format all questions by chapter
    total_q_count = 0
    toc_data = [[Paragraph("<b>Chapter / Topic</b>", styles['TOCBold']), Paragraph("<b>Questions</b>", styles['TOCBold']), Paragraph("<b>Weightage</b>", styles['TOCBold'])]]

    chapter_blocks = []
    global_q_id = 1

    for c_idx in range(1, len(chap_splits), 2):
        c_num = int(chap_splits[c_idx])
        c_text = chap_splits[c_idx+1]
        
        lines = [l.strip() for l in c_text.split('\n') if l.strip()]
        c_title = lines[2] if len(lines) > 2 else f'Chapter {c_num}'
        
        q_splits = re.split(r'\n(\d+)\.\n\[(CDS[^\n\]]+)\]', c_text)
        chap_qs = []
        
        for j in range(1, len(q_splits), 3):
            q_num = int(q_splits[j])
            src = q_splits[j+1].strip()
            body = q_splits[j+2].strip()
            
            # Match (a) ... (b) ... (c) ... (d)
            m = re.search(r'^(.*?)\s*\(a\)\s*(.*?)\s*\(b\)\s*(.*?)\s*\(c\)\s*(.*?)\s*\(d\)\s*(.*?)$', body, re.DOTALL)
            if m:
                stem = ' '.join(m.group(1).split()).strip()
                oa = ' '.join(m.group(2).split()).strip()
                ob = ' '.join(m.group(3).split()).strip()
                oc = ' '.join(m.group(4).split()).strip()
                od = ' '.join(m.group(5).split()).strip()
                stem = re.sub(r'^\d+[\.\s]+', '', stem)
            else:
                stem = ' '.join(body.split()[:40]).strip()
                oa, ob, oc, od = "Option (a)", "Option (b)", "Option (c)", "Option (d)"
                
            chap_qs.append({
                'global_id': global_q_id,
                'orig_id': q_num,
                'source': src,
                'stem': stem,
                'options': {'a': oa, 'b': ob, 'c': oc, 'd': od}
            })
            global_q_id += 1

        total_q_count += len(chap_qs)
        toc_data.append([
            Paragraph(f"Chapter {c_num:02d}: {c_title}", styles['TOCItem']),
            Paragraph(f"<b>{len(chap_qs)} Qs</b>", styles['TOCItem']),
            Paragraph("Core UPSC Scope", styles['TOCItem'])
        ])
        chapter_blocks.append((c_num, c_title, chap_qs))

    # Add TOC table to Cover
    toc_t = Table(toc_data, colWidths=[330, 80, 113])
    toc_t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(toc_t)
    story.append(PageBreak())

    # 3. Add All Questions
    for c_num, c_title, q_list in chapter_blocks:
        sec_header = Table([[
            Paragraph(f"<b>CHAPTER {c_num:02d} : {c_title.upper()} ({len(q_list)} QUESTIONS)</b>", styles['ChapBanner'])
        ]], colWidths=[523])
        sec_header.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#e2e8f0")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#475569")),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(sec_header)
        story.append(Spacer(1, 4))

        for q in q_list:
            stem_safe = escape_xml(q['stem'])
            src_safe = escape_xml(q['source'])
            oa = escape_xml(q['options']['a'])
            ob = escape_xml(q['options']['b'])
            oc = escape_xml(q['options']['c'])
            od = escape_xml(q['options']['d'])

            max_len = max(len(oa), len(ob), len(oc), len(od))
            
            q_flowables = []
            q_flowables.append(Paragraph(f"<b>{q['global_id']}.</b> {stem_safe} <font size=6.5 color='#64748b'>[{src_safe}]</font>", styles['QText']))

            if max_len <= 26:
                opt_row = Table([[
                    Paragraph(f"(a) {oa}", styles['OptText']),
                    Paragraph(f"(b) {ob}", styles['OptText']),
                    Paragraph(f"(c) {oc}", styles['OptText']),
                    Paragraph(f"(d) {od}", styles['OptText']),
                ]], colWidths=[128, 128, 128, 128])
                opt_row.setStyle(TableStyle([
                    ('TOPPADDING', (0,0), (-1,-1), 1),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                    ('LEFTPADDING', (0,0), (-1,-1), 2),
                ]))
                q_flowables.append(opt_row)
            elif max_len <= 65:
                opt_row = Table([
                    [Paragraph(f"(a) {oa}", styles['OptText']), Paragraph(f"(b) {ob}", styles['OptText'])],
                    [Paragraph(f"(c) {oc}", styles['OptText']), Paragraph(f"(d) {od}", styles['OptText'])],
                ], colWidths=[256, 256])
                opt_row.setStyle(TableStyle([
                    ('TOPPADDING', (0,0), (-1,-1), 1),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                    ('LEFTPADDING', (0,0), (-1,-1), 2),
                ]))
                q_flowables.append(opt_row)
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

    def make_canvas(*args, **kwargs):
        c = UPSCNumberedCanvas(*args, **kwargs)
        c.doc_subject = subject_title
        return c

    doc_out = SimpleDocTemplate(
        output_pdf_path,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=40,
        bottomMargin=55
    )
    doc_out.build(story, canvasmaker=make_canvas)
    print(f"Generated {output_pdf_path} with {total_q_count} questions!")


def build_all_gs_paper(gs_json_path, output_pdf_path, answer_key_path):
    print("Building Complete All-Questions GS Paper & Answer Key...")
    with open(gs_json_path, 'r', encoding='utf-8') as f:
        gs_questions = json.load(f)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle('CovTitle', fontName='Helvetica-Bold', fontSize=15, leading=19, alignment=TA_CENTER))
    styles.add(ParagraphStyle('CovSub', fontName='Helvetica-Bold', fontSize=11, leading=14, alignment=TA_CENTER))
    styles.add(ParagraphStyle('CovBadge', fontName='Helvetica-Bold', fontSize=13, leading=17, alignment=TA_CENTER, textColor=colors.HexColor("#1e3a8a")))
    styles.add(ParagraphStyle('InstText', fontName='Helvetica', fontSize=8, leading=11, alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle('ChapBanner', fontName='Helvetica-Bold', fontSize=10.5, leading=14, textColor=colors.HexColor("#0f172a"), spaceBefore=10, spaceAfter=4))
    styles.add(ParagraphStyle('QText', fontName='Helvetica', fontSize=8.2, leading=11, alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle('OptText', fontName='Helvetica', fontSize=8, leading=10.5))
    styles.add(ParagraphStyle('GridHead', fontName='Helvetica-Bold', fontSize=8, leading=10, alignment=TA_CENTER, textColor=colors.white))
    styles.add(ParagraphStyle('GridText', fontName='Helvetica', fontSize=8, leading=10, alignment=TA_CENTER))
    styles.add(ParagraphStyle('SolHead', fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=colors.HexColor("#0f172a")))
    styles.add(ParagraphStyle('SolBody', fontName='Helvetica', fontSize=8, leading=11, alignment=TA_JUSTIFY))

    # Group by chapter
    by_chap = {}
    for q in gs_questions:
        c_title = q['chapter_title']
        if c_title not in by_chap:
            by_chap[c_title] = []
        by_chap[c_title].append(q)

    # 1. QUESTION PAPER
    story = []
    top_header_data = [
        [
            Paragraph("<b>T.B.C. : CDS-ALL-GS-2024-A</b><br/><font size=7.5>Serial No. <b>940283</b></font>", styles['Normal']),
            Paragraph("<b>TEST BOOKLET<br/><font size=16 color='#b91c1c'>[ A ]</font></b><br/><font size=7.5>COMPLETE REPOSITORY</font>", styles['CovSub']),
            Paragraph("<b>General Knowledge (GS)</b><br/><b>Marks: +0.833 / -0.277</b>", styles['Normal'])
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
    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>GENERAL KNOWLEDGE — COMPLETE CHAPTER-WISE PYQ ARCHIVE</b>", styles['CovBadge']))
    story.append(Spacer(1, 12))

    instructions = [
        f"<b>1.</b> This question paper repository contains <b>ALL {len(gs_questions)} Questions</b> extracted directly from official UPSC CDS General Knowledge examination papers across 2009–2024.",
        "<b>2.</b> Questions are organized into the 6 official syllabus chapters: Polity, History, Geography, General Science, Economy, and Defence/Current Affairs.",
        "<b>3. SCORING FORMULA:</b> +0.833 marks per correct response | -0.277 marks penalty for incorrect responses.",
        "<b>4. DO NOT OPEN THIS TEST BOOKLET UNTIL YOU ARE TOLD TO DO SO.</b>"
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

    for c_title, q_list in by_chap.items():
        sec_header = Table([[
            Paragraph(f"<b>SECTION : {c_title.upper()} ({len(q_list)} QUESTIONS)</b>", styles['ChapBanner'])
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

        for q in q_list:
            stem_safe = escape_xml(q['question'])
            src_safe = escape_xml(q.get('source', 'UPSC CDS'))
            oa = escape_xml(q['options'].get('a', ''))
            ob = escape_xml(q['options'].get('b', ''))
            oc = escape_xml(q['options'].get('c', ''))
            od = escape_xml(q['options'].get('d', ''))

            max_len = max(len(oa), len(ob), len(oc), len(od))
            q_flowables = [Paragraph(f"<b>{q['id']}.</b> {stem_safe} <font size=6.5 color='#64748b'>[{src_safe}]</font>", styles['QText'])]

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

    def make_canvas(*args, **kwargs):
        c = UPSCNumberedCanvas(*args, **kwargs)
        c.doc_subject = "GENERAL KNOWLEDGE"
        return c

    doc_out = SimpleDocTemplate(output_pdf_path, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=40, bottomMargin=55)
    doc_out.build(story, canvasmaker=make_canvas)
    print(f"Generated {output_pdf_path}!")

    # 2. GS COMPANION ANSWER KEY & SOLUTIONS
    story_key = []
    story_key.append(Paragraph("<b>UNION PUBLIC SERVICE COMMISSION (UPSC)</b>", styles['CovTitle']))
    story_key.append(Spacer(1, 4))
    story_key.append(Paragraph("<b>GENERAL KNOWLEDGE (GS) — COMPLETE OFFICIAL ANSWER KEY & SOLUTIONS</b>", styles['CovSub']))
    story_key.append(Spacer(1, 10))

    # Render Scoring Grid
    rows = []
    num_cols = 10
    total_items = len(gs_questions)
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
                q = gs_questions[idx]
                row_data.append(Paragraph(f"<b>{q['id']}</b>", styles['GridText']))
                row_data.append(Paragraph(f"<b>({q['correct_answer'].upper()})</b>", styles['GridText']))
            else:
                row_data.extend(["", ""])
        rows.append(row_data)

    kt = Table(rows, colWidths=[26, 26] * num_cols)
    kt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.4, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story_key.append(kt)
    story_key.append(Spacer(1, 14))

    # Explanations
    story_key.append(Paragraph("<b>DETAILED CONSTITUTIONAL, HISTORICAL & SCIENTIFIC SOLUTIONS:</b>", styles['ChapBanner']))
    for q in gs_questions[:50]: # include top detailed explanations
        exp = escape_xml(q.get('explanation', ''))
        q_text = escape_xml(q['question'])
        sec = escape_xml(q['chapter_title'])
        q_sol_data = [
            [Paragraph(f"<b>Q.{q['id']} [{sec}] — Correct: ({q['correct_answer'].upper()})</b>", styles['SolHead'])],
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
        story_key.append(KeepTogether([q_sol_t, Spacer(1, 4)]))

    doc_key_out = SimpleDocTemplate(answer_key_path, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=40, bottomMargin=40)
    doc_key_out.build(story_key)
    print(f"Generated {answer_key_path}!")

if __name__ == '__main__':
    # 1. GS Complete Paper
    build_all_gs_paper(
        'data/cds_gs_complete_chapterwise.json',
        'UPSC_CDS_GS_All_Questions_Paper.pdf',
        'UPSC_CDS_GS_All_Questions_Answer_Key.pdf'
    )
    import shutil
    shutil.copyfile('UPSC_CDS_GS_All_Questions_Paper.pdf', 'CDS_GS_Chapterwise_PYQ.pdf')
    shutil.copyfile('UPSC_CDS_GS_All_Questions_Answer_Key.pdf', 'CDS_GS_Chapterwise_Answer_Key.pdf')
    print("Synchronized CDS_GS_Chapterwise_PYQ.pdf and CDS_GS_Chapterwise_Answer_Key.pdf!")
    
    # 2. English Complete Paper
    if os.path.exists('CDS_English_Chapterwise_PYQ.pdf'):
        build_all_questions_paper(
            'CDS_English_Chapterwise_PYQ.pdf',
            'CDS_English_Chapterwise_Answer_Key.pdf',
            'UPSC_CDS_English_All_Questions_Paper.pdf',
            'GENERAL ENGLISH',
            0.833,
            0.277
        )
    else:
        print("[Skipped] CDS_English_Chapterwise_PYQ.pdf not present, preserving existing UPSC_CDS_English_All_Questions_Paper.pdf.")
    
    # 3. Math Complete Paper
    if os.path.exists('CDS_Math_Chapterwise_PYQ.pdf'):
        build_all_questions_paper(
            'CDS_Math_Chapterwise_PYQ.pdf',
            'CDS_Math_Chapterwise_Answer_Key.pdf',
            'UPSC_CDS_Math_All_Questions_Paper.pdf',
            'ELEMENTARY MATHEMATICS',
            1.000,
            0.333
        )
    else:
        print("[Skipped] CDS_Math_Chapterwise_PYQ.pdf not present, preserving existing UPSC_CDS_Math_All_Questions_Paper.pdf.")
    
    print('ALL COMPREHENSIVE QUESTION PAPERS GENERATED SUCCESSFULLY!')
