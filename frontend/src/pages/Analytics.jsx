import { useEffect, useState } from 'react';
import { fetchPosts } from '../services/api';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const COLORS = {
    positive: '#00f5d4',
    negative: '#ff0055',
    neutral: '#00b4d8',
};

const EMOTIONS = [
    { name: 'joy', color: '#facc15' },
    { name: 'sadness', color: '#3b82f6' },
    { name: 'anger', color: '#ef4444' },
    { name: 'fear', color: '#a855f7' },
    { name: 'surprise', color: '#ec4899' },
    { name: 'disgust', color: '#f97316' },
    { name: 'neutral', color: '#a1a1aa' },
];

const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
        return (
            <div className="glass-panel p-3 rounded-lg shadow-xl border border-white/10">
                <p className="text-white font-medium text-xs mb-1 uppercase tracking-wider opacity-70">{payload[0].name}</p>
                <p className="text-lg font-bold text-white leading-none">{payload[0].value}</p>
            </div>
        );
    }
    return null;
};

export default function Analytics() {
    const [posts, setPosts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        loadData();
        const interval = setInterval(loadData, 5000);
        return () => clearInterval(interval);
    }, []);

    async function loadData() {
        try {
            const data = await fetchPosts();
            setPosts(data.posts || []);
            setError(null);
        } catch (err) {
            setError('Failed to fetch analytics data');
        } finally {
            setLoading(false);
        }
    }

    const sentimentCounts = posts.reduce((acc, post) => {
        const sentiment = post.sentiment?.sentiment || 'processing';
        if (sentiment !== 'processing') acc[sentiment] = (acc[sentiment] || 0) + 1;
        return acc;
    }, {});
    if(!sentimentCounts.neutral) sentimentCounts.neutral = 0;

    const sentimentData = [
        { name: 'positive', value: sentimentCounts.positive || 0, fill: COLORS.positive },
        { name: 'negative', value: sentimentCounts.negative || 0, fill: COLORS.negative },
        { name: 'neutral', value: sentimentCounts.neutral || 0, fill: COLORS.neutral },
    ].filter(d => d.value > 0); 

    const emotionCounts = posts.reduce((acc, post) => {
        const emotion = post.sentiment?.emotion;
        if (emotion) acc[emotion] = (acc[emotion] || 0) + 1;
        return acc;
    }, {});

    const emotionData = EMOTIONS
        .map(e => ({ name: e.name, value: emotionCounts[e.name] || 0, fill: e.color }))
        .sort((a,b) => b.value - a.value)
        .filter(d => d.value > 0);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="w-10 h-10 border-2 border-[#00f5d4] border-t-transparent rounded-full animate-spin"></div>
            </div>
        );
    }

    return (
        <div className="space-y-8 animate-slide-in">
            <div className="flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-bold text-white mb-2 tracking-tight">Analytics Overview</h1>
                    <p className="text-zinc-400 text-sm">Deep dive into sentiment patterns and emotional trends.</p>
                </div>
                <button className="px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-zinc-300 text-sm font-medium hover:bg-white/10 hover:text-white transition-colors flex items-center gap-2">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
                    Export Report
                </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="glass-panel p-6 rounded-2xl lg:col-span-1 min-h-[400px] flex flex-col">
                    <h3 className="text-lg font-bold text-white mb-6">Sentiment Share</h3>
                    <div className="flex-1 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={sentimentData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={80}
                                    paddingAngle={5}
                                    dataKey="value"
                                    cornerRadius={5}
                                    stroke="none"
                                >
                                    {sentimentData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.fill} style={{ filter: `drop-shadow(0 0 8px ${entry.fill}50)` }} />
                                    ))}
                                </Pie>
                                <Tooltip content={<CustomTooltip />} />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                    <div className="flex justify-center gap-4 mt-4">
                        {sentimentData.map(d => (
                            <div key={d.name} className="flex items-center gap-2">
                                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: d.fill }}></span>
                                <span className="text-xs text-zinc-400 capitalize">{d.name}</span>
                            </div>
                        ))}
                    </div>
                </div>


                <div className="glass-panel p-6 rounded-2xl lg:col-span-2 min-h-[400px] flex flex-col">
                    <h3 className="text-lg font-bold text-white mb-6">Emotional Spectrum</h3>
                    <div className="flex-1 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={emotionData} layout="vertical" margin={{ left: 40, right: 20 }}>
                                <XAxis type="number" hide />
                                <YAxis 
                                    dataKey="name" 
                                    type="category" 
                                    axisLine={false} 
                                    tickLine={false}
                                    tick={{ fill: '#9ca3af', fontSize: 11, textTransform: 'capitalize' }}
                                    width={60} 
                                />
                                <Tooltip content={<CustomTooltip />} cursor={{fill: 'rgba(255,255,255,0.02)'}} />
                                <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={20}>
                                    {emotionData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.fill} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>


            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                    { label: 'Total Analyzed', value: posts.length, color: 'text-white', sub: 'Posts' },
                    { label: 'Positive', value: sentimentCounts.positive || 0, color: 'text-[#00f5d4]', sub: 'Constructive' },
                    { label: 'Negative', value: sentimentCounts.negative || 0, color: 'text-[#ff0055]', sub: 'Critical' },
                    { label: 'Neutral', value: sentimentCounts.neutral || 0, color: 'text-[#00b4d8]', sub: 'Objective' },
                ].map((stat, i) => (
                    <div key={i} className="glass-panel p-5 rounded-xl text-center hover:bg-white/5 transition-colors">
                        <p className={`text-4xl font-bold mb-1 tracking-tighter ${stat.color}`}>{stat.value}</p>
                        <p className="text-xs text-zinc-500 uppercase tracking-widest font-semibold">{stat.label}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}
