import fitz
import json
import os
import io
import re
from PIL import Image

print("=== Starting Year-Wise PYQ Suite Generation ===")

os.makedirs('pyq_papers', exist_ok=True)
os.makedirs('data', exist_ok=True)

# 1. Load Manifest
with open('data/pyq_manifest.json', 'r', encoding='utf-8') as f:
    manifest = json.load(f)

eng_covers = [p['page'] for p in manifest['english']]
gs_covers = [p['page'] for p in manifest['gs']]
math_covers = [p['page'] for p in manifest['math']]

# Define years from 2014 to 2024
# Mapping index -> (Year, Edition, Label)
YEAR_MAP = {
    30: ("2024", "I", "CDS (I) 2024"),
    31: ("2024", "II", "CDS (II) 2024"),
    28: ("2023", "I", "CDS (I) 2023"),
    29: ("2023", "II", "CDS (II) 2023"),
    26: ("2022", "I", "CDS (I) 2022"),
    27: ("2022", "II", "CDS (II) 2022"),
    24: ("2021", "I", "CDS (I) 2021"),
    25: ("2021", "II", "CDS (II) 2021"),
    22: ("2020", "I", "CDS (I) 2020"),
    23: ("2020", "II", "CDS (II) 2020"),
    20: ("2019", "I", "CDS (I) 2019"),
    21: ("2019", "II", "CDS (II) 2019"),
    18: ("2018", "I", "CDS (I) 2018"),
    19: ("2018", "II", "CDS (II) 2018"),
    16: ("2017", "I", "CDS (I) 2017"),
    17: ("2017", "II", "CDS (II) 2017"),
    14: ("2016", "I", "CDS (I) 2016"),
    15: ("2016", "II", "CDS (II) 2016"),
    12: ("2015", "I", "CDS (I) 2015"),
    13: ("2015", "II", "CDS (II) 2015"),
    10: ("2014", "I", "CDS (I) 2014"),
    11: ("2014", "II", "CDS (II) 2014")
}

def extract_and_optimize(src_pdf, start_p, end_p, out_pdf):
    if os.path.exists(out_pdf) and os.path.getsize(out_pdf) > 100000:
        print(f"  [Already exists] {out_pdf} ({os.path.getsize(out_pdf)/(1024*1024):.1f} MB)")
        return
    
    doc = fitz.open(src_pdf)
    new_doc = fitz.open()
    
    # Clip pages
    actual_end = min(end_p, len(doc) - 1)
    for pno in range(start_p, actual_end + 1):
        page = doc[pno]
        rect = page.rect
        # 110 dpi delivers crisp UPSC text rendering with small footprint
        pix = page.get_pixmap(dpi=110)
        img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples).convert('L')
        bio = io.BytesIO()
        img.save(bio, format='JPEG', quality=65)
        bio.seek(0)
        
        new_page = new_doc.new_page(width=rect.width, height=rect.height)
        new_page.insert_image(rect, stream=bio.getvalue())
        
    new_doc.save(out_pdf, deflate=True)
    new_doc.close()
    doc.close()
    print(f"  [Created] {out_pdf} ({os.path.getsize(out_pdf)/(1024*1024):.1f} MB)")

print("\n--- 1. Extracting Authentic Official PDF Booklets (2018-2024) ---")
# Extract key examination sessions
sessions_to_extract = [30, 31, 28, 29, 26, 27, 24, 25, 22, 23, 20, 18]

for idx in sessions_to_extract:
    year, ed, label = YEAR_MAP[idx]
    
    # English
    e_start = eng_covers[idx]
    e_end = (eng_covers[idx+1] - 1) if (idx + 1 < len(eng_covers)) else (e_start + 27)
    e_out = f"pyq_papers/UPSC_CDS_{year}_{ed}_English_Full_Paper.pdf"
    print(f"Extracting English {label} (p.{e_start}..{e_end})...")
    extract_and_optimize('English PYQ.pdf', e_start, e_end, e_out)
    
    # GS
    g_start = gs_covers[idx]
    g_end = (gs_covers[idx+1] - 1) if (idx + 1 < len(gs_covers)) else (g_start + 43)
    g_out = f"pyq_papers/UPSC_CDS_{year}_{ed}_GS_Full_Paper.pdf"
    print(f"Extracting GS {label} (p.{g_start}..{g_end})...")
    extract_and_optimize('GS PYQ.pdf', g_start, g_end, g_out)
    
    # Math
    m_start = math_covers[idx]
    m_end = (math_covers[idx+1] - 1) if (idx + 1 < len(math_covers)) else (m_start + 39)
    m_out = f"pyq_papers/UPSC_CDS_{year}_{ed}_Math_Full_Paper.pdf"
    print(f"Extracting Math {label} (p.{m_start}..{m_end})...")
    extract_and_optimize('Math PYQ.pdf', m_start, m_end, m_out)

print("PDF extraction completed successfully!")
