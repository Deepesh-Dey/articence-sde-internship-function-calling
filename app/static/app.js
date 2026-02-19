/**
 * Universal Data Connector - Frontend
 * Upload, Voice, Hugging Face Analysis, Query
 */

const API_BASE = window.location.origin;
let lastAnalysis = '';

function toast(message, type = 'success') {
  const container = document.getElementById('toastContainer');
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  const icons = { success: '✓', error: '✕' };
  el.innerHTML = `<span>${icons[type] || icons.success}</span><span>${message}</span>`;
  container.appendChild(el);
  setTimeout(() => {
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 200);
  }, 3500);
}

async function apiGet(path, params = {}) {
  const url = new URL(path, API_BASE);
  Object.entries(params).forEach(([k, v]) => v != null && v !== '' && url.searchParams.set(k, v));
  const res = await fetch(url);
  if (!res.ok) throw new Error(await res.text().catch(() => res.statusText));
  return res.json();
}

async function apiPost(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await res.text().catch(() => res.statusText));
  return res.json();
}

async function apiUpload(path, formData) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error(await res.text().catch(() => res.statusText));
  return res.json();
}

async function checkApi() {
  const statusEl = document.getElementById('apiStatus');
  try {
    await apiGet('/health');
    statusEl.className = 'api-status connected';
    statusEl.querySelector('span:last-child').textContent = 'API Connected';
  } catch {
    statusEl.className = 'api-status error';
    statusEl.querySelector('span:last-child').textContent = 'API Offline';
  }
}

// Voice
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const SpeechSynthesis = window.speechSynthesis;

function initVoice() {
  const voiceBtn = document.getElementById('voiceInputBtn');
  const speakBtn = document.getElementById('speakResponseBtn');
  const queryEl = document.getElementById('analyzeQuery');

  if (SpeechRecognition) {
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    voiceBtn.addEventListener('click', () => {
      if (voiceBtn.classList.contains('recording')) {
        recognition.stop();
        return;
      }
      voiceBtn.classList.add('recording');
      voiceBtn.querySelector('.btn-text').textContent = 'Stop';
      recognition.start();
    });

    recognition.onresult = (e) => {
      const text = e.results[0][0].transcript;
      queryEl.value = queryEl.value ? queryEl.value + ' ' + text : text;
      voiceBtn.classList.remove('recording');
      voiceBtn.querySelector('.btn-text').textContent = 'Voice input';
    };

    recognition.onend = () => {
      voiceBtn.classList.remove('recording');
      voiceBtn.querySelector('.btn-text').textContent = 'Voice input';
    };

    recognition.onerror = () => {
      voiceBtn.classList.remove('recording');
      voiceBtn.querySelector('.btn-text').textContent = 'Voice input';
      toast('Voice recognition failed', 'error');
    };
  } else {
    voiceBtn.style.display = 'none';
  }

  speakBtn.addEventListener('click', () => {
    if (!lastAnalysis) {
      toast('Run analysis first', 'error');
      return;
    }
    const u = new SpeechSynthesisUtterance(lastAnalysis);
    u.rate = 0.95;
    SpeechSynthesis.speak(u);
  });
}

function updateFilters() {
  const source = document.getElementById('dataSource').value;
  const statusRow = document.getElementById('statusRow');
  const statusFilter = document.getElementById('statusFilter');
  statusRow.style.display = (source === 'crm' || source === 'support') ? 'block' : 'none';
  if (source === 'crm') {
    statusFilter.innerHTML = '<option value="">All</option><option value="active">Active</option><option value="inactive">Inactive</option>';
  } else if (source === 'support') {
    statusFilter.innerHTML = '<option value="">All</option><option value="open">Open</option><option value="closed">Closed</option>';
  }
  document.getElementById('priorityRow').style.display = source === 'support' ? 'block' : 'none';
  document.getElementById('metricRow').style.display = source === 'analytics' ? 'block' : 'none';
}

