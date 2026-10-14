import json
import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas

def escape_xml(s):
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
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

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

def build_paper(subject_key, subject_title, output_pdf_path, pos_mark, neg_mark, tbc_code):
    print(f"Building {subject_title} All-Questions Paper...")
    with open('data/cds_chapterwise_all.json', encoding='utf-8') as f:
        data = json.load(f)[subject_key]

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle('CovTitle', fontName='Helvetica-Bold', fontSize=15, leading=19, alignment=TA_CENTER))
    styles.add(ParagraphStyle('CovSub', fontName='Helvetica-Bold', fontSize=11, leading=14, alignment=TA_CENTER))
    styles.add(ParagraphStyle('CovBadge', fontName='Helvetica-Bold', fontSize=13, leading=17, alignment=TA_CENTER, textColor=colors.HexColor("#1e3a8a")))
    styles.add(ParagraphStyle('InstText', fontName='Helvetica', fontSize=8, leading=11, alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle('ChapBanner', fontName='Helvetica-Bold', fontSize=10, leading=13, textColor=colors.HexColor("#0f172a")))
    styles.add(ParagraphStyle('QText', fontName='Helvetica', fontSize=8.2, leading=11, alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle('OptText', fontName='Helvetica', fontSize=8, leading=10.5))

    story = []

    # Count questions
    total_q = sum(len(c['questions']) for c in data.values())

    top_header_data = [
        [
            Paragraph(f"<b>T.B.C. : {tbc_code}</b><br/><font size=7.5>Serial No. <b>940281</b></font>", styles['Normal']),
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
    story.append(Paragraph(f"<b>{subject_title.upper()} — COMPLETE CHAPTER-WISE PYQ ARCHIVE</b>", styles['CovBadge']))
    story.append(Spacer(1, 12))

    instructions = [
        f"<b>1.</b> This question paper repository contains <b>ALL {total_q} Questions</b> extracted directly from official UPSC Combined Defence Services (CDS) examination archives.",
        f"<b>2.</b> Questions are organized into all official syllabus chapters with original item prompts and 4 alternative options.",
        f"<b>3. SCORING FORMULA:</b> +{pos_mark} marks per correct response | -{neg_mark} marks penalty for incorrect responses.",
        "<b>4. DO NOT OPEN THIS TEST BOOKLET UNTIL YOU ARE TOLD TO DO SO.</b>"
    ]
    inst_t = Table([[Paragraph(txt, styles['InstText'])] for txt in instructions], colWidths=[523])
    inst_t.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(inst_t)
    story.append(PageBreak())

    global_qn = 1
    # Iterate chapters
    for ch_key, ch_data in data.items():
        ch_title = ch_data.get('title', ch_key)
        q_list = ch_data.get('questions', [])
        if not q_list:
            continue

        sec_header = Table([[
            Paragraph(f"<b>SECTION : {ch_title.upper()} ({len(q_list)} QUESTIONS)</b>", styles['ChapBanner'])
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
            stem_safe = escape_xml(q.get('question', ''))
            src_safe = escape_xml(q.get('source', 'UPSC CDS'))
            opts = q.get('options', {})
            oa = escape_xml(opts.get('a', ''))
            ob = escape_xml(opts.get('b', ''))
            oc = escape_xml(opts.get('c', ''))
            od = escape_xml(opts.get('d', ''))

            max_len = max(len(oa), len(ob), len(oc), len(od))
            q_flowables = [Paragraph(f"<b>{global_qn}.</b> {stem_safe} <font size=6.5 color='#64748b'>[{src_safe}]</font>", styles['QText'])]

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
            global_qn += 1

    def make_canvas(*args, **kwargs):
        c = UPSCNumberedCanvas(*args, **kwargs)
        c.doc_subject = subject_title
        return c

    doc_out = SimpleDocTemplate(output_pdf_path, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=40, bottomMargin=55)
    doc_out.build(story, canvasmaker=make_canvas)
    print(f"SUCCESS: Generated {output_pdf_path} ({global_qn-1} Questions)")

if __name__ == '__main__':
    build_paper(
        'english',
        'GENERAL ENGLISH',
        'UPSC_CDS_English_All_Questions_Paper.pdf',
        0.833,
        0.277,
        'CDS-ENG-ALL-24-A'
    )
    build_paper(
        'math',
        'ELEMENTARY MATHEMATICS',
        'UPSC_CDS_Math_All_Questions_Paper.pdf',
        1.000,
        0.333,
        'CDS-MATH-ALL-24-A'
    )
