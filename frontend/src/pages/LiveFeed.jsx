import { useEffect, useState } from 'react';
import { fetchPosts } from '../services/api';

function SentimentBadge({ sentiment }) {
    const styles = {
        positive: 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/50 shadow-[0_0_10px_rgba(16,185,129,0.2)]',
        negative: 'bg-rose-500/10 text-rose-400 border border-rose-500/50 shadow-[0_0_10px_rgba(244,63,94,0.2)]',
        neutral: 'bg-sky-500/10 text-sky-400 border border-sky-500/50 shadow-[0_0_10px_rgba(14,165,233,0.2)]',
    };

    const label = sentiment?.sentiment || 'processing';
    const score = sentiment?.score ? Math.round(sentiment.score * 100) : 0;

    return (
        <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold tracking-wide uppercase backdrop-blur-sm transition-all duration-300 hover:scale-105 ${styles[label] || styles.neutral}`}>
            {label} {score}%
        </span>
    );
}

function EmotionTag({ emotion }) {
    const colors = {
        joy: 'text-yellow-400 border-yellow-500/30 bg-yellow-400/5',
        sadness: 'text-blue-400 border-blue-500/30 bg-blue-400/5',
        anger: 'text-red-400 border-red-500/30 bg-red-400/5',
        fear: 'text-purple-400 border-purple-500/30 bg-purple-400/5',
        surprise: 'text-pink-400 border-pink-500/30 bg-pink-400/5',
        disgust: 'text-orange-400 border-orange-500/30 bg-orange-400/5',
        neutral: 'text-zinc-400 border-zinc-500/30 bg-zinc-400/5',
    };

    if (!emotion) return null;

    return (
        <span className={`px-2 py-0.5 rounded-md text-[10px] font-medium border ${colors[emotion] || colors.neutral}`}>
            #{emotion}
        </span>
    );
}

export default function LiveFeed({ posts: propPosts }) {
    const [posts, setPosts] = useState(propPosts || []);
    const [loading, setLoading] = useState(!propPosts);
    const [error, setError] = useState(null);


    useEffect(() => {
        if (propPosts) {
            setPosts(propPosts);
            setLoading(false);
            return;
        }
        loadData();
        const interval = setInterval(loadData, 3000);
        return () => clearInterval(interval);
    }, [propPosts]);

    async function loadData() {
        try {
            const data = await fetchPosts();
            setPosts(data.posts || []);
            setError(null);
        } catch (err) {
            setError('Failed to fetch posts');
        } finally {
            setLoading(false);
        }
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="w-8 h-8 rounded-full border-2 border-t-[#00f5d4] border-r-transparent border-b-[#7209b7] border-l-transparent animate-spin"></div>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-full glass-panel rounded-2xl p-6">
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h2 className="text-lg font-bold text-white flex items-center gap-2">
                         <span className="w-1 h-5 rounded-full bg-[#f72585] animate-pulse"></span>
                         Live Stream
                    </h2>
                    <p className="text-xs text-zinc-500 mt-1">Real-time analysis feed</p>
                </div>
                <div className="px-2 py-1 rounded bg-green-500/10 border border-green-500/20">
                    <span className="text-[10px] font-mono text-green-400 flex items-center gap-1.5">
                        <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></span>
                        LIVE
                    </span>
                </div>
            </div>


            {error && (
                <div className="mb-6 bg-red-500/10 border border-red-500/30 rounded-xl p-4 text-center">
                    <p className="text-red-400 text-sm">{error}</p>
                </div>
            )}


            {posts.length === 0 && !error && (
                <div className="flex-1 flex flex-col items-center justify-center text-zinc-500 min-h-[200px]">
                    <p className="text-sm">Waiting for incoming signals...</p>
                </div>
            )}


            <div className="space-y-3 overflow-y-auto pr-2 custom-scrollbar flex-1 max-h-[600px]">
                {posts.map((post, index) => (
                    <div
                        key={post.post_id || post.id || index}
                        className="group relative p-4 rounded-xl border border-white/5 bg-white/[0.02] hover:bg-white/[0.04] transition-all duration-300 hover:border-[#00f5d4]/30 animate-slide-in"
                        style={{ animationDelay: `${index * 50}ms` }}
                    >
                        <div className="flex items-start justify-between gap-3">
                            <div className="flex-1 space-y-2">
                                <p className="text-zinc-200 text-sm leading-relaxed font-light">{post.content}</p>
                                <div className="flex items-center gap-3">
                                    <div className="flex items-center gap-1.5 text-xs text-zinc-500 group-hover:text-zinc-400 transition-colors">
                                        <div className="w-5 h-5 rounded-full bg-gradient-to-br from-zinc-700 to-zinc-800 flex items-center justify-center text-[10px] text-zinc-300">
                                            {post.author ? post.author[0].toUpperCase() : '?'}
                                        </div>
                                        <span>@{post.author || 'anon'}</span>
                                    </div>
                                    <span className="text-zinc-700 text-[10px]">•</span>
                                    <span className="text-[10px] text-[#00b4d8] font-medium tracking-wide border border-[#00b4d8]/20 px-1.5 rounded uppercase">
                                        {post.platform || 'WEB'}
                                    </span>
                                </div>
                            </div>
                            <div className="flex flex-col items-end gap-1.5 shrink-0">
                                <SentimentBadge sentiment={post.sentiment} />
                                <EmotionTag emotion={post.sentiment?.emotion} />
                            </div>
                        </div>
                        
                        <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-[#00f5d4]/0 to-[#7209b7]/0 opacity-0 group-hover:opacity-5 transition-opacity duration-500 pointer-events-none"></div>
                    </div>
                ))}
            </div>
        </div>
    );
}
