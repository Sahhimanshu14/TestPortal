import json

print("Synchronizing mock datasets in test_data.js...")

with open('data/cds_mock_english_120.json', 'r', encoding='utf-8') as f:
    mock_eng = json.load(f)

with open('data/cds_mock_gs_120.json', 'r', encoding='utf-8') as f:
    mock_gs = json.load(f)

with open('data/cds_mock_math_100.json', 'r', encoding='utf-8') as f:
    mock_math = json.load(f)

print(f"Loaded clean mocks: English={len(mock_eng)}, GS={len(mock_gs)}, Math={len(mock_math)}")

with open('test_data.js', 'r', encoding='utf-8') as f:
    content = f.read()

# test_data.js format is: window.CDS_DATA = { ... };
# We can load the json object, replace mock_english, mock_gs, mock_math, and write back.
prefix = "window.CDS_DATA = "
suffix = ";"
idx_start = content.find(prefix)
if idx_start != -1:
    idx_end = content.rfind(suffix)
    json_str = content[idx_start + len(prefix) : idx_end].strip()
    data = json.loads(json_str)
    
    data['mock_english'] = mock_eng
    data['mock_gs'] = mock_gs
    data['mock_math'] = mock_math
    
    new_json_str = json.dumps(data, ensure_ascii=False)
    new_content = prefix + new_json_str + suffix
    
    with open('test_data.js', 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print("SUCCESS: test_data.js updated with clean, authentic mock tests!")
else:
    print("ERROR: Could not find window.CDS_DATA in test_data.js")
