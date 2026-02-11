import { useEffect, useState, useRef } from "react";
import { fetchPosts, fetchAnalytics, connectWebSocket } from "../services/api";
import DistributionChart from "../components/DistributionChart";
import SentimentChart from "../components/SentimentChart";
import LiveFeed from "../components/LiveFeed";

function StatCard({ title, value, subtitle, color }) {
  const colorStyles = {
    cyan: "border-cyan-400 shadow-cyan-400/30",
    green: "border-green-500 shadow-green-500/30",
    red: "border-red-500 shadow-red-500/30",
    gray: "border-gray-400 shadow-gray-400/30",
  };

  return (
    <div className={`p-6 rounded-2xl bg-gray-900 border-2 ${colorStyles[color]} shadow-lg`}>
      <p className="text-sm font-medium text-gray-400 mb-1">{title}</p>
      <p className="text-4xl font-bold text-white mb-1">{value}</p>
      <p className="text-sm text-gray-500">{subtitle}</p>
    </div>
  );
}

export default function Dashboard() {
  const [posts, setPosts] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState("connecting");
  const [lastUpdate, setLastUpdate] = useState(null);
  const [loading, setLoading] = useState(true);
  const wsRef = useRef(null);

  useEffect(() => {
    loadInitialData();
    const interval = setInterval(loadInitialData, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const ws = connectWebSocket(
      (message) => {
        setConnectionStatus("connected");
        setLastUpdate(new Date().toLocaleTimeString());

        if (message.type === "new_post") {
          setPosts((prev) => [message.data, ...prev.slice(0, 49)]);
          loadInitialData();
        } else if (message.type === "metrics_update") {
          loadInitialData();
        } else if (message.type === "connected") {
          setConnectionStatus("connected");
        }
      },
      () => setConnectionStatus("error"),
      () => setConnectionStatus("disconnected")
    );

    wsRef.current = ws;
    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  async function loadInitialData() {
    try {
      const [postsResponse, analyticsResponse] = await Promise.all([
        fetchPosts(50, 0, {}),
        fetchAnalytics(24),
      ]);

      setPosts(postsResponse.posts || []);
      setAnalytics(analyticsResponse);
    } catch (err) {
      console.error("Failed to load data:", err);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-cyan-400"></div>
      </div>
    );
  }

  const total = analytics?.total_count || 0;
  const positive = analytics?.positive_count || 0;
  const negative = analytics?.negative_count || 0;
  const neutral = analytics?.neutral_count || 0;
  const percentages = analytics?.percentages || { positive: 0, negative: 0, neutral: 0 };

  const distributionData = analytics?.distribution || [
    { label: "positive", count: positive, percentage: percentages.positive },
    { label: "negative", count: negative, percentage: percentages.negative },
    { label: "neutral", count: neutral, percentage: percentages.neutral },
  ];

  return (
    <div className="p-6 bg-gray-950 min-h-screen">
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Real-Time Sentiment Analysis Dashboard</h1>
          <p className="text-gray-400">Live social media sentiment monitoring</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <span className={`w-3 h-3 rounded-full ${
              connectionStatus === "connected" ? "bg-green-500" :
              connectionStatus === "connecting" ? "bg-yellow-500 animate-pulse" :
              "bg-red-500"
            }`}></span>
            <span className="text-sm text-gray-300">
              {connectionStatus === "connected" ? "Live" : connectionStatus}
            </span>
          </div>
          {lastUpdate && (
            <span className="text-sm text-gray-500">Last Update: {lastUpdate}</span>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Total Posts"
          value={total.toLocaleString()}
          subtitle="Last 24 hours"
          color="cyan"
        />
        <StatCard
          title="Positive"
          value={`${percentages.positive}%`}
          subtitle={`${positive.toLocaleString()} posts`}
          color="green"
        />
        <StatCard
          title="Negative"
          value={`${percentages.negative}%`}
          subtitle={`${negative.toLocaleString()} posts`}
          color="red"
        />
        <StatCard
          title="Neutral"
          value={`${percentages.neutral}%`}
          subtitle={`${neutral.toLocaleString()} posts`}
          color="gray"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <DistributionChart data={distributionData} />
        <LiveFeed posts={posts} />
      </div>

      <div className="mb-8">
        <SentimentChart data={distributionData} />
      </div>
    </div>
  );
}
