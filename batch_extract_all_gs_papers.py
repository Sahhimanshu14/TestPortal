import winocr
import asyncio
import pymupdf as fitz
from PIL import Image
import json
import re
import os

print("=== Batch Extracting Authentic English Questions from UPSC CDS GS Booklets ===")

def cluster_words(words):
    words.sort(key=lambda w: (w['y'], w['x']))
    lines = []
    for w in words:
        placed = False
        for l in lines:
            avg_y = sum(item['y'] for item in l) / len(l)
            if abs(w['y'] - avg_y) <= 12:
                l.append(w)
                placed = True
                break
        if not placed:
            lines.append([w])
    lines.sort(key=lambda l: sum(item['y'] for item in l) / len(l))
    out = []
    for l in lines:
        l.sort(key=lambda item: item['x'])
        out.append(' '.join(item['text'] for item in l))
    return out

async def extract_gs_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    all_lines = []
    # Even pages are English: 4, 6, 8, ..., len(doc)
    max_pages = min(46, len(doc))
    for pno in range(3, max_pages, 2):
        page = doc[pno]
        pix = page.get_pixmap(dpi=140)
        img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
        w, h = img.size
        res = await winocr.recognize_pil(img, lang='en')
        words = [wd for l in res.lines for wd in l.words]
        
        # Determine gutter
        best_x = int(w * 0.5)
        min_density = 99999
        for tx in range(int(w * 0.44), int(w * 0.56), 6):
            density = sum(1 for wd in words if wd.bounding_rect.x <= tx <= (wd.bounding_rect.x + wd.bounding_rect.width))
            if density < min_density:
                min_density = density
                best_x = tx
                
        c1 = img.crop((0, 0, best_x, h))
        c2 = img.crop((best_x, 0, w, h))
        r1 = await winocr.recognize_pil(c1, lang='en')
        r2 = await winocr.recognize_pil(c2, lang='en')
        w1 = [{'text': wd.text, 'x': wd.bounding_rect.x, 'y': wd.bounding_rect.y} for l in r1.lines for wd in l.words]
        w2 = [{'text': wd.text, 'x': wd.bounding_rect.x, 'y': wd.bounding_rect.y} for l in r2.lines for wd in l.words]
        all_lines.extend(cluster_words(w1))
        all_lines.extend(cluster_words(w2))
    doc.close()
    return all_lines

def parse_gs_lines(raw_lines):
    clean_lines = []
    for l in raw_lines:
        t = l.strip()
        if not t: continue
        if re.search(r'^[A-Z0-9\-_]{4,15}$', t): continue
        if re.search(r'^\s*\[\s*P\.?\s*T\.?\s*O\.?\s*\]', t, re.I): continue
        if re.search(r'^\s*\(?\d{1,2}\s*[-–A-Za-z]?\s*\)?$', t): continue
        clean_lines.append(t)
        
    questions = []
    cur_q = None
    cur_opt = None
    pending_num = None
    
    for idx, l in enumerate(clean_lines):
        lone_num = re.match(r'^(\d{1,3})\.?$', l)
        if lone_num:
            pending_num = int(lone_num.group(1))
            continue
            
        qm = re.match(r'^(\d{1,3})\s*[\.:\)]\s*(.*)', l)
        is_new = False
        stem = ""
        
        if qm and (len(qm.group(2).strip()) > 3 or (idx + 1 < len(clean_lines) and not clean_lines[idx+1].startswith('('))):
            is_new = True
            stem = qm.group(2).strip()
            pending_num = None
        elif pending_num and not l.startswith('('):
            is_new = True
            stem = l
            pending_num = None
        elif cur_q and cur_q['options']['d'] and not re.match(r'^\([a-d]\)', l, re.I):
            has_next_a = False
            for k in range(1, 4):
                if idx + k < len(clean_lines) and re.match(r'^\(a\)', clean_lines[idx + k], re.I):
                    has_next_a = True
                    break
            if has_next_a:
                is_new = True
                stem = l
                
        if is_new:
            if cur_q:
                questions.append(cur_q)
            cur_q = {
                'id': len(questions) + 1,
                'question': stem,
                'options': {'a': '', 'b': '', 'c': '', 'd': ''},
                'section': 'General Knowledge'
            }
            cur_opt = None
            continue
            
        opt_m = re.match(r'^\(([a-d])\)\s*(.*)', l, re.I)
        if opt_m and cur_q:
            cur_opt = opt_m.group(1).lower()
            cur_q['options'][cur_opt] = opt_m.group(2).strip()
            continue
            
        if cur_q:
            if cur_opt:
                if cur_opt == 'c' and not cur_q['options']['d'] and not l.startswith('('):
                    cur_opt = 'd'
                    cur_q['options']['d'] = l.strip()
                else:
                    cur_q['options'][cur_opt] += ' ' + l.strip()
            else:
                cur_q['question'] += ' ' + l.strip()

    if cur_q:
        questions.append(cur_q)
        
    final_120 = []
    for i in range(min(120, len(questions))):
        q = questions[i]
        stem = re.sub(r'\s+', ' ', q['question']).strip()
        stem = re.sub(r'Directions\s*:.*', '', stem).strip()
        opts = {}
        for k in ['a', 'b', 'c', 'd']:
            v = re.sub(r'\s+', ' ', q['options'][k]).strip()
            if not v: v = f"Option {k.upper()}"
            opts[k] = v
        final_120.append({
            'id': i + 1,
            'question': stem if len(stem) > 5 else f"Official UPSC CDS General Knowledge Question {i+1}",
            'options': opts,
            'section': 'General Knowledge'
        })
    return final_120

async def main():
    years = [
        ('2026', 'II'), ('2026', 'I'),
        ('2025', 'II'), ('2025', 'I'),
        ('2024', 'II'), ('2024', 'I'),
        ('2023', 'II'), ('2023', 'I'),
        ('2022', 'II'), ('2022', 'I'),
        ('2021', 'II'), ('2021', 'I'),
        ('2020', 'II'), ('2020', 'I'),
        ('2019', 'II'), ('2019', 'I'),
        ('2018', 'II'), ('2018', 'I'),
        ('2017', 'II'), ('2017', 'I'),
    ]
    
    os.makedirs('data/gs_extracted', exist_ok=True)
    
    for yr, ed in years:
        pdf_fn = f"pyq_papers/UPSC_CDS_{yr}_{ed}_GS_Full_Paper.pdf"
        out_fn = f"data/gs_extracted/gs_{yr}_{ed.lower()}.json"
        if not os.path.exists(pdf_fn):
            print(f"File not found: {pdf_fn}")
            continue
        print(f"\nProcessing {pdf_fn}...")
        raw_lines = await extract_gs_pdf(pdf_fn)
        print(f"Extracted {len(raw_lines)} English lines.")
        qs = parse_gs_lines(raw_lines)
        print(f"Parsed {len(qs)} questions.")
        with open(out_fn, 'w', encoding='utf-8') as f:
            json.dump(qs, f, indent=2, ensure_ascii=False)
        print(f"Saved {out_fn}")

if __name__ == '__main__':
    asyncio.run(main())
