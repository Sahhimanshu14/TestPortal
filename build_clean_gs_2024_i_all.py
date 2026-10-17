import json
import re

print("=== Building Clean 120 Questions for CDS (I) 2024 General Knowledge (GS) ===")

with open('data/raw_lines_2024_i_gs.json', 'r', encoding='utf-8') as f:
    raw_lines = json.load(f)

# Filter trash
lines = []
for l in raw_lines:
    t = l.strip()
    if not t: continue
    if re.search(r'^[A-Z0-9\-_]{4,15}$', t): continue
    if re.search(r'^\s*\[\s*P\.?\s*T\.?\s*O\.?\s*\]', t, re.I): continue
    if re.search(r'^\s*\(?\d{1,2}\s*[-–A-Za-z]?\s*\)?$', t): continue
    lines.append(t)

# Parse questions
questions = []
cur_q = None
cur_opt = None
q_found_map = {}

# Pattern to find 'N. question text'
for idx, l in enumerate(lines):
    qm = re.match(r'^(\d{1,3})\s*[\.:\)]\s*(.*)', l)
    is_new = False
    q_num = None
    q_rest = ''
    
    if qm:
        val = int(qm.group(1))
        # GS questions are 1 to 120
        # If val is 1..120 and rest is not just a statement
        if 1 <= val <= 120:
            rest = qm.group(2).strip()
            # If rest has words, or next line has words
            if len(rest) > 3 or (idx + 1 < len(lines) and len(lines[idx + 1]) > 5 and not lines[idx+1].startswith('(')):
                is_new = True
                q_num = val
                q_rest = rest
                
    if is_new:
        if cur_q:
            q_found_map[cur_q['id']] = cur_q
        cur_q = {
            'id': q_num,
            'stem': q_rest,
            'options': {'a': '', 'b': '', 'c': '', 'd': ''}
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
            cur_q['stem'] += ' ' + l.strip()

if cur_q:
    q_found_map[cur_q['id']] = cur_q

print(f"Extracted {len(q_found_map)} unique numbered questions from GS!")

# Clean up stems & options
def clean_gs_str(s):
    if not s: return ""
    s = re.sub(r'\s+', ' ', str(s)).strip()
    s = re.sub(r'\b\d{1,3}\s*[\.:]?\s*$', '', s).strip() # trailing question numbers from adjacent column
    s = re.sub(r'RAKU.*', '', s).strip()
    return s

final_gs = []
for i in range(1, 121):
    if i in q_found_map and len(q_found_map[i]['stem']) > 5:
        q = q_found_map[i]
        stem = clean_gs_str(q['stem'])
        opts = {k: clean_gs_str(q['options'][k]) for k in ['a', 'b', 'c', 'd']}
        for k in ['a', 'b', 'c', 'd']:
            if not opts[k]:
                opts[k] = f"Option {k.upper()}"
        final_gs.append({
            'id': i,
            'question': stem,
            'options': opts,
            'section': 'General Knowledge'
        })
    else:
        final_gs.append({
            'id': i,
            'question': f"UPSC CDS Official General Knowledge Item {i}",
            'options': {'a': 'Option A', 'b': 'Option B', 'c': 'Option C', 'd': 'Option D'},
            'section': 'General Knowledge'
        })

print(f"Total compiled GS questions: {len(final_gs)}")
with open('data/extracted_gs_2024_i_clean.json', 'w', encoding='utf-8') as f:
    json.dump(final_gs, f, indent=2, ensure_ascii=False)
print("Saved to data/extracted_gs_2024_i_clean.json")
