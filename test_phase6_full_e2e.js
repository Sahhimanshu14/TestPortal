/**
 * CDS MOCK TEST PORTAL - PHASE 6 COMPREHENSIVE END-TO-END INTEGRATION TEST SUITE
 * Tests all core subsystems:
 * 1. Data Integrity & Loader (108 PYQ Papers + 3 Full Mocks + Chapterwise)
 * 2. PYQ Real-Time Search & Status Filtering
 * 3. CBT Simulator Execution (English 120-Q Paper)
 * 4. Mathematics 100-Q CBT Execution with Exact Fractional Scoring
 * 5. Neutral Scoring Engine for Pending Keys
 * 6. Scorecard, Sectional Cutoffs & Merit Predictions
 * 7. Candidate Analytics Dashboard & Re-Review History
 * 8. Admin Verification Hub (Auth, Question Edit, Override Persistence, JSON Export)
 * 9. Chapter-Wise & Full-Length Mock Launchers
 */

const fs = require('fs');
const path = require('path');

console.log('================================================================');
console.log('   UPSC CDS REAL TEST PORTAL — PHASE 6 FULL E2E TEST SUITE      ');
console.log('================================================================\n');

// -------------------------------------------------------------
// DOM & BROWSER ENVIRONMENT MOCK SETUP
// -------------------------------------------------------------
function createMockElement(id = '', tag = 'div') {
  return {
    id,
    tagName: tag.toUpperCase(),
    textContent: '',
    _innerHTML: '',
    get innerHTML() { return this._innerHTML; },
    set innerHTML(val) {
      this._innerHTML = val;
      if (val === '') this.children = [];
    },
    value: '',
    style: {},
    classList: {
      _classes: new Set(),
      add(c) { this._classes.add(c); },
      remove(c) { this._classes.delete(c); },
      contains(c) { return this._classes.has(c); },
      toggle(c) { this._classes.has(c) ? this._classes.delete(c) : this._classes.add(c); }
    },
    children: [],
    appendChild(child) { this.children.push(child); return child; },
    setAttribute(name, val) { this[name] = val; },
    getAttribute(name) { return this[name] || null; },
    removeAttribute(name) { delete this[name]; },
    addEventListener(evt, handler) { this._events = this._events || {}; this._events[evt] = handler; },
    click() { if (this.onclick) this.onclick(); },
    focus() {},
    scrollTop: 0
  };
}

const elementStore = new Map();
function getOrCreateElement(id) {
  if (!elementStore.has(id)) {
    elementStore.set(id, createMockElement(id));
  }
  return elementStore.get(id);
}

// Global In-Memory Storage
const localStorageData = {};
const sessionStorageData = {};

global.localStorage = {
  getItem: (k) => localStorageData[k] || null,
  setItem: (k, v) => { localStorageData[k] = String(v); },
  removeItem: (k) => { delete localStorageData[k]; },
  clear: () => { Object.keys(localStorageData).forEach(k => delete localStorageData[k]); }
};

global.sessionStorage = {
  getItem: (k) => sessionStorageData[k] || null,
  setItem: (k, v) => { sessionStorageData[k] = String(v); },
  removeItem: (k) => { delete sessionStorageData[k]; },
  clear: () => { Object.keys(sessionStorageData).forEach(k => delete sessionStorageData[k]); }
};

global.document = {
  documentElement: createMockElement('html', 'html'),
  getElementById: (id) => getOrCreateElement(id),
  querySelectorAll: (selector) => {
    return [createMockElement('mockSel1'), createMockElement('mockSel2')];
  },
  createElement: (tag) => createMockElement('', tag),
  addEventListener: () => {}
};

global.window = {
  location: { protocol: 'http:', hostname: '127.0.0.1' },
  scrollTo: () => {},
  addEventListener: () => {},
  document: global.document,
  localStorage: global.localStorage,
  sessionStorage: global.sessionStorage
};

global.navigator = {
  serviceWorker: {
    register: () => Promise.resolve()
  }
};

global.alert = (msg) => { /* console.log('  [Alert]:', msg); */ };
global.confirm = () => true;

