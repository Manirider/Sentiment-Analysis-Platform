import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell
} from "recharts";

const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
        return (
            <div className="glass-panel p-3 rounded-lg shadow-xl border border-[#00f5d4]/20">
                <p className="text-white font-medium text-sm mb-1">{label}</p>
                <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-[#00f5d4]"></span>
                    <span className="text-xs text-zinc-300">{payload[0].value} posts</span>
                </div>
            </div>
        );
    }
    return null;
};

export default function SentimentChart({ data }) {
  if (!data || data.length === 0) return null;

  const chartData = data.map((item) => ({
    name: item.label.charAt(0).toUpperCase() + item.label.slice(1),
    count: item.count || 0,
    color: item.label === 'positive' ? '#00f5d4' : item.label === 'negative' ? '#ff0055' : '#00b4d8'
  }));

  return (
    <div className="glass-panel rounded-2xl p-6 h-full flex flex-col">
      <h3 className="text-lg font-bold text-white mb-6 flex items-center gap-2">
         <span className="w-1 h-5 rounded-full bg-[#7209b7]"></span>
         Volume Analysis
      </h3>
      <div className="flex-1 w-full min-h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
            <XAxis 
                dataKey="name" 
                axisLine={false} 
                tickLine={false} 
                tick={{ fill: '#9ca3af', fontSize: 12 }} 
                dy={10}
            />
            <YAxis 
                axisLine={false} 
                tickLine={false} 
                tick={{ fill: '#9ca3af', fontSize: 12 }} 
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
            <Bar dataKey="count" radius={[6, 6, 6, 6]} barSize={40}>
                {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
