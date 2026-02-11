export default function StatCard({ title, value, subtitle, color }) {
  const gradients = {
    cyan: "from-[#00b4d8]/20 to-[#0077b6]/5 border-[#00b4d8]/30 hover:border-[#00b4d8]",
    purple: "from-[#7209b7]/20 to-[#3c096c]/5 border-[#7209b7]/30 hover:border-[#7209b7]",
    green: "from-[#00f5d4]/20 to-[#00bb9f]/5 border-[#00f5d4]/30 hover:border-[#00f5d4]",
    pink: "from-[#f72585]/20 to-[#b5179e]/5 border-[#f72585]/30 hover:border-[#f72585]",
  };

  const textColors = {
    cyan: "text-[#00b4d8]",
    purple: "text-[#7209b7]",
    green: "text-[#00f5d4]",
    pink: "text-[#f72585]",
  };

  return (
    <div className={`
      relative overflow-hidden p-6 rounded-2xl border transition-all duration-300
      bg-gradient-to-br backdrop-blur-md group hover:-translate-y-1 hover:shadow-xl
      ${gradients[color] || gradients.cyan}
    `}>
      <div className="relative z-10">
        <p className="text-xs font-semibold tracking-wider text-zinc-400 uppercase mb-2">{title}</p>
        <div className="flex items-baseline gap-2">
            <h3 className="text-3xl font-bold text-white tracking-tight">{value}</h3>
        </div>
        <p className={`text-sm mt-2 font-medium ${textColors[color] || "text-zinc-500"}`}>
          {subtitle}
        </p>
      </div>
      
      
      <div className={`absolute -right-6 -bottom-6 w-24 h-24 rounded-full blur-2xl opacity-20 bg-current transition-opacity duration-300 group-hover:opacity-40 ${textColors[color]}`}></div>
    </div>
  );
}
