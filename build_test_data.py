import os, sys, fitz, re, json

os.makedirs('data', exist_ok=True)

def clean_text(t):
    if not t:
        return ""
    t = re.sub(r'[\r\n]+', ' ', t)
    t = re.sub(r'[A-Z0-9\-\.\/]{4,}\-[A-Z0-9\-\.\/]{2,}', ' ', t) # strip paper codes like P-PQFB-L-RA/9A
    t = re.sub(r'O\-DETA\-[A-Z\.\-]+', ' ', t)
    t = re.sub(r'T\.DETA\.[A-Z\.\-]+', ' ', t)
    t = re.sub(r'Page \d+ of \d+', ' ', t)
    t = re.sub(r'\s+', ' ', t)
    return t.strip()

# ==========================================
# 1. PARSE GS (QUESTIONS + EXPLANATIONS)
# ==========================================
print('--- 1. Processing GS ---')
doc_gs = fitz.open('CDS_GS_Chapterwise_PYQ.pdf')
gs_text = '\n'.join([p.get_text() for p in doc_gs])
doc_gs_key = fitz.open('CDS_GS_Chapterwise_Answer_Key.pdf')
gs_key_text = '\n'.join([p.get_text() for p in doc_gs_key])

gs_key_matches = re.findall(r'(\d+)\s*\n\s*(CDS[^\n]+)\s*\n\s*\(([A-D])\)\s*\n\s*(.*?)(?=\n\d+\s*\n\s*CDS|\nCHAPTER|\Z)', gs_key_text, re.DOTALL)
gs_keys_dict = {}
for qn, paper, ans, exp in gs_key_matches:
    gs_keys_dict[int(qn)] = {
        'paper': paper.strip(),
        'answer': ans.strip().lower(),
        'explanation': ' '.join(exp.strip().split())
    }

gs_blocks = re.split(r'Q\.(\d+)\s*\|\s*\[(UPSC\s+CDS[^\n\]]+)\]', gs_text)
gs_questions = []
for i in range(1, len(gs_blocks), 3):
    qn = int(gs_blocks[i])
    source = gs_blocks[i+1].strip()
    rest = gs_blocks[i+2].strip()
    
    opt_m = re.search(r'^(.*?)\s*\(a\)\s*(.*?)\s*\(b\)\s*(.*?)\s*\(c\)\s*(.*?)\s*\(d\)\s*(.*?)$', rest, re.DOTALL)
    if opt_m:
        stem = ' '.join(opt_m.group(1).split())
        oa = ' '.join(opt_m.group(2).split())
        ob = ' '.join(opt_m.group(3).split())
        oc = ' '.join(opt_m.group(4).split())
        od = ' '.join(opt_m.group(5).split())
        od = re.sub(r'UPSC CDS GENERAL KNOWLEDGE.*', '', od).strip()
        od = re.sub(r'CHAPTER \d+.*', '', od).strip()
        
        kd = gs_keys_dict.get(qn, {'answer': 'a', 'explanation': ''})
        sec = 'Indian Polity & Constitution' if qn <= 8 else ('Indian History & Freedom Struggle' if qn <= 14 else ('Geography' if qn <= 20 else 'General Science & Defence'))
        
        gs_questions.append({
            'id': qn,
            'source': source,
            'section': sec,
            'question': stem,
            'options': {'a': oa, 'b': ob, 'c': oc, 'd': od},
            'correct_answer': kd['answer'],
            'explanation': kd.get('explanation', '')
        })

print(f'GS total: {len(gs_questions)} questions')

# ==========================================
# 2. PARSE ENGLISH
# ==========================================
print('--- 2. Processing English ---')
doc_eng = fitz.open('CDS_English_Chapterwise_PYQ.pdf')
eng_text = '\n'.join([p.get_text() for p in doc_eng])
doc_eng_key = fitz.open('CDS_English_Chapterwise_Answer_Key.pdf')
eng_key_text = '\n'.join([p.get_text() for p in doc_eng_key])

parts = re.split(r'CHAPTER\s+(\d+)', eng_key_text)
eng_keys = {}
for i in range(1, len(parts), 2):
    c_num = int(parts[i])
    c_text = parts[i+1]
    matches = re.findall(r'(?:^|\n)\s*(\d+)\s*\n\s*\(?([a-dA-D])\)?', c_text)
    eng_keys[c_num] = dict([(int(q), ans.lower()) for q, ans in matches])

chap_titles_eng = {
    1: 'Spotting Errors',
    2: 'Synonyms',
    3: 'Antonyms',
    4: 'Idioms and Phrases',
    5: 'Ordering of Words in a Sentence (PQRS)',
    6: 'Ordering of Sentences in a Paragraph (S1-S6)',
    7: 'Fill in the Blanks',
    8: 'Prepositions and Determiners',
    9: 'Parts of Speech Identification',
    10: 'Completion of Sentences',
    11: 'Cloze Composition',
    12: 'Reading Comprehension',
    13: 'Usage of Paired Words',
    14: 'Spelling Test (Orthography)'
}

