const BASE = '/api';

function authHeader() {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

/** Returns AI provider headers from localStorage, if configured. */
function aiConfigHeaders() {
  const provider = localStorage.getItem('ai_provider');
  const apiKey  = localStorage.getItem('ai_api_key');
  const model   = localStorage.getItem('ai_model');
  const headers = {};
  if (provider) headers['X-AI-Provider'] = provider;
  if (apiKey)   headers['X-AI-Key']      = apiKey;
  if (model)    headers['X-AI-Model']    = model;
  return headers;
}

async function apiGet(path) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { ...authHeader() },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(err.detail || `Request failed with status ${res.status}`);
  }
  return res.json();
}

async function apiPost(path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeader(), ...aiConfigHeaders() },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(err.detail || `Request failed with status ${res.status}`);
  }
  return res.json();
}

export const login = (username, password) =>
  apiPost('/auth/login', { username, password });

export const register = (username, password) =>
  apiPost('/auth/register', { username, password });

export const getMe = () => apiGet('/me');

export const getConfig = () => apiGet('/config');

export const getSubmissions = () => apiGet('/submissions');

export const generateQuestion = (task) =>
  apiPost('/question', { task });

export const evaluateBoth = (data) =>
  apiPost('/evaluate/both', data);

export const generateImprovedAnswer = (taskType, question, userAnswer) =>
  apiPost('/generate-improved-answer', { taskType, question, userAnswer });