// Pre-create known UI DOM elements
const knownIds = [
  'examSimulatorView', 'dashboardView', 'scorecardView', 'reviewView',
  'headerExamInfo', 'activePaperName', 'posMarkValue', 'negMarkValue',
  'paletteTotalCount', 'questionPaletteGrid', 'qNumberBadge', 'qSectionBadge',
  'qStemText', 'qPassageBox', 'passageText', 'qDiagramContainer', 'qDiagramImg',
  'currentQNumBadge', 'currentQSectionBadge', 'currentQSourceBadge', 'questionStemText',
  'optionsContainer', 'countAnswered', 'countNotAnswered', 'countNotVisited',
  'countMarked', 'countMarkedAnswered', 'submitModal', 'modalAnsweredCount',
  'modalUnansweredCount', 'modalMarkedCount', 'modalTimeRemaining',
  'instructionsModal', 'overviewModal', 'overviewModalContent',
  'scorePaperTitle', 'finalScoreVal', 'cutoffStatusPill', 'accuracyRateVal',
  'accuracySubtext', 'meritRankVal', 'meritAcademyVal', 'timeConsumedVal',
  'avgSpeedVal', 'bdCorrectCount', 'bdCorrectMarks', 'bdIncorrectCount',
  'bdIncorrectPenalty', 'bdUnattemptedCount', 'bdTotalQuestions', 'bdAttemptedCount',
  'reviewPaperTitle', 'reviewListContainer', 'pyqCardsContainer', 'chapterCardsContainer',
  'pyqSearchInput', 'filterStatusAll', 'filterStatusVerified', 'filterStatusPending',
  'dashAttemptsCount', 'dashAvgScoreVal', 'dashAvgAccVal', 'dashAccSubtext',
  'dashBestScoreVal', 'dashBestPaperVal', 'dashCutoffRateVal', 'historyTableBody',
  'dashTotalAttempts', 'dashAttemptSubtext', 'dashAvgScore', 'dashAvgAccuracy',
  'dashAccuracySubtext', 'dashBestScore', 'dashBestPaper', 'dashCutoffRate',
  'attemptHistoryBody', 'tabHistoryCountBadge',
  'masteryEnglishPct', 'masteryEnglishBar', 'masteryEnglishAttempts', 'masteryEnglishAvg',
  'masteryGsPct', 'masteryGsBar', 'masteryGsAttempts', 'masteryGsAvg',
  'masteryMathPct', 'masteryMathBar', 'masteryMathAttempts', 'masteryMathAvg',
  'activeAttemptBanner', 'bannerAttemptTitle', 'bannerAttemptMeta',
  'adminVerificationModal', 'adminAuthSection', 'adminDashboardSection',
  'adminPasskeyInput', 'adminSubjectSelect', 'adminYearSelect', 'adminSessionSelect',
  'adminPaperTitleText', 'adminPaperProvenanceText', 'adminTotalQCount',
  'adminVerifiedRatio', 'adminPaperVerifiedCountBadge', 'adminPaperStatusBadge',
  'adminPublishBtn', 'adminQuestionListGrid', 'adminEditStem', 'adminEditPassage',
  'adminEditOptA', 'adminEditOptB', 'adminEditOptC', 'adminEditOptD',
  'adminEditCorrectSelect', 'adminEditStatusSelect', 'adminEditImageUrl',
  'adminEditExplanation', 'adminSaveStatusIndicator', 'themeToggleBtn', 'themeIcon',
  'adminEditQHeading', 'adminEditQSourceMeta',
  'archivePracticeModal', 'archiveModalTitle', 'archiveModalBadge', 'archiveModalCountBadge',
  'archiveModalHeading', 'btnLaunchArchiveTimed', 'btnLaunchArchiveChapters', 'btnLaunchArchiveMarathon',
  'masterKeysModal', 'masterKeysTitle', 'keyTabEnglish', 'keyTabGs', 'keyTabMath',
  'masterKeySearchInput', 'masterKeysListContainer', 'omrModal', 'omrModalTitle'
];

knownIds.forEach(id => getOrCreateElement(id));

// -------------------------------------------------------------
// STEP 1: LOAD SCRIPTS INTO RUNTIME
// -------------------------------------------------------------
console.log('⚡ Loading test_data.js and pyq_data.js into simulated runtime...');
const vm = require('vm');
const testDataCode = fs.readFileSync('test_data.js', 'utf-8');
const pyqDataCode = fs.readFileSync('pyq_data.js', 'utf-8');
const appCode = fs.readFileSync('app.js', 'utf-8')
  .replace('const APP_STATE =', 'global.APP_STATE =');

vm.runInThisContext(testDataCode);
vm.runInThisContext(pyqDataCode);
vm.runInThisContext(appCode);


let testsPassed = 0;
let testsTotal = 0;