function renderResult(data, meta, isAnalysis = false) {
  const content = document.getElementById('resultContent');
  const metaEl = document.getElementById('resultMeta');

  if (isAnalysis && typeof data === 'string') {
    lastAnalysis = data;
    document.getElementById('speakResponseBtn').disabled = false;
    content.innerHTML = `<pre>${data}</pre>`;
    metaEl.textContent = 'Hugging Face analysis';
    return;
  }

  if (!data || (Array.isArray(data) && data.length === 0)) {
    content.innerHTML = '<p class="placeholder">No data returned.</p>';
    metaEl.textContent = '';
    return;
  }

  metaEl.textContent = meta?.context_message || '';

  if (Array.isArray(data) && data.length > 0) {
    const first = data[0];
    if (typeof first === 'object' && first?.type === 'aggregated') {
      content.innerHTML = `<pre>${JSON.stringify(first, null, 2)}</pre>`;
      return;
    }
    const keys = Object.keys(typeof first === 'object' ? first : {});
    if (keys.length > 0) {
      const headers = keys.map(k => `<th>${k}</th>`).join('');
      const rows = data.slice(0, 20).map(row => {
        const cells = keys.map(k => {
          let v = row?.[k];
          if (v && typeof v === 'object' && String(v).startsWith('[object')) v = JSON.stringify(v);
          return `<td>${v ?? ''}</td>`;
        }).join('');
        return `<tr>${cells}</tr>`;
      }).join('');
      content.innerHTML = `<table class="data-table"><thead><tr>${headers}</tr></thead><tbody>${rows}</tbody></table>`;
      if (data.length > 20) content.innerHTML += `<p style="margin-top:0.5rem;font-size:0.85rem;color:var(--text-muted)">Showing 20 of ${data.length}</p>`;
      return;
    }
  }
  content.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
}

async function uploadData() {
  const fileInput = document.getElementById('uploadFile');
  const source = document.getElementById('uploadSource').value;
  const btn = document.getElementById('uploadBtn');

  if (!fileInput.files.length) {
    toast('Select a file', 'error');
    return;
  }

  btn.disabled = true;
  btn.querySelector('.btn-text').style.display = 'none';
  btn.querySelector('.btn-loading').style.display = 'inline';

  const formData = new FormData();
  formData.append('file', fileInput.files[0]);

  try {
    const res = await apiUpload(`/upload/${source}`, formData);
    toast(`Uploaded ${res.records} records`, 'success');
    fileInput.value = '';
  } catch (e) {
    toast(e.message || 'Upload failed', 'error');
  } finally {
    btn.disabled = false;
    btn.querySelector('.btn-text').style.display = 'inline';
    btn.querySelector('.btn-loading').style.display = 'none';
  }
}

async function analyze() {
  const query = document.getElementById('analyzeQuery').value.trim();
  const btn = document.getElementById('analyzeBtn');

  if (!query) {
    toast('Enter a question', 'error');
    return;
  }

  btn.disabled = true;
  btn.querySelector('.btn-text').style.display = 'none';
  btn.querySelector('.btn-loading').style.display = 'inline';

  const modelType = document.getElementById('modelType').value;
  try {
    const res = await apiPost('/analyze', { query, model_type: modelType });
    renderResult(res.analysis, null, true);
    toast('Analysis complete', 'success');
  } catch (e) {
    const msg = e.message || 'Analysis failed';
    toast(msg, 'error');
    document.getElementById('resultContent').innerHTML = `<p class="placeholder" style="color:var(--error)">${msg}</p>`;
  } finally {
    btn.disabled = false;
    btn.querySelector('.btn-text').style.display = 'inline';
    btn.querySelector('.btn-loading').style.display = 'none';
  }
}

async function fetchData() {
  const btn = document.getElementById('fetchDataBtn');
  const source = document.getElementById('dataSource').value;
  const voice = document.getElementById('voiceMode').checked;
  const params = { limit: 10, voice };

  if (source === 'crm' || source === 'support') {
    const status = document.getElementById('statusFilter').value;
    if (status) params.status = status;
  }
  if (source === 'support') {
    const priority = document.getElementById('priorityFilter').value;
    if (priority) params.priority = priority;
  }
  if (source === 'analytics') {
    const metric = document.getElementById('metricFilter').value.trim();
    if (metric) params.metric = metric;
  }

  btn.disabled = true;
  btn.querySelector('.btn-text').style.display = 'none';
  btn.querySelector('.btn-loading').style.display = 'inline';

  try {
    const res = await apiGet(`/data/${source}`, params);
    renderResult(res.data, res.metadata);
    toast(`Fetched ${res.metadata?.returned_results ?? res.data?.length ?? 0} items`, 'success');
  } catch (e) {
    toast(e.message || 'Request failed', 'error');
    document.getElementById('resultContent').innerHTML = `<p class="placeholder" style="color:var(--error)">${e.message}</p>`;
  } finally {
    btn.disabled = false;
    btn.querySelector('.btn-text').style.display = 'inline';
    btn.querySelector('.btn-loading').style.display = 'none';
  }
}

document.addEventListener('DOMContentLoaded', () => {
  checkApi();
  setInterval(checkApi, 15000);
  initVoice();
  updateFilters();

  document.getElementById('dataSource').addEventListener('change', updateFilters);
  document.getElementById('uploadBtn').addEventListener('click', uploadData);
  document.getElementById('analyzeBtn').addEventListener('click', analyze);
  document.getElementById('fetchDataBtn').addEventListener('click', fetchData);
});