eng_chap_splits = re.split(r'CHAPTER\s+(\d+)', eng_text)
all_eng_chapters = {}

for c_idx in range(1, len(eng_chap_splits), 2):
    c_num = int(eng_chap_splits[c_idx])
    c_text = eng_chap_splits[c_idx+1]
    c_title = chap_titles_eng.get(c_num, f'Chapter {c_num}')
    
    q_splits = re.split(r'\n(\d+)\.\n\[(CDS[^\n\]]+)\]', c_text)
    clean_list = []
    
    for j in range(1, len(q_splits), 3):
        q_num = int(q_splits[j])
        src = q_splits[j+1].strip()
        body = q_splits[j+2].strip()
        
        ans = eng_keys.get(c_num, {}).get(q_num)
        if not ans:
            continue
            
        m = re.search(r'^(.*?)\s*\(a\)\s*(.*?)\s*\(b\)\s*(.*?)\s*\(c\)\s*(.*?)\s*\(d\)\s*(.*?)$', body, re.DOTALL)
        if m:
            stem = clean_text(m.group(1))
            oa = clean_text(m.group(2))
            ob = clean_text(m.group(3))
            oc = clean_text(m.group(4))
            od = clean_text(m.group(5))
            
            stem = re.sub(r'^\d+[\.\s]+', '', stem)
            
            # Filter clean questions
            if 3 <= len(stem) <= 320 and 1 <= len(oa) <= 120 and 1 <= len(ob) <= 120 and 1 <= len(oc) <= 120 and 1 <= len(od) <= 120:
                if not any(x in oa for x in ['(a)', '(b)', '(c)']) and not any(x in ob for x in ['(a)', '(b)', '(c)']):
                    clean_list.append({
                        'orig_id': q_num,
                        'source': src,
                        'section': c_title,
                        'question': stem,
                        'options': {'a': oa, 'b': ob, 'c': oc, 'd': od},
                        'correct_answer': ans,
                        'explanation': f"Official UPSC CDS Answer Key: Option ({ans.upper()}) is the correct response for this item."
                    })
    all_eng_chapters[c_num] = {'title': c_title, 'questions': clean_list}
    print(f'Eng Ch {c_num} ({c_title}): {len(clean_list)} questions')

# Build CDS English Mock (120 Questions)
# Allocation:
# Ch 1 Spotting Errors: 20
# Ch 2 Synonyms: 15
# Ch 3 Antonyms: 15
# Ch 4 Idioms & Phrases: 15
# Ch 5 PQRS (Ordering of Words): 15
# Ch 6 Sentence Ordering (S1-S6): 15
# Ch 7 Fill in Blanks: 15
# Ch 8 Prepositions / Ch 9 Parts of Speech: 10 (5 each)
eng_mock_120 = []
mock_plan_eng = [
    (1, 20),
    (2, 15),
    (3, 15),
    (4, 15),
    (5, 15),
    (6, 15),
    (7, 15),
    (8, 5),
    (9, 5),
]

q_counter = 1
for c_num, count in mock_plan_eng:
    qs = all_eng_chapters[c_num]['questions'][:count]
    for q in qs:
        item = dict(q)
        item['id'] = q_counter
        eng_mock_120.append(item)
        q_counter += 1

print(f'English Mock 120 created: {len(eng_mock_120)} questions')

# ==========================================
# 3. PARSE MATHEMATICS
# ==========================================
print('--- 3. Processing Mathematics ---')
doc_math = fitz.open('CDS_Math_Chapterwise_PYQ.pdf')
math_text = '\n'.join([p.get_text() for p in doc_math])
doc_math_key = fitz.open('CDS_Math_Chapterwise_Answer_Key.pdf')
math_key_text = '\n'.join([p.get_text() for p in doc_math_key])

parts = re.split(r'CHAPTER\s+(\d+)', math_key_text)
math_keys = {}
for i in range(1, len(parts), 2):
    c_num = int(parts[i])
    c_text = parts[i+1]
    matches = re.findall(r'(?:^|\n)\s*(\d+)\s*\n\s*\(?([a-dA-D])\)?', c_text)
    math_keys[c_num] = dict([(int(q), ans.lower()) for q, ans in matches])

chap_titles_math = {
    1: 'Number System & Divisibility',
    2: 'HCF, LCM & Logarithms',
    3: 'Percentages, Profit, Loss & Discount',
    4: 'Simple & Compound Interest, Ratio & Mixtures',
    5: 'Time, Speed & Distance, Time & Work',
    6: 'Algebra, Polynomials & Linear Equations',
    7: 'Quadratic Equations & Progressions',
    8: 'Trigonometry & Heights and Distances',
    9: 'Geometry: Lines, Angles, Triangles & Polygons',
    10: 'Geometry: Circles, Chords & Tangents',
    11: 'Mensuration 2D: Areas & Perimeters',
    12: 'Mensuration 3D: Surface Areas & Volumes',
    13: 'Statistics & Data Interpretation'
}

math_chap_splits = re.split(r'CHAPTER\s+(\d+)', math_text)
all_math_chapters = {}

