const WS_URL = "ws://localhost:8000/ws/sentiment";

export function connectSocket(onMessage) {
  const socket = new WebSocket(WS_URL);

  socket.onopen = () => {
    console.log("WebSocket connected");
  };

  socket.onmessage = (event) => {
    const message = JSON.parse(event.data);
    onMessage(message);
  };

  socket.onerror = (err) => {
    console.error("WebSocket error", err);
  };

  return socket;
}