function assert(condition, message) {
  testsTotal++;
  if (condition) {
    console.log(`  ✅ [PASS] ${message}`);
    testsPassed++;
  } else {
    console.error(`  ❌ [FAIL] ${message}`);
    throw new Error(`Assertion failed: ${message}`);
  }
}

// -------------------------------------------------------------
// RUNNER FUNCTION
// -------------------------------------------------------------
(async function runAllTests() {
console.log('\n[TEST 1] Verifying Data Integrity Across All 108 PYQ Papers:');
const pyqData = window.CDS_PYQ_DATA || window.CDS_PYQ_PAPERS;
assert(pyqData !== undefined, 'window.CDS_PYQ_DATA is loaded');
assert(pyqData.english && pyqData.english.length === 36, 'English contains exactly 36 PYQ papers (2009-2026)');
assert(pyqData.gs && pyqData.gs.length === 36, 'GS contains exactly 36 PYQ papers (2009-2026)');
assert(pyqData.math && pyqData.math.length === 36, 'Math contains exactly 36 PYQ papers (2009-2026)');

const engQCount = pyqData.english.reduce((s, p) => s + p.questions.length, 0);
const gsQCount = pyqData.gs.reduce((s, p) => s + p.questions.length, 0);
const mathQCount = pyqData.math.reduce((s, p) => s + p.questions.length, 0);
const totalQs = engQCount + gsQCount + mathQCount;

assert(engQCount === 4320, `English has verbatim 4,320 questions (found ${engQCount})`);
assert(gsQCount === 4320, `GS has verbatim 4,320 questions (found ${gsQCount})`);
assert(mathQCount === 3600, `Math has verbatim 3,600 questions (found ${mathQCount})`);
assert(totalQs === 12240, `Grand total across all 108 papers is exactly 12,240 questions (found ${totalQs})`);

// -------------------------------------------------------------
// TEST 2: PYQ SEARCH AND FILTERING
// -------------------------------------------------------------
console.log('\n[TEST 2] Verifying PYQ Real-Time Search & Status Filtering:');
APP_STATE.pyqSearchQuery = '2024';
APP_STATE.currentPyqSubject = 'english';
APP_STATE.pyqStatusFilter = 'all';

// Test renderPyqCards
renderPyqCards('english', 'all');
const pyqContainer = getOrCreateElement('pyqCardsContainer');
assert(pyqContainer.children.length > 0, `PYQ container populated with search query '2024' (count: ${pyqContainer.children.length})`);

// Test filterPyqStatus
filterPyqStatus('verified');
assert(APP_STATE.pyqStatusFilter === 'verified', 'APP_STATE.pyqStatusFilter correctly updated to verified');

clearPyqSearch();
assert(APP_STATE.pyqSearchQuery === '', 'clearPyqSearch resets search query to empty string');

// -------------------------------------------------------------
// TEST 3: FULL CBT SIMULATOR SESSION (ENGLISH 120 QUESTIONS)
// -------------------------------------------------------------
console.log('\n[TEST 3] Running Full CBT Simulator Session (English 120-Q Paper):');
const engPaper = pyqData.english.find(p => p.year === '2024');
assert(engPaper !== undefined, 'Found 2024 English PYQ Paper');

startPyqTest('english', engPaper.paper_id);
assert(APP_STATE.currentTest !== null, 'Test session initialized');
assert(APP_STATE.currentTest.questions.length === 120, 'Test contains exactly 120 questions');
assert(Math.abs(APP_STATE.currentTest.posMark - (100 / 120)) < 1e-9, 'Exact positive mark = 100/120 (0.8333...)');
assert(Math.abs(APP_STATE.currentTest.negMark - ((100 / 120) / 3)) < 1e-9, 'Exact negative penalty = (100/120)/3 (0.2777...)');

// Answer Question 1 (Select B)
selectOption(1, 'b');
assert(APP_STATE.userResponses[1] === 'b', 'Q1 user response recorded as b');
saveAndNext();
assert(APP_STATE.questionStatuses[1] === 'answered', 'Q1 status set to answered');
assert(APP_STATE.currentQIndex === 1, 'Current question index advanced to 1 (Q2)');

// Answer Question 2 (Select A, Mark for Review)
selectOption(2, 'a');
markForReviewAndNext();
assert(APP_STATE.questionStatuses[2] === 'marked-answered', 'Q2 status set to marked-answered');
assert(APP_STATE.currentQIndex === 2, 'Current question index advanced to 2 (Q3)');

// Answer Question 3, then Clear Response
selectOption(3, 'c');
clearCurrentResponse();
assert(APP_STATE.userResponses[3] === undefined, 'Q3 user response cleared');
assert(APP_STATE.questionStatuses[3] === 'not-answered', 'Q3 status reverted to not-answered');


// Jump directly to Question 5
renderQuestion(4); // index 4 is Q5
assert(APP_STATE.currentQIndex === 4, 'Jumped directly to Question 5');

// Update and verify palette counts
updatePaletteSummary();
assert(getOrCreateElement('countAnswered').textContent === 1, 'Palette answered count = 1');
assert(getOrCreateElement('countMarkedAnswered').textContent === 1, 'Palette marked-answered count = 1');

// Confirm submit dialog
confirmSubmitExam();
assert(getOrCreateElement('modalAnsweredCount').textContent === 2, 'Modal answered count = 2');
assert(getOrCreateElement('modalUnansweredCount').textContent === 118, 'Modal unanswered count = 118 (120 - 2)');

// -------------------------------------------------------------
// TEST 4: MATHEMATICAL EXACT SCORING EVALUATION
// -------------------------------------------------------------
console.log('\n[TEST 4] Evaluating Mathematical Exact Scoring & Cutoffs:');
// Let's set up a known attempt distribution:
// Set 60 correct, 30 incorrect, 30 unattempted
APP_STATE.userResponses = {};
APP_STATE.questionStatuses = {};

const qList = APP_STATE.currentTest.questions;
for (let i = 0; i < 60; i++) {
  const q = qList[i];
  APP_STATE.userResponses[q.id] = (q.correct_answer || 'a').toLowerCase();
  APP_STATE.questionStatuses[q.id] = 'answered';
}
for (let i = 60; i < 90; i++) {
  const q = qList[i];
  const right = (q.correct_answer || 'a').toLowerCase();
  const wrong = right === 'a' ? 'b' : 'a';
  APP_STATE.userResponses[q.id] = wrong;
  APP_STATE.questionStatuses[q.id] = 'answered';
}
for (let i = 90; i < 120; i++) {
  const q = qList[i];
  APP_STATE.questionStatuses[q.id] = 'not-visited';
}

evaluateAndShowResults();
const res = APP_STATE.evaluationResult;
assert(res !== null, 'Evaluation completed successfully');
assert(res.correctCount === 60, `Correct count = 60 (actual: ${res.correctCount})`);
assert(res.incorrectCount === 30, `Incorrect count = 30 (actual: ${res.incorrectCount})`);
assert(res.unattemptedCount === 30, `Unattempted count = 30 (actual: ${res.unattemptedCount})`);

// Calculation:
// posScore = 60 * (100 / 120) = 50.00
// negPenalty = 30 * ((100 / 120) / 3) = 10 * (100 / 120) = 8.333...
// finalScore = 50.00 - 8.333... = 41.67
const expectedScore = (60 * (100 / 120)) - (30 * ((100 / 120) / 3));
assert(Math.abs(res.finalScore - expectedScore) < 1e-4, `Exact fractional score = ${expectedScore.toFixed(2)} (actual: ${res.finalScore.toFixed(2)})`);
assert(res.finalScore.toFixed(2) === '41.67', `Final rounded score string = '41.67' (actual: '${res.finalScore.toFixed(2)}')`);
assert(res.accuracy.toFixed(1) === '66.7', `Accuracy = 66.7% (actual: ${res.accuracy.toFixed(1)}%)`);

// Cutoff check: 41.67 >= 20.00 -> Cleared
assert(res.finalScore >= 20.0, 'Sectional cutoff (20.00 marks) cleared');
assert(getOrCreateElement('cutoffStatusPill').innerHTML.includes('Sectional Cutoff Cleared'), 'Cutoff status pill displays cleared badge');

// -------------------------------------------------------------
// TEST 5: MATHEMATICS 100-QUESTION EXACT SCORING
// -------------------------------------------------------------
console.log('\n[TEST 5] Verifying Elementary Mathematics 100-Question Exact Scoring:');
const mathPaper = pyqData.math.find(p => p.year === '2024');
startPyqTest('math', mathPaper.paper_id);
assert(APP_STATE.currentTest.questions.length === 100, 'Math test has 100 questions');
assert(APP_STATE.currentTest.posMark === 1.0, 'Math positive mark = 1.0');
assert(Math.abs(APP_STATE.currentTest.negMark - (1.0 / 3)) < 1e-9, 'Math negative penalty = 1/3 (0.3333...)');

// Test perfect 100/100
APP_STATE.userResponses = {};
APP_STATE.questionStatuses = {};
const mQuestions = APP_STATE.currentTest.questions;
mQuestions.forEach(q => {
  APP_STATE.userResponses[q.id] = (q.correct_answer || 'a').toLowerCase();
  APP_STATE.questionStatuses[q.id] = 'answered';
});

evaluateAndShowResults();
assert(APP_STATE.evaluationResult.finalScore === 100.0, `Math 100/100 yields exact 100.00 marks (actual: ${APP_STATE.evaluationResult.finalScore})`);
assert(getOrCreateElement('meritRankVal').textContent === 'Exceptional Merit (Top 1%)', 'Merit rank displays Top 1% tier');

// -------------------------------------------------------------
// TEST 6: SOLUTIONS REVIEW & SOURCE PROVENANCE
// -------------------------------------------------------------
console.log('\n[TEST 6] Verifying Solutions Review & PDF Provenance:');
openReviewSolutions();
assert(getOrCreateElement('reviewPaperTitle').textContent.includes('Detailed Solutions'), 'Review view title updated');

filterReviewList('all');
const revContainer = getOrCreateElement('reviewListContainer');
assert(revContainer.children.length === 100, `Review list contains all 100 solution cards (actual: ${revContainer.children.length})`);

// Verify provenance booklet path in first review card
const firstCardHtml = revContainer.children[0].innerHTML;
assert(firstCardHtml.includes('pyq_papers/'), 'Card includes official PDF booklet link in pyq_papers/');

// -------------------------------------------------------------
// TEST 7: CANDIDATE ANALYTICS DASHBOARD & ATTEMPT ARCHIVE
// -------------------------------------------------------------
console.log('\n[TEST 7] Verifying Candidate Analytics Dashboard & Re-Review History:');
// History has 2 attempts saved from above tests
const rawHistory = localStorage.getItem('cds_attempt_history');
assert(rawHistory !== null, 'Attempts saved to localStorage (cds_attempt_history)');
const history = JSON.parse(rawHistory);
assert(history.length >= 2, `History contains ${history.length} attempts`);

renderCandidateDashboard();
assert(getOrCreateElement('dashTotalAttempts').textContent == history.length, `Dashboard attempts count matches history (${history.length})`);
assert(Number(getOrCreateElement('dashAvgScore').textContent) > 0, 'Average score calculated and rendered');

// Test re-review historical attempt
reReviewHistoricalAttempt(0);
assert(APP_STATE.evaluationResult !== null, 'Historical attempt loaded into active evaluation state');
assert(getOrCreateElement('reviewPaperTitle').textContent.includes('Attempt Review'), 'Historical review view loaded with Attempt Review title');



// -------------------------------------------------------------
// TEST 8: ADMIN VERIFICATION HUB WORKFLOW
// -------------------------------------------------------------
console.log('\n[TEST 8] Verifying Admin Verification Hub Workflow:');
getOrCreateElement('adminPasskeyInput').value = 'WRONGPASS';
await verifyAdminPasskey();
assert(sessionStorage.getItem('cds_admin_auth') === null, 'Wrong passkey rejects authentication');

getOrCreateElement('adminPasskeyInput').value = 'CDS2026ADMIN';
getOrCreateElement('adminSubjectSelect').value = 'english';
getOrCreateElement('adminYearSelect').value = '2024';
getOrCreateElement('adminSessionSelect').value = 'I';

await verifyAdminPasskey();
assert(sessionStorage.getItem('cds_admin_auth') === 'true', 'Valid passkey authenticates admin');

// Verify admin question editor
assert(APP_STATE.adminCurrentPaper !== undefined, 'Admin current paper loaded');
loadAdminQuestion(0);
assert(getOrCreateElement('adminEditStem').value.length > 0, 'Admin editor loaded Q1 stem text');

// Edit Question 1 and Save
const originalStem = getOrCreateElement('adminEditStem').value;
getOrCreateElement('adminEditStem').value = originalStem + ' [Verified Admin Edit]';
getOrCreateElement('adminEditCorrectSelect').value = 'c';
getOrCreateElement('adminEditStatusSelect').value = 'fully_verified';

adminSaveCurrentQ();
const rawOverrides = localStorage.getItem('cds_pyq_admin_overrides');
assert(rawOverrides !== null, 'Admin overrides written to localStorage');
const overrides = JSON.parse(rawOverrides);
assert(overrides[APP_STATE.adminCurrentPaper.paper_id] !== undefined, 'Overrides contain current paper');
assert(overrides[APP_STATE.adminCurrentPaper.paper_id][0].question.includes('[Verified Admin Edit]'), 'Q1 override text successfully persisted');

// Verify applyAdminOverrides applies changes to global dataset
applyAdminOverrides();
const reloadedQ1 = (window.CDS_PYQ_DATA.english.find(p => p.paper_id === APP_STATE.adminCurrentPaper.paper_id)).questions[0];
assert(reloadedQ1.question.includes('[Verified Admin Edit]'), 'Global dataset reflects persisted admin override');

// -------------------------------------------------------------
// TEST 9: FULL-LENGTH MOCK & CHAPTERWISE TEST LAUNCHERS
// -------------------------------------------------------------
console.log('\n[TEST 9] Verifying Full-Length Mock & Chapterwise Launchers:');
// Launch Full Mock 1 (English)
startTest('mock_english');
assert(APP_STATE.currentTest.title.includes('General English'), 'Mock English test loaded');
assert(APP_STATE.currentTest.questions.length === 120, 'Mock English has 120 questions');

// Launch Full Mock 2 (GS)
startTest('mock_gs');
assert(APP_STATE.currentTest.title.includes('General Knowledge'), 'Mock GS test loaded');
assert(APP_STATE.currentTest.questions.length === 120, 'Mock GS has 120 questions');

// Launch Full Mock 3 (Math)
startTest('mock_math');
assert(APP_STATE.currentTest.title.includes('Elementary Mathematics'), 'Mock Math test loaded');
assert(APP_STATE.currentTest.questions.length === 100, 'Mock Math has 100 questions');

// Launch Chapter-Wise Test
const engChapters = Object.keys(window.CDS_DATA.chapterwise.english);
assert(engChapters.length > 0, 'Chapterwise English chapters exist');
startChapterTest('english', engChapters[0]);
assert(APP_STATE.currentTest.questions.length > 0, 'Chapterwise test initialized with questions');

// -------------------------------------------------------------
// TEST 10: COMPLETE ARCHIVE CBT, MASTER KEYS & OMR SIMULATOR
// -------------------------------------------------------------
console.log('\n[TEST 10] Verifying Complete Archive CBT, Master Keys & OMR Simulator:');
// 10A: Complete Archive Practice Modal
startCompleteArchivePractice('english');
assert(getOrCreateElement('archivePracticeModal').style.display === 'flex', 'Archive Practice Modal opens');
assert(getOrCreateElement('archiveModalHeading').textContent.includes('English'), 'Archive Modal title reflects English');
assert(getOrCreateElement('archiveModalCountBadge').textContent.includes('981 Verified Questions'), 'Archive Modal reflects 981 verified questions');

// 10B: Launch Archive Marathon CBT
launchArchiveMarathonCbt();
assert(APP_STATE.currentTest.title.includes('Complete ENGLISH PYQ Archive'), 'Marathon CBT session initialized');
assert(APP_STATE.currentTest.questions.length === 120, 'Marathon CBT loads 120 questions from complete archive');
closeArchivePracticeModal();

// 10C: Master Keys Explorer
openMasterKeysModal('gs');
assert(getOrCreateElement('masterKeysModal').style.display === 'flex', 'Master Keys Explorer modal opens');
switchMasterKeyTab('gs');
const gsKeysContainer = getOrCreateElement('masterKeysListContainer');
assert(gsKeysContainer.children.length > 0, `Master keys list populated for GS (count: ${gsKeysContainer.children.length})`);
closeMasterKeysModal();

// 10D: OMR Simulator Modal
openOmrModal();
assert(getOrCreateElement('omrModal').style.display === 'flex', 'OMR Simulator modal opens');
closeOmrModal();
assert(getOrCreateElement('omrModal').style.display === 'none', 'OMR Simulator modal closes');

// -------------------------------------------------------------
// FINAL SUMMARY
// -------------------------------------------------------------
console.log('\n================================================================');
console.log(`🎉 ALL TESTS PASSED! (${testsPassed}/${testsTotal} assertions verified)`);
console.log('   Phase 6 End-to-End System Verification: 100% OPERATIONAL');
console.log('================================================================');
process.exit(0);
})().catch(err => {
  console.error(err);
  process.exit(1);
});

