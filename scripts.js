const $ = (sel) => document.querySelector(sel);
const cfg = { writingTimeMinutes: 60, minWordsTaskA: 80, minWordsTaskB: 200 };
const state = { token: null, user: null };

// Theme handling with persistence
const themeStorageKey = 'tef_theme';
function applyTheme(theme){
  document.documentElement.setAttribute('data-theme', theme);
  const btn = document.getElementById('themeToggleBtn');
  const label = document.getElementById('themeModeLabel');
  if(btn && label){
    // Show the TARGET mode (what you'll switch to), not the current mode
    if(theme === 'dark'){
      // Currently dark -> offer to switch to Light Mode
      btn.classList.remove('btn-outline-light');
      btn.classList.add('btn-light');
      btn.innerHTML = '<i class="bi bi-sun-fill me-2"></i><span id="themeModeLabel">Light Mode</span>';
    } else {
      // Currently light -> offer to switch to Dark Mode
      btn.classList.remove('btn-light');
      btn.classList.add('btn-outline-light');
      btn.innerHTML = '<i class="bi bi-moon-stars-fill me-2"></i><span id="themeModeLabel">Dark Mode</span>';
    }
  }
  localStorage.setItem(themeStorageKey, theme);
}

(function initTheme(){
  const saved = localStorage.getItem(themeStorageKey);
  const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  const theme = saved || (prefersDark ? 'dark' : 'light');
  applyTheme(theme);
  const btn = document.getElementById('themeToggleBtn');
  if(btn){
    btn.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme') || 'light';
      const next = current === 'dark' ? 'light' : 'dark';
      applyTheme(next);
    });
  }
})();

function authHeader(){ return state.token ? { 'Authorization': `Bearer ${state.token}` } : {}; }
function showOnly(id){
  ['authScreen','startScreen','setupScreen','writingScreen','evaluationScreen','dashboardScreen'].forEach(x=>{
    const el = document.getElementById(x);
    if(!el) return; 
    if(x===id) {
      el.classList.remove('d-none');
      // Add fade in animation
      el.classList.add('animate-fade-in');
    } else {
      el.classList.add('d-none');
      el.classList.remove('animate-fade-in');
    }
  });
}

// Clear all auth form fields (login and registration)
function clearAuthForms(){
  ['loginUsername','loginPassword','regUsername','regPassword','regPassword2'].forEach(id => {
    const el = document.getElementById(id);
    if(el){ el.value = ''; }
  });
}

// Logout handler
function logOut(){
  state.token = null;
  state.user = null;
  localStorage.removeItem('token');
  // Clear all auth inputs
  clearAuthForms();
  // Hide navbar buttons meant for authenticated users
  const navHomeBtnEl = document.getElementById('navHomeBtn');
  if(navHomeBtnEl){ navHomeBtnEl.classList.add('d-none'); }
  const logoutBtnEl = document.getElementById('logoutBtn');
  if(logoutBtnEl){ logoutBtnEl.classList.add('d-none'); }
  // Reset writing flow if present
  if(typeof resetWritingFlow === 'function') resetWritingFlow();
  // Go back to auth screen
  showOnly('authScreen');
  if(typeof showAuth === 'function') showAuth('login');
}

// Load config from backend
fetch('/api/config').then(r => r.json()).then(data => {
  cfg.writingTimeMinutes = data.writingTimeMinutes;
  cfg.minWordsTaskA = data.minWordsTaskA;
  cfg.minWordsTaskB = data.minWordsTaskB;
  $('#appVersion').textContent = `v${data.version}`;
}).catch(()=>{});

// Global nav Home button -> Start screen (only when authenticated)
const navHome = document.getElementById('navHomeBtn');
if(navHome){ navHome.addEventListener('click', () => { if(state.token){ showOnly('startScreen'); } else { showOnly('authScreen'); } }); }
const logoutBtn = document.getElementById('logoutBtn');
if(logoutBtn){ logoutBtn.addEventListener('click', logOut); }

// Always land on login on app start (no auto-login)
(function initAuth(){
  state.token = null;
  localStorage.removeItem('token');
  showOnly('authScreen');
  showAuth('login');
  // Ensure Home stays hidden until logged in
  const navHomeBtnEl = document.getElementById('navHomeBtn');
  if(navHomeBtnEl){ navHomeBtnEl.classList.add('d-none'); }
  const logoutBtnElInit = document.getElementById('logoutBtn');
  if(logoutBtnElInit){ logoutBtnElInit.classList.add('d-none'); }
})();

