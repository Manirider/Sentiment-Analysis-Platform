import { useRef } from 'react';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";

const COLORS = {
  positive: "#00f5d4",
  negative: "#ff0055",
  neutral: "#00b4d8",
};

const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
        return (
            <div className="glass-panel p-3 rounded-lg shadow-xl">
                <p className="text-white font-medium text-sm">{payload[0].name}</p>
                <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs text-zinc-300">count:</span>
                    <span className="text-[#00f5d4] font-bold">{payload[0].value}</span>
                </div>
            </div>
        );
    }
    return null;
};

export default function DistributionChart({ data }) {
  if (!data || data.length === 0) return null;

  const total = data.reduce((sum, item) => sum + (item.count || 0), 0);
  if (total === 0) return null;

  const chartData = data
    .filter((item) => (item.count || 0) > 0)
    .map((item) => ({
      name: item.label.charAt(0).toUpperCase() + item.label.slice(1),
      value: item.count || 0,
      color: COLORS[item.label] || "#6b7280",
    }));

  return (
    <div className="glass-panel rounded-2xl p-6 h-full flex flex-col">
      <h3 className="text-lg font-bold text-white mb-6 flex items-center gap-2">
        <span className="w-1 h-5 rounded-full bg-[#00f5d4]"></span>
        Sentiment Distribution
      </h3>
      <div className="flex-1 w-full min-h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              innerRadius={80}
              outerRadius={110}
              paddingAngle={4}
              stroke="none"
              cornerRadius={6}
            >
              {chartData.map((entry, index) => (
                <Cell 
                    key={`cell-${index}`} 
                    fill={entry.color}
                    style={{ filter: `drop-shadow(0px 0px 8px ${entry.color}40)` }}
                />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} cursor={false} />
            <Legend 
                verticalAlign="bottom" 
                height={36} 
                iconType="circle"
                formatter={(value) => <span className="text-zinc-400 text-sm font-medium ml-1">{value}</span>}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
