const API_BASE = import.meta.env.VITE_API_URL || "/api";

async function request(endpoint, options = {}) {
  const token = localStorage.getItem("token");
  const headers = {
    "Content-Type": "application/json",
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers,
  };

  const res = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });

  if (res.status === 401) {
    localStorage.removeItem("token");
    window.location.href = "/login";
    throw new Error("Unauthorized");
  }

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || "Request failed");
  }

  return res;
}

export const api = {
  // Auth
  signup: (data) =>
    request("/auth/signup", {
      method: "POST",
      body: JSON.stringify(data),
    }).then((r) => r.json()),

  login: (data) =>
    request("/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    }).then((r) => r.json()),

  getMe: () => request("/auth/me").then((r) => r.json()),

  // Chats
  getChats: () => request("/chats/").then((r) => r.json()),

  createChat: () =>
    request("/chats/", {
      method: "POST",
      body: JSON.stringify({}),
    }).then((r) => r.json()),

  getChat: (id) => request(`/chats/${id}`).then((r) => r.json()),

  deleteChat: (id) => request(`/chats/${id}`, { method: "DELETE" }),

  sendMessage: (chatId, content) =>
    request(`/chats/${chatId}/messages`, {
      method: "POST",
      body: JSON.stringify({ content }),
    }).then((r) => r.json()),

  // Resumes
  getResumes: () => request("/resumes/").then((r) => r.json()),

  generateResume: (chatId, pageCount) => {
    const token = localStorage.getItem("token");
    return fetch(`${API_BASE}/resumes/generate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ chat_id: chatId, page_count: pageCount }),
    });
  },

  downloadResume: (id) => {
    const token = localStorage.getItem("token");
    return fetch(`${API_BASE}/resumes/${id}/download`, {
      headers: { Authorization: `Bearer ${token}` },
    });
  },
};
