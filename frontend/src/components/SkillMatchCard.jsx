
import { Check, AlertCircle, Sparkles, XCircle } from "lucide-react";

const SkillMatchCard = ({ matchedSkills = [], missingSkills = [] }) => {
  return (
    <div className="space-y-6 w-full font-sans">
      {/* Row 1: Matched & Missing */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full">
        {/* Matched Skills */}
        <div className="glass-card p-6 rounded-xl border border-slate-800/60 space-y-4">
          <div className="flex items-center gap-2 text-emerald-405">
            <Check className="w-5 h-5 flex-shrink-0" />
            <h4 className="text-sm font-semibold text-slate-200">
              Matched Skills ({matchedSkills.length})
            </h4>
          </div>
          <div className="flex flex-wrap gap-2">
            {matchedSkills.length > 0 ? (
              matchedSkills.map((skill) => (
                <span 
                  key={skill} 
                  className="px-2.5 py-1 rounded-full bg-emerald-950/20 border border-emerald-900/30 text-emerald-400 text-xs font-semibold capitalize"
                >
                  {skill}
                </span>
              ))
            ) : (
              <span className="text-xs text-slate-500">No overlapping skills found.</span>
            )}
          </div>
        </div>

        {/* Missing Skills */}
        <div className="glass-card p-6 rounded-xl border border-slate-800/60 space-y-4">
          <div className="flex items-center gap-2 text-rose-450">
            <AlertCircle className="w-5 h-5 flex-shrink-0 text-rose-400" />
            <h4 className="text-sm font-semibold text-slate-200">
              Missing Skills ({missingSkills.length})
            </h4>
          </div>
          <div className="flex flex-wrap gap-2">
            {missingSkills.length > 0 ? (
              missingSkills.map((skill) => (
                <span 
                  key={skill} 
                  className="px-2.5 py-1 rounded-full bg-rose-950/20 border border-rose-900/30 text-rose-400 text-xs font-semibold capitalize"
                >
                  {skill}
                </span>
              ))
            ) : (
              <span className="text-xs text-slate-500">Excellent! No missing skills.</span>
            )}
          </div>
        </div>
      </div>

      {/* Row 2: Recommended & Not Recommended */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full">
        {/* Recommended Skills To Add */}
        <div className="glass-card p-6 rounded-xl border border-slate-800/60 space-y-4">
          <div className="flex items-center gap-2 text-indigo-400">
            <Sparkles className="w-5 h-5 flex-shrink-0 animate-pulse" />
            <h4 className="text-sm font-semibold text-slate-200">
              Recommended Skills To Add
            </h4>
          </div>
          <div className="flex flex-wrap gap-2">
            {missingSkills.length > 0 ? (
              missingSkills.map((skill) => (
                <span 
                  key={skill} 
                  className="px-2.5 py-1 rounded-full bg-indigo-950/20 border border-indigo-900/30 text-indigo-400 text-xs font-semibold capitalize"
                >
                  {skill}
                </span>
              ))
            ) : (
              <span className="text-xs text-slate-500">No additional skills needed.</span>
            )}
          </div>
        </div>

        {/* Skills Not Recommended To Add */}
        <div className="glass-card p-6 rounded-xl border border-slate-800/60 space-y-4">
          <div className="flex items-center gap-2 text-slate-400">
            <XCircle className="w-5 h-5 flex-shrink-0 text-slate-505" />
            <h4 className="text-sm font-semibold text-slate-200">
              Skills Not Recommended To Add
            </h4>
          </div>
          <ul className="list-disc list-inside text-xs text-slate-400 space-y-1.5 pl-1">
            <li>Skills not present in Job Description</li>
            <li>Skills unrelated to target role</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default SkillMatchCard;