for c_idx in range(1, len(math_chap_splits), 2):
    c_num = int(math_chap_splits[c_idx])
    c_text = math_chap_splits[c_idx+1]
    c_title = chap_titles_math.get(c_num, f'Chapter {c_num}')
    
    q_splits = re.split(r'\n(\d+)\.\n\[(CDS[^\n\]]+)\]', c_text)
    clean_list = []
    
    for j in range(1, len(q_splits), 3):
        q_num = int(q_splits[j])
        src = q_splits[j+1].strip()
        body = q_splits[j+2].strip()
        
        ans = math_keys.get(c_num, {}).get(q_num)
        if not ans:
            continue
            
        m = re.search(r'^(.*?)\s*\(a\)\s*(.*?)\s*\(b\)\s*(.*?)\s*\(c\)\s*(.*?)\s*\(d\)\s*(.*?)$', body, re.DOTALL)
        if m:
            stem = clean_text(m.group(1))
            oa = clean_text(m.group(2))
            ob = clean_text(m.group(3))
            oc = clean_text(m.group(4))
            od = clean_text(m.group(5))
            
            stem = re.sub(r'^\d+[\.\s]+', '', stem)
            
            if 3 <= len(stem) <= 320 and 1 <= len(oa) <= 120 and 1 <= len(ob) <= 120 and 1 <= len(oc) <= 120 and 1 <= len(od) <= 120:
                if not any(x in oa for x in ['(a)', '(b)', '(c)']) and not any(x in ob for x in ['(a)', '(b)', '(c)']):
                    clean_list.append({
                        'orig_id': q_num,
                        'source': src,
                        'section': c_title,
                        'question': stem,
                        'options': {'a': oa, 'b': ob, 'c': oc, 'd': od},
                        'correct_answer': ans,
                        'explanation': f"Official UPSC CDS Answer Key: Option ({ans.upper()}) is the correct response for this item."
                    })
    all_math_chapters[c_num] = {'title': c_title, 'questions': clean_list}
    print(f'Math Ch {c_num} ({c_title}): {len(clean_list)} questions')

# Build CDS Mathematics Mock (100 Questions)
# Allocation matching UPSC Blueprint:
# Ch 1 Number System: 15
# Ch 2 HCF, LCM & Log: 6
# Ch 3 Percentages & Profit/Loss: 10
# Ch 4 SI, CI & Ratio: 8
# Ch 5 Time & Distance / Work: 10
# Ch 6 Algebra & Polynomials: 12
# Ch 7 Quadratic Equations: 5
# Ch 8 Trigonometry: 12
# Ch 9 Geometry (Triangles/Lines): 10
# Ch 10 Geometry (Circles): 4
# Ch 11 Mensuration 2D: 4
# Ch 12 Mensuration 3D: 4
math_mock_100 = []
mock_plan_math = [
    (1, 15),
    (2, 6),
    (3, 10),
    (4, 8),
    (5, 10),
    (6, 12),
    (7, 5),
    (8, 12),
    (9, 10),
    (10, 4),
    (11, 4),
    (12, 4),
]

q_counter = 1
for c_num, count in mock_plan_math:
    qs = all_math_chapters[c_num]['questions'][:count]
    for q in qs:
        item = dict(q)
        item['id'] = q_counter
        math_mock_100.append(item)
        q_counter += 1

print(f'Math Mock 100 created: {len(math_mock_100)} questions')

# Save all JSON datasets
with open('data/cds_mock_english_120.json', 'w', encoding='utf-8') as f:
    json.dump(eng_mock_120, f, indent=2, ensure_ascii=False)

with open('data/cds_mock_gs.json', 'w', encoding='utf-8') as f:
    json.dump(gs_questions, f, indent=2, ensure_ascii=False)

with open('data/cds_mock_math_100.json', 'w', encoding='utf-8') as f:
    json.dump(math_mock_100, f, indent=2, ensure_ascii=False)

# Chapterwise aggregate
chapterwise_data = {
    'english': {f'ch_{k}': v for k, v in all_eng_chapters.items()},
    'gs': {
        'ch_1': {'title': 'Indian Polity & Constitution', 'questions': [q for q in gs_questions if q['section'] == 'Indian Polity & Constitution']},
        'ch_2': {'title': 'Indian History & Freedom Struggle', 'questions': [q for q in gs_questions if q['section'] == 'Indian History & Freedom Struggle']},
        'ch_3': {'title': 'Geography (Physical, Indian & World)', 'questions': [q for q in gs_questions if q['section'] == 'Geography']},
        'ch_4': {'title': 'General Science & Defence', 'questions': [q for q in gs_questions if q['section'] == 'General Science & Defence']},
    },
    'math': {f'ch_{k}': v for k, v in all_math_chapters.items()}
}

with open('data/cds_chapterwise_all.json', 'w', encoding='utf-8') as f:
    json.dump(chapterwise_data, f, indent=2, ensure_ascii=False)

print('=== DATASETS SUCCESSFULLY GENERATED ===')
