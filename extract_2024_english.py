import pymupdf as fitz
import asyncio
import winocr
import sys
import os
import re
import json
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

print("=== Extracting Exact Questions from UPSC CDS 2024 (I) English Full Paper ===")

def cluster_words_to_lines(words):
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
    
    for pno in range(1, len(doc)):
        page = doc[pno]
        pix = page.get_pixmap(dpi=150)
        img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
        w, h = img.size
        
        res = await winocr.recognize_pil(img, lang='en')
        words = [wd for l in res.lines for wd in l.words]
        
        # Dynamic gutter detection
        best_x = int(w * 0.5)
        min_density = 9999
        for test_x in range(int(w * 0.43), int(w * 0.57), 5):
            density = sum(1 for wd in words if wd.bounding_rect.x <= test_x <= (wd.bounding_rect.x + wd.bounding_rect.width))
            if density < min_density:
                min_density = density
                best_x = test_x
                
        crossing = sum(1 for l in res.lines if len(l.words) > 0 and l.words[0].bounding_rect.x < best_x - 30 and (l.words[len(l.words)-1].bounding_rect.x + l.words[len(l.words)-1].bounding_rect.width) > best_x + 30)
        is_two_col = (crossing < 3)
        
        if is_two_col:
            c1 = img.crop((0, 0, best_x - 2, h))
            c2 = img.crop((best_x + 2, 0, w, h))
            r1 = await winocr.recognize_pil(c1, lang='en')
            r2 = await winocr.recognize_pil(c2, lang='en')
            w1 = [{'text': wd.text, 'x': wd.bounding_rect.x, 'y': wd.bounding_rect.y} for l in r1.lines for wd in l.words]
            w2 = [{'text': wd.text, 'x': wd.bounding_rect.x, 'y': wd.bounding_rect.y} for l in r2.lines for wd in l.words]
            all_lines.extend(cluster_words_to_lines(w1))
            all_lines.extend(cluster_words_to_lines(w2))
        else:
            w_all = [{'text': wd.text, 'x': wd.bounding_rect.x, 'y': wd.bounding_rect.y} for l in res.lines for wd in l.words]
            all_lines.extend(cluster_words_to_lines(w_all))
            
    doc.close()
    return all_lines

def parse_english_questions(raw_lines):
    # Filter header/footer trash
    cleaned = []
    for l in raw_lines:
        t = l.strip()
        if not t: continue
        if re.search(r'^[A-Z0-9\-_]{4,15}$', t): continue
        if re.search(r'^\s*\[\s*P\.?\s*T\.?\s*O\.?\s*\]', t, re.I): continue
        if re.search(r'^\s*\d{1,2}\s*$', t): continue
        cleaned.append(t)
        
    questions = []
    cur_q = None
    cur_opt = None
    cur_direction = ""
    
    for line in cleaned:
        if line.lower().startswith("directions :") or line.lower().startswith("direction :"):
            cur_direction = line
            continue
            
        norm_line = re.sub(r'^(?:IO|Io|lO|ll)\.', '10.', line)
        qm = re.match(r'^(\d{1,3})\.\s*(.*)', norm_line)
        if qm:
            if cur_q:
                questions.append(cur_q)
            q_num = int(qm.group(1))
            cur_q = {
                'id': q_num,
                'direction': cur_direction,
                'stem_lines': [qm.group(2).strip()] if qm.group(2).strip() else [],
                'options': {'a': '', 'b': '', 'c': '', 'd': ''}
            }
            cur_opt = None
            continue
            
        opt_m = re.match(r'^\(([a-d])\)\s*(.*)', line, re.I)
        if opt_m and cur_q:
            cur_opt = opt_m.group(1).lower()
            cur_q['options'][cur_opt] = opt_m.group(2).strip()
            continue
            
        if cur_q:
            if cur_opt:
                # If currently at 'c' and line has no marker, it might be option 'd'
                if cur_opt == 'c' and not cur_q['options']['d'] and not line.startswith('('):
                    cur_opt = 'd'
                    cur_q['options']['d'] = line.strip()
                else:
                    cur_q['options'][cur_opt] += ' ' + line.strip()
            else:
                cur_q['stem_lines'].append(line.strip())
                
    if cur_q:
        questions.append(cur_q)
        
    return questions

async def run():
    lines = await extract_pdf_lines('pyq_papers/UPSC_CDS_2024_I_English_Full_Paper.pdf')
    qs = parse_english_questions(lines)
    print(f"Extracted {len(qs)} questions from 2024 I English!")
    
    # Check question numbers
    found_nums = set(q['id'] for q in qs)
    print(f"Unique Q numbers: {len(found_nums)}, Min={min(found_nums)}, Max={max(found_nums)}")
    
    # Save structured questions
    with open('data/extracted_2024_i_english.json', 'w', encoding='utf-8') as f:
        json.dump(qs, f, indent=2, ensure_ascii=False)
    print("Saved to data/extracted_2024_i_english.json")

if __name__ == '__main__':
    asyncio.run(run())
