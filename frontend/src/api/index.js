const BASE = '/api';

function authHeader() {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
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
    headers: { 'Content-Type': 'application/json', ...authHeader() },
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
