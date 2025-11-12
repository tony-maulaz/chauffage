const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

async function handleResponse(response) {
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `API error (${response.status})`);
  }
  return response.json();
}

export async function fetchSensors() {
  const res = await fetch(`${API_BASE}/sensors`);
  return handleResponse(res);
}

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  return handleResponse(res);
}
