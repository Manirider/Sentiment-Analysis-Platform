import axios from "axios";

const API_BASE = "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
});

export const fetchPosts = async (limit = 50, offset = 0, filters = {}) => {
  const params = new URLSearchParams();
  params.append("limit", limit);
  params.append("offset", offset);

  if (filters.platform) params.append("platform", filters.platform);
  if (filters.sentiment) params.append("sentiment", filters.sentiment);

  const response = await api.get(`/api/posts?${params.toString()}`);
  return response.data;
};

export const fetchAnalytics = async (hours = 24) => {
  const response = await api.get(`/api/analytics?hours=${hours}`);
  return response.data;
};

export const fetchHealth = async () => {
  const response = await api.get("/api/health");
  return response.data;
};

export const connectWebSocket = (onMessage, onError, onClose) => {
  const ws = new WebSocket("ws://localhost:8000/ws/sentiment");

  ws.onopen = () => {
    console.log("WebSocket connected");
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      if (onMessage) onMessage(data);
    } catch (e) {
      console.error("WebSocket message parse error:", e);
    }
  };

  ws.onerror = (error) => {
    console.error("WebSocket error:", error);
    if (onError) onError(error);
  };

  ws.onclose = (event) => {
    console.log("WebSocket closed:", event.code, event.reason);
    if (onClose) onClose(event);
  };

  return ws;
};

export default api;
