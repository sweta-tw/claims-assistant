
const API_BASE_URL = "/api";

async function request(path, { token, ...options } = {}) {
  const headers = {
    ...(options.body ? { "Content-Type": "application/json" } : {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  let response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers,
    });
  } catch {
    throw new Error(
      "Cannot connect to FastAPI. Check that the backend is running."
    );
  }

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const detail = data?.detail;
    const message = Array.isArray(detail)
      ? detail.map((item) => item.msg || "Invalid input").join(", ")
      : detail || `Request failed with HTTP ${response.status}`;

    const error = new Error(message);
    error.status = response.status;
    throw error;
  }

  return data;
}

export function login(username, password) {
  return request("/auth/token", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
}

export function getClaims(token) {
  return request("/claims", { token });
}

export function getClaim(token, claimId) {
  return request(`/claims/${encodeURIComponent(claimId)}`, { token });
}

export function createClaim(token, { customer, amount }) {
  return request("/claims", {
    method: "POST",
    token,
    body: JSON.stringify({
      customer: customer.trim(),
      amount: Number(amount),
    }),
  });
}

export function updateClaimStatus(token, claimId, status) {
  return request(`/claims/${encodeURIComponent(claimId)}/status`, {
    method: "PUT",
    token,
    body: JSON.stringify({ status }),
  });
}

export function deleteClaim(token, claimId) {
  return request(`/claims/${encodeURIComponent(claimId)}`, {
    method: "DELETE",
    token,
  });
}

export function sendChatMessage(token, message, history = []) {
  return request("/assistant/chat", {
    method: "POST",
    token,
    body: JSON.stringify({
      message,
      history: history.map(({ role, content }) => ({ role, content })),
    }),
  });
}
