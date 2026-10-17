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
};

// ==========================================================================
// INITIALIZATION & EVENT LISTENERS
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  renderChapterCards('english');
  renderPyqCards('math', 'all');
  setupKeyboardShortcuts();
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

// Dashboard Tabs
function switchDashboardTab(tab) {
  const tabFull = document.getElementById('tabFullMock');
  const tabChap = document.getElementById('tabChapter');
  const tabPyq = document.getElementById('tabPyq');
  const paneFull = document.getElementById('paneFullMock');
  const paneChap = document.getElementById('paneChapter');
  const panePyq = document.getElementById('panePyq');

  // Reset all
  tabFull.classList.remove('active');
  tabChap.classList.remove('active');
  if (tabPyq) tabPyq.classList.remove('active');
  paneFull.classList.remove('active');
  paneChap.classList.remove('active');
  if (panePyq) panePyq.classList.remove('active');

  if (tab === 'full') {
    tabFull.classList.add('active');
    paneFull.classList.add('active');
  } else if (tab === 'chapter') {
    tabChap.classList.add('active');
    paneChap.classList.add('active');
  } else if (tab === 'pyq') {
    if (tabPyq) tabPyq.classList.add('active');
    if (panePyq) panePyq.classList.add('active');
    renderPyqCards(APP_STATE.currentPyqSubject, APP_STATE.currentPyqYear);
  }
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
  }
  renderPyqCards(APP_STATE.currentPyqSubject, year);
}