// Login/Register toggle
function showAuth(mode){
  const login = document.getElementById('authLogin');
  const register = document.getElementById('authRegister');
  // Always clear fields when switching views
  clearAuthForms();
  if(mode === 'login'){ login.classList.remove('d-none'); register.classList.add('d-none'); }
  else { register.classList.remove('d-none'); login.classList.add('d-none'); }
}
document.addEventListener('click', (e)=>{
  if(e.target && e.target.id === 'toRegisterLink'){ e.preventDefault(); showAuth('register'); }
  if(e.target && e.target.id === 'toLoginLink'){ e.preventDefault(); showAuth('login'); }
});

// Auth handlers
$('#loginBtn').onclick = async () => {
  const body = { username: $('#loginUsername').value.trim(), password: $('#loginPassword').value };
  const r = await fetch('/api/auth/login', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(body)});
  const j = await r.json();
  if(r.ok && j?.access_token){
    state.token = j.access_token; localStorage.setItem('token', state.token);
    const me = await fetch('/api/me', { headers: { ...authHeader() }}).then(x=>x.json());
    state.user=me;
    const navHomeBtnEl = document.getElementById('navHomeBtn');
    if(navHomeBtnEl){ navHomeBtnEl.classList.remove('d-none'); }
    const logoutBtnEl = document.getElementById('logoutBtn');
    if(logoutBtnEl){ logoutBtnEl.classList.remove('d-none'); }
    showOnly('startScreen');
    loadDashboard();
  } else { alert(j?.detail || 'Login failed'); }
};
$('#registerBtn').onclick = async () => {
  const username = $('#regUsername').value.trim();
  const password = $('#regPassword').value;
  const password2 = ($('#regPassword2') ? $('#regPassword2').value : '');
  if(!username || !password){ alert('Username and password are required.'); return; }
  if(password !== password2){ alert('Passwords do not match.'); return; }
  const body = { username, password };
  const r = await fetch('/api/auth/register', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(body)});
  const j = await r.json();
  if(r.ok){ alert('Account created. Please login.'); showAuth('login'); } else { alert(j?.detail || 'Registration failed'); }
};

// Nav
function resetWritingFlow(){
  // Clear questions
  const qa = $('#taskAQuestion');
  const qb = $('#taskBQuestion');
  if(qa) qa.value = '';
  if(qb) qb.value = '';

  // Clear responses
  const ra = $('#taskAResponse');
  const rb = $('#taskBResponse');
  if(ra) ra.value = '';
  if(rb) rb.value = '';

  // Reset displays and counters
  const qda = $('#taskAQuestionDisplay');
  const qdb = $('#taskBQuestionDisplay');
  if(qda) qda.textContent = '';
  if(qdb) qdb.textContent = '';
  const wca = $('#wordCountA');
  const wcb = $('#wordCountB');
  if(wca) wca.textContent = '0';
  if(wcb) wcb.textContent = '0';

  // Disable buttons
  const beginBtn = $('#beginWritingBtn');
  if(beginBtn) beginBtn.disabled = true;
  const submitBtn = $('#submitBoth');
  if(submitBtn) submitBtn.disabled = true;

  // Stop and reset timer
  if(timerId){ clearInterval(timerId); timerId = null; }
  endAt = null;
  const timerEl = $('#timer');
  if(timerEl) timerEl.textContent = '--:--:--';

  // Ensure derived states stay consistent
  if(typeof updateBeginEnabled === 'function') updateBeginEnabled();
  if(typeof updateCounts === 'function') updateCounts();
  if(typeof updateSubmitEnabled === 'function') updateSubmitEnabled();
}

$('#startWritingBtn').onclick = () => { resetWritingFlow(); showOnly('setupScreen'); };
$('#backToStartBtn').onclick = () => { showOnly('startScreen'); };

