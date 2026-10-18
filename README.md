# ⚔️ UPSC CDS Real Test Portal & CBT Simulator

An authentic, offline-first Computer-Based Test (CBT) examination simulator and printable test paper repository for the **Union Public Service Commission (UPSC) Combined Defence Services (CDS)** examination (IMA | INA | AFA | OTA).

![UPSC CDS Examination Portal Banner](gs_pyq_page1.png)

---

## 🚀 Key Highlights

- **Complete Year-Wise Official PYQ Archive (2009–2026):**
  - **Whole Question Papers Uploaded:** Every single exam paper has the **complete, full set of questions** (Exactly **120 Questions** for English, **120 Questions** for GS, and **100 Questions** for Mathematics).
  - **Year 2026 Official Papers:** Includes BOTH **CDS 1 2026 (CDS I 2026)** and **CDS 2 2026 (CDS II 2026)** full examination papers for English (120 Qs each), GS (120 Qs each), and Math (100 Qs each) along with official question booklets.
  - **Math PYQ:** 36 official year-wise examination papers covering 2009 to 2026 (100 Qs each = 3,600 questions) in CBT quiz format + official downloadable PDF booklets.
  - **GS PYQ:** 36 official year-wise examination papers covering 2009 to 2026 (120 Qs each = 4,320 questions) with constitutional, scientific, and defence explanations + official PDF booklets.
  - **English PYQ:** 36 official year-wise examination papers covering 2009 to 2026 (120 Qs each = 4,320 questions) across all syllabus topics + official PDF booklets.
  - **Total:** 108 full examination papers with **12,240 questions** in CBT quiz simulator format and 108 authentic question booklets in PDF.
  - Instant toggle between **Math, GS, and English PYQs** with year filter pills (2009 through 2026 with dedicated 2026 CDS 1 & 2 filter).
- **Aesthetic Day-Mode (Light Mode) & Distraction-Free UI/UX:**
  - Modern, aesthetic day-mode with soft ambient lighting, clean white card surfaces, refined elevation shadows, and zero artificial "AI colour" glows.
  - Strict 1240px container alignment, uniform card heights, and polished typography.
  - Dedicated **Portal Navigator System**:
    - **Header Navigation Bar**: Instant shortcuts to PYQs, Mocks, Chapter Series, and Booklets.
    - **Header Navigator Button**: Quick menu popover.
    - **CBT Question Navigator**: Instant palette drawer toggle and question jumping during exams.
    - **Floating Navigator (FAB)**: Expandable quick menu with smooth section jumps and "Back to Top" scrolling.
  - Real-time countdown timer with pause/resume and low-time alert.
  - Authentic 5-state question palette: Answered (Green), Not Answered (Red), Not Visited (Gray), Marked for Review (Purple), and Answered & Marked for Review (Purple + Green).
  - Save & Next, Clear Response, Mark for Review & Next, and Question Overview modals.
- **Accurate Scoring Standard:**
  - Official UPSC negative marking formulas (+0.833 / -0.277 for English & GS, +1.000 / -0.333 for Mathematics).
  - Mandatory **20.00 Marks (20%)** sectional qualifying threshold check.
  - Merit classification analytics (*Top 1% Exceptional for IMA/AFA, Strong Competitive, Average, Disqualified*).
  - Filterable solution rationales (*All, Correct, Incorrect, Unattempted*).
- **Comprehensive Question Archive & Test Booklets:**
  - Full-length Mock Tests for Paper I (English), Paper II (GS), and Paper III (Mathematics).
  - Dedicated Chapter-wise Test Series with **all 12,240 questions** without missing any question: **14 English chapters (4,320 Qs)**, **6 GS subjects (4,320 Qs)**, and **13 Mathematics chapters (3,600 Qs)**.
  - Printable UPSC-styled question paper booklets, companion answer keys, and machine-gradable OMR sheets.

---

## ⚡ Quick Start (Local Run)

Start the local server with one command:

```bash
# Using Python
python server.py

# Or using Node / NPM
npm start
```

Then visit:
```
http://localhost:8080/index.html
```

---

## 🌐 Cloud Deployment Options

This portal is static-ready and can be deployed with zero configuration:

- **Vercel**: Pre-configured via `vercel.json` (push and deploy).
- **Netlify**: Pre-configured via `netlify.toml` with PDF inline viewing headers.
- **GitHub Pages**: Automated workflow ready in `.github/workflows/deploy.yml`.
- **Docker**: Production-ready Nginx Alpine container available via `Dockerfile`.

See [**DEPLOYMENT_GUIDE.md**](./DEPLOYMENT_GUIDE.md) for full step-by-step instructions.

---

## 📚 Bundled Test Papers & OMR Sheet

| File Name | Subject / Description | Items | Marks |
|---|---|---|---|
| `UPSC_CDS_Paper_I_English_Real_Test_Paper.pdf` | General English Full Mock Booklet | 120 Qs | 100 |
| `UPSC_CDS_Paper_II_General_Knowledge_Real_Test_Paper.pdf` | General Knowledge Real Mock Booklet | 120 Qs | 100 |
| `UPSC_CDS_Paper_III_Elementary_Mathematics_Real_Test_Paper.pdf` | Elementary Mathematics Full Mock Booklet | 100 Qs | 100 |
| `UPSC_CDS_English_All_Questions_Paper.pdf` | English Complete Archive Booklet (8 Authentic Sessions) | 960 Qs | Compendium |
| `UPSC_CDS_GS_All_Questions_Paper.pdf` | General Knowledge Complete Archive Booklet (8 Authentic Sessions) | 960 Qs | Compendium |
| `UPSC_CDS_GS_All_Questions_Answer_Key.pdf` | General Knowledge Official Solutions & Keys Compendium | 960 Qs | Compendium |
| `UPSC_CDS_Math_All_Questions_Paper.pdf` | Mathematics Complete Archive Booklet (8 Authentic Sessions) | 800 Qs | Compendium |
| `UPSC_CDS_Official_OMR_Sheet.pdf` | Authentic UPSC CDS 120-bubble OMR Answer Sheet | 120 Items | — |
| `UPSC_CDS_Official_Answer_Keys_and_Solutions.pdf` | Comprehensive Master Scoring Keys & Solutions | Papers I–III | — |

> **Note on Question Counts:**  
> - **Interactive CBT Question Bank:** **12,240 Total Authentic Past-Year Questions** across 108 full papers (36 English × 120 = 4,320 Qs; 36 GS × 120 = 4,320 Qs; 36 Math × 100 = 3,600 Qs).
> - **Downloadable All-Questions Booklets:** Compile the 8 most recent authentic examination sessions (960 English, 960 GS, 800 Math) with complete tables of contents and section separators.
> - **Downloadable Timed Mock Booklets:** Standard 120/100-question UPSC exam-length papers.

---

## 🛠️ Tech Stack

- **Frontend:** Vanilla HTML5, CSS3 (Custom Design System, Glassmorphism, Dark/Light Themes), Modern JavaScript (ES6+).
- **Data Engine:** Pre-compiled high-performance JSON bundles & `test_data.js`.
- **PDF Generation:** Python & ReportLab with official UPSC examination formatting.
- **Hosting / CI/CD:** GitHub Pages / Vercel / Netlify / Docker.

---

## 📄 License
MIT License.
