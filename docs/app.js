// Configure your backend base URL before deploying to GitHub Pages (optional)
// Example: const API_BASE_URL = "https://your-backend.example.com";
const API_BASE_URL = "https://YOUR-BACKEND-URL.com";

function el(id) { return document.getElementById(id); }

const DEFAULT_INTERVIEW_QUESTION = 'Tell me about a time you solved a difficult technical problem.';
const QUESTION_STORAGE_KEY = 'INTERVIEW_QUESTION';

// --- Key storage (BYOK) ---
function getStoredKey() {
  const persistent = localStorage.getItem('GEMINI_STORE') === '1';
  const key = persistent ? localStorage.getItem('GEMINI_API_KEY') : sessionStorage.getItem('GEMINI_API_KEY');
  return key || null;
}

function saveKey(key, persist) {
  if (persist) {
    localStorage.setItem('GEMINI_API_KEY', key);
    localStorage.setItem('GEMINI_STORE', '1');
    sessionStorage.removeItem('GEMINI_API_KEY');
  } else {
    sessionStorage.setItem('GEMINI_API_KEY', key);
    localStorage.removeItem('GEMINI_API_KEY');
    localStorage.removeItem('GEMINI_STORE');
  }
}

function clearKey() {
  localStorage.removeItem('GEMINI_API_KEY');
  localStorage.removeItem('GEMINI_STORE');
  sessionStorage.removeItem('GEMINI_API_KEY');
}

function updateKeyUI() {
  const key = getStoredKey();
  el('api_key_input').value = key ? key : '';
  const persist = localStorage.getItem('GEMINI_STORE') === '1';
  el('persist_key').checked = persist;
}

function getStoredQuestion() {
  const storedQuestion = localStorage.getItem(QUESTION_STORAGE_KEY);
  return storedQuestion === null ? DEFAULT_INTERVIEW_QUESTION : storedQuestion;
}

function saveQuestion(question) {
  localStorage.setItem(QUESTION_STORAGE_KEY, question);
}

function updateQuestionUI() {
  el('question').value = getStoredQuestion();
}

// --- Gemini direct call ---
async function callGeminiDirect(model, requestBody, apiKey, timeoutMs = 30000) {
  const base = 'https://generativelanguage.googleapis.com/v1';
  const url = `${base}/models/${encodeURIComponent(model)}:generateContent?key=${encodeURIComponent(apiKey)}`;

  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody),
      signal: controller.signal,
    });
    clearTimeout(id);
    const text = await res.text();
    let data = null;
    try { data = JSON.parse(text); } catch(e) { data = null; }
    return { ok: res.ok, status: res.status, data, text };
  } catch (e) {
    clearTimeout(id);
    return { ok: false, status: 0, error: String(e) };
  }
}

// --- Local scoring fallback ---
function localScore(story) {
  // Basic heuristics similar to backend scoring
  const s = (story.situation || '').trim();
  const a = (story.action || '').trim();
  const r = (story.result || '').trim();

  const situation_len = s.split(/\s+/).filter(Boolean).length;
  const action_len = a.split(/\s+/).filter(Boolean).length;
  const result_len = r.split(/\s+/).filter(Boolean).length;
  const has_numbers = /\d/.test(r);
  const personal = /\b(i |my |me )/i.test(a);

  let score = 'Skilled';
  if (situation_len < 20 || action_len < 30 || result_len < 20) score = 'Unskilled';
  if (!personal) score = 'Unskilled';
  if (action_len > 200 && result_len < 50) score = 'Overused';
  if (has_numbers && action_len > 50 && situation_len > 20) score = 'Talented';

  const notes = [];
  if (situation_len < 20) notes.push('Add more context to the Situation.');
  if (action_len < 50) notes.push('Expand the Action with specific steps and decisions.');
  if (!personal) notes.push("Use 'I' statements to emphasize your role.");
  if (result_len < 20) notes.push('Quantify results with numbers if possible.');

  return { score, score_description: `Basic heuristic: ${score}`, ai_feedback: notes.join('\n') };
}

// --- UI helpers ---
function showOutput(html) { el('output').innerHTML = html; }
function showError(msg) { el('output').innerText = `Error: ${msg}`; }

// --- Event handlers ---
el('save_key').addEventListener('click', () => {
  const v = el('api_key_input').value.trim();
  const persist = el('persist_key').checked;
  if (!v) { alert('Please paste your Gemini API key before saving.'); return; }
  saveKey(v, persist);
  updateKeyUI();
  alert('API key saved in your browser.');
});

el('clear_key').addEventListener('click', () => {
  clearKey();
  updateKeyUI();
  alert('API key cleared from browser storage.');
});

el('question').addEventListener('input', () => {
  saveQuestion(el('question').value);
});

