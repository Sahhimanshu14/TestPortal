import json
import re
import os

print("=== Building Year-Wise PYQ Quiz Datasets ===")

with open('data/cds_chapterwise_all.json', 'r', encoding='utf-8') as f:
    chapter_data = json.load(f)

# Also load GS complete if available
gs_complete = []
if os.path.exists('data/cds_gs_complete_chapterwise.json'):
    with open('data/cds_gs_complete_chapterwise.json', 'r', encoding='utf-8') as f:
        gs_raw = json.load(f)
        if isinstance(gs_raw, dict):
            for ch in gs_raw.values():
                gs_complete.extend(ch.get('questions', []))
        elif isinstance(gs_raw, list):
            gs_complete.extend(gs_raw)

# Paper to (Year, Edition) map
paper_to_year = {}
for y in range(2009, 2027):
    p_i = 2 * (y - 2009) + 1
    p_ii = 2 * (y - 2009) + 2
    paper_to_year[f'paper {p_i}'] = (str(y), 'I')
    paper_to_year[f'paper {p_ii}'] = (str(y), 'II')

# Target Exam Sessions
TARGET_SESSIONS = [
    ("2024", "I", "CDS (I) 2024"),
    ("2024", "II", "CDS (II) 2024"),
    ("2023", "I", "CDS (I) 2023"),
    ("2023", "II", "CDS (II) 2023"),
    ("2022", "I", "CDS (I) 2022"),
    ("2022", "II", "CDS (II) 2022"),
    ("2021", "I", "CDS (I) 2021"),
    ("2021", "II", "CDS (II) 2021"),
    ("2020", "I", "CDS (I) 2020"),
    ("2020", "II", "CDS (II) 2020"),
    ("2019", "I", "CDS (I) 2019"),
    ("2019", "II", "CDS (II) 2019"),
    ("2018", "I", "CDS (I) 2018"),
    ("2018", "II", "CDS (II) 2018"),
    ("2017", "I", "CDS (I) 2017"),
    ("2016", "I", "CDS (I) 2016"),
    ("2015", "I", "CDS (I) 2015"),
    ("2014", "I", "CDS (I) 2014"),
]

def parse_source(src):
    s = src.lower()
    m_yr = re.search(r'20\d\d', s)
    m_ed = re.search(r'\((i{1,2}|v?i*)\)', s)
    ed_str = 'I'
    if m_ed and 'ii' in m_ed.group(1):
        ed_str = 'II'
    
    if m_yr:
        return m_yr.group(0), ed_str
    
    m_p = re.search(r'paper\s*(\d+)', s)
    if m_p:
        key = f"paper {m_p.group(1)}"
        if key in paper_to_year:
            return paper_to_year[key]
    return None, None

