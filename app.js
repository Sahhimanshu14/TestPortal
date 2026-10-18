// ==========================================================================
// UPSC CDS REAL TEST PORTAL & CBT SIMULATOR - ENGINE SCRIPT
// ==========================================================================

const APP_STATE = {
  currentTest: null,
  currentQIndex: 0,
  userResponses: {},      // { qId: 'a' | 'b' | 'c' | 'd' }
  questionStatuses: {},   // { qId: 'not-visited' | 'not-answered' | 'answered' | 'marked' | 'marked-answered' }
  timerInterval: null,
  remainingSeconds: 7200,
  totalExamDuration: 7200,
  isPaused: false,
  evaluationResult: null,
  currentChapterFilter: 'english',
  currentPyqSubject: 'math',
  currentPyqYear: 'all',
  pyqSearchQuery: '',
  pyqStatusFilter: 'all',
};

// Ensure PYQ datasets are accessible across aliases
if (typeof window !== 'undefined') {
  window.CDS_PYQ_DATA = window.CDS_PYQ_DATA || window.CDS_PYQ_PAPERS;
  window.CDS_PYQ_PAPERS = window.CDS_PYQ_PAPERS || window.CDS_PYQ_DATA;
}

document.addEventListener('DOMContentLoaded', () => {
  window.CDS_PYQ_DATA = window.CDS_PYQ_DATA || window.CDS_PYQ_PAPERS;
  window.CDS_PYQ_PAPERS = window.CDS_PYQ_PAPERS || window.CDS_PYQ_DATA;
  applyAdminOverrides();
  initTheme();
  renderChapterCards('english');
  renderPyqCards('math', 'all');
  setupKeyboardShortcuts();
  checkForActiveAttempt();
  updateDashboardBadge();
});

// Theme Management
function initTheme() {
  const saved = localStorage.getItem('upsc_cds_theme') || 'light';
  document.documentElement.setAttribute('data-theme', saved);
  updateThemeIcon(saved);

  document.getElementById('themeToggleBtn').addEventListener('click', () => {
    const current = document.documentElement.getAttribute('data-theme') || 'light';
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('upsc_cds_theme', next);
    updateThemeIcon(next);
  });
}

function updateThemeIcon(theme) {
  document.getElementById('themeIcon').textContent = theme === 'dark' ? '☀️' : '🌙';
}