// Generate questions
$('#genTaskABtn').onclick = async () => {
  const btn = $('#genTaskABtn'); const spin = $('#spinnerTaskA');
  try{
    if(btn) btn.disabled = true; if(spin) spin.classList.remove('d-none');
    const r = await fetch('/api/question', { method: 'POST', headers: {'Content-Type': 'application/json', ...authHeader()}, body: JSON.stringify({task: 'A'})});
    const j = await r.json();
    $('#taskAQuestion').value = j.question || '';
    updateBeginEnabled();
  } catch { /* noop */ }
  finally { if(spin) spin.classList.add('d-none'); if(btn) btn.disabled = false; }
};
$('#genTaskBBtn').onclick = async () => {
  const btn = $('#genTaskBBtn'); const spin = $('#spinnerTaskB');
  try{
    if(btn) btn.disabled = true; if(spin) spin.classList.remove('d-none');
    const r = await fetch('/api/question', { method: 'POST', headers: {'Content-Type': 'application/json', ...authHeader()}, body: JSON.stringify({task: 'B'})});
    const j = await r.json();
    $('#taskBQuestion').value = j.question || '';
    updateBeginEnabled();
  } catch { /* noop */ }
  finally { if(spin) spin.classList.add('d-none'); if(btn) btn.disabled = false; }
};
$('#clearTaskABtn').onclick = ()=> { $('#taskAQuestion').value=''; updateBeginEnabled(); };
$('#clearTaskBBtn').onclick = ()=> { $('#taskBQuestion').value=''; updateBeginEnabled(); };

// Begin writing
let timerId = null; let endAt = null;
function startTimer(minutes){
  endAt = Date.now() + minutes*60*1000;
  renderTimer();
  timerId = setInterval(renderTimer, 1000);
}
function renderTimer(){
  const remaining = Math.max(0, endAt - Date.now());
  const s = Math.floor(remaining/1000); const h = Math.floor(s/3600); const m = Math.floor((s%3600)/60); const sec = s%60;
  $('#timer').textContent = `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(sec).padStart(2,'0')}`;
  if(remaining<=0 && timerId){ clearInterval(timerId); timerId=null; }
}

// Enable Begin Writing only if both questions exist
function updateBeginEnabled(){
  const hasAq = $('#taskAQuestion').value.trim().length > 0;
  const hasBq = $('#taskBQuestion').value.trim().length > 0;
  $('#beginWritingBtn').disabled = !(hasAq && hasBq);
}
['input','change'].forEach(e => {
  $('#taskAQuestion').addEventListener(e, updateBeginEnabled);
  $('#taskBQuestion').addEventListener(e, updateBeginEnabled);
});
// Guard on click
$('#beginWritingBtn').onclick = () => {
  updateBeginEnabled();
  if($('#beginWritingBtn').disabled){
    alert('Please provide both Task A and Task B questions before beginning to write.');
    return;
  }
  showOnly('writingScreen');
  $('#taskAQuestionDisplay').textContent = $('#taskAQuestion').value.trim();
  $('#taskBQuestionDisplay').textContent = $('#taskBQuestion').value.trim();
  startTimer(cfg.writingTimeMinutes);
};

// Word counts
function countWords(txt){
  return (txt.trim().match(/\b\w+\b/g)||[]).length;
}
function updateCounts(){
  $('#wordCountA').textContent = countWords($('#taskAResponse').value);
  $('#wordCountB').textContent = countWords($('#taskBResponse').value);
}
['input','change'].forEach(e => {
  $('#taskAResponse').addEventListener(e, updateCounts);
  $('#taskBResponse').addEventListener(e, updateCounts);
});

$('#resetA').onclick = ()=> { $('#taskAResponse').value=''; updateCounts(); };
$('#resetB').onclick = ()=> { $('#taskBResponse').value=''; updateCounts(); };

// Enable single Submit when both responses have content
function updateSubmitEnabled(){
  const hasA = $('#taskAResponse').value.trim().length > 0;
  const hasB = $('#taskBResponse').value.trim().length > 0;
  $('#submitBoth').disabled = !(hasA && hasB);
}
['input','change'].forEach(e => {
  $('#taskAResponse').addEventListener(e, updateSubmitEnabled);
  $('#taskBResponse').addEventListener(e, updateSubmitEnabled);
});
updateSubmitEnabled();

