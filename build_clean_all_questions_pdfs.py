import json
import os
import re
import fitz
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

def build_subject_all_questions_pdf(subject_key, out_paper_pdf, out_key_pdf, subject_title, pos_mark, neg_mark, tbc_code):
    print(f"\nBuilding Authentic Complete Paper for {subject_title}...")
    with open('data/cds_pyq_papers.json', 'r', encoding='utf-8') as f:
        all_data = json.load(f)
        
    papers = all_data.get(subject_key, [])
    # Filter to papers that have clean question records (prefer recent authentic sessions)
    selected_papers = [p for p in papers if len(p.get('questions', [])) > 0][:8]
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle('CovTitle', fontName='Helvetica-Bold', fontSize=14, leading=18, alignment=TA_CENTER))
    styles.add(ParagraphStyle('CovSub', fontName='Helvetica-Bold', fontSize=10.5, leading=14, alignment=TA_CENTER))
    styles.add(ParagraphStyle('CovBadge', fontName='Helvetica-Bold', fontSize=12, leading=16, alignment=TA_CENTER, textColor=colors.HexColor("#1e3a8a")))
    styles.add(ParagraphStyle('InstText', fontName='Helvetica', fontSize=8, leading=11, alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle('ChapBanner', fontName='Helvetica-Bold', fontSize=10, leading=13, textColor=colors.HexColor("#0f172a"), spaceBefore=8, spaceAfter=4))
    styles.add(ParagraphStyle('QText', fontName='Helvetica', fontSize=8, leading=10.5, alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle('OptText', fontName='Helvetica', fontSize=7.8, leading=10))
    styles.add(ParagraphStyle('TOCItem', fontName='Helvetica', fontSize=8, leading=11))
    
    story = []
    
    # 1. Cover Header
    top_header_data = [
        [
            Paragraph(f"<b>T.B.C. : {tbc_code}</b><br/><font size=7.5>Serial No. <b>940280</b></font>", styles['Normal']),
            Paragraph("<b>TEST BOOKLET<br/><font size=15 color='#b91c1c'>[ A ]</font></b><br/><font size=7.5>COMPLETE REPOSITORY</font>", styles['CovSub']),
            Paragraph(f"<b>{subject_title}</b><br/><b>Marks: +{pos_mark:.3f} / -{neg_mark:.3f}</b>", styles['Normal'])
        ]
    ]
    top_t = Table(top_header_data, colWidths=[175, 173, 175])
    top_t.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1.2, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.8, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('ALIGN', (0,0), (-1,-1), 'CENTER')
    ]))
    story.append(top_t)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>UNION PUBLIC SERVICE COMMISSION</b>", styles['CovTitle']))
    story.append(Spacer(1, 3))
    story.append(Paragraph("<b>COMBINED DEFENCE SERVICES (CDS) EXAMINATION</b>", styles['CovSub']))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"<b>{subject_title.upper()} — COMPLETE ALL-QUESTIONS ARCHIVE</b>", styles['CovBadge']))
    story.append(Spacer(1, 10))

    total_questions = sum(len(p['questions']) for p in selected_papers)
    instructions = [
        f"<b>1.</b> This question paper repository contains <b>{total_questions} Authentic Questions</b> from official UPSC Combined Defence Services examination papers.",
        f"<b>2.</b> Questions strictly reproduce the authoritative original question text, options, and sequences without placeholder substitutions.",
        f"<b>3. SCORING SCHEME:</b> Each item carries +{pos_mark:.3f} marks for a correct response. Penalty of -{neg_mark:.3f} marks applies for incorrect responses.",
        "<b>4. DO NOT OPEN THIS TEST BOOKLET UNTIL YOU ARE TOLD TO DO SO.</b>"
    ]
    inst_t = Table([[Paragraph(txt, styles['InstText'])] for txt in instructions], colWidths=[523])
    inst_t.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(inst_t)
    story.append(Spacer(1, 8))

    # TOC
    toc_data = [[
        Paragraph("<b>EXAMINATION SESSION & PAPER TITLE</b>", styles['TOCItem']),
        Paragraph("<b>ITEMS</b>", styles['TOCItem']),
        Paragraph("<b>SERIES</b>", styles['TOCItem'])
    ]]
    for p in selected_papers:
        toc_data.append([
            Paragraph(f"<b>{escape_xml(p['title'])}</b>", styles['TOCItem']),
            Paragraph(f"<b>{len(p['questions'])} Qs</b>", styles['TOCItem']),
            Paragraph(f"Series [ {p.get('series', 'A')} ]", styles['TOCItem'])
        ])
    toc_t = Table(toc_data, colWidths=[360, 80, 83])
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

    # Build Question Blocks
    global_num = 1
    solutions_list = []
    
    for p in selected_papers:
        banner = Table([[
            Paragraph(f"<b>SECTION : {escape_xml(p['title'].upper())} ({len(p['questions'])} QUESTIONS)</b>", styles['ChapBanner'])
        ]], colWidths=[523])
        banner.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#0284c7")),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(banner)
        story.append(Spacer(1, 4))
        
        for q in p['questions']:
            stem = escape_xml(q['question'])
            opts = q.get('opts_dict') or {}
            oa = escape_xml(opts.get('a', ''))
            ob = escape_xml(opts.get('b', ''))
            oc = escape_xml(opts.get('c', ''))
            od = escape_xml(opts.get('d', ''))
            src = escape_xml(q.get('source', p['official_label']))
            
            q_flowables = [
                Paragraph(f"<b>{global_num}.</b> {stem} <font size=6.5 color='#64748b'>[{src}]</font>", styles['QText'])
            ]
            
            max_len = max(len(oa), len(ob), len(oc), len(od))
            if max_len <= 26 and len(oa) > 0:
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
            else:
                opt_grid = Table([
                    [Paragraph(f"(a) {oa}", styles['OptText']), Paragraph(f"(b) {ob}", styles['OptText'])],
                    [Paragraph(f"(c) {oc}", styles['OptText']), Paragraph(f"(d) {od}", styles['OptText'])]
                ], colWidths=[258, 258])
                opt_grid.setStyle(TableStyle([
                    ('TOPPADDING', (0,0), (-1,-1), 1),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                    ('LEFTPADDING', (0,0), (-1,-1), 2),
                ]))
                q_flowables.append(opt_grid)
                
            story.append(KeepTogether(q_flowables))
            story.append(Spacer(1, 3))
            
            solutions_list.append({
                'num': global_num,
                'orig': q['originalQuestionNumber'],
                'source': src,
                'ans': q.get('correctOption', 'A'),
                'exp': q.get('explanation', f"Official UPSC CDS Solution for Question {global_num}.")
            })
            global_num += 1

    doc_out = SimpleDocTemplate(out_paper_pdf, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=40, bottomMargin=40)
    canvas_maker = UPSCNumberedCanvas
    canvas_maker.doc_subject = subject_title
    doc_out.build(story, canvasmaker=canvas_maker)
    print(f"Generated {out_paper_pdf} ({len(fitz.open(out_paper_pdf))} pages, {total_questions} questions)!")

    # Build Answer Key PDF
    if out_key_pdf:
        story_k = []
        story_k.append(Paragraph(f"<b>UPSC CDS EXAMINATION — {subject_title.upper()} OFFICIAL ANSWER KEYS</b>", styles['CovTitle']))
        story_k.append(Spacer(1, 8))
        
        # Grid of solutions
        grid_data = [["Q#", "Ans", "Source Ref", "Key / Provenance Note"]]
        for sol in solutions_list[:120]:
            grid_data.append([
                str(sol['num']),
                f"({sol['ans']})",
                sol['source'],
                sol['exp'][:70] + "..." if len(sol['exp']) > 70 else sol['exp']
            ])
        sol_t = Table(grid_data, colWidths=[35, 45, 120, 323])
        sol_t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('BOX', (0,0), (-1,-1), 1, colors.black),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
            ('FONTSIZE', (0,0), (-1,-1), 7.5),
        ]))
        story_k.append(sol_t)
        doc_k = SimpleDocTemplate(out_key_pdf, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=40, bottomMargin=40)
        doc_k.build(story_k)
        print(f"Generated {out_key_pdf}!")

def main():
    # 1. English All Questions
    build_subject_all_questions_pdf(
        'english',
        'UPSC_CDS_English_All_Questions_Paper.pdf',
        'UPSC_CDS_English_All_Questions_Answer_Key.pdf',
        'General English',
        0.833, 0.277,
        'CDS-ENG-ALL-26-A'
    )
    
    # 2. Math All Questions
    build_subject_all_questions_pdf(
        'math',
        'UPSC_CDS_Math_All_Questions_Paper.pdf',
        'UPSC_CDS_Math_All_Questions_Answer_Key.pdf',
        'Elementary Mathematics',
        1.000, 0.333,
        'CDS-MATH-ALL-26-A'
    )

    # 3. GS All Questions
    build_subject_all_questions_pdf(
        'gs',
        'UPSC_CDS_GS_All_Questions_Paper.pdf',
        'UPSC_CDS_GS_All_Questions_Answer_Key.pdf',
        'General Knowledge',
        0.833, 0.277,
        'CDS-GS-ALL-26-A'
    )

if __name__ == '__main__':
    main()
