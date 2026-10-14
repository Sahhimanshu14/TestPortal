from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def draw_omr(filename="UPSC_CDS_Official_OMR_Sheet.pdf"):
    c = canvas.Canvas(filename, pagesize=A4)
    w, h = A4  # 595.28 x 841.89

    # Margin & Border
    margin = 20
    c.setLineWidth(1.5)
    c.setStrokeColor(colors.black)
    c.rect(margin, margin, w - 2*margin, h - 2*margin)

    # Scanner Alignment Marks (Corner Black Squares)
    sq_size = 14
    c.setFillColor(colors.black)
    c.rect(margin + 4, h - margin - 4 - sq_size, sq_size, sq_size, fill=1)
    c.rect(w - margin - 4 - sq_size, h - margin - 4 - sq_size, sq_size, sq_size, fill=1)
    c.rect(margin + 4, margin + 4, sq_size, sq_size, fill=1)
    c.rect(w - margin - 4 - sq_size, margin + 4, sq_size, sq_size, fill=1)

    # Header
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(w/2, h - 42, "UNION PUBLIC SERVICE COMMISSION")
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(w/2, h - 56, "COMBINED DEFENCE SERVICES (CDS) EXAMINATION")
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#1e3a8a"))
    c.drawCentredString(w/2, h - 69, "OFFICIAL OMR ANSWER SHEET (OBJECTIVE TYPE)")
    c.setFillColor(colors.black)

    # Serial No & Barcode dummy
    c.setFont("Courier-Bold", 9)
    c.drawString(margin + 25, h - 50, "OMR SHEET NO: CDS-2024-894102")
    c.setFont("Helvetica", 8)
    c.drawString(w - margin - 150, h - 50, "USE BLACK BALL POINT PEN ONLY")

    # Divider line
    c.setLineWidth(1)
    c.line(margin, h - 76, w - margin, h - 76)

    # TOP SECTION: Instructions & Candidate particulars
    # Box 1: Instructions (Left)
    c.setLineWidth(0.8)
    c.rect(margin + 5, h - 165, 175, 84)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(margin + 10, h - 88, "IMPORTANT INSTRUCTIONS:")
    c.setFont("Helvetica", 6.8)
    c.drawString(margin + 10, h - 100, "1. Darken ONLY ONE circle completely for each item.")
    c.drawString(margin + 10, h - 110, "2. Do not fold, tear or make any stray marks on sheet.")
    c.drawString(margin + 10, h - 120, "3. Negative marking: 1/3rd penalty for wrong answer.")
    c.drawString(margin + 10, h - 132, "CORRECT METHOD:    WRONG METHODS:")
    
    # Draw bubble examples
    c.circle(margin + 95, h - 130, 4.5, fill=1) # Correct
    c.circle(margin + 155, h - 130, 4.5, fill=0) # Wrong (with cross)
    c.line(margin + 152, h - 133, margin + 158, h - 127)
    c.line(margin + 152, h - 127, margin + 158, h - 133)
    c.setFont("Helvetica", 6.5)
    c.drawString(margin + 10, h - 146, "Darken fully: ●          Cross ✖  Tick ✔  Half ◐  Invalid")

    # Box 2: Candidate Name (Center)
    c.rect(margin + 185, h - 165, 185, 84)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(margin + 190, h - 88, "CANDIDATE'S NAME (IN CAPITAL LETTERS):")
    # Draw 16 letter boxes
    bw = 9.8
    for row in range(2):
        for col in range(16):
            c.rect(margin + 192 + col * bw, h - 112 - row * 16, bw, 13)
    c.setFont("Helvetica", 6.5)
    c.drawString(margin + 192, h - 152, "Leave one box blank between First, Middle & Last name.")

    # Box 3: Test Booklet Series & Subject Code (Right)
    c.rect(margin + 375, h - 165, 175, 84)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(margin + 382, h - 88, "BOOKLET SERIES")
    c.drawString(margin + 472, h - 88, "SUBJECT CODE")
    
    # Booklet Series Circles A, B, C, D
    series_list = ["A", "B", "C", "D"]
    for i, s in enumerate(series_list):
        cx = margin + 395 + i * 16
        cy = h - 108
        c.circle(cx, cy, 5.5, fill=0)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawCentredString(cx, cy - 2.5, s)
        c.setFont("Helvetica", 7)
        c.drawCentredString(cx, cy - 14, f"[{s}]")

    # Subject Code Boxes & Bubbles
    c.rect(margin + 480, h - 118, 14, 14)
    c.rect(margin + 498, h - 118, 14, 14)
    c.setFont("Helvetica", 6.5)
    c.drawString(margin + 475, h - 132, "01: Eng | 02: GS | 03: Math")

    # ROLL NUMBER & EXAM CENTER SECTION (h - 172 down to h - 280)
    c.setLineWidth(0.8)
    # Roll Number Box (Left)
    c.rect(margin + 5, h - 285, 235, 115)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(margin + 12, h - 182, "ROLL NUMBER (7 DIGITS):")
    
    # 7 digit columns
    digit_w = 30
    for col in range(7):
        rx = margin + 14 + col * digit_w
        # top box for writing digit
        c.rect(rx, h - 200, 24, 14)
        # 10 bubbles below for digits 0-9
        for d in range(10):
            by = h - 212 - d * 7
            c.circle(rx + 12, by, 3.2, fill=0)
            c.setFont("Helvetica", 5.5)
            c.drawCentredString(rx + 12, by - 1.8, str(d))

    # Center Code & Academy Box (Right)
    c.rect(margin + 245, h - 285, 305, 115)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(margin + 255, h - 182, "EXAMINATION DETAILS & TARGET ACADEMY:")
    
    c.setFont("Helvetica", 7.5)
    c.drawString(margin + 255, h - 198, "Target Academy Choice:   [  ] IMA    [  ] INA    [  ] AFA    [  ] OTA")
    c.drawString(margin + 255, h - 212, "Examination Centre: _____________________________________________")
    c.drawString(margin + 255, h - 226, "Date of Examination:  DD / MM / YYYY")
    
    # Candidate Declaration
    c.rect(margin + 252, h - 280, 290, 48)
    c.setFont("Helvetica-Oblique", 6.8)
    c.drawString(margin + 256, h - 240, "Candidate Declaration: I hereby certify that the particulars filled above are")
    c.drawString(margin + 256, h - 249, "correct and complete. I have read all instructions given on the Test Booklet.")
    
    # Signature Boxes
    c.line(margin + 395, h - 280, margin + 395, h - 253)
    c.setFont("Helvetica-Bold", 7)
    c.drawString(margin + 260, h - 262, "Candidate's Signature:")
    c.drawString(margin + 402, h - 262, "Invigilator's Signature & Stamp:")

    # MAIN RESPONSE BUBBLE GRID (120 QUESTIONS)
    # Divided into 4 columns of 30 questions each
    grid_top = h - 295
    grid_bottom = margin + 15
    grid_h = grid_top - grid_bottom  # approx 510 pt
    
    col_w = (w - 2 * margin - 10) / 4 # ~134 pt each
    
    opt_labels = ["A", "B", "C", "D"]
    row_step = grid_h / 31 # ~16.4 pt per row
    
    for c_idx in range(4):
        cx0 = margin + 5 + c_idx * (col_w + 2)
        # Column container box
        c.rect(cx0, grid_bottom, col_w, grid_h)
        
        # Header for column
        c.setFillColor(colors.HexColor("#f1f5f9"))
        c.rect(cx0, grid_top - 16, col_w, 16, fill=1, stroke=1)
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(cx0 + 4, grid_top - 12, "Q#")
        for oi, ol in enumerate(opt_labels):
            c.drawCentredString(cx0 + 36 + oi * 24, grid_top - 12, ol)
        
        # 30 Questions in this column
        start_q = c_idx * 30 + 1
        for q_offset in range(30):
            q_num = start_q + q_offset
            qy = grid_top - 20 - (q_offset + 0.6) * (row_step - 0.4)
            
            # Subtle alternate row shading
            if q_offset % 5 == 4:
                c.setLineWidth(0.4)
                c.setStrokeColor(colors.HexColor("#94a3b8"))
                c.line(cx0, qy - 4, cx0 + col_w, qy - 4)
                c.setStrokeColor(colors.black)
                c.setLineWidth(0.8)
                
            # Q Number
            c.setFont("Helvetica-Bold", 7)
            c.drawString(cx0 + 4, qy - 2.5, f"{q_num:02d}")
            
            # 4 Bubbles (A, B, C, D)
            for oi, ol in enumerate(opt_labels):
                bx = cx0 + 36 + oi * 24
                c.setLineWidth(0.6)
                c.circle(bx, qy, 4.2, fill=0)
                c.setFont("Helvetica", 5.5)
                c.drawCentredString(bx, qy - 2, ol)

    # Footer note
    c.setFont("Helvetica", 6.5)
    c.drawCentredString(w/2, margin + 4, "UPSC COMBINED DEFENCE SERVICES (CDS) EXAMINATION - MACHINE GRADED OMR SHEET | CONFIDENTIAL")

    c.save()
    print(f"Generated authentic OMR Sheet: {filename}")

if __name__ == "__main__":
    draw_omr()