function renderPyqCards(subject, yearFilter) {
  const container = document.getElementById('pyqCardsContainer');
  if (!container) return;
  container.innerHTML = '';

  if (!window.CDS_PYQ_DATA || !window.CDS_PYQ_DATA[subject]) {
    container.innerHTML = `
      <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--text-muted);">
        <p style="font-size: 16px;">Loading PYQ Papers archive...</p>
      </div>
    `;
    return;
  }

  const papers = window.CDS_PYQ_DATA[subject];
  const filtered = (yearFilter === 'all') 
    ? papers 
    : papers.filter(p => p.year === yearFilter);

  // Update counter in UI banner if present
  const countEl = document.getElementById('pyqTotalPapersCount');
  if (countEl) countEl.textContent = papers.length;

  if (filtered.length === 0) {
    container.innerHTML = `
      <div style="grid-column: 1/-1; text-align: center; padding: 48px; background: var(--bg-tertiary); border-radius: var(--radius-lg);">
        <h4 style="font-size: 18px; margin-bottom: 8px;">No papers found for Year ${yearFilter}</h4>
        <p style="color: var(--text-muted); font-size: 14px; margin-bottom: 16px;">Try selecting "All Years" to view complete 2009–2026 UPSC CDS papers archive.</p>
        <button class="btn btn-secondary btn-sm" onclick="filterPyqYear('all', null)">View All Years</button>
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

    const topicsHtml = (p.sections || []).map(sec => `<span class="pyq-topic-tag">${sec}</span>`).join('');

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
  if (!window.CDS_PYQ_DATA || !window.CDS_PYQ_DATA[subject]) {
    alert("Year-wise PYQ data not found!");
    return;
  }
  const paper = window.CDS_PYQ_DATA[subject].find(p => p.paper_id === paperId);
  if (!paper || !paper.questions || paper.questions.length === 0) {
    alert("Selected question paper is not loaded!");
    return;
  }

  setupTestSession({
    title: paper.title,
    subject: `${paper.subject_title} (${paper.year} PYQ)`,
    questions: paper.questions,
    posMark: paper.pos_mark,
    negMark: paper.neg_mark,
    duration: paper.duration_minutes * 60
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

  setupTestSession({
    title,
    subject,
    questions,
    posMark,
    negMark,
    duration
  });
}

function startChapterTest(subject, chapterKey) {
  const ch = window.CDS_DATA.chapterwise[subject][chapterKey];
  if (!ch || !ch.questions || ch.questions.length === 0) return;

  const isMath = subject === 'math';
  const posMark = isMath ? 1.0 : 0.833;
  const negMark = isMath ? 0.333 : 0.277;
  // Dynamic duration: 1.2 min per question
  const duration = Math.max(900, ch.questions.length * 75);

  // Normalize IDs 1..N
  const questions = ch.questions.map((q, idx) => ({
    ...q,
    id: idx + 1,
    section: ch.title
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
  document.getElementById('questionStemText').textContent = q.question;

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
}

function markForReviewAndNext() {
  const q = APP_STATE.currentTest.questions[APP_STATE.currentQIndex];
  const hasAnswer = Boolean(APP_STATE.userResponses[q.id]);

  APP_STATE.questionStatuses[q.id] = hasAnswer ? 'marked-answered' : 'marked';
  renderPalette();
  updatePaletteSummary();
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

    const statusBadge = item.status === 'correct' 
      ? '<span class="badge badge-green">CORRECT (+0.833)</span>' 
      : (item.status === 'incorrect' ? '<span class="badge badge-rose" style="background:rgba(244,63,94,0.15); color:#f43f5e;">INCORRECT (-0.277)</span>' : '<span class="badge badge-amber">UNATTEMPTED (0)</span>');

    const optKeys = ['a', 'b', 'c', 'd'];
    let optsHtml = '';
    optKeys.forEach(k => {
      const isCorrect = k === item.correctChoice;
      const isUserWrong = item.userChoice === k && !isCorrect;
      const cls = isCorrect ? 'is-correct' : (isUserWrong ? 'is-user-wrong' : '');
      const mark = isCorrect ? '✅ Official UPSC Answer' : (isUserWrong ? '❌ Your Selection' : '');

      optsHtml += `
        <div class="review-opt ${cls}">
          <span><b>(${k.toUpperCase()})</b> ${q.options[k]}</span>
          ${mark ? `<span style="font-size:11.5px;">${mark}</span>` : ''}
        </div>
      `;
    });

    card.innerHTML = `
      <div class="review-card-top">
        <div>
          <b>Question ${q.id}</b> • <span style="font-size:12px; color:var(--text-muted);">${q.section || 'General'}</span>
        </div>
        ${statusBadge}
      </div>
      <div class="review-card-title">${q.question}</div>
      <div class="review-opts">
        ${optsHtml}
      </div>
      <div class="review-explanation">
        <b>Constitutional / Official Rationale:</b><br/>
        ${q.explanation || `According to the official UPSC Combined Defence Services examination answer key, Option (${item.correctChoice.toUpperCase()}) is the correct response.`}
      </div>
    `;
    container.appendChild(card);
  });
}

// ==========================================================================
// KEYBOARD SHORTCUTS
// ==========================================================================

function setupKeyboardShortcuts() {
  document.addEventListener('keydown', e => {
    // Only in exam simulator
    if (document.getElementById('examSimulatorView').style.display !== 'block') return;

    if (e.key === 'ArrowRight' || e.key === 'n') {
      navigateQuestion(1);
    } else if (e.key === 'ArrowLeft' || e.key === 'p') {
      navigateQuestion(-1);
    } else if (e.key === '1' || e.key === 'a') {
      const q = APP_STATE.currentTest.questions[APP_STATE.currentQIndex];
      selectOption(q.id, 'a');
    } else if (e.key === '2' || e.key === 'b') {
      const q = APP_STATE.currentTest.questions[APP_STATE.currentQIndex];
      selectOption(q.id, 'b');
    } else if (e.key === '3' || e.key === 'c') {
      const q = APP_STATE.currentTest.questions[APP_STATE.currentQIndex];
      selectOption(q.id, 'c');
    } else if (e.key === '4' || e.key === 'd') {
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

function toggleNavigatorPopup() {
  const popup = document.getElementById('navigatorPopup');
  if (!popup) return;
  const isHidden = popup.style.display === 'none' || popup.style.display === '';
  popup.style.display = isHidden ? 'block' : 'none';
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
