const API_BASE = "http://localhost:8000";

export async function fetchStats() {
  const res = await fetch(`${API_BASE}/api/sentiments`);
  return res.json();
}

export async function fetchRecentPosts() {
  const res = await fetch(`${API_BASE}/api/posts`);
  return res.json();
}

export async function createPost(content, author = "anonymous") {
  const res = await fetch(`${API_BASE}/api/posts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content, author, platform: "web" }),
  });
  return res.json();
}