function renderJudge(container, judge){
  const just = judge?.justification || '';
  const rec = judge?.recommendation || '';
  const originals = Array.isArray(judge?.originals) ? judge.originals : [];
  const corrections = Array.isArray(judge?.corrections) ? judge.corrections : [];
  let pairs = [];
  const n = Math.max(originals.length, corrections.length);
  for(let i=0;i<n;i++){
    const o = originals[i] ?? '';
    const c = corrections[i] ?? '';
    if(o || c){ pairs.push(`<div class="d-flex align-items-center gap-2 mb-2"><span class="text-danger">${o}</span> <i class="bi bi-arrow-right text-muted"></i> <span class="text-success">${c}</span></div>`); }
  }
  container.innerHTML = `
    <div class="mb-3">
      <h4 class="h6 text-primary mb-2"><i class="bi bi-chat-text me-2"></i>Analysis</h4>
      <p class="mb-0">${just}</p>
    </div>
    <div class="mb-3">
      <h4 class="h6 text-success mb-2"><i class="bi bi-lightbulb me-2"></i>Recommendation</h4>
      <p class="mb-0">${rec}</p>
    </div>
    ${pairs.length ? `<div class="mt-3"><h4 class="h6 text-warning mb-2"><i class="bi bi-pencil me-2"></i>Corrections</h4>${pairs.join('')}</div>` : ''}
  `;
}

$('#submitBoth').onclick = async () => {
  // Move to evaluation screen
  showOnly('evaluationScreen');
  $('#judgeA').innerHTML = '';
  $('#judgeB').innerHTML = '';
  $('#finalScoreCenter').textContent = '/700';
  const spinnerBox = document.getElementById('evalSpinner');
  if(spinnerBox) spinnerBox.classList.remove('d-none');

  const body = {
    task_a_question: $('#taskAQuestionDisplay').textContent,
    task_a_response: $('#taskAResponse').value,
    task_b_question: $('#taskBQuestionDisplay').textContent,
    task_b_response: $('#taskBResponse').value
  };

  fetch('/api/evaluate/both', { method: 'POST', headers: {'Content-Type': 'application/json', ...authHeader()}, body: JSON.stringify(body)})
    .then(r => r.json())
    .then(j => {
      if(j?.taskA?.judge){ renderJudge($('#judgeA'), j.taskA.judge); }
      if(j?.taskB?.judge){ renderJudge($('#judgeB'), j.taskB.judge); }
      if(typeof j?.finalScore === 'number'){
        $('#finalScoreCenter').textContent = `${j.finalScore}/700`;
      }
      const titleEl = document.getElementById('evaluationHeaderTitle');
      if(titleEl) titleEl.textContent = 'Evaluation Complete';
      if(spinnerBox) spinnerBox.classList.add('d-none');
      loadDashboard();
    })
    .catch(() => {
      $('#judgeA').innerHTML = '<div class="alert alert-danger"><i class="bi bi-exclamation-triangle me-2"></i>Evaluation failed. Please try again.</div>';
      const titleEl = document.getElementById('evaluationHeaderTitle');
      if(titleEl) titleEl.textContent = 'Evaluation Failed';
      if(spinnerBox) spinnerBox.classList.add('d-none');
    });
};

