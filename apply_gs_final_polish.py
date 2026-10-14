import json
import os
import re

def apply_polish():
    json_path = 'data/cds_gs_complete_chapterwise.json'
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 1. Fix Q4
    data[3]['question'] = (
        "According to the Constitution (Fifty-Second Amendment) Act 1985 as amended in 2003, "
        "a legislator attracts disqualification under the Tenth Schedule if:\n"
        "1. He voluntarily gives up the membership of the party on whose ticket he was elected.\n"
        "2. He votes or abstains from voting contrary to any direction issued by his political party.\n"
        "3. As a result of split, less than one-third of the members formed a new group or party in the house.\n"
        "4. A member who has been elected as an independent member joins any political party.\n"
        "Select the correct answer using the code given below :"
    )
    data[3]['options'] = {
        'a': '2 and 3 only',
        'b': '1, 2 and 4 only',
        'c': '1 and 3 only',
        'd': '1, 2, 3 and 4'
    }
    data[3]['correct_answer'] = 'b'
    data[3]['explanation'] = (
        "Under the Tenth Schedule (Anti-Defection Law), a member is disqualified if they voluntarily give up party membership, "
        "vote contrary to party whip without prior permission, or if an independent member joins any political party. "
        "The 91st Amendment (2003) deleted the exemption for 1/3rd split, requiring at least 2/3rd for merger."
    )

    # 2. Fix Q71
    data[70]['question'] = "During the year 2009-2010, which one of the following sectors recorded the highest growth rate in the Indian economy?"
    data[70]['options']['d'] = "Manufacturing"
    data[70]['explanation'] = "According to Economic Survey data for 2009-10, the manufacturing and industrial sectors recorded double-digit expansion following stimulus measures."

    # 3. Fix Q76
    data[75]['question'] = (
        "Which of the following National Parks of India are declared as World Heritage Sites by UNESCO?\n"
        "1. Keoladeo National Park\n"
        "2. Sundarbans National Park\n"
        "3. Kaziranga National Park\n"
        "4. Ranthambore National Park\n"
        "Select the correct answer using the code given below :"
    )
    data[75]['options'] = {
        'a': '1 and 2 only',
        'b': '1, 2 and 3 only',
        'c': '3 and 4 only',
        'd': '1, 2, 3 and 4'
    }
    data[75]['correct_answer'] = 'b'
    data[75]['explanation'] = (
        "Keoladeo National Park (1985), Kaziranga National Park (1985), and Sundarbans National Park (1987) "
        "are UNESCO World Heritage Sites. Ranthambore National Park is not inscribed on the World Heritage List."
    )

    # 4. Fix Q118
    data[117]['question'] = "Lysosome is formed from which one of the following cell organelles?"
    data[117]['options'] = {
        'a': 'Nucleus',
        'b': 'Endoplasmic reticulum',
        'c': 'Golgi bodies',
        'd': 'Ribosomes'
    }
    data[117]['correct_answer'] = 'c'
    data[117]['explanation'] = "Lysosomes are membrane-bound organelles containing digestive enzymes that are packaged and budded off from the Golgi apparatus/bodies."

    # 5. Fix Q128
    data[127]['question'] = "What is a 'Green Data Centre'?"
    data[127]['options'] = {
        'a': 'A data centre created by environmentalists to keep records of clean production technology',
        'b': 'A repository for storage and management of data where mechanical, electrical, and computer systems are optimized for maximum energy efficiency and minimal environmental footprint',
        'c': 'A data centre for green buildings optimizing power consumption using solar energy',
        'd': 'A repository providing information about small industries adopting energy efficiency measures'
    }
    data[127]['correct_answer'] = 'b'
    data[127]['explanation'] = "A green data centre is an enterprise storage repository where lighting, electrical, cooling, and compute systems are engineered to achieve maximum power usage effectiveness (PUE) and minimal carbon emissions."

    # 6. Fix Q193 (lead acid battery -> General Science)
    data[192]['chapter_id'] = 4
    data[192]['chapter_title'] = "General Science (Physics, Chemistry, Biology)"
    data[192]['question'] = (
        "Which of the following statements about the commonly used automobile battery are true?\n"
        "1. It is usually a lead-acid battery.\n"
        "2. It has six cells with a potential of 2 Volt each.\n"
        "3. Its cells work as Galvanic Cells while discharging power.\n"
        "4. Its cells work as electrolytic cells while recharging.\n"
        "Select the correct answer using the code given below :"
    )
    data[192]['options'] = {
        'a': '1, 2, 3 and 4',
        'b': '1, 2 and 3 only',
        'c': '2 and 4 only',
        'd': '3 and 4 only'
    }
    data[192]['correct_answer'] = 'a'
    data[192]['explanation'] = "A standard 12V car battery consists of six 2V lead-acid cells connected in series. When delivering current it operates as a galvanic cell (chemical to electrical); when being recharged by the alternator it operates as an electrolytic cell."

    # 7. Fix Q194
    data[193]['question'] = (
        "Consider the following statements about the National Wildlife Action Plan (NWAP) of India for 2017-2031:\n"
        "1. This is the Third National Wildlife Action Plan.\n"
        "2. The NWAP is unique as this is the first time India has recognized the concerns relating to climate change impact on wildlife.\n"
        "3. The NWAP has ten components.\n"
        "Which of the statements given above is/are correct?"
    )
    data[193]['options'] = {
        'a': '1 only',
        'b': '1 and 2 only',
        'c': '2 and 3 only',
        'd': '1, 2 and 3'
    }
    data[193]['correct_answer'] = 'b'
    data[193]['explanation'] = (
        "The NWAP 2017-2031 is India's 3rd National Wildlife Action Plan. It is notable for integrating climate change impacts into wildlife planning for the first time. It has 17 priority themes and 103 conservation actions."
    )

    # 8. Fix Q230 (tea stimulating effect -> General Science)
    data[229]['chapter_id'] = 4
    data[229]['chapter_title'] = "General Science (Physics, Chemistry, Biology)"
    data[229]['question'] = "Which one of the following is responsible for the stimulating effect of tea?"
    data[229]['options'] = {
        'a': 'Tannin',
        'b': 'Steroid',
        'c': 'Alkaloid (Caffeine / Theine)',
        'd': 'Flavonoid'
    }
    data[229]['correct_answer'] = 'c'
    data[229]['explanation'] = "The stimulating effect of tea is primarily due to the purine alkaloid caffeine (also known as theine), which acts as a central nervous system stimulant."

    # Sort strictly by chapter_id
    data.sort(key=lambda x: x['chapter_id'])
    for i, q in enumerate(data):
        q['id'] = i + 1

    # Save to json
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Polished {len(data)} questions saved to {json_path}")

    # Synchronize data/cds_mock_gs.json
    with open('data/cds_mock_gs.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Synchronize data/cds_chapterwise_all.json
    all_cw_path = 'data/cds_chapterwise_all.json'
    if os.path.exists(all_cw_path):
        with open(all_cw_path, 'r', encoding='utf-8') as f:
            all_cw = json.load(f)
        
        # Build chapterwise GS dict
        gs_chapters = {}
        for q in data:
            cid = f"ch_{q['chapter_id']}"
            if cid not in gs_chapters:
                gs_chapters[cid] = {
                    "id": cid,
                    "title": q['chapter_title'],
                    "subject": "gs",
                    "questions": []
                }
            gs_chapters[cid]["questions"].append(q)
        
        all_cw['gs'] = gs_chapters
        with open(all_cw_path, 'w', encoding='utf-8') as f:
            json.dump(all_cw, f, indent=2, ensure_ascii=False)
        print("Synchronized data/cds_chapterwise_all.json")

        # Synchronize test_data.js
        test_data_obj = {
            "mock_english": json.load(open('data/cds_mock_english_120.json', encoding='utf-8')) if os.path.exists('data/cds_mock_english_120.json') else [],
            "mock_gs": data,
            "mock_math": json.load(open('data/cds_mock_math_100.json', encoding='utf-8')) if os.path.exists('data/cds_mock_math_100.json') else [],
            "all_gs": data,
            "chapterwise": all_cw
        }
        with open('test_data.js', 'w', encoding='utf-8') as f:
            f.write("window.CDS_DATA = " + json.dumps(test_data_obj, ensure_ascii=False) + ";\n")
        print("Synchronized test_data.js")

if __name__ == '__main__':
    apply_polish()
