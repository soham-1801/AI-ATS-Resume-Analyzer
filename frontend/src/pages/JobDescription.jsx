import { useState, useEffect } from "react";
import atsService from "../services/atsService";
import LoadingSpinner from "../components/LoadingSpinner";
import { 
  Briefcase, 
  Trash2, 
  Plus, 
  AlertCircle, 
  CheckCircle,
  Calendar
} from "lucide-react";

const JobDescription = () => {
  const [jds, setJds] = useState([]);
  const [description, setDescription] = useState("");
  
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const fetchJds = async () => {
    try {
      const response = await atsService.getAllJds();
      setJds(response.data);
    } catch (err) {
      console.error("Failed to load JDs:", err);
      setError("Failed to fetch job profiles.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchJds();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!description.trim()) return;

    setError("");
    setSuccess("");
    setSubmitting(true);

    try {
      await atsService.createJd(description);
      setSuccess("Job profile registered successfully!");
      setDescription("");
      fetchJds();
    } catch (err) {
      console.error(err);
      setError("Failed to save job profile.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this job description?")) return;
    setError("");
    setSuccess("");

    try {
      await atsService.deleteJd(id);
      setSuccess("Job description deleted.");
      setJds(jds.filter((jd) => jd.id !== id));
    } catch (err) {
      console.error(err);
      setError("Failed to delete job description.");
    }
  };

  return (
    <div className="space-y-8">
      {/* Messages */}
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

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Input Form Panel */}
        <div className="glass-card rounded-xl p-6 border border-slate-800/60 h-fit space-y-4">
          <div>
            <h4 className="text-sm font-semibold text-slate-200">Add Job Description</h4>
            <p className="text-xs text-slate-500">Paste target job description details</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <textarea
              required
              rows={12}
              value={description}
              onChange={(e) => setDescription(e.value || e.target.value)}
              placeholder="Paste job responsibilities, skills, qualifications, or requirements..."
              className="w-full p-4 rounded-xl bg-slate-950/60 border border-slate-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-sm text-slate-200 placeholder-slate-600 outline-none transition-all resize-none"
            />
            <button
              type="submit"
              disabled={submitting || !description.trim()}
              className="w-full py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm transition-all flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/20 disabled:opacity-50"
            >
              <Plus className="w-4 h-4" />
              {submitting ? "Saving..." : "Add Profile"}
            </button>
          </form>
        </div>

        {/* Existing List */}
        <div className="lg:col-span-2 space-y-4">
          <div className="glass-card rounded-xl p-6 border border-slate-800/60">
            <h4 className="text-sm font-semibold text-slate-200 mb-4">Saved Job Profiles</h4>

            {loading ? (
              <LoadingSpinner />
            ) : jds.length > 0 ? (
              <div className="space-y-4">
                {jds.map((jd) => (
                  <div
                    key={jd.id}
                    className="p-4 rounded-xl bg-slate-950/40 border border-slate-900 hover:border-slate-800 transition-colors flex flex-col justify-between gap-4"
                  >
                    <div className="flex justify-between items-start gap-4">
                      <div className="flex items-start gap-4">
                        <div className="w-10 h-10 rounded-lg bg-emerald-600/10 border border-emerald-500/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                          <Briefcase className="w-5 h-5 text-emerald-400" />
                        </div>
                        <div>
                          <p className="text-xs font-bold text-slate-400">Profile ID: #{jd.id}</p>
                          <span className="flex items-center gap-1 text-[10px] text-slate-500 mt-1">
                            <Calendar className="w-3.5 h-3.5" />
                            Created {new Date(jd.created_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>

                      <button
                        onClick={() => handleDelete(jd.id)}
                        className="p-2 rounded-lg bg-slate-900 border border-slate-800 hover:border-rose-900 hover:text-rose-400 text-slate-500 transition-colors"
                        title="Delete profile"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>

                    <div className="p-3 bg-slate-950/60 rounded-lg text-xs text-slate-300 font-mono line-clamp-3 leading-relaxed whitespace-pre-wrap select-text">
                      {jd.description}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 border border-dashed border-slate-850 rounded-xl text-slate-500 text-sm">
                No job profiles created yet. Use the left panel to submit one.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default JobDescription;
