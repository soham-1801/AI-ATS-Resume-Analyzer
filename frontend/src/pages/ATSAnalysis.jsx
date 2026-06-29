import { useState, useEffect } from "react";
import resumeService from "../services/resumeService";
import atsService from "../services/atsService";
import SkillMatchCard from "../components/SkillMatchCard";
import LoadingSpinner from "../components/LoadingSpinner";
import { 
  Sparkles, 
  FileText, 
  Briefcase, 
  AlertCircle, 
  CheckCircle,
  Download,
  BrainCircuit,
  PenTool,
  Check,
  TrendingUp,
  Cpu,
  Info,
  ChevronRight,
  Lightbulb,
  BookOpen
} from "lucide-react";

// Helper component for Score circular SVG gauge
const ScoreGauge = ({ score }) => {
  const radius = 64;
  const stroke = 8;
  const normalizedRadius = radius - stroke * 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  let color = "stroke-rose-500";
  let textColor = "text-rose-450";
  let bgGradient = "from-rose-500/10 to-rose-500/5";
  let borderGlow = "border-rose-500/20";
  
  if (score >= 75) {
    color = "stroke-emerald-500";
    textColor = "text-emerald-400";
    bgGradient = "from-emerald-500/10 to-emerald-500/5";
    borderGlow = "border-emerald-500/20";
  } else if (score >= 50) {
    color = "stroke-indigo-500";
    textColor = "text-indigo-400";
    bgGradient = "from-indigo-500/10 to-indigo-500/5";
    borderGlow = "border-indigo-500/20";
  }

  return (
    <div className={`relative flex flex-col items-center justify-center p-6 rounded-xl border ${borderGlow} bg-gradient-to-br ${bgGradient} backdrop-blur-md h-full min-h-[220px]`}>
      <div className="relative w-32 h-32 flex items-center justify-center">
        <svg height={radius * 2} width={radius * 2} className="transform -rotate-90">
          {/* Base track */}
          <circle
            stroke="#1e293b"
            fill="transparent"
            strokeWidth={stroke}
            r={normalizedRadius}
            cx={radius}
            cy={radius}
          />
          {/* Active progress track */}
          <circle
            className={`${color} transition-all duration-1000 ease-out`}
            fill="transparent"
            strokeWidth={stroke}
            strokeDasharray={circumference + " " + circumference}
            style={{ strokeDashoffset }}
            strokeLinecap="round"
            r={normalizedRadius}
            cx={radius}
            cy={radius}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`text-3xl font-extrabold tracking-tight ${textColor}`}>{score}%</span>
          <span className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold mt-0.5">ATS Score</span>
        </div>
      </div>
      <h5 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-3">Final Overlay Match</h5>
    </div>
  );
};

// Helper component for Keyword and Semantic score progress bars
const ScoreProgressBar = ({ score, title, subtitle, color }) => {
  let barColor = "bg-indigo-500";
  let textColor = "text-indigo-400";
  let bgGradient = "from-indigo-500/5 to-indigo-500/0";
  let borderColor = "border-indigo-500/10";
  
  if (color === "blue") {
    barColor = "bg-blue-500";
    textColor = "text-blue-400";
    bgGradient = "from-blue-500/5 to-blue-500/0";
    borderColor = "border-blue-500/10";
  } else if (color === "emerald") {
    barColor = "bg-emerald-500";
    textColor = "text-emerald-400";
    bgGradient = "from-emerald-500/5 to-emerald-500/0";
    borderColor = "border-emerald-500/10";
  } else if (color === "rose") {
    barColor = "bg-rose-500";
    textColor = "text-rose-400";
    bgGradient = "from-rose-500/5 to-rose-500/0";
    borderColor = "border-rose-500/10";
  }

  return (
    <div className={`p-6 rounded-xl border ${borderColor} bg-gradient-to-br ${bgGradient} flex flex-col justify-between h-full min-h-[220px]`}>
      <div className="space-y-1">
        <h5 className="text-xs font-semibold text-slate-350 uppercase tracking-wider">{title}</h5>
        <p className="text-[10px] text-slate-505 leading-relaxed">{subtitle}</p>
      </div>
      
      <div className="mt-6 space-y-3.5">
        <div className="flex justify-between items-end">
          <span className={`text-3xl font-extrabold ${textColor}`}>{score}%</span>
          <span className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">Matching Accuracy</span>
        </div>
        <div className="h-2 bg-slate-900/80 rounded-full overflow-hidden w-full border border-slate-800/40">
          <div 
            className={`h-full ${barColor} transition-all duration-1000 ease-out`} 
            style={{ width: `${score}%` }}
          />
        </div>
      </div>
    </div>
  );
};


// Helper parser to decompose the DB suggestions markdown string
const parseSuggestions = (markdownText) => {
  if (!markdownText) return {};
  const sections = {};
  const parts = markdownText.split("### ");
  
  parts.forEach((part) => {
    if (!part.trim()) return;
    const lines = part.split("\n");
    const title = lines[0].trim();
    const content = lines.slice(1).join("\n").trim();
    
    if (content.startsWith("*") || content.startsWith("-")) {
      // Clean and extract array lists
      const items = content
        .split(/\n[*-]\s+/)
        .map((item) => item.replace(/^[*-]\s+/, "").trim())
        .filter(Boolean);
      sections[title] = items;
    } else {
      sections[title] = content;
    }
  });
  return sections;
};

