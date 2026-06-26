import { useState, useEffect } from "react";
import dashboardService from "../services/dashboardService";
import atsService from "../services/atsService";
import AnalyticsChart from "../components/AnalyticsChart";
import LoadingSpinner from "../components/LoadingSpinner";
import { 
  FileText, 
  TrendingUp, 
  Award, 
  Download,
  Calendar,
  Layers
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell
} from "recharts";

const Dashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [downloadingId, setDownloadingId] = useState(null);
  const [downloadError, setDownloadError] = useState("");

  const fetchAnalytics = async () => {
    try {
      const response = await dashboardService.getAnalytics();
      setData(response.data);
    } catch (err) {
      console.error("Failed to load dashboard data:", err);
      setError("Failed to retrieve dashboard analytics. Check database configuration.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchAnalytics();
  }, []);

  const handleDownloadPdf = async (resultId) => {
    console.log(`[DASHBOARD] handleDownloadPdf invoked. resultId:`, resultId, `type:`, typeof resultId);
    if (!resultId) {
      setDownloadError("Invalid audit result ID.");
      return;
    }
    console.log(`[DASHBOARD] Starting PDF report download for result ID: ${resultId}`);
    setDownloadError("");
    setDownloadingId(resultId);

    try {
      const response = await atsService.downloadPdf(resultId);
      const file = new Blob([response.data], { type: "application/pdf" });
      const fileURL = URL.createObjectURL(file);
      const link = document.createElement("a");
      link.href = fileURL;
      link.setAttribute("download", `ATS_Report_Result_${resultId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      console.log(`[DASHBOARD] Successful PDF download for result ID: ${resultId}`);
    } catch (err) {
      console.error("[DASHBOARD] Failed to download PDF report:", err);
      setDownloadError(err.response?.data?.detail || "Failed to download PDF evaluation report.");
    } finally {
      setDownloadingId(null);
    }
  };

  if (loading) {
    return <LoadingSpinner size="lg" />;
  }

  if (error) {
    return (
      <div className="p-4 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm">
        {error}
      </div>
    );
  }

  const chartData = data?.score_history || [];
  
  // Extract top skill for the metric card
  const topSkillItem = data?.top_skills && data.top_skills.length > 0 ? data.top_skills[0] : null;

  // Formatting skills data for Recharts distribution bar chart
  const skillChartData = data?.top_skills?.map(item => ({
    name: item.skill,
    count: item.count
  })) || [];

  const skillColors = ["#6366f1", "#3b82f6", "#10b981", "#f59e0b", "#ec4899", "#8b5cf6"];

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* 1. Metrics Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Total Resumes */}
        <div className="glass-card rounded-xl p-6 border border-slate-800/60 relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:scale-110 transition-transform">
            <FileText className="w-16 h-16 text-indigo-450" />
          </div>
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Resumes</p>
          <h3 className="text-3xl font-extrabold text-slate-100 mt-2">{data?.total_resumes}</h3>
          <p className="text-xs text-slate-500 mt-1">Uploaded document profiles</p>
        </div>

        {/* Total Analyses */}
        <div className="glass-card rounded-xl p-6 border border-slate-800/60 relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:scale-110 transition-transform">
            <TrendingUp className="w-16 h-16 text-blue-450" />
          </div>
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Analyses</p>
          <h3 className="text-3xl font-extrabold text-slate-100 mt-2">{data?.total_analyses}</h3>
          <p className="text-xs text-slate-500 mt-1">Comparisons executed</p>
        </div>

        {/* Average ATS Score */}
        <div className="glass-card rounded-xl p-6 border border-slate-800/60 relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:scale-110 transition-transform">
            <Award className="w-16 h-16 text-emerald-450" />
          </div>
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Average ATS Score</p>
          <h3 className="text-3xl font-extrabold text-emerald-405 mt-2">{data?.average_ats_score}%</h3>
          <p className="text-xs text-slate-500 mt-1">Weighted overlap alignment</p>
        </div>

        {/* Top Skill Card */}
        <div className="glass-card rounded-xl p-6 border border-slate-800/60 relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:scale-110 transition-transform">
            <Layers className="w-16 h-16 text-violet-400" />
          </div>
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Top Matched Skill</p>
          <h3 className="text-2xl font-extrabold text-violet-400 mt-2.5 truncate capitalize">
            {topSkillItem ? topSkillItem.skill : "N/A"}
          </h3>
          <p className="text-xs text-slate-500 mt-1">
            {topSkillItem ? `${topSkillItem.count} matches across profiles` : "No matches computed"}
          </p>
        </div>
      </div>

      {/* 2. Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Chart 1: ATS Score Trend */}
        <div className="glass-card rounded-xl p-6 border border-slate-800/60 space-y-4">
          <div>
            <h4 className="text-sm font-semibold text-slate-200">ATS Score Trend</h4>
            <p className="text-xs text-slate-500">Timeline view of scores across your last 10 audits</p>
          </div>
          <div className="h-64">
            <AnalyticsChart data={chartData} />
          </div>
        </div>

        {/* Chart 2: Skill Distribution */}
        <div className="glass-card rounded-xl p-6 border border-slate-800/60 space-y-4">
          <div>
            <h4 className="text-sm font-semibold text-slate-200">Skill Distribution</h4>
            <p className="text-xs text-slate-500">Most frequent technologies found in your profiles</p>
          </div>
          <div className="h-64">
            {skillChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={skillChartData} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                  <XAxis dataKey="name" stroke="#64748b" fontSize={10} tickLine={false} />
                  <YAxis stroke="#64748b" fontSize={10} tickLine={false} allowDecimals={false} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "8px" }}
                    itemStyle={{ color: "#38bdf8", fontSize: "12px", fontWeight: "bold" }}
                  />
                  <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                    {skillChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={skillColors[index % skillColors.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center border border-dashed border-slate-800 rounded-lg text-slate-500 text-xs">
                Run an ATS scan to see your tech skill frequencies
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 3. Table: Recent Analyses */}
      <div className="glass-card rounded-xl border border-slate-800/60 overflow-hidden">
        {/* Table Header */}
        <div className="p-6 border-b border-slate-800/60 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h4 className="text-sm font-semibold text-slate-200">Recent Analyses Logs</h4>
            <p className="text-xs text-slate-500">Detailed list of your latest assessments and PDF exports</p>
          </div>
          {downloadError && (
            <div className="px-4 py-2 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-450 text-xs flex items-center gap-3 animate-fadeIn">
              <span>{downloadError}</span>
              <button 
                onClick={() => setDownloadError("")} 
                className="text-rose-405 hover:text-rose-300 font-bold select-none cursor-pointer"
              >
                ✕
              </button>
            </div>
          )}
        </div>

        {/* Table Body */}
        <div className="overflow-x-auto">
          {chartData.length > 0 ? (
            <table className="w-full text-left border-collapse text-xs select-text">
              <thead>
                <tr className="border-b border-slate-800/60 bg-slate-900/30 text-slate-400 font-semibold uppercase tracking-wider">
                  <th className="p-4 pl-6">Analysis Date</th>
                  <th className="p-4">Target Position</th>
                  <th className="p-4 text-center">Score</th>
                  <th className="p-4 text-right pr-6">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-850">
                {[...chartData].reverse().slice(0, 5).map((item, index) => (
                  <tr key={index} className="hover:bg-slate-900/10 transition-colors">
                    <td className="p-4 pl-6 text-slate-300 font-medium">
                      <span className="flex items-center gap-2">
                        <Calendar className="w-3.5 h-3.5 text-slate-500" />
                        {item.date}
                      </span>
                    </td>
                    <td className="p-4 text-slate-200 font-semibold">{item.job_title}</td>
                    <td className="p-4 text-center">
                      <span className={`px-2 py-0.5 rounded-full font-bold inline-block border ${
                        item.score >= 75 
                          ? "bg-emerald-950/20 border-emerald-500/20 text-emerald-400" 
                          : item.score >= 50 
                            ? "bg-blue-950/20 border-blue-500/20 text-blue-400" 
                            : "bg-rose-950/20 border-rose-500/20 text-rose-400"
                      }`}>
                        {item.score}%
                      </span>
                    </td>
                    <td className="p-4 text-right pr-6">
                      <button
                        onClick={() => {
                          console.log("[DASHBOARD] PDF Report button clicked. Item data:", item);
                          handleDownloadPdf(item.id);
                        }}
                        disabled={downloadingId !== null}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-905 border border-slate-800 hover:border-slate-700 text-slate-400 hover:text-slate-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-semibold select-none cursor-pointer"
                      >
                        {downloadingId === item.id ? (
                          <div className="w-3.5 h-3.5 border-2 border-indigo-450 border-t-transparent rounded-full animate-spin" />
                        ) : (
                          <Download className="w-3.5 h-3.5" />
                        )}
                        {downloadingId === item.id ? "Downloading..." : "PDF Report"}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="text-center py-12 text-slate-500 border-none">
              No recent match records. Navigate to the ATS Scanner to begin.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
