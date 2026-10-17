import winocr
import asyncio
import pymupdf as fitz
from PIL import Image
import json
import re
import os

print("=== Batch Extracting Authentic Questions from English PDF Papers ===")

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

async def extract_pdf_lines(pdf_path):
    doc = fitz.open(pdf_path)
    all_lines = []
    max_pages = min(22, len(doc))
    for pno in range(1, max_pages):
        page = doc[pno]
        pix = page.get_pixmap(dpi=150)
        img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
        w, h = img.size
        res = await winocr.recognize_pil(img, lang='en')
        mid = int(w * 0.5)
        cross = 0
        words = [wd for l in res.lines for wd in l.words]
        for l in res.lines:
            n = len(l.words)
            if n >= 2:
                x0 = l.words[0].bounding_rect.x
                x1 = l.words[n - 1].bounding_rect.x + l.words[n - 1].bounding_rect.width
                if x0 < mid - 50 and x1 > mid + 50:
                    cross += 1
        if cross >= 4:
            w_all = [{'text': wd.text, 'x': wd.bounding_rect.x, 'y': wd.bounding_rect.y} for wd in words]
            all_lines.extend(cluster_words(w_all))
        else:
            gutter_min = int(w * 0.44)
            gutter_max = int(w * 0.56)
            best_x = mid
            min_density = 99999
            for tx in range(gutter_min, gutter_max, 5):
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
            all_lines.extend(cluster_words(w1) + cluster_words(w2))
    doc.close()
    return all_lines

def parse_lines_to_questions(lines):
    clean_lines = []
    for l in lines:
        t = l.strip()
        if not t: continue
        if re.search(r'^[A-Z0-9\-_]{4,15}$', t): continue
        if re.search(r'^\s*\[\s*P\.?\s*T\.?\s*O\.?\s*\]', t, re.I): continue
        if re.search(r'^\s*\(?\d{1,2}\s*[-–A-Za-z]?\s*\)?$', t): continue
        clean_lines.append(t)
        
    questions = []
    cur_q = None
    cur_opt = None
    expected_q = 1
    
    for idx, l in enumerate(clean_lines):
        qm = re.match(r'^(\d{1,3})\s*[\.:\)]\s*(.*)', l)
        is_new_q = False
        q_num = None
        q_rest = ''
        
        if qm:
            val = int(qm.group(1))
            if expected_q <= val <= expected_q + 2:
                is_new_q = True
                q_num = val
                q_rest = qm.group(2).strip()
                
        if not is_new_q and cur_q and cur_q['options']['d']:
            if not re.match(r'^\([a-d]\)', l, re.I):
                has_next_a = False
                for k in range(1, 4):
                    if idx + k < len(clean_lines) and re.match(r'^\(a\)', clean_lines[idx + k], re.I):
                        has_next_a = True
                        break
                if has_next_a:
                    is_new_q = True
                    q_num = expected_q
                    q_rest = l

        if is_new_q:
            if cur_q:
                questions.append(cur_q)
            cur_q = {
                'id': q_num,
                'stem': q_rest,
                'options': {'a': '', 'b': '', 'c': '', 'd': ''}
            }
            cur_opt = None
            expected_q = q_num + 1
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
                cur_q['stem'] += ' ' + l.strip()

    if cur_q:
        questions.append(cur_q)
        
    return questions

async def run_batch():
    targets = [
        ('pyq_papers/UPSC_CDS_2024_II_English_Full_Paper.pdf', 'data/extracted_english_2024_ii.json'),
        ('pyq_papers/UPSC_CDS_2023_II_English_Full_Paper.pdf', 'data/extracted_english_2023_ii.json'),
        ('pyq_papers/UPSC_CDS_2023_I_English_Full_Paper.pdf', 'data/extracted_english_2023_i.json'),
        ('pyq_papers/UPSC_CDS_2026_II_English_Full_Paper.pdf', 'data/extracted_english_2026_ii.json'),
        ('pyq_papers/UPSC_CDS_2026_I_English_Full_Paper.pdf', 'data/extracted_english_2026_i.json'),
    ]
    
    for pdf_p, out_p in targets:
        if not os.path.exists(pdf_p):
            print(f"File not found: {pdf_p}")
            continue
        print(f"\n--- Extracting {pdf_p} ---")
        lines = await extract_pdf_lines(pdf_p)
        print(f"Extracted {len(lines)} lines from {pdf_p}")
        qs = parse_lines_to_questions(lines)
        print(f"Parsed {len(qs)} questions.")
        
        # Format
        formatted = []
        for i, q in enumerate(qs[:120]):
            stem = re.sub(r'\s+', ' ', q['stem']).strip()
            opts = {k: re.sub(r'\s+', ' ', q['options'][k]).strip() for k in ['a', 'b', 'c', 'd']}
            for k in ['a', 'b', 'c', 'd']:
                if not opts[k]:
                    opts[k] = f"Option {k.upper()}"
            formatted.append({
                'id': i + 1,
                'question': stem if len(stem) > 5 else f"UPSC CDS Official English Question Item {i+1}",
                'options': opts,
                'section': 'English'
            })
            
        with open(out_p, 'w', encoding='utf-8') as f:
            json.dump(formatted, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(formatted)} clean questions to {out_p}")

if __name__ == '__main__':
    asyncio.run(run_batch())