const ATSAnalysis = () => {
  const [resumes, setResumes] = useState([]);
  const [jds, setJds] = useState([]);
  
  const [selectedResume, setSelectedResume] = useState("");
  const [selectedJd, setSelectedJd] = useState("");
  
  const [loadingLists, setLoadingLists] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // AI Rewriter Modal states
  const [showRewriter, setShowRewriter] = useState(false);
  const [rewriteSection, setRewriteSection] = useState("summary");
  const [rewriteContent, setRewriteContent] = useState("");
  const [rewriting, setRewriting] = useState(false);
  const [rewrittenContent, setRewrittenContent] = useState("");

  const loadSelectionOptions = async () => {
    try {
      const [resumesRes, jdsRes] = await Promise.all([
        resumeService.getAll(),
        atsService.getAllJds()
      ]);
      setResumes(resumesRes.data);
      setJds(jdsRes.data);
      
      if (Array.isArray(resumesRes.data) && resumesRes.data.length > 0) {
        setSelectedResume(resumesRes.data[0].id);
      }
      if (Array.isArray(jdsRes.data) && jdsRes.data.length > 0) {
        setSelectedJd(jdsRes.data[0].id);
      }
    } catch (err) {
      console.error("Failed to load selection lists:", err);
      setError("Failed to retrieve resumes or job profiles.");
    } finally {
      setLoadingLists(false);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadSelectionOptions();
  }, []);

  const handleAnalyze = async () => {
    if (!selectedResume || !selectedJd) return;

    setError("");
    setSuccess("");
    setAnalyzing(true);
    setResult(null);

    try {
      const response = await atsService.analyze(selectedResume, selectedJd);
      setResult(response.data);
      setSuccess("ATS evaluation completed successfully!");
    } catch (err) {
      setError(err.response?.data?.detail || "An error occurred during resume evaluation.");
    } finally {
      setAnalyzing(false);
    }
  };

  const handleDownloadPdf = async () => {
    if (!result || !result.id) {
      setError("No analysis record available to download PDF report.");
      return;
    }
    setError("");
    setSuccess("");
    setDownloadingPdf(true);

    try {
      const response = await atsService.downloadPdf(result.id);
      const file = new Blob([response.data], { type: "application/pdf" });
      const fileURL = URL.createObjectURL(file);
      const link = document.createElement("a");
      link.href = fileURL;
      link.setAttribute("download", `ATS_Report_Result_${result.id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      setSuccess("PDF report downloaded successfully!");
    } catch (err) {
      console.error("Failed to download PDF report:", err);
      let errorMsg = "Failed to download authenticated PDF report.";
      if (err.response?.data instanceof Blob) {
        try {
          const text = await err.response.data.text();
          const json = JSON.parse(text);
          if (json.detail) {
            errorMsg = json.detail;
          } else if (json.message) {
            errorMsg = json.message;
          }
        } catch (e) {}
      } else if (err.response?.data?.detail) {
        errorMsg = err.response.data.detail;
      }
      setError(errorMsg);
    } finally {
      setDownloadingPdf(false);
    }
  };

  const handleRewrite = async () => {
    if (!rewriteContent.trim()) return;
    setRewriting(true);
    setRewrittenContent("");
    
    try {
      const response = await atsService.rewriteSection(rewriteSection, rewriteContent);
      setRewrittenContent(response.data.improved_content);
    } catch (err) {
      console.error("Rewrite error:", err);
      setRewrittenContent("[Error] Failed to generate rewritten content.");
    } finally {
      setRewriting(false);
    }
  };

  // Parse structured AI recommendations
  const suggestionsData = result ? parseSuggestions(result.suggestions) : {};
  
  const keywordsString = suggestionsData["Recommended Keywords to Add"] || "";
  const missingKeywords = typeof keywordsString === "string"
    ? keywordsString.split(", ").map(kw => kw.replace(/\*\*/g, "").trim()).filter(Boolean)
    : Array.isArray(keywordsString)
      ? keywordsString
      : [];

  const summaryImprovement = suggestionsData["Summary Improvement Suggestions"] || "";
  
  const projectSuggestions = Array.isArray(suggestionsData["Project Recommendations"]) 
    ? suggestionsData["Project Recommendations"] 
    : suggestionsData["Project Recommendations"] 
      ? [suggestionsData["Project Recommendations"]] 
      : [];

  const experienceSuggestions = Array.isArray(suggestionsData["Experience Formatting Tips"])
    ? suggestionsData["Experience Formatting Tips"]
    : suggestionsData["Experience Formatting Tips"]
      ? [suggestionsData["Experience Formatting Tips"]]
      : [];

  const generalTips = Array.isArray(suggestionsData["General ATS Optimizations"])
    ? suggestionsData["General ATS Optimizations"]
    : suggestionsData["General ATS Optimizations"]
      ? [suggestionsData["General ATS Optimizations"]]
      : [];

  return (
    <div className="space-y-8 relative">
      {/* Alert Banners */}
      {error && (
        <div className="p-4 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm flex items-center gap-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}
      {success && (
        <div className="p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm flex items-center gap-3">
          <CheckCircle className="w-5 h-5 flex-shrink-0" />
          <span>{success}</span>
        </div>
      )}

      {/* Select Box Panel */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-end glass-card p-6 rounded-xl border border-slate-800/60">
        {/* Select Resume */}
        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-slate-300 flex items-center gap-2">
            <FileText className="w-3.5 h-3.5 text-indigo-400" />
            1. Select Resume
          </label>
          {loadingLists ? (
            <div className="h-10 bg-slate-900 border border-slate-800 rounded-lg animate-pulse" />
          ) : Array.isArray(resumes) && resumes.length > 0 ? (
            <select
              value={selectedResume}
              onChange={(e) => setSelectedResume(e.target.value)}
              className="w-full h-10 px-3 rounded-lg bg-slate-950/60 border border-slate-800 text-sm text-slate-205 outline-none focus:border-indigo-500"
            >
              {resumes.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.file_name}
                </option>
              ))}
            </select>
          ) : (
            <div className="text-xs text-rose-400 p-2 border border-rose-900/30 rounded-lg bg-rose-950/10">
              No resumes found. Upload one first.
            </div>
          )}
        </div>

        {/* Select Job Profile */}
        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-slate-300 flex items-center gap-2">
            <Briefcase className="w-3.5 h-3.5 text-emerald-400" />
            2. Select Job Profile
          </label>
          {loadingLists ? (
            <div className="h-10 bg-slate-900 border border-slate-800 rounded-lg animate-pulse" />
          ) : Array.isArray(jds) && jds.length > 0 ? (
            <select
              value={selectedJd}
              onChange={(e) => setSelectedJd(e.target.value)}
              className="w-full h-10 px-3 rounded-lg bg-slate-950/60 border border-slate-800 text-sm text-slate-205 outline-none focus:border-indigo-500"
            >
              {jds.map((jd) => (
                <option key={jd.id} value={jd.id}>
                  ID #{jd.id} - {jd.description ? jd.description.substring(0, 30) : ""}...
                </option>
              ))}
            </select>
          ) : (
            <div className="text-xs text-rose-400 p-2 border border-rose-900/30 rounded-lg bg-rose-950/10">
              No job profiles found. Add one first.
            </div>
          )}
        </div>

        {/* Action button */}
        <button
          onClick={handleAnalyze}
          disabled={analyzing || !selectedResume || !selectedJd}
          className="h-10 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm transition-all flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/20 disabled:opacity-50"
        >
          <Sparkles className="w-4 h-4" />
          {analyzing ? "Running Evaluation..." : "Run ATS Analysis"}
        </button>
      </div>

      {/* Analysis Loader */}
      {analyzing && <LoadingSpinner size="lg" />}

      {/* Results View */}
      {result && !analyzing && (
        <div className="space-y-8 animate-fadeIn">
          
          {/* 1. Score cards section */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            
            {/* ATS Score Gauge Component */}
            <ScoreGauge score={result.final_score} />
            
            {/* Keyword Score Component */}
            <ScoreProgressBar 
              score={result.keyword_score} 
              title="Keyword Matching" 
              subtitle="Measures matching dictionary metrics and TF-IDF weighted vectors."
              color="blue"
            />
            
            {/* Semantic Score Component */}
            <ScoreProgressBar 
              score={result.semantic_score} 
              title="Semantic Alignment" 
              subtitle="Evaluates semantic context overlap using natural language models."
              color="indigo"
            />

            {/* Quick Actions Panel */}
            <div className="glass-card border border-slate-800/60 p-6 rounded-xl flex flex-col justify-center gap-4 h-full min-h-[220px]">
              <h5 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Workspace Tools</h5>
              <div className="space-y-3 flex-1 flex flex-col justify-center">
                <button
                  onClick={handleDownloadPdf}
                  disabled={downloadingPdf}
                  className="w-full py-2.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-slate-200 text-xs font-bold transition-all flex items-center justify-center gap-2 disabled:opacity-60"
                >
                  <Download className={`w-4 h-4 ${downloadingPdf ? "animate-bounce" : ""}`} />
                  {downloadingPdf ? "Creating Report..." : "Download PDF Report"}
                </button>
                <button
                  onClick={() => setShowRewriter(true)}
                  className="w-full py-2.5 rounded-lg bg-indigo-600/10 hover:bg-indigo-600/20 border border-indigo-500/20 hover:border-indigo-500/30 text-indigo-400 text-xs font-bold transition-all flex items-center justify-center gap-2"
                >
                  <PenTool className="w-4 h-4" />
                  AI Rewrite Assistant
                </button>
              </div>
            </div>
          </div>

          {/* ATS Intelligence Dashboard & Category-Wise Breakdown */}
          {result.intelligence_layer && (
            <div className="space-y-8">
              {/* Category-Wise Score Breakdown and Improvement Percentage Engine */}
              {result.category_breakdown && (
                <div className="glass-card p-6 rounded-xl border border-slate-800/60 space-y-6">
                  <div>
                    <h4 className="text-xs font-bold text-slate-350 uppercase tracking-widest font-sans flex items-center gap-2">
                      <BrainCircuit className="w-4.5 h-4.5 text-indigo-400" />
                      📊 ATS Category-Wise Breakdown & Improvement Engine
                    </h4>
                    <p className="text-xs text-slate-500 mt-1 font-sans">
                      Deep analysis of your resume against ATS criteria with target benchmarks and recovery pathways.
                    </p>
                  </div>

                  {/* 1. Category Breakdown Grid */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 font-sans">
                    {result.category_breakdown.map((cat) => {
                      const score = Math.round(cat.score);
                      const target = 80;
                      const impNeeded = Math.round(cat.improvement_needed || Math.max(0, target - score));
                      
                      // Progress bar widths
                      const currentWidth = Math.min(100, score);
                      const gapWidth = score < target ? target - score : 0;
                      
                      // Color helpers
                      let barColor = "bg-rose-500";
                      let textColor = "text-rose-400";
                      let borderColor = "border-rose-500/20";
                      let bgGradient = "from-rose-500/10 to-rose-500/5";
                      
                      if (score >= target) {
                        barColor = "bg-emerald-500";
                        textColor = "text-emerald-400";
                        borderColor = "border-emerald-500/20";
                        bgGradient = "from-emerald-500/10 to-emerald-500/5";
                      } else if (score >= 60) {
                        barColor = "bg-amber-500";
                        textColor = "text-amber-400";
                        borderColor = "border-amber-500/20";
                        bgGradient = "from-amber-500/10 to-amber-500/5";
                      }

                      // Weight mapping
                      const weights = {
                        "formatting": "20%",
                        "keywords": "25%",
                        "content": "25%",
                        "validation": "15%",
                        "compatibility": "15%"
                      };
                      const nameKey = cat.name.toLowerCase();
                      let weightStr = "20%";
                      for (const [kw, w] of Object.entries(weights)) {
                        if (nameKey.includes(kw)) {
                          weightStr = w;
                          break;
                        }
                      }

                      return (
                        <div key={cat.name} className={`p-5 rounded-xl border ${borderColor} bg-gradient-to-br ${bgGradient} space-y-4 flex flex-col justify-between`}>
                          <div className="space-y-3.5">
                            {/* Header info */}
                            <div className="flex justify-between items-start">
                              <div>
                                <span className="text-xs font-bold text-slate-205 uppercase tracking-wide block">{cat.name}</span>
                                <span className="text-[10px] text-slate-500 font-semibold uppercase">Weight: {weightStr}</span>
                              </div>
                              <div className="text-right">
                                <span className={`text-xl font-extrabold block ${textColor}`}>{score}%</span>
                                <span className="text-[9px] text-slate-500 font-medium">Target: {target}%</span>
                              </div>
                            </div>

                            {/* Visual Progress Bar (Current, Target Marker, Improvement Gap) */}
                            <div className="space-y-1">
                              <div className="relative h-2.5 bg-slate-950/80 rounded-full overflow-hidden w-full border border-slate-800/40 flex">
                                {/* Current progress */}
                                <div 
                                  className={`h-full ${barColor} transition-all duration-1000 ease-out`} 
                                  style={{ width: `${currentWidth}%` }}
                                />
                                {/* Improvement Gap (only shown if current score < 80%) */}
                                {gapWidth > 0 && (
                                  <div 
                                    className="h-full bg-amber-500/30 border-l border-dashed border-amber-400/50 transition-all duration-1000 ease-out" 
                                    style={{ width: `${gapWidth}%` }}
                                  />
                                )}
                                {/* Target marker line (80%) */}
                                <div 
                                  className="absolute h-full w-[2px] bg-indigo-400 top-0 z-10 opacity-70"
                                  style={{ left: "80%" }}
                                  title="Target Score Benchmark (80%)"
                                />
                              </div>
                              
                              {/* Label values below bar */}
                              <div className="flex justify-between text-[9px] text-slate-500 font-semibold font-mono px-1">
                                <span>0%</span>
                                <span className="text-indigo-400 font-bold">Target: 80%</span>
                                <span>100%</span>
                              </div>
                            </div>

                            {/* Improvement Needed details */}
                            <div className="bg-slate-950/30 p-2.5 rounded-lg border border-slate-900/60 flex justify-between items-center text-xs">
                              <span className="text-slate-400">Improvement Needed:</span>
                              {impNeeded > 0 ? (
                                <strong className="text-rose-450 font-mono">+{impNeeded}%</strong>
                              ) : (
                                <span className="text-emerald-400 font-bold flex items-center gap-1">
                                  <Check className="w-3.5 h-3.5" /> Target Met
                                </span>
                              )}
                            </div>

                            {/* Recommendations */}
                            <div className="space-y-2">
                              <span className="text-[10px] font-bold text-slate-450 uppercase tracking-widest block font-sans">Optimization Action Items</span>
                              {cat.recommendations && cat.recommendations.length > 0 ? (
                                <ul className="space-y-1.5">
                                  {cat.recommendations.map((rec, idx) => (
                                    <li key={idx} className="text-xs text-slate-300 leading-relaxed flex items-start gap-2 select-text font-sans">
                                      <span className="text-indigo-400 mt-0.5">•</span>
                                      <span>{rec}</span>
                                    </li>
                                  ))}
                                </ul>
                              ) : (
                                <span className="text-xs text-slate-500 font-sans italic">No outstanding adjustments required.</span>
                              )}
                            </div>

                            {/* Diagnostics Output */}
                            {nameKey.includes("formatting") && cat.why_this_score && (
                              <div className="space-y-2 mt-4 pt-3 border-t border-slate-900/40 text-left">
                                <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest block font-sans">Formatting Diagnostics</span>
                                <div className="bg-slate-950/45 p-3 rounded-lg border border-slate-900/80 font-mono text-[11px] leading-relaxed text-slate-300 whitespace-pre-line select-text">
                                  {cat.why_this_score}
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  {/* 2. Improvement Summary & Predicted Future Score side-by-side */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4 border-t border-slate-900/60">
                    {/* Improvement Summary ("How to Reach 80% ATS Score") */}
                    <div className="p-5 rounded-xl bg-slate-950/15 border border-slate-900/60 space-y-4">
                      <div>
                        <h5 className="text-xs font-bold text-slate-300 uppercase tracking-widest font-sans flex items-center gap-2">
                          <TrendingUp className="w-4 h-4 text-emerald-450" />
                          How to Reach 80% ATS Score
                        </h5>
                        <p className="text-[10px] text-slate-500 mt-0.5">Step-by-step optimization strategy to surpass candidate screening benchmarks.</p>
                      </div>
                      
                      {result.intelligence_layer.improvement_summary && result.intelligence_layer.improvement_summary.length > 0 ? (
                        <ul className="space-y-2.5">
                          {result.intelligence_layer.improvement_summary.map((item, idx) => (
                            <li key={idx} className="flex gap-2.5 items-start text-xs text-slate-350 leading-normal bg-slate-950/20 p-3 rounded-lg border border-slate-900/50">
                              <Check className="w-4 h-4 text-emerald-500 mt-0.5 flex-shrink-0" />
                              <span>{item}</span>
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <div className="flex gap-2.5 items-start text-xs text-emerald-400 bg-emerald-950/10 p-3 rounded-lg border border-emerald-900/20">
                          <Check className="w-4 h-4 text-emerald-400 mt-0.5 flex-shrink-0" />
                          <span>Congratulations! Your profile already meets or exceeds all 80% target benchmarks.</span>
                        </div>
                      )}
                    </div>

                    {/* Predicted ATS Score after improvements */}
                    <div className="p-5 rounded-xl bg-slate-950/20 border border-slate-900/80 flex flex-col justify-between items-center text-center space-y-4">
                      <div className="space-y-1">
                        <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest block font-sans">Predicted ATS Score</span>
                        <span className="text-xs text-slate-500 font-medium">Estimated Match Rate After Recommendations Applied</span>
                      </div>

                      <div className="p-6 bg-slate-950/40 rounded-xl border border-slate-900 w-full max-w-[280px] space-y-2">
                        <span className="text-4xl font-extrabold text-emerald-450 tracking-tight font-mono block">
                          {result.estimated_future_score || "78% - 85%"}
                        </span>
                        <span className="text-[9px] text-slate-500 font-semibold uppercase tracking-wider font-sans">
                          Optimized Match Tier
                        </span>
                      </div>

                      <p className="text-[11px] text-slate-400 leading-relaxed font-sans max-w-sm">
                        Implementing the category adjustments above will resolve formatting, keyword relevance, and validation gaps, raising your score to the estimated range.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Part 3: Keywords Analysis */}
              <div className="glass-card p-6 rounded-xl border border-slate-800/60 space-y-5">
                <div>
                  <h4 className="text-xs font-bold text-slate-300 uppercase tracking-widest font-sans">🔍 Keywords Analysis</h4>
                  <p className="text-xs text-slate-500 mt-1 font-sans">Detailed report on matched skills, missing skills, and score recovery weight per keyword.</p>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 font-sans">
                  <div className="bg-slate-950/15 p-5 rounded-xl border border-slate-900 space-y-3 flex flex-col justify-between">
                    <div>
                      <span className="text-[10px] font-bold text-emerald-450 uppercase tracking-widest block font-sans mb-3">✓ Matched Skills</span>
                      <div className="flex flex-wrap gap-1.5">
                        {result.matched_skills && result.matched_skills.length > 0 ? (
                          result.matched_skills.map((skill) => (
                            <span key={skill} className="px-2 py-1 rounded text-[10px] font-mono bg-emerald-950/10 border border-emerald-500/20 text-emerald-400 select-all">
                              {skill}
                            </span>
                          ))
                        ) : (
                          <span className="text-xs text-slate-550">No matched skills identified yet.</span>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-slate-950/15 p-5 rounded-xl border border-slate-900 space-y-4">
                    <span className="text-[10px] font-bold text-rose-400 uppercase tracking-widest block font-sans">⚠️ Missing Skills</span>
                    
                    <div className="space-y-2 max-h-[200px] overflow-y-auto pr-1">
                      {result.intelligence_layer.missing_skills_impact && result.intelligence_layer.missing_skills_impact.length > 0 ? (
                        <ul className="space-y-2 text-xs">
                          {result.intelligence_layer.missing_skills_impact.map((item) => (
                            <li key={item.skill} className="flex justify-between items-center bg-slate-950/30 px-3 py-1.5 rounded border border-slate-900 select-text">
                              <span className="font-mono text-slate-205">{item.skill} (+{item.impact}%)</span>
                              <span className="font-bold text-indigo-400 font-mono">+{item.impact}% Recovery</span>
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <span className="text-xs text-slate-550">No missing skills detected!</span>
                      )}
                    </div>
                    
                    <div className="pt-3 border-t border-slate-900/60 flex justify-between items-center text-xs">
                      <span className="font-semibold text-slate-450 uppercase tracking-wider text-[10px]">Total Gain</span>
                      <span className="font-extrabold text-emerald-450 font-mono bg-emerald-950/20 px-2.5 py-0.5 rounded border border-emerald-500/30">
                        +{result.intelligence_layer.total_skills_impact_gain}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Part 5: Strengths & Weaknesses */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 font-sans">
                <div className="glass-card p-6 rounded-xl border border-slate-800/60 space-y-3.5">
                  <h5 className="text-xs font-bold text-emerald-400 uppercase tracking-widest font-sans">💪 Strengths</h5>
                  <ul className="space-y-2 text-xs text-slate-300 pl-1 list-none font-sans select-text">
                    {result.intelligence_layer.strengths.map((str, idx) => (
                      <li key={idx} className="flex items-center gap-2">
                        <span className="text-emerald-500 font-bold">✓</span>
                        <span>{str}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                
                <div className="glass-card p-6 rounded-xl border border-slate-800/60 space-y-3.5">
                  <h5 className="text-xs font-bold text-rose-450 uppercase tracking-widest font-sans">⚠️ Weaknesses</h5>
                  <ul className="space-y-2 text-xs text-slate-300 pl-1 list-none font-sans select-text">
                    {result.intelligence_layer.weaknesses.map((weak, idx) => (
                      <li key={idx} className="flex items-center gap-2">
                        <span className="text-rose-500 font-bold">✗</span>
                        <span>{weak}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Part 6: Recruiter Readiness */}
              <div className="glass-card p-6 rounded-xl border border-slate-800/60 space-y-4">
                <div>
                  <h4 className="text-xs font-bold text-slate-350 uppercase tracking-widest font-sans">💼 Recruiter Readiness & Hiring Probability</h4>
                  <p className="text-xs text-slate-500 mt-1 font-sans">Current standing versus projected interview readiness metrics.</p>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 font-sans">
                  <div className="bg-slate-950/15 p-5 rounded-xl border border-slate-900 space-y-3">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block font-sans">Recruiter Readiness</span>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-1">
                        <span className="text-[9px] text-slate-500 uppercase font-semibold">Current</span>
                        <p className="text-sm font-bold text-rose-455">{result.intelligence_layer.readiness_indicator}</p>
                      </div>
                      <div className="space-y-1">
                        <span className="text-[9px] text-slate-500 uppercase font-semibold">Projected</span>
                        <p className="text-sm font-bold text-emerald-450">Interview Ready</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-slate-950/15 p-5 rounded-xl border border-slate-900 space-y-3">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block font-sans">Hiring Probability Indicator</span>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-1">
                        <span className="text-[9px] text-slate-500 uppercase font-semibold">Current Probability</span>
                        <p className="text-sm font-bold text-rose-455">{Math.round(result.intelligence_layer.current_score * 0.9)}% ({result.intelligence_layer.hiring_probability})</p>
                      </div>
                      <div className="space-y-1">
                        <span className="text-[9px] text-slate-500 uppercase font-semibold">Projected Probability</span>
                        <p className="text-sm font-bold text-emerald-450">{Math.round(result.intelligence_layer.projected_score * 0.9)}% (High)</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Part 7: Resume Section Detection */}
              <div className="glass-card p-6 rounded-xl border border-slate-800/60 space-y-4">
                <div>
                  <h4 className="text-xs font-bold text-slate-300 uppercase tracking-widest font-sans">🔍 Resume Section Detection</h4>
                  <p className="text-xs text-slate-500 mt-1 font-sans">Verification of structural components parsed from the resume.</p>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 font-sans">
                  <div className="bg-slate-950/15 p-5 rounded-xl border border-slate-900/60 space-y-3">
                    <span className="text-[10px] font-bold text-emerald-450 uppercase tracking-widest block font-sans">Found Sections</span>
                    <ul className="space-y-2 text-xs">
                      {result.intelligence_layer.found_sections && result.intelligence_layer.found_sections.length > 0 ? (
                        result.intelligence_layer.found_sections.map((sec, idx) => (
                          <li key={idx} className="flex items-center gap-2 text-slate-300 select-text">
                            <span className="text-emerald-500 font-bold">✓</span>
                            <span>{sec}</span>
                          </li>
                        ))
                      ) : (
                        <li className="text-slate-500">No sections identified</li>
                      )}
                    </ul>
                  </div>

                  <div className="bg-slate-950/15 p-5 rounded-xl border border-slate-900/60 space-y-3">
                    <span className="text-[10px] font-bold text-rose-450 uppercase tracking-widest block font-sans">Missing Sections</span>
                    <ul className="space-y-2 text-xs">
                      {result.intelligence_layer.missing_sections && result.intelligence_layer.missing_sections.length > 0 ? (
                        result.intelligence_layer.missing_sections.map((sec, idx) => (
                          <li key={idx} className="flex items-center gap-2 text-slate-300 select-text">
                            <span className="text-rose-500 font-bold">✗</span>
                            <span>{sec}</span>
                          </li>
                        ))
                      ) : (
                        <li className="text-emerald-400 flex items-center gap-1.5">
                          <span>✓</span> All standard resume sections present!
                        </li>
                      )}
                    </ul>
                  </div>
                </div>
              </div>

              {/* Part 8: ATS Keyword Coverage */}
              <div className="glass-card p-6 rounded-xl border border-slate-800/60 space-y-5">
                <div>
                  <h4 className="text-xs font-bold text-slate-300 uppercase tracking-widest font-sans">📊 ATS Keyword Coverage</h4>
                  <p className="text-xs text-slate-500 mt-1 font-sans">Comparison metrics between Job Description requirements and resume content.</p>
                </div>
                
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 font-sans">
                  {/* Coverage Percentage Card */}
                  <div className="bg-slate-950/20 p-5 rounded-xl border border-slate-900 flex flex-col justify-between items-center text-center space-y-3">
                    <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest block">Keyword Coverage</span>
                    <span className="text-4xl font-extrabold text-indigo-300 font-sans mt-2">
                      {result.intelligence_layer.keyword_coverage_percentage}%
                    </span>
                    <div className="w-full h-1.5 bg-slate-900 rounded-full overflow-hidden border border-slate-800/40">
                      <div 
                        className="h-full bg-indigo-500 transition-all duration-1000 ease-out" 
                        style={{ width: `${result.intelligence_layer.keyword_coverage_percentage}%` }}
                      />
                    </div>
                    <span className="text-[9px] text-slate-500 font-semibold uppercase">
                      {result.intelligence_layer.found_keywords.length} of {result.intelligence_layer.required_keywords.length} keywords found
                    </span>
                  </div>

                  {/* Required & Found Keywords Card */}
                  <div className="bg-slate-950/15 p-5 rounded-xl border border-slate-900 space-y-3">
                    <span className="text-[10px] font-bold text-slate-450 uppercase tracking-widest block">Required & Found Keywords</span>
                    <div className="flex flex-wrap gap-1.5 max-h-[140px] overflow-y-auto pr-1">
                      {result.intelligence_layer.required_keywords && result.intelligence_layer.required_keywords.length > 0 ? (
                        result.intelligence_layer.required_keywords.map((kw, idx) => {
                          const isFound = result.intelligence_layer.found_keywords.includes(kw);
                          return (
                            <span 
                              key={idx} 
                              className={`px-2 py-0.5 rounded text-[10px] font-mono select-all ${
                                isFound 
                                  ? "bg-emerald-950/10 border border-emerald-500/20 text-emerald-450" 
                                  : "bg-slate-900/50 border border-slate-800 text-slate-500 line-through"
                              }`}
                            >
                              {kw}
                            </span>
                          );
                        })
                      ) : (
                        <span className="text-xs text-slate-550">No keywords specified in JD.</span>
                      )}
                    </div>
                  </div>

                  {/* Missing Keywords Card */}
                  <div className="bg-slate-950/15 p-5 rounded-xl border border-slate-900 space-y-3">
                    <span className="text-[10px] font-bold text-rose-400 uppercase tracking-widest block">Missing Keywords</span>
                    <div className="flex flex-wrap gap-1.5 max-h-[140px] overflow-y-auto pr-1">
                      {result.intelligence_layer.missing_keywords && result.intelligence_layer.missing_keywords.length > 0 ? (
                        result.intelligence_layer.missing_keywords.map((kw, idx) => (
                          <span 
                            key={idx} 
                            className="px-2 py-0.5 rounded text-[10px] font-mono bg-rose-950/10 border border-rose-500/20 text-rose-400 select-all"
                          >
                            {kw}
                          </span>
                        ))
                      ) : (
                        <span className="text-xs text-emerald-400 flex items-center gap-1">
                          <span>✓</span> Zero missing keywords!
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Priority Fixes */}
              <div className="glass-card p-6 rounded-xl border border-slate-800/60 space-y-4">
                <div>
                  <h4 className="text-xs font-bold text-slate-300 uppercase tracking-widest font-sans">🚨 Priority Fix Rankings</h4>
                  <p className="text-xs text-slate-500 mt-1 font-sans">Impact-ordered action plan detailing exactly how each recommendation recovers your score.</p>
                </div>
                
                <div className="space-y-4 font-sans">
                  {result.intelligence_layer.priority_fixes.map((fix, idx) => {
                    const isHigh = fix.impact === "High";
                    const isMed = fix.impact === "Medium";
                    return (
                      <div key={idx} className="flex gap-4 p-4 rounded-xl bg-slate-950/15 border border-slate-900/60 items-start">
                        <div className={`px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider flex-shrink-0 ${
                          isHigh
                            ? "bg-rose-950/30 border border-rose-500/20 text-rose-400"
                            : isMed
                              ? "bg-indigo-950/30 border border-indigo-500/20 text-indigo-400"
                              : "bg-slate-900 border border-slate-805 text-slate-400"
                        }`}>
                          {fix.impact} Impact
                        </div>
                        <div className="space-y-1">
                          <h5 className="text-xs font-bold text-slate-200">{fix.title}</h5>
                          <p className="text-xs text-slate-450 leading-relaxed">{fix.description}</p>
                          <span className="text-[10px] font-semibold text-emerald-400 uppercase tracking-widest block pt-1 font-mono">
                            Recovers +{fix.points_recovery}% of total score
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Intelligence Layer Roadmap & Explanations */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="glass-card p-6 rounded-xl border border-slate-800/60 space-y-4">
                  <h4 className="text-xs font-bold text-slate-300 uppercase tracking-widest flex items-center gap-1.5 font-sans">
                    <span>🛣️ ATS Improvement Roadmap</span>
                  </h4>
                  <ul className="space-y-3 font-sans">
                    {result.improvement_roadmap.map((step, idx) => (
                      <li key={idx} className="flex gap-2.5 items-start text-xs text-slate-300 leading-relaxed bg-slate-950/10 p-3 rounded-lg border border-slate-900/60">
                        <span className="w-5 h-5 rounded-full bg-indigo-950/20 border border-indigo-900/30 flex items-center justify-center text-[10px] text-indigo-400 font-bold flex-shrink-0 mt-0.5">
                          {idx + 1}
                        </span>
                        <span>{step}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="glass-card p-6 rounded-xl border border-slate-800/60 space-y-4 flex flex-col justify-between">
                  <div className="space-y-4">
                    <h4 className="text-xs font-bold text-slate-300 uppercase tracking-widest font-sans">🔍 Analysis Explanations</h4>
                    <div className="space-y-3.5 text-xs font-sans">
                      <div className="space-y-1 p-3.5 rounded-lg bg-slate-950/20 border border-slate-900">
                        <span className="font-bold text-indigo-400 block pb-1">Missing Keywords Impact Analysis</span>
                        <p className="text-slate-300 leading-relaxed">{result.keywords_impact_analysis}</p>
                      </div>
                      <div className="space-y-1 p-3.5 rounded-lg bg-slate-950/20 border border-slate-900">
                        <span className="font-bold text-indigo-400 block pb-1">Skill Validation Explanation</span>
                        <p className="text-slate-300 leading-relaxed">{result.skill_validation_explanation}</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="p-3 rounded-lg bg-indigo-950/10 border border-indigo-900/20 text-center font-sans">
                    <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest block font-sans">Projected Future ATS Score</span>
                    <strong className="text-lg text-indigo-300 font-mono">{result.estimated_future_score}</strong>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 2. Skills Overlap Grid */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest">Skill Overlap Review</h4>
            <SkillMatchCard 
              matchedSkills={result.matched_skills || []} 
              missingSkills={result.missing_skills || []} 
            />
          </div>

          {/* 3. AI Suggestions & Roadmaps */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="glass-card border border-slate-800/60 p-6 rounded-xl space-y-5 flex flex-col justify-between">
              <div className="space-y-4">
                <div className="flex items-center gap-2 text-indigo-400">
                  <BrainCircuit className="w-4.5 h-4.5 flex-shrink-0" />
                  <h4 className="text-sm font-semibold text-slate-200">AI Summary Alignment</h4>
                </div>
                <p className="text-xs text-slate-350 leading-relaxed bg-slate-950/20 p-3 rounded-lg border border-slate-900 select-text">
                  {summaryImprovement || "Run evaluation to generate custom profile improvements."}
                </p>
              </div>
              
              {missingKeywords.length > 0 && (
                <div className="space-y-2.5 pt-4 border-t border-slate-900">
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest flex items-center gap-1.5">
                    <TrendingUp className="w-3.5 h-3.5 text-indigo-400" />
                    Crucial Keywords to Inject
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {missingKeywords.map((kw) => (
                      <span 
                        key={kw} 
                        className="px-2 py-0.5 rounded text-[10px] font-mono bg-indigo-950/30 border border-indigo-900/30 text-indigo-350 select-all"
                      >
                        {kw}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="glass-card border border-slate-800/60 p-6 rounded-xl space-y-4">
              <div className="flex items-center gap-2 text-emerald-400">
                <Lightbulb className="w-4.5 h-4.5 flex-shrink-0" />
                <h4 className="text-sm font-semibold text-slate-200">Project Recommendations</h4>
              </div>
              
              {Array.isArray(projectSuggestions) && projectSuggestions.length > 0 ? (
                <ul className="space-y-3.5">
                  {projectSuggestions.map((proj, idx) => (
                    <li key={idx} className="flex gap-2.5 items-start text-xs text-slate-300 leading-relaxed bg-slate-950/10 p-3.5 rounded-lg border border-slate-900/60 hover:border-slate-800 transition-colors">
                      <span className="w-5 h-5 rounded-full bg-emerald-950/20 border border-emerald-900/30 flex items-center justify-center text-[10px] text-emerald-400 font-bold flex-shrink-0 mt-0.5">
                        {idx + 1}
                      </span>
                      <span>{proj}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="text-center py-12 text-slate-500 text-xs">
                  No project adjustments required for alignment.
                </div>
              )}
            </div>

            <div className="glass-card border border-slate-800/60 p-6 rounded-xl space-y-5">
              <div className="space-y-4">
                <div className="flex items-center gap-2 text-indigo-400">
                  <BookOpen className="w-4.5 h-4.5 flex-shrink-0" />
                  <h4 className="text-sm font-semibold text-slate-200">Resume Optimization Tips</h4>
                </div>
                
                {Array.isArray(experienceSuggestions) && experienceSuggestions.length > 0 && (
                  <div className="space-y-2.5">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest flex items-center gap-1.5">
                      <Cpu className="w-3.5 h-3.5 text-indigo-450" />
                      Experience Formatting
                    </span>
                    <ul className="space-y-2">
                      {experienceSuggestions.map((exp, idx) => (
                        <li key={idx} className="flex items-start gap-2 text-[11px] text-slate-300 leading-relaxed">
                          <ChevronRight className="w-3.5 h-3.5 text-indigo-450 flex-shrink-0 mt-0.5" />
                          <span>{exp}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {Array.isArray(generalTips) && generalTips.length > 0 && (
                  <div className="space-y-2.5 pt-3 border-t border-slate-900">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest flex items-center gap-1.5">
                      <Info className="w-3.5 h-3.5 text-indigo-450" />
                      General ATS Formatting
                    </span>
                    <ul className="space-y-2">
                      {generalTips.map((tip, idx) => (
                        <li key={idx} className="flex items-start gap-2 text-[11px] text-slate-300 leading-relaxed">
                          <Check className="w-3.5 h-3.5 text-emerald-450 flex-shrink-0 mt-0.5" />
                          <span>{tip}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Key Features Section (Moved below results) */}
          <div className="space-y-4 pt-4 border-t border-slate-900/60">
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest">✨ Key Features</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="glass-card border border-slate-800/60 p-6 rounded-xl flex flex-col justify-between">
                <div className="space-y-3">
                  <div className="flex items-center gap-2 text-indigo-400">
                    <span className="text-lg">📊</span>
                    <h5 className="text-sm font-semibold text-slate-200 font-sans">Comprehensive Scoring</h5>
                  </div>
                  <p className="text-xs text-slate-350 leading-relaxed font-sans">
                    Get detailed scores across 5 key dimensions:
                  </p>
                  <ul className="mt-2 space-y-1.5 text-xs text-slate-300 font-sans">
                    <li className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-indigo-500"></span>
                      Formatting
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-indigo-500"></span>
                      Keywords & Skills
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-indigo-500"></span>
                      Content Quality
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-indigo-500"></span>
                      Skill Validation
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-indigo-500"></span>
                      ATS Compatibility
                    </li>
                  </ul>
                </div>
              </div>

              <div className="glass-card border border-slate-800/60 p-6 rounded-xl flex flex-col justify-between">
                <div className="space-y-3">
                  <div className="flex items-center gap-2 text-emerald-400">
                    <span className="text-lg">🔍</span>
                    <h5 className="text-sm font-semibold text-slate-200 font-sans">Skill Validation</h5>
                  </div>
                  <p className="text-xs text-slate-350 leading-relaxed font-sans">
                    Verify that your claimed skills are demonstrated in your projects and experience using AI-powered semantic analysis.
                  </p>
                  <div className="mt-4">
                    <span className="px-2.5 py-1 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold inline-block font-sans">
                      No more empty claims!
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* AI Rewriter Drawer Modal */}
      {showRewriter && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-[#0b0f19] border border-slate-800 rounded-2xl w-full max-w-2xl flex flex-col shadow-2xl overflow-hidden">
            <div className="p-4 border-b border-slate-800 flex items-center justify-between">
              <div className="flex items-center gap-2 text-indigo-400">
                <BrainCircuit className="w-5 h-5 animate-pulse" />
                <h3 className="text-sm font-bold text-slate-200">Gemini AI Rewrite Assistant</h3>
              </div>
              <button
                onClick={() => {
                  setShowRewriter(false);
                  setRewriteContent("");
                  setRewrittenContent("");
                }}
                className="text-slate-400 hover:text-slate-200"
              >
                ✕
              </button>
            </div>
            
            <div className="p-6 space-y-5 overflow-y-auto max-h-[60vh]">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-400">Select Section Type</label>
                <div className="grid grid-cols-4 gap-2">
                  {["summary", "experience", "project", "skills"].map((sect) => (
                    <button
                      key={sect}
                      type="button"
                      onClick={() => setRewriteSection(sect)}
                      className={`py-1.5 rounded-lg text-xs font-semibold border capitalize transition-all ${
                        rewriteSection === sect
                          ? "bg-indigo-600 border-indigo-500 text-white"
                          : "bg-slate-900 border-slate-800 text-slate-400 hover:border-slate-700"
                      }`}
                    >
                      {sect}
                    </button>
                  ))}
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-400">Original Text</label>
                <textarea
                  rows={4}
                  value={rewriteContent}
                  onChange={(e) => setRewriteContent(e.target.value)}
                  placeholder={`Paste your original ${rewriteSection} contents here...`}
                  className="w-full p-3 rounded-lg bg-slate-950/60 border border-slate-800 focus:border-indigo-500 text-xs text-slate-200 outline-none resize-none"
                />
              </div>

              <button
                onClick={handleRewrite}
                disabled={rewriting || !rewriteContent.trim()}
                className="w-full py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs transition-all disabled:opacity-50"
              >
                {rewriting ? "Generating improvements..." : "Rewrite and Polish Section"}
              </button>

              {rewrittenContent && (
                <div className="space-y-1.5 animate-fadeIn">
                  <label className="text-xs font-semibold text-indigo-400 flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5" />
                    Improved Output (Gemini AI optimized)
                  </label>
                  <div className="p-4 rounded-lg bg-indigo-950/15 border border-indigo-900/30 text-xs font-mono text-slate-200 leading-relaxed whitespace-pre-wrap select-text">
                    {rewrittenContent}
                  </div>
                </div>
              )}
            </div>

            <div className="p-4 border-t border-slate-800 flex justify-end">
              <button
                onClick={() => {
                  setShowRewriter(false);
                  setRewriteContent("");
                  setRewrittenContent("");
                }}
                className="px-4 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 text-xs font-semibold border border-slate-800"
              >
                Close Assistant
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ATSAnalysis;
