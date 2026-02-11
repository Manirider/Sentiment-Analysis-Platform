import { BarChart, Bar, XAxis, YAxis, Tooltip } from "recharts";

export default function EmotionBar({ data }) {
  const chartData = Object.entries(data).map(([emotion, count]) => ({
    emotion,
    count,
  }));

  return (
    <BarChart width={400} height={300} data={chartData}>
      <XAxis dataKey="emotion" />
      <YAxis />
      <Tooltip />
      <Bar dataKey="count" />
    </BarChart>
  );
}
