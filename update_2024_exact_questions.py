import json
import re

print("Updating CDS (I) 2024 English Paper with EXACT questions from PDF...")

# Load exact questions extracted from UPSC_CDS_2024_I_English_Full_Paper.pdf
exact_q_map = {
    1: {
        "question": "The leader's views were equivocal on the contentious issue.",
        "options": {
            "a": "obscure",
            "b": "ambiguous",
            "c": "clear",
            "d": "vague"
        },
        "section": "Antonyms"
    },
    2: {
        "question": "The authorities interacted with a group of mutinous students.",
        "options": {
            "a": "unruly",
            "b": "contumacious",
            "c": "seditious",
            "d": "obedient"
        },
        "section": "Antonyms"
    },
    3: {
        "question": "His behaviour was quite belligerent.",
        "options": {
            "a": "bellicose",
            "b": "antagonistic",
            "c": "combative",
            "d": "amiable"
        },
        "section": "Antonyms"
    },
    4: {
        "question": "He was effusive in his praise.",
        "options": {
            "a": "exuberant",
            "b": "profuse",
            "c": "voluble",
            "d": "reticent"
        },
        "section": "Antonyms"
    },
    5: {
        "question": "He is often accused of being iniquitous in his conduct.",
        "options": {
            "a": "preposterous",
            "b": "execrable",
            "c": "virtuous",
            "d": "revolting"
        },
        "section": "Antonyms"
    },
    6: {
        "question": "Working in dim light ________ eye issues such as glaucoma.",
        "options": {
            "a": "contributes",
            "b": "precipitates",
            "c": "eradicates",
            "d": "eliminates"
        },
        "section": "Fill in the Blanks"
    },
    7: {
        "question": "He owns several sports cars and has an ________ lifestyle.",
        "options": {
            "a": "opulent",
            "b": "occult",
            "c": "ocular",
            "d": "obscure"
        },
        "section": "Fill in the Blanks"
    },
    8: {
        "question": "Those medicines, ________ are used to treat kidney infection, have been withdrawn from the market.",
        "options": {
            "a": "what",
            "b": "which",
            "c": "when",
            "d": "who"
        },
        "section": "Fill in the Blanks"
    },
    9: {
        "question": "________ intake of sugar can cause health problems.",
        "options": {
            "a": "Access",
            "b": "Excess of",
            "c": "Excessive",
            "d": "Excessively"
        },
        "section": "Fill in the Blanks"
    },
    10: {
        "question": "She suffered ________ pain because of the leg injury.",
        "options": {
            "a": "hurting",
            "b": "excruciating",
            "c": "consuming",
            "d": "protracting"
        },
        "section": "Fill in the Blanks"
    },
    11: {
        "question": "The country's politics ________ complex, with more than ten parties competing for power.",
        "options": {
            "a": "are",
            "b": "am",
            "c": "is",
            "d": "were"
        },
        "section": "Fill in the Blanks"
    },
    12: {
        "question": "The job advertisement stipulates that the applicant ________ three years' experience.",
        "options": {
            "a": "have",
            "b": "had",
            "c": "shall have",
            "d": "must have"
        },
        "section": "Fill in the Blanks"
    },
    13: {
        "question": "Newspapers have reported heavy flooding in the coastal areas. The damage ________ to be extensive.",
        "options": {
            "a": "expected",
            "b": "is expecting",
            "c": "has been expected",
            "d": "is expected"
        },
        "section": "Fill in the Blanks"
    },
    14: {
        "question": "The local bank was robbed by a group of men, ________ were armed.",
        "options": {
            "a": "four of whom",
            "b": "four of these",
            "c": "four of those",
            "d": "four whom"
        },
        "section": "Fill in the Blanks"
    },
    15: {
        "question": "The country ________ several economic changes in the past two decades.",
        "options": {
            "a": "underwent",
            "b": "had undergone",
            "c": "will be undergoing",
            "d": "have been undergoing"
        },
        "section": "Fill in the Blanks"
    },
    16: {
        "question": "A watched pot never boils",
        "options": {
            "a": "Surveillance destroys creativity",
            "b": "To experience failure due to over eagerness",
            "c": "To have no chance of achieving something",
            "d": "Desperate anticipation makes time drag"
        },
        "section": "Idioms and Phrases"
    },
    17: {
        "question": "Look to your laurels",
        "options": {
            "a": "To make an extra effort to secure one's position",
            "b": "To look suitable for a particular situation",
            "c": "To guard one's trophies",
            "d": "To praise oneself"
        },
        "section": "Idioms and Phrases"
    },
    18: {
        "question": "Play devil's advocate",
        "options": {
            "a": "To try to defeat someone by tricking",
            "b": "To perform with a lot of skills",
            "c": "To delay doing something",
            "d": "To pretend to be against an idea in order to discuss it more carefully"
        },
        "section": "Idioms and Phrases"
    },
    19: {
        "question": "Be in the same boat",
        "options": {
            "a": "To say two things in the same breath",
            "b": "To be in the same unpleasant situation",
            "c": "To do something that is dangerous",
            "d": "To pretend to be something that you are"
        },
        "section": "Idioms and Phrases"
    },
    20: {
        "question": "Tilt at windmills",
        "options": {
            "a": "To be young and inexperienced",
            "b": "To celebrate good news",
            "c": "To blow hot air",
            "d": "To waste time dealing with enemies and problems that do not exist"
        },
        "section": "Idioms and Phrases"
    },
    21: {
        "question": "P: the essence of human resource development\nQ: education which plays a significant and\nR: is remedial role in\nS: balancing the socio-economic fabric of the country\nThe correct sequence should be:",
        "options": {
            "a": "P S Q R",
            "b": "P Q S R",
            "c": "R S Q P",
            "d": "R Q S P"
        },
        "section": "Ordering of Words in a Sentence (PQRS)"
    },
    22: {
        "question": "P: in this endeavour gender budgeting\nQ: is central to mitigate gender inequalities\nR: is a critical strategy\nS: and financing for gender equality\nThe correct sequence should be:",
        "options": {
            "a": "Q P R S",
            "b": "Q R P S",
            "c": "S R Q P",
            "d": "S P R Q"
        },
        "section": "Ordering of Words in a Sentence (PQRS)"
    },
    23: {
        "question": "P: balanced diet and are vital items of\nQ: are essential ingredients for a wholesome and\nR: fruit and vegetables\nS: mass consumption\nThe correct sequence should be:",
        "options": {
            "a": "R Q P S",
            "b": "R P S Q",
            "c": "S R P Q",
            "d": "S Q R P"
        },
        "section": "Ordering of Words in a Sentence (PQRS)"
    },
    24: {
        "question": "P: relating to the reduction of greenhouse gases\nQ: and extending financial support to\nR: developing countries\nS: India's position is reflected in decisions\nThe correct sequence should be:",
        "options": {
            "a": "S R P Q",
            "b": "S P Q R",
            "c": "P R S Q",
            "d": "R S P Q"
        },
        "section": "Ordering of Words in a Sentence (PQRS)"
    },
    25: {
        "question": "P: disbursement of pension expeditiously\nQ: all efforts are made to process the\nR: once all requisite documents are received\nS: from the beneficiaries\nThe correct sequence should be:",
        "options": {
            "a": "Q P S R",
            "b": "R S Q P",
            "c": "P R S Q",
            "d": "S P Q R"
        },
        "section": "Ordering of Words in a Sentence (PQRS)"
    }
}