// Evaluate button
el('evaluate').addEventListener('click', async () => {
  const story = {
    question: el('question').value || '',
    competency: el('competency').value || '',
    situation: el('situation').value || '',
    task: el('task').value || '',
    action: el('action').value || '',
    result: el('result').value || '',
  };

  // Basic validation
  if (!story.situation || !story.task || !story.action || !story.result) {
    showError('Please fill in all STAR fields before evaluating.');
    return;
  }

  const useAI = el('use_ai_eval').checked;
  const apiKey = getStoredKey();

  showOutput('⏳ Evaluating...');

  if (useAI) {
    if (!apiKey) {
      showError('Missing API key. Paste your Gemini API key in Settings to use AI evaluation, or uncheck "Use AI for evaluation" to use local scoring.');
      return;
    }

    // Build prompt for Gemini to provide concise suggestions and a score
    const prompt = `You are an expert interview coach. Score the following STAR story as Talented / Skilled / Unskilled / Overused and provide 2 concise, actionable suggestions to improve it.\n\nQuestion: ${story.question}\nCompetency: ${story.competency}\nSituation: ${story.situation}\nTask: ${story.task}\nAction: ${story.action}\nResult: ${story.result}`;

    try {
      const requestBody = { contents: [{ parts: [{ text: prompt }] }] };
      const resp = await callGeminiDirect('gemini-1.5-flash', requestBody, apiKey);
      if (!resp.ok) {
        if (resp.status === 401 || resp.status === 403) {
          showError('Invalid or unauthorized API key.');
          return;
        }
        if (resp.status === 429) {
          showError('Rate limited by Gemini. Please wait and try again later.');
          return;
        }
        showError(`Upstream error (${resp.status}): ${resp.error || resp.text}`);
        return;
      }

      const candidates = (resp.data && resp.data.candidates) || [];
      const text = (candidates[0] && candidates[0].content && candidates[0].content.parts && candidates[0].content.parts[0].text) || (resp.data && JSON.stringify(resp.data)) || resp.text;
      // Attempt to parse score line from response
      let scoreMatch = text.match(/\b(Talented|Skilled|Unskilled|Overused)\b/i);
      const parsedScore = scoreMatch ? scoreMatch[0] : null;

      const outputHtml = `<h3>Score: ${parsedScore || 'AI'} </h3><pre>${text}</pre>`;
      showOutput(outputHtml);
    } catch (e) {
      showError(`AI evaluation failed: ${e}`);
    }
  } else {
    const res = localScore(story);
    const html = `<h3>Score: ${res.score}</h3><p>${res.score_description}</p><h4>Suggestions</h4><pre>${res.ai_feedback}</pre>`;
    showOutput(html);
  }
});

// Generate polished STAR
el('generate').addEventListener('click', async () => {
  const apiKey = getStoredKey();
  const story = {
    situation: el('situation').value || '',
    task: el('task').value || '',
    action: el('action').value || '',
    result: el('result').value || '',
  };
  if (!story.situation || !story.task || !story.action || !story.result) {
    showError('Please fill all STAR fields before generating a polished response.');
    return;
  }
  showOutput('⏳ Generating polished STAR...');

  const prompt = `Polish the following STAR answer into a concise, interview-ready response:\n\nSituation: ${story.situation}\nTask: ${story.task}\nAction: ${story.action}\nResult: ${story.result}`;

  if (apiKey) {
    try {
      const requestBody = { contents: [{ parts: [{ text: prompt }] }] };
      const resp = await callGeminiDirect('gemini-1.5-flash', requestBody, apiKey);
      if (!resp.ok) {
        if (resp.status === 401 || resp.status === 403) { showError('Invalid or unauthorized API key.'); return; }
        if (resp.status === 429) { showError('Rate limited by Gemini. Please try later.'); return; }
        showError(`Upstream error (${resp.status}): ${resp.error || resp.text}`); return;
      }
      const candidates = (resp.data && resp.data.candidates) || [];
      const text = (candidates[0] && candidates[0].content && candidates[0].content.parts && candidates[0].content.parts[0].text) || (resp.data && JSON.stringify(resp.data)) || resp.text;
      showOutput(`<h3>Polished STAR</h3><pre>${text}</pre>`);
    } catch (e) { showError(`Generation failed: ${e}`); }
  } else if (API_BASE_URL && !API_BASE_URL.includes('YOUR-BACKEND-URL')) {
    // Fallback to backend if configured
    try {
      const resp = await fetch(`${API_BASE_URL}/api/gemini`, { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ model: 'gemini-1.5-flash', contents: [{ parts: [{ text: prompt }] }] }) });
      const envelope = await resp.json().catch(()=>null);
      if (!envelope) { showError('Invalid response from backend'); return; }
      if (!envelope.success) { showError(`Backend error: ${envelope.error}`); return; }
      const data = envelope.data || {};
      const text = (data.candidates && data.candidates[0] && data.candidates[0].content && data.candidates[0].content.parts && data.candidates[0].content.parts[0].text) || 'No response';
      showOutput(`<h3>Polished STAR</h3><pre>${text}</pre>`);
    } catch (e) { showError(`Backend generation failed: ${e}`); }
  } else {
    showError('No API key provided. Paste your Gemini key in Settings to generate polished STAR, or configure a backend.');
  }
});

// Initialize UI
updateKeyUI();
updateQuestionUI();
