import { startMockInterview, sendMockMessage } from './mockApi';

const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');
const REQUEST_TIMEOUT_MS = 20_000;

export const USE_MOCK_API = import.meta.env.VITE_USE_MOCK_API === 'true';

function toBackendCandidate(candidate) {
  return candidate.apiCandidate ?? candidate;
}

function validateResponse(payload) {
  if (!payload || typeof payload.reply !== 'string' || typeof payload.done !== 'boolean') {
    throw new Error('InterVista returned an unexpected response. Please try again.');
  }

  if (payload.done) {
    const { feedback } = payload;
    const fieldsAreValid = feedback
      && typeof feedback.summary === 'string'
      && ['strengths', 'gaps', 'next'].every((field) => Array.isArray(feedback[field]) && feedback[field].every((item) => typeof item === 'string'));
    if (!fieldsAreValid) throw new Error('InterVista could not prepare interview feedback. Please try again.');
  }

  return payload;
}

async function postInterview(payload) {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch(`${API_BASE_URL}/api/interview`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal: controller.signal
    });
    const body = await response.json().catch(() => null);
    if (!response.ok) throw new Error(body?.detail || 'Unable to connect to InterVista. Please try again.');
    return validateResponse(body);
  } catch (error) {
    if (error.name === 'AbortError') throw new Error('InterVista took too long to respond. Please try again.');
    if (error instanceof TypeError) throw new Error('Unable to connect to InterVista. Please try again.');
    throw error;
  } finally {
    window.clearTimeout(timeout);
  }
}

export async function startInterview({ sessionId, candidate }) {
  if (USE_MOCK_API) return startMockInterview({ sessionId, candidate });
  return postInterview({ sessionId, candidate: toBackendCandidate(candidate) });
}

export async function sendInterviewMessage({ sessionId, message, candidate, questionNumber }) {
  if (USE_MOCK_API) return sendMockMessage({ sessionId, message, candidate, questionNumber });
  return postInterview({ sessionId, message });
}
