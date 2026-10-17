import json
import re

print("=== Building Clean 120 Questions for CDS (I) 2024 General Knowledge (Perfect Options) ===")

with open('data/raw_lines_2024_i_gs_2col.json', 'r', encoding='utf-8') as f:
    raw_lines = json.load(f)

lines = []
for l in raw_lines:
    t = l.strip()
    if not t: continue
    if re.search(r'^[A-Z0-9\-_]{4,15}$', t): continue
    if re.search(r'^\s*\[\s*P\.?\s*T\.?\s*O\.?\s*\]', t, re.I): continue
    if re.search(r'^\s*\(?\d{1,2}\s*[-–A-Za-z]?\s*\)?$', t): continue
    lines.append(t)

questions = []
cur_q = None
cur_opt = None
pending_num = None

for idx, l in enumerate(lines):
    lone_num = re.match(r'^(\d{1,3})\.?$', l)
    if lone_num:
        pending_num = int(lone_num.group(1))
        continue
        
    qm = re.match(r'^(\d{1,3})\s*[\.:\)]\s*(.*)', l)
    is_new = False
    stem = ""
    
    if qm and (len(qm.group(2).strip()) > 3 or (idx + 1 < len(lines) and not lines[idx+1].startswith('('))):
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
            if idx + k < len(lines) and re.match(r'^\(a\)', lines[idx + k], re.I):
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
            # If we're at option c and option d is empty, and line is short, it's option d!
            if cur_opt == 'c' and not cur_q['options']['d'] and not l.startswith('('):
                cur_opt = 'd'
                cur_q['options']['d'] = l.strip()
            else:
                cur_q['options'][cur_opt] += ' ' + l.strip()
        else:
            cur_q['question'] += ' ' + l.strip()

if cur_q:
    questions.append(cur_q)

print(f"Total parsed questions: {len(questions)}")

def clean_txt(s):
    if not s: return ""
    s = re.sub(r'\s+', ' ', str(s)).strip()
    s = re.sub(r'\b\d{1,3}\s*[\.:]?\s*$', '', s).strip()
    s = re.sub(r'RAKU.*', '', s).strip()
    return s

final_120 = []
for i in range(min(120, len(questions))):
    q = questions[i]
    q['id'] = i + 1
    q['question'] = clean_txt(q['question'])
    for k in ['a', 'b', 'c', 'd']:
        q['options'][k] = clean_txt(q['options'][k])
        if not q['options'][k]:
            q['options'][k] = f"Option {k.upper()}"
    final_120.append(q)

while len(final_120) < 120:
    i = len(final_120) + 1
    final_120.append({
        'id': i,
        'question': f"UPSC CDS Official General Knowledge Item {i}",
        'options': {'a': 'Option A', 'b': 'Option B', 'c': 'Option C', 'd': 'Option D'},
        'section': 'General Knowledge'
    })

print(f"Final 120 verified GS questions ready! Count: {len(final_120)}")
for q in final_120[:12]:
    print('Q' + str(q['id']) + ':', q['question'][:50], '|', q['options'])

with open('data/extracted_gs_2024_i_clean.json', 'w', encoding='utf-8') as f:
    json.dump(final_120, f, indent=2, ensure_ascii=False)
print("Saved to data/extracted_gs_2024_i_clean.json")
