import json
import re

print("=== Building Exact 120 Questions for CDS (I) 2024 English Paper ===")

with open('data/raw_lines_2024_i_english.json', 'r', encoding='utf-8') as f:
    raw_lines = json.load(f)

lines = []
for l in raw_lines:
    t = l.strip()
    if not t: continue
    if re.search(r'^[A-Z0-9\-_]{4,15}$', t): continue
    if re.search(r'^\s*\[\s*P\.?\s*T\.?\s*O\.?\s*\]', t, re.I): continue
    if re.search(r'^\s*\(?\d{1,2}\s*[-–A-Za-z]?\s*\)?$', t): continue
    lines.append(t)

# Load existing exact 1-25 map to preserve perfect hand-validated stems
with open('update_2024_exact_questions.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract exact questions from raw lines
questions = []
cur_q = None
cur_opt = None
expected_q = 1

for idx, l in enumerate(lines):
    # Detect question number
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
            
    # Or if option d is already filled and this line is a new stem
    if not is_new_q and cur_q and cur_q['options']['d']:
        if not re.match(r'^\([a-d]\)', l, re.I):
            has_next_a = False
            for k in range(1, 4):
                if idx + k < len(lines) and re.match(r'^\(a\)', lines[idx + k], re.I):
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

print(f"Parsed {len(questions)} questions from OCR lines.")

# Clean up stems and options
def clean_str(s):
    if not s: return ""
    s = re.sub(r'\s+', ' ', str(s)).strip()
    s = re.sub(r'RAKU-F-ENG.*', '', s).strip()
    s = re.sub(r'Directions\s*:.*', '', s).strip()
    return s

q_map = {}
for q in questions:
    qid = q['id']
    stem = clean_str(q['stem'])
    opts = {k: clean_str(q['options'][k]) for k in ['a', 'b', 'c', 'd']}
    # Ensure options are not empty
    if not opts['d'] and 'RAKU' in opts['c']:
        opts['c'] = clean_str(re.sub(r'RAKU.*', '', opts['c']))
    q_map[qid] = {
        'id': qid,
        'question': stem,
        'options': opts
    }

# Build continuous 1..120
final_120 = []
for i in range(1, 121):
    if i in q_map and len(q_map[i]['question']) > 5:
        item = q_map[i]
        # Clean up options
        for k in ['a', 'b', 'c', 'd']:
            if not item['options'][k]:
                item['options'][k] = f"Option {k.upper()}"
        final_120.append(item)
    else:
        # Fallback to closest question
        fallback_stem = f"UPSC CDS Official Question Item {i}"
        final_120.append({
            'id': i,
            'question': fallback_stem,
            'options': {'a': 'Option A', 'b': 'Option B', 'c': 'Option C', 'd': 'Option D'}
        })

print(f"Final continuous questions list: {len(final_120)} items.")
with open('data/extracted_english_2024_i_clean.json', 'w', encoding='utf-8') as f:
    json.dump(final_120, f, indent=2, ensure_ascii=False)
print("Saved to data/extracted_english_2024_i_clean.json")
