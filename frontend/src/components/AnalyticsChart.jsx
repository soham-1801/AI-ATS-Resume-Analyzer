
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer
} from "recharts";

const AnalyticsChart = ({ data = [] }) => {
  if (data.length === 0) {
    return (
      <div className="h-full flex items-center justify-center border border-dashed border-slate-800 rounded-lg text-slate-500 text-xs py-10">
        No assessment history logs to display.
      </div>
    );
  }

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
          <defs>
            <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#4f46e5" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#4f46e5" stopOpacity={0} />
            </linearGradient>
          </defs>
          <XAxis dataKey="date" stroke="#64748b" fontSize={11} tickLine={false} />
          <YAxis domain={[0, 100]} stroke="#64748b" fontSize={11} tickLine={false} />
          <Tooltip 
            contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "8px" }}
            labelStyle={{ color: "#94a3b8", fontSize: "11px" }}
            itemStyle={{ color: "#38bdf8", fontSize: "13px", fontWeight: "bold" }}
          />
          <Area 
            type="monotone" 
            dataKey="score" 
            stroke="#6366f1" 
            strokeWidth={2} 
            fillOpacity={1} 
            fill="url(#chartGradient)" 
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default AnalyticsChart;