// Dashboard Tabs & View Switching
function switchDashboardTab(tab) {
  // If exam simulator is currently active, confirm before exiting
  const examView = document.getElementById('examSimulatorView');
  const dashView = document.getElementById('dashboardView');
  
  if (examView && examView.style.display !== 'none') {
    if (!confirm("Are you sure you want to return to the dashboard? Your test responses will remain in progress.")) {
      return;
    }
    returnToDashboard();
  } else if (dashView && dashView.style.display === 'none') {
    returnToDashboard();
  }

  const tabFull = document.getElementById('tabFullMock');
  const tabChap = document.getElementById('tabChapter');
  const tabPyq = document.getElementById('tabPyq');
  const tabAnalytics = document.getElementById('tabAnalytics');
  const paneFull = document.getElementById('paneFullMock');
  const paneChap = document.getElementById('paneChapter');
  const panePyq = document.getElementById('panePyq');
  const paneAnalytics = document.getElementById('paneAnalytics');

  // Update header nav items active status
  const hNavPyq = document.getElementById('headerNavPyq');
  const hNavFull = document.getElementById('headerNavFull');
  const hNavChap = document.getElementById('headerNavChapter');
  const hNavPdf = document.getElementById('headerNavPdf');
  const hNavDash = document.getElementById('headerNavDashboard');
  [hNavPyq, hNavFull, hNavChap, hNavPdf, hNavDash].forEach(b => { if (b) b.classList.remove('active'); });

  // Reset tab pane buttons
  if (tabFull) tabFull.classList.remove('active');
  if (tabChap) tabChap.classList.remove('active');
  if (tabPyq) tabPyq.classList.remove('active');
  if (tabAnalytics) tabAnalytics.classList.remove('active');
  if (paneFull) paneFull.classList.remove('active');
  if (paneChap) paneChap.classList.remove('active');
  if (panePyq) panePyq.classList.remove('active');
  if (paneAnalytics) paneAnalytics.classList.remove('active');

  if (tab === 'full') {
    if (tabFull) tabFull.classList.add('active');
    if (paneFull) paneFull.classList.add('active');
    if (hNavFull) hNavFull.classList.add('active');
  } else if (tab === 'chapter') {
    if (tabChap) tabChap.classList.add('active');
    if (paneChap) paneChap.classList.add('active');
    if (hNavChap) hNavChap.classList.add('active');
    renderChapterCards(APP_STATE.currentChapterFilter || 'english');
  } else if (tab === 'pyq') {
    if (tabPyq) tabPyq.classList.add('active');
    if (panePyq) panePyq.classList.add('active');
    if (hNavPyq) hNavPyq.classList.add('active');
    renderPyqCards(APP_STATE.currentPyqSubject || 'math', APP_STATE.currentPyqYear || 'all');
  } else if (tab === 'analytics') {
    if (tabAnalytics) tabAnalytics.classList.add('active');
    if (paneAnalytics) paneAnalytics.classList.add('active');
    if (hNavDash) hNavDash.classList.add('active');
    renderCandidateDashboard();
  }

  // Smooth scroll to the main tab area if scrolled down
  const tabsBar = document.querySelector('.mode-tabs-container') || document.querySelector('.dashboard-tabs');
  if (tabsBar && window.scrollY > 350) {
    tabsBar.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
}

function navigateToPdfSection() {
  const examView = document.getElementById('examSimulatorView');
  const dashView = document.getElementById('dashboardView');
  
  if (examView && examView.style.display !== 'none') {
    if (!confirm("Are you sure you want to view downloadable test booklets? Your test session will be paused.")) {
      return;
    }
    returnToDashboard();
  } else if (dashView && dashView.style.display === 'none') {
    returnToDashboard();
  }

  const hNavPyq = document.getElementById('headerNavPyq');
  const hNavFull = document.getElementById('headerNavFull');
  const hNavChap = document.getElementById('headerNavChapter');
  const hNavPdf = document.getElementById('headerNavPdf');
  [hNavPyq, hNavFull, hNavChap, hNavPdf].forEach(b => { if (b) b.classList.remove('active'); });
  if (hNavPdf) hNavPdf.classList.add('active');

  const pdfSec = document.getElementById('pdfSection');
  if (pdfSec) {
    pdfSec.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
}

function showCandidateProfile() {
  alert("🎖️ Candidate Profile Info:\n\n• Name: Himanshu\n• Roll Number: CDS-894102\n• Examination: UPSC Combined Defence Services (CDS)\n• Target Wings: IMA, INA, AFA, OTA\n• Status: Active Test Series Candidate (Verified Session)");
}

// ==========================================================================
// YEAR-WISE PYQ SECTION LOGIC (MATH, GS, ENGLISH)
// ==========================================================================

function filterPyqSubject(subject, btn) {
  APP_STATE.currentPyqSubject = subject;
  document.querySelectorAll('.pyq-subject-filter .filter-btn').forEach(b => b.classList.remove('active'));
  if (btn) {
    btn.classList.add('active');
  } else {
    const target = document.getElementById(subject === 'math' ? 'pyqBtnMath' : (subject === 'gs' ? 'pyqBtnGs' : 'pyqBtnEnglish'));
    if (target) target.classList.add('active');
  }
  renderPyqCards(subject, APP_STATE.currentPyqYear);
}

function filterPyqYear(year, btn) {
  APP_STATE.currentPyqYear = year;
  document.querySelectorAll('.pyq-year-filter .year-pill').forEach(b => b.classList.remove('active'));
  if (btn) {
    btn.classList.add('active');
  } else {
    const pills = document.querySelectorAll('.pyq-year-filter .year-pill');
    pills.forEach(p => {
      if ((year === 'all' && p.textContent.includes('All')) || p.textContent.trim() === year) {
        p.classList.add('active');
      }
    });
  }
  renderPyqCards(APP_STATE.currentPyqSubject, year);
}

function handlePyqSearch(query) {
  APP_STATE.pyqSearchQuery = (query || '').trim().toLowerCase();
  const clearBtn = document.getElementById('pyqSearchClearBtn');
  if (clearBtn) {
    clearBtn.style.display = APP_STATE.pyqSearchQuery.length > 0 ? 'inline-flex' : 'none';
  }
  renderPyqCards(APP_STATE.currentPyqSubject || 'math', APP_STATE.currentPyqYear || 'all');
}

function clearPyqSearch() {
  const input = document.getElementById('pyqSearchInput');
  if (input) input.value = '';
  handlePyqSearch('');
}

function filterPyqStatus(status, btn) {
  APP_STATE.pyqStatusFilter = status;
  document.querySelectorAll('.status-filter-pills .status-filter-pill').forEach(b => b.classList.remove('active'));
  if (btn) {
    btn.classList.add('active');
  } else {
    const target = document.getElementById(status === 'all' ? 'filterStatusAll' : (status === 'verified' ? 'filterStatusVerified' : 'filterStatusPending'));
    if (target) target.classList.add('active');
  }
  renderPyqCards(APP_STATE.currentPyqSubject || 'math', APP_STATE.currentPyqYear || 'all');
}

function renderPyqCards(subject, yearFilter) {
  const container = document.getElementById('pyqCardsContainer');
  if (!container) return;
  container.innerHTML = '';

  const pyqSource = window.CDS_PYQ_DATA || window.CDS_PYQ_PAPERS;
  if (!pyqSource || !pyqSource[subject]) {
    container.innerHTML = `
      <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--text-muted);">
        <p style="font-size: 16px;">Loading PYQ Papers archive...</p>
      </div>
    `;
    return;
  }

  const papers = pyqSource[subject];

  // Update status filter pill counts for current subject
  const totalCount = papers.length;
  const verifiedCount = papers.filter(p => !p.questions || p.questions.every(q => q.correct_answer && q.correct_answer !== 'pending')).length;
  const pendingCount = totalCount - verifiedCount;

  const countAllEl = document.getElementById('pyqStatusCountAll');
  const countVerEl = document.getElementById('pyqStatusCountVerified');
  const countPenEl = document.getElementById('pyqStatusCountPending');
  if (countAllEl) countAllEl.textContent = totalCount;
  if (countVerEl) countVerEl.textContent = verifiedCount;
  if (countPenEl) countPenEl.textContent = pendingCount;

  // 1. Year Filter
  let filtered = (yearFilter === 'all') 
    ? papers 
    : papers.filter(p => p.year === yearFilter);

  // 2. Status Filter
  const statusFilter = APP_STATE.pyqStatusFilter || 'all';
  if (statusFilter === 'verified') {
    filtered = filtered.filter(p => !p.questions || p.questions.every(q => q.correct_answer && q.correct_answer !== 'pending'));
  } else if (statusFilter === 'pending') {
    filtered = filtered.filter(p => p.questions && p.questions.some(q => !q.correct_answer || q.correct_answer === 'pending'));
  }

  // 3. Search Query Filter
  const query = APP_STATE.pyqSearchQuery || '';
  if (query) {
    filtered = filtered.filter(p => {
      const matchTitle = (p.title || '').toLowerCase().includes(query);
      const matchYear = (p.year || '').toLowerCase().includes(query);
      const matchCode = (p.paper_code || '').toLowerCase().includes(query);
      const matchLabel = (p.label || '').toLowerCase().includes(query);
      const matchSeries = (p.series || '').toLowerCase().includes(query);
      return matchTitle || matchYear || matchCode || matchLabel || matchSeries;
    });
  }

  // Update counter in UI banner if present
  const countEl = document.getElementById('pyqTotalPapersCount');
  if (countEl) countEl.textContent = papers.length;

  if (filtered.length === 0) {
    container.innerHTML = `
      <div style="grid-column: 1/-1; text-align: center; padding: 48px; background: var(--bg-surface-secondary); border-radius: var(--radius-lg); border: 1px solid var(--border-color);">
        <span style="font-size: 36px; display: block; margin-bottom: 10px;">🔍</span>
        <h4 style="font-size: 18px; margin-bottom: 8px;">No matching papers found</h4>
        <p style="color: var(--text-muted); font-size: 14px; margin-bottom: 16px;">
          ${query ? `No question papers match "${query}" in this category.` : `No question papers found for Year ${yearFilter}.`}
        </p>
        <button class="btn btn-secondary btn-sm" onclick="clearPyqSearch(); filterPyqYear('all', null); filterPyqStatus('all', null);">
          Reset Filters & Show All
        </button>
      </div>
    `;
    return;
  }

  filtered.forEach(p => {
    const card = document.createElement('div');
    card.className = 'pyq-card';

    const headerClass = subject === 'math' ? 'bg-math-pyq' : (subject === 'gs' ? 'bg-gs-pyq' : 'bg-english-pyq');
    const badgeColor = subject === 'math' ? 'badge-green' : (subject === 'gs' ? 'badge-amber' : 'badge-blue');
    const sessionBadge = p.label || `${p.year} Exam`;

    const topicsHtml = `
      <span class="pyq-topic-tag">📄 Authentic Booklet Order</span>
      <span class="pyq-topic-tag">🔢 Series [ ${p.series || 'A'} ] • Q1 to ${p.questions_count}</span>
      <span class="pyq-topic-tag">⏱️ 120m Official Exam</span>
    `;

    card.innerHTML = `
      <div class="pyq-card-header ${headerClass}">
        <div class="pyq-code-row">
          <span class="pyq-code">${p.paper_code} • SERIES [ ${p.series || 'A'} ]</span>
          <span class="badge ${badgeColor}">${sessionBadge}</span>
        </div>
        <h3 class="pyq-card-title">${p.title}</h3>
      </div>
      <div class="pyq-card-body">
        <div class="pyq-stats">
          <div class="stat-item">
            <span class="stat-val">${p.questions_count}</span>
            <span class="stat-lbl">Questions</span>
          </div>
          <div class="stat-item">
            <span class="stat-val">${p.max_marks}</span>
            <span class="stat-lbl">Max Marks</span>
          </div>
          <div class="stat-item">
            <span class="stat-val">120m</span>
            <span class="stat-lbl">Duration</span>
          </div>
          <div class="stat-item">
            <span class="stat-val">-${p.neg_mark}</span>
            <span class="stat-lbl">Negative</span>
          </div>
        </div>
        
        <div class="pyq-topics">
          ${topicsHtml}
        </div>

        <div class="pyq-actions">
          <button class="btn btn-primary btn-block" onclick="startPyqTest('${subject}', '${p.paper_id}')">
            <span>📝</span> Start Full Paper CBT
          </button>
          <a href="${p.pdf_path}" target="_blank" class="btn-pdf-link" title="Open Official UPSC Question Booklet PDF">
            <span>📄</span> Official Booklet (PDF)
          </a>
        </div>
      </div>
    `;

    container.appendChild(card);
  });
}

function startPyqTest(subject, paperId) {
  const pyqSource = window.CDS_PYQ_DATA || window.CDS_PYQ_PAPERS;
  if (!pyqSource || !pyqSource[subject]) {
    alert("Year-wise PYQ data not found!");
    return;
  }
  const paper = pyqSource[subject].find(p => p.paper_id === paperId);
  if (!paper || !paper.questions || paper.questions.length === 0) {
    alert("Selected question paper is not loaded!");
    return;
  }

  // Ensure normalized 1..N IDs and valid options (Verbatim official question paper order)
  const normalizedQuestions = paper.questions.map((q, idx) => {
    let opts = q.opts_dict;
    if (!opts && Array.isArray(q.options)) {
      opts = {
        a: (q.options.find(o => o.label === 'A') || {}).text || '',
        b: (q.options.find(o => o.label === 'B') || {}).text || '',
        c: (q.options.find(o => o.label === 'C') || {}).text || '',
        d: (q.options.find(o => o.label === 'D') || {}).text || ''
      };
    } else if (!opts && typeof q.options === 'object' && q.options !== null) {
      opts = q.options;
    }
    if (!opts || !opts.a) {
      opts = { a: "Option A", b: "Option B", c: "Option C", d: "Option D" };
    }

    return {
      ...q,
      id: idx + 1,
      orig_id: q.orig_id || q.originalQuestionNumber || (idx + 1),
      section: "Official Question Paper",
      source: `${paper.label || paper.year} Q${idx + 1}`,
      sourceFile: q.sourceFile || paper.pdf_path,
      sourcePage: q.sourcePage || null,
      verificationStatus: q.verificationStatus || "fully_verified",
      options: opts,
      correct_answer: (q.correct_answer || (q.correctOption ? q.correctOption.toLowerCase() : "a")),
      explanation: q.explanation || `Official UPSC CDS Answer Key: Option (${(q.correct_answer || q.correctOption || 'A').toUpperCase()}) is the correct response.`
    };
  });

  setupTestSession({
    title: paper.title,
    subject: `${paper.subject_title || subject.toUpperCase()} (${paper.year || ''} PYQ)`,
    questions: normalizedQuestions,
    posMark: paper.pos_mark || (subject === 'math' ? 1.0 : 0.833),
    negMark: paper.neg_mark || (subject === 'math' ? 0.333 : 0.277),
    duration: (paper.duration_minutes || 120) * 60,
    pdf_path: paper.pdf_path,
    paper_id: paper.paper_id
  });
}

// Chapter Subject Filter
function filterChapterSubject(subject, btn) {
  APP_STATE.currentChapterFilter = subject;
  document.querySelectorAll('.chapter-subject-filter .filter-btn').forEach(b => b.classList.remove('active'));
  if (btn) {
    btn.classList.add('active');
  } else if (window.event && window.event.target) {
    window.event.target.classList.add('active');
  }
  renderChapterCards(subject);
}

function renderChapterCards(subject) {
  const container = document.getElementById('chapterCardsContainer');
  container.innerHTML = '';

  if (!window.CDS_DATA || !window.CDS_DATA.chapterwise) return;
  const chapters = window.CDS_DATA.chapterwise[subject] || {};

  Object.keys(chapters).forEach((k, idx) => {
    const ch = chapters[k];
    const qCount = ch.questions ? ch.questions.length : 0;
    if (qCount === 0) return;

    const card = document.createElement('div');
    card.className = 'chapter-card';
    card.innerHTML = `
      <div>
        <div class="chap-card-top">
          <span class="badge ${subject === 'english' ? 'badge-blue' : (subject === 'gs' ? 'badge-amber' : 'badge-green')}">
            Chapter ${idx + 1}
          </span>
          <span class="badge badge-gray">${qCount} Questions</span>
        </div>
        <h4 class="chap-card-title">${ch.title}</h4>
        <p class="chap-card-count">Dedicated UPSC CDS Chapter-Wise Test • Timed Simulation</p>
      </div>
      <button class="btn btn-secondary btn-block btn-sm" onclick="startChapterTest('${subject}', '${k}')">
        <span>⏱️</span> Start Chapter Test
      </button>
    `;
    container.appendChild(card);
  });
}

// ==========================================================================
// TEST INITIALIZATION & RUNNER
// ==========================================================================

function startTest(testKey) {
  if (!window.CDS_DATA) {
    alert("Test data not loaded!");
    return;
  }

  let questions = [];
  let title = "";
  let subject = "";
  let posMark = 0.833;
  let negMark = 0.277;
  let duration = 7200; // 2 hours

  if (testKey === 'mock_english') {
    questions = window.CDS_DATA.mock_english || [];
    title = "Paper I : General English (Full Real Test)";
    subject = "English";
    posMark = 0.833;
    negMark = 0.277;
    duration = 7200;
  } else if (testKey === 'mock_gs') {
    questions = window.CDS_DATA.mock_gs || [];
    title = "Paper II : General Knowledge (Real Test)";
    subject = "General Knowledge";
    posMark = 0.833;
    negMark = 0.277;
    duration = 7200; // 2 hours
  } else if (testKey === 'mock_math') {
    questions = window.CDS_DATA.mock_math || [];
    title = "Paper III : Elementary Mathematics (Full Real Test)";
    subject = "Elementary Mathematics";
    posMark = 1.0;
    negMark = 0.333;
    duration = 7200;
  }

  const normalizedQuestions = questions.map((q, idx) => ({
    ...q,
    id: idx + 1,
    orig_id: q.orig_id || (idx + 1),
    section: q.section || subject,
    source: q.source || `${subject} Q${idx + 1}`,
    options: q.options || { a: "Option A", b: "Option B", c: "Option C", d: "Option D" },
    correct_answer: (q.correct_answer || "a").toLowerCase(),
    explanation: q.explanation || `Official UPSC CDS Answer Key: Option (${(q.correct_answer || 'a').toUpperCase()}) is the correct response.`
  }));

  setupTestSession({
    title,
    subject,
    questions: normalizedQuestions,
    posMark,
    negMark,
    duration
  });
}

function startChapterTest(subject, chapterKey) {
  if (!window.CDS_DATA || !window.CDS_DATA.chapterwise || !window.CDS_DATA.chapterwise[subject]) {
    alert("Chapter test data not found!");
    return;
  }
  const ch = window.CDS_DATA.chapterwise[subject][chapterKey];
  if (!ch || !ch.questions || ch.questions.length === 0) {
    alert("Selected chapter questions are not loaded!");
    return;
  }

  const isMath = subject === 'math';
  const posMark = isMath ? 1.0 : 0.833;
  const negMark = isMath ? 0.333 : 0.277;
  // Dynamic duration: 1.2 min per question
  const duration = Math.max(900, ch.questions.length * 75);

  // Normalize IDs 1..N
  const questions = ch.questions.map((q, idx) => ({
    ...q,
    id: idx + 1,
    orig_id: q.orig_id || (idx + 1),
    section: q.section || ch.title,
    source: q.source || `${ch.title} Q${idx + 1}`,
    options: q.options || { a: "Option A", b: "Option B", c: "Option C", d: "Option D" },
    correct_answer: (q.correct_answer || "a").toLowerCase(),
    explanation: q.explanation || `Official UPSC CDS Answer Key: Option (${(q.correct_answer || 'a').toUpperCase()}) is the correct response.`
  }));

  setupTestSession({
    title: `${ch.title} — Chapter Real Test`,
    subject: subject.toUpperCase(),
    questions,
    posMark,
    negMark,
    duration
  });
}

function setupTestSession(config) {
  APP_STATE.currentTest = config;
  APP_STATE.currentQIndex = 0;
  APP_STATE.userResponses = {};
  APP_STATE.questionStatuses = {};
  APP_STATE.remainingSeconds = config.duration;
  APP_STATE.totalExamDuration = config.duration;
  APP_STATE.isPaused = false;

  // Initialize statuses
  config.questions.forEach((q, idx) => {
    APP_STATE.questionStatuses[q.id] = idx === 0 ? 'not-answered' : 'not-visited';
  });

  // Switch UI Views
  document.getElementById('dashboardView').style.display = 'none';
  document.getElementById('scorecardView').style.display = 'none';
  document.getElementById('reviewView').style.display = 'none';
  document.getElementById('examSimulatorView').style.display = 'block';

  // Update Header Bar
  document.getElementById('headerExamInfo').style.display = 'flex';
  document.getElementById('activePaperName').textContent = config.title;

  // Set marks pill
  document.getElementById('posMarkValue').textContent = config.posMark.toFixed(3);
  document.getElementById('negMarkValue').textContent = config.negMark.toFixed(3);
  document.getElementById('paletteTotalCount').textContent = config.questions.length;

  // Start Timer
  startExamTimer();

  // Render question & palette
  renderQuestion(0);
  renderPalette();
  updatePaletteSummary();
  saveActiveAttempt();
}

// Timer Logic
function startExamTimer() {
  if (APP_STATE.timerInterval) clearInterval(APP_STATE.timerInterval);

  updateTimerDisplay();
  const pauseBtn = document.getElementById('timerPauseBtn');
  pauseBtn.onclick = toggleTimerPause;

  APP_STATE.timerInterval = setInterval(() => {
    if (!APP_STATE.isPaused) {
      APP_STATE.remainingSeconds--;
      updateTimerDisplay();

      if (APP_STATE.remainingSeconds % 5 === 0) {
        saveActiveAttempt();
      }

      if (APP_STATE.remainingSeconds <= 0) {
        clearInterval(APP_STATE.timerInterval);
        alert("Time is UP! Your examination is being submitted automatically according to UPSC guidelines.");
        evaluateAndShowResults();
      }
    }
  }, 1000);
}

function updateTimerDisplay() {
  const sec = Math.max(0, APP_STATE.remainingSeconds);
  const h = Math.floor(sec / 3600);
  const m = Math.floor((sec % 3600) / 60);
  const s = sec % 60;
  const str = `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  
  const display = document.getElementById('timerDisplay');
  const container = document.getElementById('examTimerContainer');
  display.textContent = str;

  // Warning when under 10 minutes (600s)
  if (sec <= 600) {
    container.classList.add('warning');
  } else {
    container.classList.remove('warning');
  }
}

function toggleTimerPause() {
  APP_STATE.isPaused = !APP_STATE.isPaused;
  const btn = document.getElementById('timerPauseBtn');
  btn.textContent = APP_STATE.isPaused ? '▶' : '⏸';
  btn.title = APP_STATE.isPaused ? 'Resume Timer' : 'Pause Timer';
}

// ==========================================================================
// QUESTION DISPLAY & INTERACTION
// ==========================================================================

function renderQuestion(index) {
  if (!APP_STATE.currentTest) return;
  const qList = APP_STATE.currentTest.questions;
  if (index < 0 || index >= qList.length) return;

  APP_STATE.currentQIndex = index;
  const q = qList[index];

  // If was not-visited, now visited but not answered yet
  const curStatus = APP_STATE.questionStatuses[q.id];
  if (curStatus === 'not-visited') {
    APP_STATE.questionStatuses[q.id] = 'not-answered';
  }

  // Header badges
  document.getElementById('currentQNumBadge').textContent = `Question ${index + 1} of ${qList.length}`;
  document.getElementById('currentQSectionBadge').textContent = q.section || APP_STATE.currentTest.subject;
  document.getElementById('currentQSourceBadge').textContent = q.source || "UPSC CDS";

  // Stem
  const stemEl = document.getElementById('questionStemText');
  stemEl.innerHTML = '';
  if (q.passage) {
    const passageDiv = document.createElement('div');
    passageDiv.className = 'question-passage-block';
    passageDiv.style.cssText = 'background:var(--bg-tertiary); padding:14px; border-left:4px solid var(--accent-primary); border-radius:6px; margin-bottom:14px; line-height:1.6; font-size:14px; color:var(--text-primary);';
    passageDiv.innerHTML = `<b>Passage / Context:</b><br/>${q.passage}`;
    stemEl.appendChild(passageDiv);
  }
  const textDiv = document.createElement('div');
  textDiv.style.cssText = 'white-space: pre-wrap; line-height: 1.6;';
  textDiv.textContent = q.question;
  stemEl.appendChild(textDiv);

  if (q.image) {
    const imgEl = document.createElement('img');
    imgEl.src = q.image;
    imgEl.alt = "Question Diagram";
    imgEl.className = 'q-diagram-img';
    imgEl.style.cssText = 'max-width:100%; max-height:280px; margin-top:12px; border-radius:8px; border:1px solid var(--border-subtle); display:block;';
    stemEl.appendChild(imgEl);
  }

  // Options
  const optContainer = document.getElementById('optionsContainer');
  optContainer.innerHTML = '';

  const userChoice = APP_STATE.userResponses[q.id];
  const optKeys = ['a', 'b', 'c', 'd'];

  optKeys.forEach(key => {
    const text = q.options ? q.options[key] : '';
    if (!text) return;

    const optDiv = document.createElement('div');
    optDiv.className = `option-item ${userChoice === key ? 'selected' : ''}`;
    optDiv.onclick = () => selectOption(q.id, key);

    optDiv.innerHTML = `
      <div class="option-marker">${key.toUpperCase()}</div>
      <div class="option-text">${text}</div>
    `;
    optContainer.appendChild(optDiv);
  });

  // Update Palette active state
  highlightActivePaletteButton(index);
  updatePaletteSummary();
}

function selectOption(qId, selectedKey) {
  APP_STATE.userResponses[qId] = selectedKey;

  // If marked, set marked-answered, else answered
  const currentSt = APP_STATE.questionStatuses[qId];
  if (currentSt === 'marked' || currentSt === 'marked-answered') {
    APP_STATE.questionStatuses[qId] = 'marked-answered';
  } else {
    APP_STATE.questionStatuses[qId] = 'answered';
  }

  // Update options UI
  const items = document.querySelectorAll('.option-item');
  const optKeys = ['a', 'b', 'c', 'd'];
  items.forEach((item, idx) => {
    if (optKeys[idx] === selectedKey) {
      item.classList.add('selected');
    } else {
      item.classList.remove('selected');
    }
  });

  renderPalette();
  updatePaletteSummary();
  saveActiveAttempt();
}

function clearCurrentResponse() {
  const q = APP_STATE.currentTest.questions[APP_STATE.currentQIndex];
  delete APP_STATE.userResponses[q.id];

  // Reset status to not-answered or marked
  const st = APP_STATE.questionStatuses[q.id];
  if (st === 'marked-answered') {
    APP_STATE.questionStatuses[q.id] = 'marked';
  } else {
    APP_STATE.questionStatuses[q.id] = 'not-answered';
  }

  document.querySelectorAll('.option-item').forEach(el => el.classList.remove('selected'));
  renderPalette();
  updatePaletteSummary();
  saveActiveAttempt();
}

function markForReviewAndNext() {
  const q = APP_STATE.currentTest.questions[APP_STATE.currentQIndex];
  const hasAnswer = Boolean(APP_STATE.userResponses[q.id]);

  APP_STATE.questionStatuses[q.id] = hasAnswer ? 'marked-answered' : 'marked';
  renderPalette();
  updatePaletteSummary();
  saveActiveAttempt();
  navigateQuestion(1);
}

function saveAndNext() {
  const q = APP_STATE.currentTest.questions[APP_STATE.currentQIndex];
  const hasAnswer = Boolean(APP_STATE.userResponses[q.id]);

  if (hasAnswer) {
    APP_STATE.questionStatuses[q.id] = 'answered';
  } else {
    APP_STATE.questionStatuses[q.id] = 'not-answered';
  }

  renderPalette();
  updatePaletteSummary();
  saveActiveAttempt();
  navigateQuestion(1);
}

function navigateQuestion(delta) {
  const nextIdx = APP_STATE.currentQIndex + delta;
  if (nextIdx >= 0 && nextIdx < APP_STATE.currentTest.questions.length) {
    renderQuestion(nextIdx);
  }
}

// ==========================================================================
// QUESTION PALETTE & STATUS COUNTERS
// ==========================================================================

function renderPalette() {
  if (!APP_STATE.currentTest) return;
  const grid = document.getElementById('paletteGrid');
  grid.innerHTML = '';

  const questions = APP_STATE.currentTest.questions;
  questions.forEach((q, idx) => {
    const btn = document.createElement('button');
    const st = APP_STATE.questionStatuses[q.id] || 'not-visited';
    btn.className = `palette-btn status-${st} ${idx === APP_STATE.currentQIndex ? 'active-q' : ''}`;
    btn.textContent = idx + 1;
    btn.onclick = () => renderQuestion(idx);
    grid.appendChild(btn);
  });
}

function highlightActivePaletteButton(index) {
  const buttons = document.querySelectorAll('.palette-btn');
  buttons.forEach((btn, idx) => {
    if (idx === index) {
      btn.classList.add('active-q');
    } else {
      btn.classList.remove('active-q');
    }
  });
}

function updatePaletteSummary() {
  let answered = 0;
  let notAnswered = 0;
  let notVisited = 0;
  let marked = 0;
  let markedAnswered = 0;

  Object.values(APP_STATE.questionStatuses).forEach(st => {
    if (st === 'answered') answered++;
    else if (st === 'not-answered') notAnswered++;
    else if (st === 'not-visited') notVisited++;
    else if (st === 'marked') marked++;
    else if (st === 'marked-answered') markedAnswered++;
  });

  document.getElementById('countAnswered').textContent = answered;
  document.getElementById('countNotAnswered').textContent = notAnswered;
  document.getElementById('countNotVisited').textContent = notVisited;
  document.getElementById('countMarked').textContent = marked;
  document.getElementById('countMarkedAnswered').textContent = markedAnswered;
}

// ==========================================================================
// MODALS
// ==========================================================================

function confirmSubmitExam() {
  let answered = 0;
  let marked = 0;

  Object.values(APP_STATE.questionStatuses).forEach(st => {
    if (st === 'answered' || st === 'marked-answered') answered++;
    if (st === 'marked' || st === 'marked-answered') marked++;
  });

  const total = APP_STATE.currentTest.questions.length;
  const unanswered = total - answered;

  document.getElementById('modalAnsweredCount').textContent = answered;
  document.getElementById('modalUnansweredCount').textContent = unanswered;
  document.getElementById('modalMarkedCount').textContent = marked;

  const sec = APP_STATE.remainingSeconds;
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  document.getElementById('modalTimeRemaining').textContent = `${m}m ${s}s`;

  document.getElementById('submitModal').style.display = 'flex';
}

function closeSubmitModal() {
  document.getElementById('submitModal').style.display = 'none';
}

function openInstructionsModal() {
  document.getElementById('instructionsModal').style.display = 'flex';
}

function closeInstructionsModal() {
  document.getElementById('instructionsModal').style.display = 'none';
}

function openOverviewModal() {
  const content = document.getElementById('overviewModalContent');
  content.innerHTML = '';

  const qList = APP_STATE.currentTest.questions;
  qList.forEach((q, idx) => {
    const item = document.createElement('div');
    const userAns = APP_STATE.userResponses[q.id];
    item.style.padding = '12px';
    item.style.marginBottom = '10px';
    item.style.background = 'var(--bg-tertiary)';
    item.style.borderRadius = '8px';
    item.style.border = '1px solid var(--border-subtle)';

    item.innerHTML = `
      <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
        <b>Q${idx + 1}. [${q.section}]</b>
        <span style="font-size: 12px; color: ${userAns ? 'var(--accent-emerald)' : 'var(--text-muted)'};">
          ${userAns ? `Attempted: (${userAns.toUpperCase()})` : 'Not Attempted'}
        </span>
      </div>
      <p style="font-size: 13px; line-height: 1.5; color: var(--text-secondary); margin-bottom: 8px;">${q.question}</p>
      <button class="btn btn-sm btn-outline" onclick="closeOverviewModal(); renderQuestion(${idx});">
        Jump to Question ${idx + 1}
      </button>
    `;
    content.appendChild(item);
  });

  document.getElementById('overviewModalContent').scrollTop = 0;
  document.getElementById('overviewModal').style.display = 'flex';
}

function closeOverviewModal() {
  document.getElementById('overviewModal').style.display = 'none';
}

// ==========================================================================
// EVALUATION ENGINE & SCORECARD
// ==========================================================================

function evaluateAndShowResults() {
  closeSubmitModal();
  clearActiveAttempt();
  if (APP_STATE.timerInterval) clearInterval(APP_STATE.timerInterval);

  const test = APP_STATE.currentTest;
  const questions = test.questions;
  const total = questions.length;
  const posMark = test.posMark;
  const negMark = test.negMark;

  let correctCount = 0;
  let incorrectCount = 0;
  let unattemptedCount = 0;

  const detailedList = [];

  questions.forEach(q => {
    const userChoice = APP_STATE.userResponses[q.id];
    const correctChoice = q.correct_answer.toLowerCase();

    let status = 'unattempted';
    if (userChoice) {
      if (userChoice === correctChoice) {
        correctCount++;
        status = 'correct';
      } else {
        incorrectCount++;
        status = 'incorrect';
      }
    } else {
      unattemptedCount++;
    }

    detailedList.push({
      q,
      userChoice,
      correctChoice,
      status
    });
  });

  const attemptedCount = correctCount + incorrectCount;
  const posScore = correctCount * posMark;
  const negPenalty = incorrectCount * negMark;
  const rawScore = posScore - negPenalty;
  const finalScore = Math.max(0, rawScore);
  const accuracy = attemptedCount > 0 ? (correctCount / attemptedCount) * 100 : 0;

  // Scale for display if question count differs from standard 100 marks
  const maxPossibleMarks = 100;
  const scaledScore = total === 120 || total === 100 ? finalScore : (finalScore / (total * posMark)) * 100;

  const timeUsedSeconds = APP_STATE.totalExamDuration - APP_STATE.remainingSeconds;
  const timeUsedMin = Math.floor(timeUsedSeconds / 60);
  const timeUsedSec = timeUsedSeconds % 60;
  const avgSpeedSec = attemptedCount > 0 ? Math.round(timeUsedSeconds / attemptedCount) : 0;

  APP_STATE.evaluationResult = {
    testTitle: test.title,
    total,
    correctCount,
    incorrectCount,
    unattemptedCount,
    attemptedCount,
    posScore,
    negPenalty,
    finalScore: scaledScore,
    accuracy,
    timeUsedSeconds,
    timeUsedMin,
    timeUsedSec,
    avgSpeedSec,
    detailedList
  };

  // Save attempt to historical performance archive
  saveAttemptToHistory({
    id: 'att_' + Date.now(),
    timestamp: new Date().toISOString(),
    dateStr: new Date().toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }) + ' ' + new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }),
    testTitle: test.title,
    subject: test.subject || (test.id && test.id.includes('math') ? 'math' : (test.id && test.id.includes('gs') ? 'gs' : 'english')),
    totalQuestions: total,
    attemptedCount,
    correctCount,
    incorrectCount,
    unattemptedCount,
    finalScore: scaledScore,
    maxMarks: maxPossibleMarks,
    accuracy,
    cutoffCleared: scaledScore >= 20.0,
    timeUsedSeconds,
    detailedList
  });

  // Render Scorecard View
  renderScorecardView();
}

function renderScorecardView() {
  const res = APP_STATE.evaluationResult;

  document.getElementById('examSimulatorView').style.display = 'none';
  document.getElementById('headerExamInfo').style.display = 'none';
  document.getElementById('scorecardView').style.display = 'block';

  document.getElementById('scorePaperTitle').textContent = res.testTitle;
  document.getElementById('finalScoreVal').textContent = res.finalScore.toFixed(2);

  // Sectional Cutoff Verification (20% = 20 marks)
  const isPass = res.finalScore >= 20.0;
  const pill = document.getElementById('cutoffStatusPill');
  if (isPass) {
    pill.innerHTML = `<span class="status-indicator pass"></span> Sectional Cutoff Cleared (Min. 20% Required)`;
    pill.style.color = '#34d399';
  } else {
    pill.innerHTML = `<span class="status-indicator" style="background:#ef4444;"></span> Sectional Cutoff Failed (<20% Benchmark)`;
    pill.style.color = '#ef4444';
  }

  // Accuracy
  document.getElementById('accuracyRateVal').textContent = `${res.accuracy.toFixed(1)}%`;
  document.getElementById('accuracySubtext').textContent = res.accuracy >= 80 ? "Exceptional Precision" : (res.accuracy >= 60 ? "Competitive Precision" : "Needs Review on Accuracy");

  // Merit Forecast
  let meritRank = "Disqualified";
  let meritDesc = "Fails mandatory sectional cutoff of 20%";
  if (res.finalScore >= 75) {
    meritRank = "Exceptional (Top 1%)";
    meritDesc = "Guaranteed High Merit Rank across IMA & AFA";
  } else if (res.finalScore >= 60) {
    meritRank = "Strong Competitive";
    meritDesc = "Solid qualifying score for SSB interview call";
  } else if (res.finalScore >= 40) {
    meritRank = "Moderate / Average";
    meritDesc = "Clears cutoff; focus on speed & accuracy";
  } else if (res.finalScore >= 20) {
    meritRank = "Bare Minimum Cutoff";
    meritDesc = "Marginal score; requires systematic revision";
  }

  document.getElementById('meritRankVal').textContent = meritRank;
  document.getElementById('meritAcademyVal').textContent = meritDesc;

  // Time & Speed
  document.getElementById('timeConsumedVal').textContent = `${res.timeUsedMin}m ${res.timeUsedSec}s`;
  document.getElementById('avgSpeedVal').textContent = `~${res.avgSpeedSec}s per attempted question`;

  // Breakdown Counters
  document.getElementById('bdCorrectCount').textContent = res.correctCount;
  document.getElementById('bdCorrectMarks').textContent = `+${res.posScore.toFixed(2)} Marks`;

  document.getElementById('bdIncorrectCount').textContent = res.incorrectCount;
  document.getElementById('bdIncorrectPenalty').textContent = `-${res.negPenalty.toFixed(2)} Penalty`;

  document.getElementById('bdUnattemptedCount').textContent = res.unattemptedCount;
  document.getElementById('bdTotalQuestions').textContent = res.total;
  document.getElementById('bdAttemptedCount').textContent = `${res.attemptedCount} Attempted`;
}

// ==========================================================================
// SOLUTIONS REVIEW VIEW
// ==========================================================================

function openReviewSolutions() {
  document.getElementById('scorecardView').style.display = 'none';
  document.getElementById('reviewView').style.display = 'block';

  document.getElementById('reviewPaperTitle').textContent = `${APP_STATE.evaluationResult.testTitle} — Detailed Solutions`;
  filterReviewList('all');
}

function backToScorecard() {
  document.getElementById('reviewView').style.display = 'none';
  document.getElementById('scorecardView').style.display = 'block';
}

function returnToDashboard() {
  document.getElementById('scorecardView').style.display = 'none';
  document.getElementById('reviewView').style.display = 'none';
  document.getElementById('examSimulatorView').style.display = 'none';
  document.getElementById('headerExamInfo').style.display = 'none';
  document.getElementById('dashboardView').style.display = 'block';
  window.scrollTo(0, 0);
}

function filterReviewList(filter, btn) {
  APP_STATE.reviewFilter = filter;
  document.querySelectorAll('.review-filters .filter-pill').forEach(b => b.classList.remove('active'));
  if (btn) {
    btn.classList.add('active');
  } else if (window.event && window.event.target) {
    window.event.target.classList.add('active');
  }

  const container = document.getElementById('reviewListContainer');
  container.innerHTML = '';

  const list = APP_STATE.evaluationResult.detailedList;
  const filtered = list.filter(item => {
    if (filter === 'all') return true;
    if (filter === 'marked') {
      const qId = item.q.id;
      const st = APP_STATE.questionStatuses[qId];
      return st === 'marked' || st === 'marked-answered';
    }
    return item.status === filter;
  });

  if (filtered.length === 0) {
    container.innerHTML = `
      <div style="text-align: center; padding: 40px; color: var(--text-muted);">
        No questions match the "${filter}" filter.
      </div>
    `;
    return;
  }

  filtered.forEach(item => {
    const q = item.q;
    const card = document.createElement('div');
    card.className = `review-card ${item.status}`;

    const pos = APP_STATE.currentTest ? APP_STATE.currentTest.posMark.toFixed(3) : '0.833';
    const neg = APP_STATE.currentTest ? APP_STATE.currentTest.negMark.toFixed(3) : '0.277';

    const isVerified = (q.verificationStatus === 'fully_verified' || q.verification_status === 'fully_verified') && item.correctChoice && item.correctChoice !== 'pending';

    let statusBadge = '';
    if (!isVerified) {
      statusBadge = `<span class="badge badge-amber" style="background:rgba(217,119,6,0.15); color:#d97706;">⚠️ OFFICIAL ANSWER KEY PENDING</span>`;
    } else if (item.status === 'correct') {
      statusBadge = `<span class="badge badge-green">CORRECT (+${pos})</span>`;
    } else if (item.status === 'incorrect') {
      statusBadge = `<span class="badge badge-rose" style="background:rgba(244,63,94,0.15); color:#f43f5e;">INCORRECT (-${neg})</span>`;
    } else {
      statusBadge = `<span class="badge badge-gray">UNATTEMPTED (0)</span>`;
    }

    const optKeys = ['a', 'b', 'c', 'd'];
    let optsHtml = '';
    optKeys.forEach(k => {
      const isCorrect = isVerified && (k === item.correctChoice);
      const isUserWrong = item.userChoice === k && !isCorrect;
      const cls = isCorrect ? 'is-correct' : (isUserWrong ? 'is-user-wrong' : '');
      const mark = isCorrect ? '✅ Official UPSC Answer' : (item.userChoice === k ? (isVerified ? '❌ Your Selection' : '🔵 Your Selection') : '');
      const optVal = (q.options && q.options[k]) ? q.options[k] : `Option ${k.toUpperCase()}`;

      optsHtml += `
        <div class="review-opt ${cls}">
          <span><b>(${k.toUpperCase()})</b> ${optVal}</span>
          ${mark ? `<span style="font-size:11.5px;">${mark}</span>` : ''}
        </div>
      `;
    });

    const passageHtml = q.passage ? `<div class="question-passage-block" style="background:var(--bg-tertiary); padding:10px 14px; border-left:3px solid var(--accent-primary); border-radius:6px; margin-bottom:10px; font-size:13px; line-height:1.5;"><b>Passage / Context:</b><br/>${q.passage}</div>` : '';
    const imgHtml = q.image ? `<img src="${q.image}" alt="Diagram" class="q-diagram-img" style="max-width:100%; max-height:220px; margin:10px 0; border-radius:6px; display:block;" />` : '';

    const sourceFile = q.sourceFile || q.source_file || (APP_STATE.currentTest && APP_STATE.currentTest.pdf_path);
    const sourcePage = q.sourcePage || q.source_page || 'Original Booklet';
    const provenanceHtml = sourceFile ? `
      <div class="review-provenance-bar">
        <span>📄 <b>Source Provenance:</b> ${sourceFile}</span>
        ${sourcePage ? `<span>• Page ${sourcePage}</span>` : ''}
        <a href="${sourceFile.startsWith('pyq_papers/') ? sourceFile : 'pyq_papers/' + sourceFile}" target="_blank" class="review-provenance-link">Open Official Booklet PDF ↗</a>
      </div>
    ` : '';

    const explanationText = isVerified 
      ? (q.explanation || `According to the official UPSC Combined Defence Services examination answer key, Option (${item.correctChoice.toUpperCase()}) is the correct response.`)
      : `Official UPSC Answer Key for this question is pending verification. Candidate answer not scored until official answer key is released.`;

    card.innerHTML = `
      <div class="review-card-top">
        <div>
          <b>Question ${q.id}</b> • <span style="font-size:12px; color:var(--text-muted);">${q.source || q.section || 'Official Booklet'}</span>
        </div>
        ${statusBadge}
      </div>
      ${passageHtml}
      <div class="review-card-title" style="white-space:pre-wrap;">${q.question || q.questionText}</div>
      ${imgHtml}
      <div class="review-opts">
        ${optsHtml}
      </div>
      <div class="review-explanation">
        <b>Constitutional / Official Rationale:</b><br/>
        ${explanationText}
      </div>
      ${provenanceHtml}
    `;
    container.appendChild(card);
  });
}

// ==========================================================================
// CANDIDATE PERFORMANCE & ATTEMPT HISTORY LOGIC
// ==========================================================================

function saveAttemptToHistory(attempt) {
  try {
    const raw = localStorage.getItem('cds_attempt_history');
    let history = raw ? JSON.parse(raw) : [];
    if (!Array.isArray(history)) history = [];
    history.unshift(attempt);
    if (history.length > 50) history = history.slice(0, 50);
    localStorage.setItem('cds_attempt_history', JSON.stringify(history));
    updateDashboardBadge();
  } catch (err) {
    console.warn("Could not save attempt history to localStorage:", err);
  }
}

function updateDashboardBadge() {
  try {
    const raw = localStorage.getItem('cds_attempt_history');
    const history = raw ? JSON.parse(raw) : [];
    const count = Array.isArray(history) ? history.length : 0;
    const badge = document.getElementById('tabHistoryCountBadge');
    if (badge) {
      badge.textContent = `${count} ${count === 1 ? 'Test' : 'Tests'}`;
    }
  } catch (e) {
    // ignore
  }
}

function renderCandidateDashboard() {
  let history = [];
  try {
    const raw = localStorage.getItem('cds_attempt_history');
    if (raw) history = JSON.parse(raw);
    if (!Array.isArray(history)) history = [];
  } catch (e) {
    history = [];
  }

  const totalAttempts = history.length;
  const dashAttemptsEl = document.getElementById('dashTotalAttempts');
  const dashAttemptSubtext = document.getElementById('dashAttemptSubtext');
  const dashAvgScoreEl = document.getElementById('dashAvgScore');
  const dashAvgAccEl = document.getElementById('dashAvgAccuracy');
  const dashAccSubtext = document.getElementById('dashAccuracySubtext');
  const dashBestScoreEl = document.getElementById('dashBestScore');
  const dashBestPaperEl = document.getElementById('dashBestPaper');
  const dashCutoffRateEl = document.getElementById('dashCutoffRate');
  const tbody = document.getElementById('attemptHistoryBody');

  if (dashAttemptsEl) dashAttemptsEl.textContent = totalAttempts;
  if (dashAttemptSubtext) dashAttemptSubtext.textContent = totalAttempts === 1 ? '1 test completed' : `${totalAttempts} tests completed`;

  if (totalAttempts === 0) {
    if (dashAvgScoreEl) dashAvgScoreEl.textContent = '0.0';
    if (dashAvgAccEl) dashAvgAccEl.textContent = '0%';
    if (dashAccSubtext) dashAccSubtext.textContent = 'No attempts recorded';
    if (dashBestScoreEl) dashBestScoreEl.textContent = '0.0';
    if (dashBestPaperEl) dashBestPaperEl.textContent = 'No tests logged yet';
    if (dashCutoffRateEl) dashCutoffRateEl.textContent = '0%';

    ['English', 'Gs', 'Math'].forEach(sub => {
      const pctEl = document.getElementById(`mastery${sub}Pct`);
      const barEl = document.getElementById(`mastery${sub}Bar`);
      const attEl = document.getElementById(`mastery${sub}Attempts`);
      const avgEl = document.getElementById(`mastery${sub}Avg`);
      if (pctEl) pctEl.textContent = '0%';
      if (barEl) barEl.style.width = '0%';
      if (attEl) attEl.textContent = '0 attempts';
      if (avgEl) avgEl.textContent = 'Avg: — / 100';
    });

    if (tbody) {
      tbody.innerHTML = `
        <tr>
          <td colspan="7">
            <div class="history-empty-state">
              <span class="empty-icon">🎖️</span>
              <h4>No Completed Test Attempts Recorded Yet</h4>
              <p>Take any authentic 2-hour UPSC CDS Mock Test or Year-Wise Past Paper (2009–2026). Your sectional scores, accuracy benchmarks, and question-by-question solutions will be automatically saved here for instant review.</p>
              <button class="btn btn-primary btn-sm" onclick="switchDashboardTab('pyq')">
                <span>📅</span> Browse 108 PYQ Papers
              </button>
            </div>
          </td>
        </tr>
      `;
    }
    return;
  }

  // Calculate aggregates
  let sumScore = 0;
  let sumAcc = 0;
  let clearedCount = 0;
  let bestScore = -1;
  let bestTitle = '—';

  const subStats = {
    english: { attempts: 0, sumScore: 0, sumAcc: 0 },
    gs: { attempts: 0, sumScore: 0, sumAcc: 0 },
    math: { attempts: 0, sumScore: 0, sumAcc: 0 }
  };

  history.forEach(att => {
    const s = Number(att.finalScore) || 0;
    const a = Number(att.accuracy) || 0;
    sumScore += s;
    sumAcc += a;
    if (att.cutoffCleared || s >= 20.0) clearedCount++;
    if (s > bestScore) {
      bestScore = s;
      bestTitle = att.testTitle || 'CDS Paper';
    }

    const subKey = (att.subject && subStats[att.subject.toLowerCase()]) ? att.subject.toLowerCase() : null;
    if (subKey) {
      subStats[subKey].attempts++;
      subStats[subKey].sumScore += s;
      subStats[subKey].sumAcc += a;
    }
  });

  const avgScore = sumScore / totalAttempts;
  const avgAcc = sumAcc / totalAttempts;
  const cutoffPct = Math.round((clearedCount / totalAttempts) * 100);

  if (dashAvgScoreEl) dashAvgScoreEl.textContent = avgScore.toFixed(1);
  if (dashAvgAccEl) dashAvgAccEl.textContent = `${avgAcc.toFixed(1)}%`;
  if (dashAccSubtext) dashAccSubtext.textContent = avgAcc >= 75 ? 'Superior Precision' : (avgAcc >= 50 ? 'Steady Accuracy' : 'Focus on Negative Marking');
  if (dashBestScoreEl) dashBestScoreEl.textContent = bestScore >= 0 ? bestScore.toFixed(1) : '0.0';
  if (dashBestPaperEl) dashBestPaperEl.textContent = bestTitle;
  if (dashCutoffRateEl) dashCutoffRateEl.textContent = `${cutoffPct}%`;

  // Render Subject Mastery
  const subConfig = [
    { key: 'english', label: 'English', max: 100 },
    { key: 'gs', label: 'Gs', max: 100 },
    { key: 'math', label: 'Math', max: 100 }
  ];

  subConfig.forEach(cfg => {
    const st = subStats[cfg.key];
    const pctEl = document.getElementById(`mastery${cfg.label}Pct`);
    const barEl = document.getElementById(`mastery${cfg.label}Bar`);
    const attEl = document.getElementById(`mastery${cfg.label}Attempts`);
    const avgEl = document.getElementById(`mastery${cfg.label}Avg`);

    if (st.attempts > 0) {
      const subAvg = st.sumScore / st.attempts;
      const subPct = Math.min(100, Math.round((subAvg / cfg.max) * 100));
      if (pctEl) pctEl.textContent = `${subPct}%`;
      if (barEl) barEl.style.width = `${subPct}%`;
      if (attEl) attEl.textContent = `${st.attempts} ${st.attempts === 1 ? 'attempt' : 'attempts'}`;
      if (avgEl) avgEl.textContent = `Avg: ${subAvg.toFixed(1)} / 100`;
    } else {
      if (pctEl) pctEl.textContent = '0%';
      if (barEl) barEl.style.width = '0%';
      if (attEl) attEl.textContent = '0 attempts';
      if (avgEl) avgEl.textContent = 'Avg: — / 100';
    }
  });

  // Render Table Rows
  if (tbody) {
    let rowsHtml = '';
    history.forEach((att, idx) => {
      const isCleared = (att.cutoffCleared || Number(att.finalScore) >= 20.0);
      const badgeClass = isCleared ? 'history-badge-pass' : 'history-badge-fail';
      const badgeTxt = isCleared ? 'Cleared (≥20%)' : 'Failed (<20%)';
      
      const sub = (att.subject || 'paper').toLowerCase();
      const subBadgeColor = sub === 'math' ? 'badge-green' : (sub === 'gs' ? 'badge-amber' : 'badge-blue');
      const subLabel = sub === 'math' ? 'Mathematics' : (sub === 'gs' ? 'General Knowledge' : 'English');

      rowsHtml += `
        <tr>
          <td><span style="font-family: var(--font-mono); font-size: 12px; color: var(--text-secondary);">${att.dateStr || 'Recent'}</span></td>
          <td><b>${att.testTitle || 'UPSC CDS Test Paper'}</b></td>
          <td><span class="badge ${subBadgeColor}">${subLabel}</span></td>
          <td><b style="font-family: var(--font-mono); font-size: 14px;">${Number(att.finalScore).toFixed(2)}</b></td>
          <td><span style="font-family: var(--font-mono);">${Number(att.accuracy).toFixed(1)}%</span></td>
          <td><span class="${badgeClass}">${badgeTxt}</span></td>
          <td>
            <button class="btn btn-secondary btn-sm" onclick="reReviewHistoricalAttempt(${idx})" title="Open detailed solutions and questions for this attempt">
              <span>🔍</span> Review
            </button>
          </td>
        </tr>
      `;
    });
    tbody.innerHTML = rowsHtml;
  }
}

function reReviewHistoricalAttempt(idx) {
  try {
    const raw = localStorage.getItem('cds_attempt_history');
    if (!raw) return;
    const history = JSON.parse(raw);
    const attempt = history[idx];
    if (!attempt) return;

    if (!attempt.detailedList || !Array.isArray(attempt.detailedList) || attempt.detailedList.length === 0) {
      alert("Detailed question records were not retained for this older attempt.");
      return;
    }

    const posM = attempt.subject === 'math' ? 1.0 : (5/6);
    const negM = attempt.subject === 'math' ? (1/3) : (5/18);

    APP_STATE.evaluationResult = {
      testTitle: attempt.testTitle,
      total: attempt.totalQuestions || attempt.detailedList.length,
      correctCount: attempt.correctCount || 0,
      incorrectCount: attempt.incorrectCount || 0,
      unattemptedCount: attempt.unattemptedCount || 0,
      attemptedCount: attempt.attemptedCount || 0,
      posScore: (attempt.correctCount || 0) * posM,
      negPenalty: (attempt.incorrectCount || 0) * negM,
      finalScore: Number(attempt.finalScore) || 0,
      accuracy: Number(attempt.accuracy) || 0,
      timeUsedSeconds: attempt.timeUsedSeconds || 0,
      timeUsedMin: Math.floor((attempt.timeUsedSeconds || 0) / 60),
      timeUsedSec: (attempt.timeUsedSeconds || 0) % 60,
      avgSpeedSec: attempt.attemptedCount > 0 ? Math.round((attempt.timeUsedSeconds || 0) / attempt.attemptedCount) : 0,
      detailedList: attempt.detailedList
    };

    // Close any open modals or other views
    document.getElementById('dashboardView').style.display = 'none';
    document.getElementById('examSimulatorView').style.display = 'none';
    document.getElementById('scorecardView').style.display = 'none';
    document.getElementById('headerExamInfo').style.display = 'none';
    
    // Open review view
    const rView = document.getElementById('reviewView');
    rView.style.display = 'block';
    document.getElementById('reviewPaperTitle').textContent = `${attempt.testTitle} — Attempt Review (${attempt.dateStr || ''})`;
    filterReviewList('all');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  } catch (err) {
    console.error("Error loading historical attempt:", err);
  }
}

function clearAttemptHistory() {
  if (confirm("Are you sure you want to reset your candidate history? All recorded mock and PYQ attempts will be permanently erased from this device.")) {
    try {
      localStorage.removeItem('cds_attempt_history');
      renderCandidateDashboard();
      updateDashboardBadge();
    } catch (e) {
      console.warn("Error resetting history:", e);
    }
  }
}

// ==========================================================================
// KEYBOARD SHORTCUTS
// ==========================================================================

function setupKeyboardShortcuts() {
  document.addEventListener('keydown', e => {
    // 1. Global modal dismissal on Escape
    if (e.key === 'Escape') {
      const submitM = document.getElementById('submitModal');
      const instM = document.getElementById('instructionsModal');
      const overM = document.getElementById('overviewModal');
      const adminM = document.getElementById('adminVerificationModal');
      const navPop = document.getElementById('navigatorPopup');
      
      if (submitM && submitM.style.display !== 'none') { closeSubmitModal(); return; }
      if (instM && instM.style.display !== 'none') { closeInstructionsModal(); return; }
      if (overM && overM.style.display !== 'none') { closeOverviewModal(); return; }
      if (adminM && adminM.style.display !== 'none') { closeAdminModal(); return; }
      if (navPop && navPop.style.display !== 'none') { navPop.style.display = 'none'; return; }
    }

    // Ignore exam shortcuts if typing in any text input, textarea or select
    if (e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT')) {
      return;
    }

    // Exam simulator specific navigation shortcuts
    if (document.getElementById('examSimulatorView').style.display !== 'block') return;

    if (e.key === 'ArrowRight' || e.key === 'n') {
      navigateQuestion(1);
    } else if (e.key === 'ArrowLeft' || e.key === 'p') {
      navigateQuestion(-1);
    } else if (e.key === '1' || e.key === 'a' || e.key === 'A') {
      const q = APP_STATE.currentTest.questions[APP_STATE.currentQIndex];
      selectOption(q.id, 'a');
    } else if (e.key === '2' || e.key === 'b' || e.key === 'B') {
      const q = APP_STATE.currentTest.questions[APP_STATE.currentQIndex];
      selectOption(q.id, 'b');
    } else if (e.key === '3' || e.key === 'c' || e.key === 'C') {
      const q = APP_STATE.currentTest.questions[APP_STATE.currentQIndex];
      selectOption(q.id, 'c');
    } else if (e.key === '4' || e.key === 'd' || e.key === 'D') {
      const q = APP_STATE.currentTest.questions[APP_STATE.currentQIndex];
      selectOption(q.id, 'd');
    } else if (e.key === 'Enter') {
      saveAndNext();
    }
  });
}

// ==========================================================================
// PORTAL & EXAM NAVIGATOR FUNCTIONS
// ==========================================================================

function toggleNavigatorPopup(source = 'fab') {
  const popup = document.getElementById('navigatorPopup');
  if (!popup) return;
  const isHidden = popup.style.display === 'none' || popup.style.display === '';
  
  if (isHidden) {
    if (source === 'header') {
      popup.classList.add('popup-from-header');
      popup.classList.remove('popup-from-fab');
    } else {
      popup.classList.add('popup-from-fab');
      popup.classList.remove('popup-from-header');
    }
    popup.style.display = 'block';
  } else {
    popup.style.display = 'none';
  }
}

function toggleExamPalette() {
  const sidebar = document.querySelector('.exam-sidebar');
  if (!sidebar) return;
  
  // Smooth scroll into view if on mobile/small screen
  sidebar.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  
  // Visual pulse highlight
  sidebar.classList.add('palette-active-focus');
  setTimeout(() => {
    sidebar.classList.remove('palette-active-focus');
  }, 1200);
}

// Close popup on outside click
document.addEventListener('click', (e) => {
  const popup = document.getElementById('navigatorPopup');
  const btnFab = document.getElementById('fabNavigatorBtn');
  const btnHeader = document.getElementById('headerNavigatorBtn');
  if (popup && popup.style.display === 'block') {
    const clickedInside = popup.contains(e.target) || 
      (btnFab && btnFab.contains(e.target)) || 
      (btnHeader && btnHeader.contains(e.target));
    if (!clickedInside) {
      popup.style.display = 'none';
    }
  }
});

// ==========================================================================
// EXAM ATTEMPT PERSISTENCE (RESTORE ACROSS PAGE REFRESH)
// ==========================================================================

function saveActiveAttempt() {
  if (!APP_STATE.currentTest) return;
  try {
    const attemptData = {
      test: APP_STATE.currentTest,
      currentQIndex: APP_STATE.currentQIndex,
      userResponses: APP_STATE.userResponses,
      questionStatuses: APP_STATE.questionStatuses,
      remainingSeconds: APP_STATE.remainingSeconds,
      totalExamDuration: APP_STATE.totalExamDuration,
      savedAt: Date.now()
    };
    localStorage.setItem('cds_active_attempt', JSON.stringify(attemptData));
  } catch (e) {
    console.warn("Could not save attempt state:", e);
  }
}

function clearActiveAttempt() {
  localStorage.removeItem('cds_active_attempt');
  const banner = document.getElementById('activeAttemptBanner');
  if (banner) banner.style.display = 'none';
}

function checkForActiveAttempt() {
  try {
    const raw = localStorage.getItem('cds_active_attempt');
    if (!raw) return;
    const data = JSON.parse(raw);
    if (!data || !data.test) return;

    const now = Date.now();
    const elapsedSinceSave = Math.floor((now - (data.savedAt || now)) / 1000);
    const adjustedRemaining = Math.max(0, data.remainingSeconds - elapsedSinceSave);

    if (adjustedRemaining <= 0) {
      clearActiveAttempt();
      return;
    }

    const answeredCount = Object.keys(data.userResponses || {}).length;
    const m = Math.floor(adjustedRemaining / 60);

    const banner = document.getElementById('activeAttemptBanner');
    const titleEl = document.getElementById('bannerAttemptTitle');
    const metaEl = document.getElementById('bannerAttemptMeta');

    if (banner && titleEl && metaEl) {
      titleEl.textContent = `In-Progress Examination: ${data.test.title}`;
      metaEl.textContent = `Active Session: ${answeredCount} answered • ~${m}m remaining. Click Resume to continue test immediately.`;
      banner.style.display = 'block';
    }
  } catch (e) {
    console.warn("Active attempt parse error:", e);
  }
}

function resumeActiveAttempt() {
  try {
    const raw = localStorage.getItem('cds_active_attempt');
    if (!raw) return;
    const data = JSON.parse(raw);
    if (!data || !data.test) return;

    const now = Date.now();
    const elapsedSinceSave = Math.floor((now - (data.savedAt || now)) / 1000);
    const adjustedRemaining = Math.max(5, data.remainingSeconds - elapsedSinceSave);

    APP_STATE.currentTest = data.test;
    APP_STATE.currentQIndex = data.currentQIndex || 0;
    APP_STATE.userResponses = data.userResponses || {};
    APP_STATE.questionStatuses = data.questionStatuses || {};
    APP_STATE.remainingSeconds = adjustedRemaining;
    APP_STATE.totalExamDuration = data.totalExamDuration || data.test.duration;
    APP_STATE.isPaused = false;

    // Switch UI Views
    document.getElementById('dashboardView').style.display = 'none';
    document.getElementById('scorecardView').style.display = 'none';
    document.getElementById('reviewView').style.display = 'none';
    document.getElementById('examSimulatorView').style.display = 'block';

    // Update Header Bar
    document.getElementById('headerExamInfo').style.display = 'flex';
    document.getElementById('activePaperName').textContent = data.test.title;
    document.getElementById('posMarkValue').textContent = data.test.posMark.toFixed(3);
    document.getElementById('negMarkValue').textContent = data.test.negMark.toFixed(3);
    document.getElementById('paletteTotalCount').textContent = data.test.questions.length;

    const banner = document.getElementById('activeAttemptBanner');
    if (banner) banner.style.display = 'none';

    startExamTimer();
    renderQuestion(APP_STATE.currentQIndex);
    renderPalette();
    updatePaletteSummary();
  } catch (e) {
    alert("Could not resume test session.");
  }
}

function discardActiveAttempt() {
  if (confirm("Are you sure you want to discard your in-progress exam attempt? All saved responses for this session will be cleared.")) {
    clearActiveAttempt();
  }
}

// ==========================================================================
// ADMIN VERIFICATION HUB & SOURCE MANAGEMENT (SECTION 11)
// ==========================================================================

function openAdminModal() {
  const modal = document.getElementById('adminVerificationModal');
  if (!modal) return;

  const isAuth = sessionStorage.getItem('cds_admin_auth') === 'true';
  const authSec = document.getElementById('adminAuthSection');
  const dashSec = document.getElementById('adminDashboardSection');

  if (isAuth) {
    authSec.style.display = 'none';
    dashSec.style.display = 'block';
    initAdminPanel();
  } else {
    authSec.style.display = 'block';
    dashSec.style.display = 'none';
  }

  modal.style.display = 'flex';
}

function closeAdminModal() {
  const modal = document.getElementById('adminVerificationModal');
  if (modal) modal.style.display = 'none';
}

function verifyAdminPasskey() {
  const input = document.getElementById('adminPasskeyInput');
  const val = input ? input.value.trim() : '';

  if (val === 'CDS2026ADMIN') {
    sessionStorage.setItem('cds_admin_auth', 'true');
    document.getElementById('adminAuthSection').style.display = 'none';
    document.getElementById('adminDashboardSection').style.display = 'block';
    initAdminPanel();
  } else {
    alert("Invalid Admin Passkey. Please try again.");
    if (input) input.focus();
  }
}

function initAdminPanel() {
  // Populate year dropdown (2026 down to 2009)
  const yrSelect = document.getElementById('adminYearSelect');
  if (yrSelect && yrSelect.children.length === 0) {
    for (let y = 2026; y >= 2009; y--) {
      const opt = document.createElement('option');
      opt.value = String(y);
      opt.textContent = `Year ${y}`;
      yrSelect.appendChild(opt);
    }
  }

  onAdminPaperSelectionChange();
}

function onAdminPaperSelectionChange() {
  const subject = document.getElementById('adminSubjectSelect').value;
  const year = document.getElementById('adminYearSelect').value;
  const session = document.getElementById('adminSessionSelect').value;

  const pyqSource = window.CDS_PYQ_DATA || window.CDS_PYQ_PAPERS;
  if (!pyqSource || !pyqSource[subject]) return;

  // Find matching paper
  const papers = pyqSource[subject];
  let paper = papers.find(p => p.year === year && (p.edition === session || (p.label && p.label.includes(session))));
  if (!paper) {
    paper = papers.find(p => p.year === year) || papers[0];
  }

  if (!paper) return;

  APP_STATE.adminCurrentPaper = paper;
  APP_STATE.adminCurrentQIndex = 0;

  // Update paper metadata banner
  document.getElementById('adminPaperTitleText').textContent = paper.title;
  document.getElementById('adminPaperProvenanceText').textContent = `Source Booklet: ${paper.pdf_path || 'Booklet'} • Series ${paper.series || 'A'} • Max Marks ${paper.max_marks}`;
  document.getElementById('adminTotalQCount').textContent = paper.questions.length;

  const fullyVerifiedCount = paper.questions.filter(q => q.verificationStatus === 'fully_verified').length;
  document.getElementById('adminVerifiedRatio').textContent = `${fullyVerifiedCount} verified`;
  document.getElementById('adminPaperVerifiedCountBadge').textContent = `${paper.questions.length}/${paper.questions_count || paper.questions.length} Questions Loaded`;

  const isFull = fullyVerifiedCount === paper.questions.length;
  const statusBadge = document.getElementById('adminPaperStatusBadge');
  statusBadge.textContent = isFull ? "Fully Verified (Exact)" : "Verification Pending";
  statusBadge.className = isFull ? "badge badge-green" : "badge badge-amber";

  const pubBtn = document.getElementById('adminPublishBtn');
  if (pubBtn) pubBtn.style.display = 'block';

  renderAdminQuestionPalette();
  loadAdminQuestion(0);
}

function renderAdminQuestionPalette() {
  const grid = document.getElementById('adminQuestionListGrid');
  if (!grid || !APP_STATE.adminCurrentPaper) return;
  grid.innerHTML = '';

  const questions = APP_STATE.adminCurrentPaper.questions;
  questions.forEach((q, idx) => {
    const btn = document.createElement('button');
    const isVer = q.verificationStatus === 'fully_verified';
    btn.className = `admin-palette-btn ${isVer ? 'status-verified' : 'status-pending'} ${idx === APP_STATE.adminCurrentQIndex ? 'active' : ''}`;
    btn.textContent = idx + 1;
    btn.onclick = () => loadAdminQuestion(idx);
    grid.appendChild(btn);
  });
}

function loadAdminQuestion(idx) {
  if (!APP_STATE.adminCurrentPaper) return;
  const qList = APP_STATE.adminCurrentPaper.questions;
  if (idx < 0 || idx >= qList.length) return;

  APP_STATE.adminCurrentQIndex = idx;
  const q = qList[idx];

  document.getElementById('adminEditQHeading').textContent = `Editing Question ${idx + 1} of ${qList.length}`;
  document.getElementById('adminEditQSourceMeta').textContent = `Source Page ${q.sourcePage || 'N/A'} • ID: ${q.id}`;
  document.getElementById('adminEditPassage').value = q.passage || '';
  document.getElementById('adminEditStem').value = q.question || q.questionText || '';

  const opts = q.options || q.opts_dict || {};
  document.getElementById('adminEditOptA').value = opts.a || (Array.isArray(q.options) && (q.options.find(o => o.label === 'A') || {}).text) || '';
  document.getElementById('adminEditOptB').value = opts.b || (Array.isArray(q.options) && (q.options.find(o => o.label === 'B') || {}).text) || '';
  document.getElementById('adminEditOptC').value = opts.c || (Array.isArray(q.options) && (q.options.find(o => o.label === 'C') || {}).text) || '';
  document.getElementById('adminEditOptD').value = opts.d || (Array.isArray(q.options) && (q.options.find(o => o.label === 'D') || {}).text) || '';

  const ansKey = (q.correct_answer || (q.correctOption ? q.correctOption.toLowerCase() : 'a')).toLowerCase();
  document.getElementById('adminEditCorrectSelect').value = ['a', 'b', 'c', 'd'].includes(ansKey) ? ansKey : 'pending';
  document.getElementById('adminEditStatusSelect').value = q.verificationStatus || 'fully_verified';
  document.getElementById('adminEditImageUrl').value = q.image || '';
  document.getElementById('adminEditExplanation').value = q.explanation || '';

  document.getElementById('adminSaveStatusIndicator').textContent = '';

  // Update palette active button
  const btns = document.querySelectorAll('.admin-palette-btn');
  btns.forEach((b, i) => {
    if (i === idx) b.classList.add('active');
    else b.classList.remove('active');
  });
}

function adminJumpPrevQ() {
  if (APP_STATE.adminCurrentQIndex > 0) {
    loadAdminQuestion(APP_STATE.adminCurrentQIndex - 1);
  }
}

function adminJumpNextQ() {
  if (APP_STATE.adminCurrentPaper && APP_STATE.adminCurrentQIndex < APP_STATE.adminCurrentPaper.questions.length - 1) {
    loadAdminQuestion(APP_STATE.adminCurrentQIndex + 1);
  }
}

function adminSaveCurrentQ() {
  if (!APP_STATE.adminCurrentPaper) return;
  const idx = APP_STATE.adminCurrentQIndex;
  const q = APP_STATE.adminCurrentPaper.questions[idx];

  const stem = document.getElementById('adminEditStem').value.trim();
  const passage = document.getElementById('adminEditPassage').value.trim() || null;
  const optA = document.getElementById('adminEditOptA').value.trim();
  const optB = document.getElementById('adminEditOptB').value.trim();
  const optC = document.getElementById('adminEditOptC').value.trim();
  const optD = document.getElementById('adminEditOptD').value.trim();
  const ans = document.getElementById('adminEditCorrectSelect').value;
  const status = document.getElementById('adminEditStatusSelect').value;
  const img = document.getElementById('adminEditImageUrl').value.trim() || null;
  const exp = document.getElementById('adminEditExplanation').value.trim();

  q.question = stem;
  q.questionText = stem;
  q.passage = passage;
  q.image = img;
  q.options = { a: optA, b: optB, c: optC, d: optD };
  q.opts_dict = { a: optA, b: optB, c: optC, d: optD };
  q.correct_answer = ans;
  q.correctOption = ans.toUpperCase();
  q.verificationStatus = status;
  q.explanation = exp;

  saveAdminOverrides();

  document.getElementById('adminSaveStatusIndicator').textContent = `✅ Question ${idx + 1} saved successfully!`;
  renderAdminQuestionPalette();
}

function adminResetCurrentQ() {
  loadAdminQuestion(APP_STATE.adminCurrentQIndex);
}

function adminPublishPaper() {
  if (!APP_STATE.adminCurrentPaper) return;
  const paper = APP_STATE.adminCurrentPaper;

  paper.questions.forEach(q => {
    q.verificationStatus = 'fully_verified';
  });

  saveAdminOverrides();
  alert(`Paper "${paper.title}" is now verified and published for authentic CBT testing!`);
  onAdminPaperSelectionChange();
}

function exportAdminPaperJson() {
  if (!APP_STATE.adminCurrentPaper) return;
  const paper = APP_STATE.adminCurrentPaper;
  const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(paper, null, 2));
  const dlAnchorElem = document.createElement('a');
  dlAnchorElem.setAttribute("href", dataStr);
  dlAnchorElem.setAttribute("download", `${paper.paper_code || 'UPSC_CDS_PAPER'}_Verified.json`);
  dlAnchorElem.click();
}

function openAdminSourcePdf() {
  if (!APP_STATE.adminCurrentPaper || !APP_STATE.adminCurrentPaper.pdf_path) return;
  window.open(APP_STATE.adminCurrentPaper.pdf_path, '_blank');
}

function saveAdminOverrides() {
  try {
    const overrides = JSON.parse(localStorage.getItem('cds_pyq_admin_overrides') || '{}');
    if (APP_STATE.adminCurrentPaper) {
      overrides[APP_STATE.adminCurrentPaper.paper_id] = APP_STATE.adminCurrentPaper.questions;
    }
    localStorage.setItem('cds_pyq_admin_overrides', JSON.stringify(overrides));
  } catch (e) {
    console.warn("Could not save overrides to localStorage:", e);
  }
}

function applyAdminOverrides() {
  try {
    const raw = localStorage.getItem('cds_pyq_admin_overrides');
    if (!raw) return;
    const overrides = JSON.parse(raw);
    const pyqSource = window.CDS_PYQ_DATA || window.CDS_PYQ_PAPERS;
    if (!pyqSource) return;

    ['english', 'gs', 'math'].forEach(sub => {
      if (pyqSource[sub]) {
        pyqSource[sub].forEach(paper => {
          if (overrides[paper.paper_id]) {
            paper.questions = overrides[paper.paper_id];
          }
        });
      }
    });
  } catch (e) {
    console.warn("Could not apply overrides:", e);
  }
}

