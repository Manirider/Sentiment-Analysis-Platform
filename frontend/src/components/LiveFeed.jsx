export default function LiveFeed({ posts }) {
  const getSentimentColor = (label) => {
    switch (label?.toLowerCase()) {
      case "positive":
        return "text-green-500";
      case "negative":
        return "text-red-500";
      case "neutral":
      default:
        return "text-gray-400";
    }
  };

  const getEmotionEmoji = (emotion) => {
    switch (emotion?.toLowerCase()) {
      case "happy":
        return "😊";
      case "angry":
        return "😠";
      case "sad":
        return "😢";
      case "neutral":
      default:
        return "😐";
    }
  };

  const getSourceIcon = (platform) => {
    switch (platform?.toLowerCase()) {
      case "twitter":
        return "🐦";
      case "reddit":
        return "🔴";
      case "facebook":
        return "📘";
      case "instagram":
        return "📸";
      case "tiktok":
        return "🎵";
      default:
        return "📱";
    }
  };

  if (!posts || posts.length === 0) {
    return (
      <div className="bg-gray-800 rounded-lg p-4 h-80 flex items-center justify-center">
        <p className="text-gray-400">No posts available</p>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg p-4 h-80 overflow-hidden">
      <h3 className="text-lg font-semibold text-white mb-4">Live Feed</h3>
      <div className="overflow-y-auto h-56 space-y-3 pr-2">
        {posts.slice(0, 20).map((post, index) => {
          const sentiment = post.sentiment || {};
          return (
            <div
              key={post.post_id || index}
              className="bg-gray-700 rounded-lg p-3 transition-all hover:bg-gray-600"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <span className="text-lg">{getSourceIcon(post.platform)}</span>
                  <span className="text-sm text-gray-300">{post.platform || "unknown"}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`text-sm font-medium ${getSentimentColor(sentiment.label)}`}>
                    {sentiment.label || "analyzing..."}
                  </span>
                  <span className="text-lg">{getEmotionEmoji(sentiment.emotion)}</span>
                </div>
              </div>
              <p className="text-sm text-gray-200 line-clamp-2">
                {post.content || "No content"}
              </p>
              <div className="flex justify-between items-center mt-2">
                <span className="text-xs text-gray-500">@{post.author || "anonymous"}</span>
                {sentiment.confidence !== undefined && (
                  <span className="text-xs text-gray-500">
                    {(sentiment.confidence * 100).toFixed(0)}% confidence
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
