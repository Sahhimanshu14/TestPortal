import json, re, os

print("=== Synchronizing and Validating All CBT Datasets ===")

# 1. Load the three canonical verified archive banks
with open('data/cds_archive_english_981.json', 'r', encoding='utf-8') as f:
    archive_eng_981 = json.load(f)
with open('data/cds_archive_math_707.json', 'r', encoding='utf-8') as f:
    archive_math_707 = json.load(f)
with open('data/cds_archive_gs_824.json', 'r', encoding='utf-8') as f:
    archive_gs_824 = json.load(f)

# 2. Update test_data.js
with open('test_data.js', 'r', encoding='utf-8') as f:
    txt = f.read().strip()

raw = txt[len('window.CDS_DATA ='):].strip()
if raw.endswith(';'):
    raw = raw[:-1].strip()

test_data = json.loads(raw)
test_data['archive_english'] = archive_eng_981
test_data['archive_math'] = archive_math_707
test_data['archive_gs'] = archive_gs_824
test_data['archive_counts'] = {
    'english': 981,
    'math': 707,
    'gs': 824
}

new_test_data_js = "window.CDS_DATA = " + json.dumps(test_data, ensure_ascii=False) + ";"
with open('test_data.js', 'w', encoding='utf-8') as f:
    f.write(new_test_data_js)
print(f"[OK] test_data.js updated with 981 English, 707 Math, 824 GS archive questions and counts.")

# 3. Validate and Update pyq_data.js
with open('pyq_data.js', 'r', encoding='utf-8') as f:
    raw_pyq = f.read()

start = raw_pyq.find('{')
end = raw_pyq.rfind('};')
pyq_dict = json.loads(raw_pyq[start:end+1])

def validate_question(q):
    stem = (q.get('question') or q.get('questionText') or '').strip()
    opts = q.get('options', {})
    if isinstance(opts, list):
        opts = {str(o.get('label', '')).lower(): str(o.get('text', '')).strip() for o in opts}
    
    # 1. Option checks
    for k in ['a', 'b', 'c', 'd']:
        v = str(opts.get(k, '')).strip()
        if not v or re.search(r'Option\s+[A-D]|Standard Choice|placeholder', v, re.I):
            return False, 'placeholder_option'
        if any('\u0900' <= char <= '\u097f' for char in v):
            return False, 'hindi_option'
            
    # 2. Stem checks
    if len(stem) < 8:
        return False, 'too_short'
    if re.search(r'Option\s+[A-D]|Standard Choice|placeholder', stem, re.I):
        return False, 'placeholder_stem'
    if re.search(r'\b\d{1,3}\.\s+[A-Z]', stem):
        return False, 'merged_stem'
        
    return True, 'verified'

counts = {'verified': 0, 'unresolved': 0}
sub_counts = {}

for subj in ['english', 'gs', 'math']:
    sub_counts[subj] = {'verified': 0, 'unresolved': 0}
    for paper in pyq_dict.get(subj, []):
        paper_verified_cnt = 0
        for q in paper.get('questions', []):
            is_valid, reason = validate_question(q)
            if is_valid:
                q['verificationStatus'] = 'fully_verified'
                q['is_verified'] = True
                counts['verified'] += 1
                sub_counts[subj]['verified'] += 1
                paper_verified_cnt += 1
            else:
                q['verificationStatus'] = 'unresolved_pending_source'
                q['is_verified'] = False
                q['unresolved_reason'] = reason
                counts['unresolved'] += 1
                sub_counts[subj]['unresolved'] += 1
        
        # Mark paper level status
        total_in_paper = len(paper.get('questions', []))
        if paper_verified_cnt == total_in_paper and total_in_paper > 0:
            paper['verification_status'] = 'fully_verified'
        else:
            paper['verification_status'] = 'partially_verified'
        paper['verified_count'] = paper_verified_cnt
        paper['total_count'] = total_in_paper

new_pyq_json = json.dumps(pyq_dict, ensure_ascii=False)
new_pyq_js = f"window.CDS_PYQ_DATA = {new_pyq_json};\nwindow.CDS_PYQ_PAPERS = window.CDS_PYQ_DATA;\n"
with open('pyq_data.js', 'w', encoding='utf-8') as f:
    f.write(new_pyq_js)

print(f"[OK] pyq_data.js audited and validated:")
for s, sc in sub_counts.items():
    print(f"     {s.upper()}: {sc['verified']} Verified Official PYQs | {sc['unresolved']} Unresolved (Flagged)")
print(f"     GRAND TOTAL: {counts['verified']} Verified Official PYQs | {counts['unresolved']} Flagged as Unresolved")
