import winocr
import asyncio
import pymupdf as fitz
from PIL import Image
import json
import re
import os
import sys

print("=== Full Extraction of Authentic 2026-II English Paper ===")

async def extract_page_lines(page):
    pix = page.get_pixmap(dpi=150)
    img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
    w, h = img.size
    mid = w * 0.5
    res = await winocr.recognize_pil(img, lang='en')
    
    all_words = []
    for l in res.lines:
        for wd in l.words:
            all_words.append({
                'text': wd.text,
                'x': wd.bounding_rect.x,
                'y': wd.bounding_rect.y,
                'w': wd.bounding_rect.width,
                'h': wd.bounding_rect.height
            })
            
    # Filter running header/footer
    content_words = [w for w in all_words if 60 < w['y'] < h - 90]
    
    col1_words = [w for w in content_words if w['x'] + w['w'] / 2 < mid]
    col2_words = [w for w in content_words if w['x'] + w['w'] / 2 >= mid]
    
    def lines_from_words(words):
        if not words: return []
        words = sorted(words, key=lambda item: (item['y'], item['x']))
        lines = []
        for wd in words:
            attached = False
            for line in lines:
                avg_y = sum(item['y'] for item in line) / len(line)
                if abs(wd['y'] - avg_y) <= 10:
                    line.append(wd)
                    attached = True
                    break
            if not attached:
                lines.append([wd])
        lines = sorted(lines, key=lambda l: sum(item['y'] for item in l) / len(l))
        result = []
        for l in lines:
            l = sorted(l, key=lambda item: item['x'])
            result.append(' '.join(item['text'] for item in l))
        return result

    return lines_from_words(col1_words) + lines_from_words(col2_words)

def normalize_qnum(s):
    s = s.strip()
    s = re.sub(r'^[Il]\.', '1.', s)
    s = re.sub(r'^IO\.', '10.', s)
    s = re.sub(r'^ll\.', '11.', s)
    s = re.sub(r'^l2\.', '12.', s)
    m = re.match(r'^(\d{1,3})\s*[\.:\)]\s*(.*)', s)
    if m:
        return int(m.group(1)), m.group(2).strip()
    return None, s

async def run():
    pdf_path = 'pyq_papers/UPSC_CDS_2026_II_English_Full_Paper.pdf'
    doc = fitz.open(pdf_path)
    print(f"Opened {pdf_path} ({len(doc)} pages)")
    
    all_lines = []
    for pno in range(1, len(doc)):
        page_lines = await extract_page_lines(doc[pno])
        all_lines.extend(page_lines)
    doc.close()
    
    print(f"Extracted {len(all_lines)} raw assembled lines across all pages.")
    
    # Parse lines into structured questions
    questions = {}
    current_q = None
    current_opt = None
    direction_buffer = []
    expected_q = 1
    
    for l in all_lines:
        t = l.strip()
        if not t: continue
        
        # Filter running footers / exam codes
        if re.search(r'BFVS-F-GNE|T\.B\.C\.|^\s*\d{1,2}\s*$|\[\s*P\.?\s*T\.?\s*O\.?\s*\]', t):
            continue
            
        # Directions
        if re.match(r'^Directions\s*:', t, re.I):
            direction_buffer = [t]
            continue
        if direction_buffer and not re.match(r'^(?:[Il]|\d{1,3})\s*[\.:\)]', t) and not re.match(r'^\([a-d]\)', t, re.I):
            if len(direction_buffer) < 5:
                direction_buffer.append(t)
                continue
                
        # Question stem
        qn, rest = normalize_qnum(t)
        if qn is not None and expected_q <= qn <= expected_q + 2 and (not re.match(r'^\([a-d]\)', t, re.I)):
            current_q = {
                'number': qn,
                'stem': rest,
                'passage': ' '.join(direction_buffer) if direction_buffer else None,
                'options': {'a': '', 'b': '', 'c': '', 'd': ''}
            }
            questions[qn] = current_q
            current_opt = None
            direction_buffer = []
            expected_q = qn + 1
            continue
            
        # Options
        opt_m = re.match(r'^\(([a-dA-D])\)\s*(.*)', t)
        if opt_m and current_q:
            current_opt = opt_m.group(1).lower()
            current_q['options'][current_opt] = opt_m.group(2).strip()
            continue
            
        # Continuation
        if current_q:
            if current_opt:
                current_q['options'][current_opt] += (' ' if current_q['options'][current_opt] else '') + t
            else:
                current_q['stem'] += (' ' if current_q['stem'] else '') + t

    print(f"Successfully extracted {len(questions)} unique questions (1..120)!")
    
    # Save cleanly
    with open('data/extracted_2026_ii_english_clean.json', 'w', encoding='utf-8') as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
    print("Saved to data/extracted_2026_ii_english_clean.json")

if __name__ == '__main__':
    asyncio.run(run())
