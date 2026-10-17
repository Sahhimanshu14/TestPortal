import winocr
import asyncio
import pymupdf as fitz
from PIL import Image
import json
import re

print("=== Extracting All 120 Questions from UPSC CDS 2024 (I) General Knowledge (GS) Full Paper ===")

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

async def extract_page_lines(img):
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
        # 1-column page
        w_all = [{'text': wd.text, 'x': wd.bounding_rect.x, 'y': wd.bounding_rect.y} for wd in words]
        return cluster_words(w_all)
    else:
        # 2-column page: find best gutter
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
        return cluster_words(w1) + cluster_words(w2)

async def run():
    doc = fitz.open('pyq_papers/UPSC_CDS_2024_I_GS_Full_Paper.pdf')
    print(f"Total pages in GS PDF: {len(doc)}")
    all_lines = []
    # In UPSC bilingual GS booklets, English pages are the EVEN pages:
    # 4, 6, 8, 10, ..., 44 (indices 3, 5, 7, ..., 43)
    for pno in range(3, len(doc), 2):
        page = doc[pno]
        pix = page.get_pixmap(dpi=150)
        img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
        plines = await extract_page_lines(img)
        print(f"Page {pno+1:2d} (English): extracted {len(plines)} lines")
        all_lines.extend(plines)
        
    with open('data/raw_lines_2024_i_gs.json', 'w', encoding='utf-8') as f:
        json.dump(all_lines, f, indent=2, ensure_ascii=False)
    print("Done! Total GS English lines extracted:", len(all_lines))

if __name__ == '__main__':
    asyncio.run(run())
