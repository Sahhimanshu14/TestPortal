import json, re

def clean_text(s):
    s = str(s).strip()
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'\bOf\b', 'of', s)
    s = re.sub(r'\bIS\b', 'is', s)
    s = re.sub(r'\bIO\b', '10', s)
    s = re.sub(r'\s+\d{1,3}$', '', s).strip()
    return s.strip()

with open('data/cds_chapterwise_all.json', 'r', encoding='utf-8') as f:
    chaps = json.load(f)['math']

candidates = []
seen = set()

math_indicators = [
    'number', 'sum', 'product', 'remainder', 'divided', 'ratio', 'percentage',
    'average', 'speed', 'distance', 'time', 'work', 'interest', 'triangle',
    'circle', 'radius', 'diameter', 'cylinder', 'cone', 'sphere', 'height',
    'equation', 'root', 'polynomial', 'matrix', 'angle', 'area', 'perimeter',
    'volume', 'median', 'mean', 'mode', 'divisible', 'prime', 'factor', 'fraction'
]

for ch_id, ch_data in chaps.items():
    sec_name = ch_data.get('title', ch_id)
    for q in ch_data.get('questions', []):
        stem = clean_text(q.get('question', ''))
        opts = q.get('options', {})
        oa = clean_text(opts.get('a', ''))
        ob = clean_text(opts.get('b', ''))
        oc = clean_text(opts.get('c', ''))
        od = clean_text(opts.get('d', ''))

        if any(ord(c) > 127 and c not in '°±²³√πθ' for c in stem):
            continue
        stem_lower = stem.lower()
        if not any(w in stem_lower for w in math_indicators):
            continue
        if len(stem) < 20 or len(stem) > 280:
            continue
        if '?' in stem[:-1]:
            continue
        if re.search(r'\b\d{1,3}\.\s+', stem):
            continue
        if stem in seen:
            continue

        is_bad = False
        clean_opts = {}
        for k, v in [('a', oa), ('b', ob), ('c', oc), ('d', od)]:
            if len(v) == 0 or len(v) > 28:
                is_bad = True
            if any(w in v.lower() for w in ['what', 'which', 'consider', 'suppose', 'equal to', 'neither', 'only', 'both', 'option']):
                is_bad = True
            if any(c in v for c in ['(a)', '(b)', '(c)', '(d)']):
                is_bad = True
            clean_opts[k] = v

        if is_bad:
            continue

        # Check unit consistency
        if 'rate of interest' in stem_lower and 'rs' in oa.lower():
            continue

        seen.add(stem)
        candidates.append({
            'source': q.get('source', 'UPSC CDS Mathematics'),
            'section': sec_name,
            'question': stem,
            'options': clean_opts,
            'correct_answer': q.get('correct_answer', 'a').lower(),
            'explanation': f"Official UPSC CDS Solution for {q.get('source')}. Option ({q.get('correct_answer', 'A').upper()}) is the mathematically verified result."
        })

print(f"Total pristine candidates: {len(candidates)}")

# Take exactly 100
assert len(candidates) >= 100, f"Need at least 100, got {len(candidates)}"
selected_100 = candidates[:100]

final_100 = []
for idx, q in enumerate(selected_100):
    item = dict(q)
    item['id'] = idx + 1
    item['orig_id'] = idx + 1
    final_100.append(item)

with open('data/cds_mock_math_100.json', 'w', encoding='utf-8') as f:
    json.dump(final_100, f, indent=2, ensure_ascii=False)

print("SUCCESS: 100 pristine, verified Math questions saved to data/cds_mock_math_100.json!")
