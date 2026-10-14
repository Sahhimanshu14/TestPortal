import json, re

def strip_trailing_garbage(text):
    if not text:
        return ""
    # Strip paper codes like P-DETB-J-HL - A 102. 103. 38
    text = re.sub(r'P\-[A-Z0-9\-\/]+\s*[\-A-Z0-9\s]*', ' ', text)
    text = re.sub(r'T\-[A-Z0-9\-\/]+\s*[\-A-Z0-9\s]*', ' ', text)
    text = re.sub(r'Q\-[A-Z0-9\-\/]+\s*[\-A-Z0-9\s]*', ' ', text)
    text = re.sub(r'SPSS\-[A-Z0-9\-\/]+\s*[\-A-Z0-9\s]*', ' ', text)
    
    # Match patterns where next question starts
    patterns = [
        r'\s+\d{1,3}\.\s+.*',
        r'\s+IOS\.\s+.*',
        r'\s+Which\s+(?:one|of|among|substances|water|is|are|country|dance|metals|water|plant|places|statements)\b.*',
        r'\s+Consider\s+the\s+following.*',
        r'\s+Identify\s+the\s+correct.*',
        r'\s+What\s+(?:is|was|are|does|are)\b.*',
        r'\s+Who\s+(?:among|was|were|holds)\b.*',
        r'\s+Where\s+(?:is|was)\b.*',
        r'\s+When\s+(?:was|did|a)\b.*',
        r'\s+In\s+(?:appreciation|IP|the|IP\s+Spoofing)\b.*',
        r'\s+Match\s+List.*',
        r'\s+Select\s+the\s+correct.*',
        r'\s+Directions\s*:.*',
        r'\s+Fat\s+can\s+be\s+separated.*',
        r'\s+Cattle\s+are\s+capable.*',
        r'\s+Central\s+and\s+State\s+govern-?\s*ments\b.*',
        r'\s+Neither\s+I\s+nor\s+2\s+\d+.*',
        r'\s+Use\s+of\s+superior\s+military\s+technology\s+by\s+the\s+invading\s+army\s+\d+.*',
        r'\s+It\s+will\s+make\s+the\s+temperature\s+go\s+up\s+and\s+down\s+\d+.*',
        r'\s+mountain\s+ranges.*'
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m and m.start() > 2:
            text = text[:m.start()].strip()
            
    # Clean multiple spaces and trailing hyphens
    text = re.sub(r'\s+', ' ', text).strip()
    text = text.rstrip('- ').rstrip(',').strip()
    return text

def clean_all():
    with open('data/cds_gs_complete_chapterwise.json', 'r', encoding='utf-8') as f:
        qs = json.load(f)

    cleaned_count = 0
    for q in qs:
        # Clean stem
        stem_before = q['question']
        stem_after = strip_trailing_garbage(stem_before)
        if stem_after != stem_before:
            q['question'] = stem_after

        # Clean each option
        for k in ['a', 'b', 'c', 'd']:
            orig = q['options'][k]
            cleaned = strip_trailing_garbage(orig)
            if cleaned != orig:
                q['options'][k] = cleaned
                cleaned_count += 1

    print(f"Cleaned {cleaned_count} options across all 227 questions!")

    # Validate all 227 questions
    for q in qs:
        qid = q['id']
        for k in ['a', 'b', 'c', 'd']:
            v = q['options'][k].strip()
            assert len(v) > 0, f"Q{qid} option {k} is empty!"
            assert len(v) <= 220, f"Q{qid} option {k} is too long ({len(v)}): {v}"
            assert not any(t in v for t in ['(a)', '(b)', '(c)', '(d)']), f"Q{qid} option {k} has option tag: {v}"

    with open('data/cds_gs_complete_chapterwise.json', 'w', encoding='utf-8') as f:
        json.dump(qs, f, indent=2, ensure_ascii=False)
    print("Saved clean data/cds_gs_complete_chapterwise.json!")

    # Update data/cds_mock_gs.json
    mock_gs = [dict(q) for q in qs[:120]]
    for i, q in enumerate(mock_gs):
        q['id'] = i + 1
    with open('data/cds_mock_gs.json', 'w', encoding='utf-8') as f:
        json.dump(mock_gs, f, indent=2, ensure_ascii=False)
    print("Saved clean data/cds_mock_gs.json!")

    # Update data/cds_chapterwise_all.json
    with open('data/cds_chapterwise_all.json', 'r', encoding='utf-8') as f:
        chap_all = json.load(f)

    gs_chaps = {
        1: {"title": "Indian Polity & Constitution", "questions": []},
        2: {"title": "Indian History & Freedom Struggle", "questions": []},
        3: {"title": "Geography (Physical, Indian & World)", "questions": []},
        4: {"title": "General Science (Physics, Chemistry, Biology)", "questions": []},
        5: {"title": "Indian Economy & Social Development", "questions": []},
        6: {"title": "Defence, Military & Current Affairs", "questions": []}
    }
    for q in qs:
        cid = q["chapter_id"]
        gs_chaps[cid]["questions"].append(q)

    chap_all["gs"] = {
        f"ch_{k}": gs_chaps[k] for k in range(1, 7)
    }
    with open('data/cds_chapterwise_all.json', 'w', encoding='utf-8') as f:
        json.dump(chap_all, f, indent=2, ensure_ascii=False)
    print("Saved clean data/cds_chapterwise_all.json!")

    # Update test_data.js
    with open('test_data.js', 'r', encoding='utf-8') as f:
        s = f.read()
    idx = s.find('{')
    test_data = json.loads(s[idx:s.rfind('}')+1])
    test_data["all_gs"] = qs
    test_data["mock_gs"] = mock_gs
    test_data["chapterwise"]["gs"] = chap_all["gs"]
    with open('test_data.js', 'w', encoding='utf-8') as f:
        f.write("window.CDS_DATA = " + json.dumps(test_data, ensure_ascii=False) + ";\n")
    print("Saved clean test_data.js!")

if __name__ == '__main__':
    clean_all()