// Dashboard
function renderSubmissions(list){
  if(!Array.isArray(list) || list.length===0){ 
    $('#dashboardList').innerHTML = `
      <div class="text-center py-5">
        <div class="icon-feature icon-warning mx-auto mb-3">
          <i class="bi bi-inbox"></i>
        </div>
        <p class="text-muted">No submissions yet. Start your first practice session!</p>
      </div>
    `;
    return; 
  }
  const formatEastern = (iso) => new Intl.DateTimeFormat('en-US', { year:'numeric', month:'short', day:'2-digit', hour:'2-digit', minute:'2-digit', second:'2-digit', hour12:false, timeZone:'America/New_York', timeZoneName:'short' }).format(new Date(iso));
  let html = `<div class="accordion" id="submissionsAccordion">`;
  list.forEach((s, idx) => {
    const errorPairs = (arr1, arr2) => {
      if(!Array.isArray(arr1) && !Array.isArray(arr2)) return '';
      let out = [];
      const n = Math.max((arr1||[]).length, (arr2||[]).length);
      for(let i=0;i<n;i++){
        const o = (arr1||[])[i] ?? '';
        const c = (arr2||[])[i] ?? '';
        if(o || c) out.push(`<div class="d-flex align-items-center gap-2 mb-1"><span class="text-danger small">${o}</span> <i class="bi bi-arrow-right text-muted"></i> <span class="text-success small">${c}</span></div>`);
      }
      return out.length ? `<div class="mt-2">${out.join('')}</div>` : '';
    };
    html += `
    <div class="accordion-item border-0 mb-3" style="border-radius: 12px; overflow: hidden; box-shadow: var(--card-shadow);">
      <h2 class="accordion-header" id="heading${idx}">
        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse${idx}" aria-expanded="false" aria-controls="collapse${idx}" style="border-radius: 12px;">
          <div class="d-flex flex-column flex-md-row w-100 justify-content-between align-items-start align-items-md-center">
            <div class="d-flex align-items-center gap-3">
              <div class="icon-feature icon-primary" style="width: 32px; height: 32px; font-size: 1rem;">
                <i class="bi bi-file-text"></i>
              </div>
              <div>
                <div class="fw-semibold">${formatEastern(s.created_at)}</div>
                <div class="small text-muted">Practice Session</div>
              </div>
            </div>
            <div class="score-display" style="font-size: 1.25rem; padding: 0.5rem 1rem; margin: 0;">
              ${s.final_score ?? '-'}
            </div>
          </div>
        </button>
      </h2>
      <div id="collapse${idx}" class="accordion-collapse collapse" aria-labelledby="heading${idx}" data-bs-parent="#submissionsAccordion">
        <div class="accordion-body" style="background: var(--bg-secondary);">
          <div class="row g-4">
            <div class="col-lg-6">
              <div class="premium-card">
                <div class="card-header">
                  <h4 class="h6 mb-0"><i class="bi bi-file-text me-2"></i>Task A</h4>
                </div>
                <div class="card-body">
                  <div class="mb-3">
                    <h5 class="h6 text-muted mb-1">Question</h5>
                    <p class="small">${(s.task_a_question||'').replace(/</g,'&lt;')}</p>
                  </div>
                  <div class="mb-3">
                    <h5 class="h6 text-muted mb-1">Response</h5>
                    <p class="small">${(s.task_a_response||'').replace(/</g,'&lt;')}</p>
                  </div>
                  <div class="mb-3">
                    <h5 class="h6 text-primary mb-1">Analysis</h5>
                    <p class="small">${(s.justification_a||'').replace(/</g,'&lt;')}</p>
                  </div>
                  <div class="mb-3">
                    <h5 class="h6 text-success mb-1">Recommendation</h5>
                    <p class="small">${(s.recommendation_a||'').replace(/</g,'&lt;')}</p>
                  </div>
                  ${errorPairs(s.originals_a, s.corrections_a) ? `<div><h5 class="h6 text-warning mb-1">Corrections</h5>${errorPairs(s.originals_a, s.corrections_a)}</div>` : ''}
                </div>
              </div>
            </div>
            <div class="col-lg-6">
              <div class="premium-card">
                <div class="card-header">
                  <h4 class="h6 mb-0"><i class="bi bi-envelope me-2"></i>Task B</h4>
                </div>
                <div class="card-body">
                  <div class="mb-3">
                    <h5 class="h6 text-muted mb-1">Question</h5>
                    <p class="small">${(s.task_b_question||'').replace(/</g,'&lt;')}</p>
                  </div>
                  <div class="mb-3">
                    <h5 class="h6 text-muted mb-1">Response</h5>
                    <p class="small">${(s.task_b_response||'').replace(/</g,'&lt;')}</p>
                  </div>
                  <div class="mb-3">
                    <h5 class="h6 text-primary mb-1">Analysis</h5>
                    <p class="small">${(s.justification_b||'').replace(/</g,'&lt;')}</p>
                  </div>
                  <div class="mb-3">
                    <h5 class="h6 text-success mb-1">Recommendation</h5>
                    <p class="small">${(s.recommendation_b||'').replace(/</g,'&lt;')}</p>
                  </div>
                  ${errorPairs(s.originals_b, s.corrections_b) ? `<div><h5 class="h6 text-warning mb-1">Corrections</h5>${errorPairs(s.originals_b, s.corrections_b)}</div>` : ''}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    `;
  });
  html += `</div>`;
  $('#dashboardList').innerHTML = html;
}
function loadDashboard(){
  fetch('/api/submissions', { headers: { ...authHeader() }})
    .then(r=> r.ok ? r.json() : [])
    .then(renderSubmissions)
    .catch(()=>{});
}
$('#dashboardBtn').onclick = () => { showOnly('dashboardScreen'); loadDashboard(); };
$('#refreshDashboard').onclick = loadDashboard;
$('#backToMainFromDashboard').onclick = () => { showOnly('startScreen'); };
// Navigate back to Home from evaluation screen
const backHomeBtn = document.getElementById('backToHomeFromEvaluation');
if(backHomeBtn){ backHomeBtn.addEventListener('click', () => { if(state.token){ showOnly('startScreen'); } else { showOnly('authScreen'); } }); }