# Load cds_pyq_papers.json
with open('data/cds_pyq_papers.json', 'r', encoding='utf-8') as f:
    pyq_db = json.load(f)

# Find CDS (I) 2024 English Paper
found = False
for paper in pyq_db['english']:
    if paper.get('year') == '2024' and paper.get('edition') == 'I':
        found = True
        for q in paper['questions']:
            qid = q.get('id')
            if qid in exact_q_map:
                ex = exact_q_map[qid]
                q['question'] = ex['question']
                q['options'] = ex['options']
                q['section'] = ex['section']
                q['source'] = f"CDS (I) 2024 Q{qid}"
        print(f"Updated CDS (I) 2024 English Paper questions 1 to 25!")
        break

if not found:
    print("Error: Paper not found!")

# Save back to cds_pyq_papers.json and pyq_data.js
with open('data/cds_pyq_papers.json', 'w', encoding='utf-8') as f:
    json.dump(pyq_db, f, indent=2, ensure_ascii=False)

pyq_js = "window.CDS_PYQ_DATA = window.CDS_PYQ_PAPERS = " + json.dumps(pyq_db, ensure_ascii=False) + ";\n"
with open('pyq_data.js', 'w', encoding='utf-8') as f:
    f.write(pyq_js)

print("Saved updated cds_pyq_papers.json and pyq_data.js successfully!")