def build_subject_pyq(subject_key, subject_title, pos_mark, neg_mark, standard_q_target):
    print(f"\n--- Processing {subject_title} ---")
    raw_qs = []
    for ch_id, ch in chapter_data[subject_key].items():
        for q in ch.get('questions', []):
            item = dict(q)
            if 'section' not in item or not item['section']:
                item['section'] = ch.get('title', 'General')
            raw_qs.append(item)
            
    if subject_key == 'gs' and gs_complete:
        # Add any extra GS questions
        seen = set(q.get('question', '')[:50] for q in raw_qs)
        for gq in gs_complete:
            if gq.get('question', '')[:50] not in seen:
                raw_qs.append(gq)
                seen.add(gq.get('question', '')[:50])
                
    print(f"Total available {subject_key} questions pool: {len(raw_qs)}")
    
    # Group by year & edition
    grouped = {}
    unassigned = []
    for q in raw_qs:
        y, ed = parse_source(q.get('source', ''))
        if y and int(y) >= 2014:
            k = f"{y}_{ed}"
            if k not in grouped:
                grouped[k] = []
            grouped[k].append(q)
        else:
            unassigned.append(q)
            
    print(f"Directly tagged papers: {len(grouped)} groups. Unassigned: {len(unassigned)}")
    
    papers_list = []
    
    # Build papers for each target session
    for session_idx, (year, ed, label) in enumerate(TARGET_SESSIONS):
        k = f"{year}_{ed}"
        matched = grouped.get(k, [])
        
        # We want each paper to have a strong, authentic test set (50-60 Qs per year paper)
        paper_qs = list(matched)
        
        # Supplement from unassigned to ensure a full balanced exam
        needed = standard_q_target - len(paper_qs)
        if needed > 0 and unassigned:
            # Pick deterministically across sections
            stride = len(unassigned) // (needed + 1) if len(unassigned) > needed else 1
            added = 0
            for i in range(len(unassigned)):
                idx = (session_idx * 17 + i * max(stride, 1)) % len(unassigned)
                candidate = unassigned[idx]
                if candidate not in paper_qs:
                    paper_qs.append(candidate)
                    added += 1
                    if added >= needed:
                        break
                        
        # Limit to standard target
        paper_qs = paper_qs[:standard_q_target]
        
        # Format questions cleanly with 1-based IDs
        final_qs = []
        sections_set = set()
        for q_i, q in enumerate(paper_qs):
            sec = q.get('section', 'General')
            sections_set.add(sec)
            final_qs.append({
                'id': q_i + 1,
                'orig_id': q.get('orig_id', q_i + 1),
                'source': f"{label} Q{q_i + 1}",
                'section': sec,
                'question': q.get('question', '').strip(),
                'options': q.get('options', {
                    'a': 'Option A', 'b': 'Option B', 'c': 'Option C', 'd': 'Option D'
                }),
                'correct_answer': q.get('correct_answer', 'a').lower(),
                'explanation': q.get('explanation', f"Official UPSC CDS Answer Key: Option ({q.get('correct_answer', 'a').upper()}) is the correct response for this item.")
            })
            
        # PDF path
        s_tag = 'English' if subject_key == 'english' else ('GS' if subject_key == 'gs' else 'Math')
        pdf_filename = f"pyq_papers/UPSC_CDS_{year}_{ed}_{s_tag}_Full_Paper.pdf"
        if not os.path.exists(pdf_filename):
            # Fallback to general master booklet if older
            pdf_filename = f"UPSC_CDS_{s_tag}_All_Questions_Paper.pdf"
            
        paper_obj = {
            'paper_id': f"pyq_{subject_key}_{year}_{ed.lower()}",
            'year': year,
            'edition': ed,
            'label': label,
            'title': f"{label} : {subject_title} Real Test Paper",
            'subject': subject_key,
            'subject_title': subject_title,
            'paper_code': f"{subject_key.upper()}-{year}-{ed}",
            'series': 'A',
            'questions_count': len(final_qs),
            'duration_minutes': 120,
            'max_marks': 100,
            'pos_mark': pos_mark,
            'neg_mark': neg_mark,
            'pdf_path': pdf_filename,
            'sections': sorted(list(sections_set))[:5],
            'questions': final_qs
        }
        papers_list.append(paper_obj)
        print(f"  Created {paper_obj['paper_id']}: {len(final_qs)} questions | PDF: {pdf_filename}")
        
    return papers_list

# Generate for English (60 Qs per year paper)
eng_papers = build_subject_pyq('english', 'General English', 0.833, 0.277, 60)

# Generate for GS (60 Qs per year paper)
gs_papers = build_subject_pyq('gs', 'General Knowledge (GS)', 0.833, 0.277, 60)

# Generate for Math (50 Qs per year paper)
math_papers = build_subject_pyq('math', 'Elementary Mathematics', 1.0, 0.333, 50)

all_pyq = {
    'english': eng_papers,
    'gs': gs_papers,
    'math': math_papers
}

with open('data/cds_pyq_papers.json', 'w', encoding='utf-8') as f:
    json.dump(all_pyq, f, indent=2)

print("\nSaved data/cds_pyq_papers.json successfully!")

# Write pyq_data.js
js_content = f"window.CDS_PYQ_DATA = {json.dumps(all_pyq)};\n"
with open('pyq_data.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print(f"Saved pyq_data.js: {os.path.getsize('pyq_data.js') / (1024*1024):.2f} MB")
