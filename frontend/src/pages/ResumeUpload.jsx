import { useState, useEffect } from "react";
import resumeService from "../services/resumeService";
import UploadZone from "../components/UploadZone";
import LoadingSpinner from "../components/LoadingSpinner";
import { 
  FileText, 
  Trash2, 
  AlertCircle, 
  CheckCircle,
  Eye,
  Calendar,
  X
} from "lucide-react";

const ResumeUpload = () => {
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [viewResume, setViewResume] = useState(null);

  const fetchResumes = async () => {
    try {
      const response = await resumeService.getAll();
      setResumes(response.data);
    } catch (err) {
      console.error("Failed to load resumes:", err);
      setError("Failed to fetch resumes. Please log in again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchResumes();
  }, []);

  const handleUpload = async (file) => {
    setError("");
    setSuccess("");
    setUploading(true);
    setUploadProgress(0);

    const formData = new FormData();
    formData.append("file", file);

    try {
      await resumeService.upload(formData, (progressEvent) => {
        const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        setUploadProgress(percent);
      });
      setSuccess("Resume uploaded and parsed successfully!");
      await fetchResumes();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to upload and parse file.");
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const handleUploadError = (errorMsg) => {
    setError(errorMsg);
    setSuccess("");
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this resume?")) return;
    setError("");
    setSuccess("");

    try {
      await resumeService.delete(id);
      setSuccess("Resume deleted.");
      setResumes(resumes.filter((r) => r.id !== id));
      if (viewResume?.id === id) setViewResume(null);
    } catch (err) {
      console.error(err);
      setError("Failed to delete resume.");
    }
  };

  return (
    <div className="space-y-8 relative">
      {/* Alert Messages */}
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
        {/* Decomposed Upload Zone component! */}
        <div className="glass-card rounded-xl p-6 border border-slate-800/60 h-fit space-y-4">
          <div>
            <h4 className="text-sm font-semibold text-slate-200">Upload New Resume</h4>
            <p className="text-xs text-slate-500">Add your PDF or Word document for analysis</p>
          </div>
          <UploadZone 
            onUpload={handleUpload} 
            isUploading={uploading} 
            uploadProgress={uploadProgress}
            onError={handleUploadError}
          />
        </div>

        {/* Resumes list container */}
        <div className="lg:col-span-2 space-y-4">
          <div className="glass-card rounded-xl p-6 border border-slate-800/60">
            <h4 className="text-sm font-semibold text-slate-200 mb-4">Your Uploaded Resumes</h4>

            {loading ? (
              <LoadingSpinner />
            ) : resumes.length > 0 ? (
              <div className="space-y-3">
                {resumes.map((resume) => (
                  <div
                    key={resume.id}
                    className="flex items-center justify-between p-3.5 rounded-xl bg-slate-950/40 border border-slate-900 hover:border-slate-800 transition-colors"
                  >
                    <div className="flex items-center gap-4 min-w-0">
                      <div className="w-10 h-10 rounded-lg bg-indigo-600/10 border border-indigo-500/10 flex items-center justify-center flex-shrink-0">
                        <FileText className="w-5 h-5 text-indigo-400" />
                      </div>
                      <div className="min-w-0">
                        <p className="text-sm font-semibold text-slate-200 truncate pr-4">{resume.file_name}</p>
                        <span className="flex items-center gap-1.5 text-xs text-slate-500 mt-1">
                          <Calendar className="w-3.5 h-3.5" /> 
                          {new Date(resume.upload_date).toLocaleDateString()}
                        </span>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => setViewResume(resume)}
                        className="p-2 rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-400 hover:text-slate-200 transition-colors"
                        title="Preview text content"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(resume.id)}
                        className="p-2 rounded-lg bg-slate-900 border border-slate-800 hover:border-rose-900 hover:text-rose-400 text-slate-500 transition-colors"
                        title="Delete resume"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 border border-dashed border-slate-850 rounded-xl text-slate-500 text-sm">
                No resumes uploaded yet. Drag a file into the upload zone to get started.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Resume Text Preview Modal Drawer */}
      {viewResume && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-fadeIn">
          <div className="bg-[#0b0f19] border border-slate-800 rounded-2xl w-full max-w-3xl max-h-[85vh] flex flex-col shadow-2xl overflow-hidden">
            <div className="p-4 border-b border-slate-800 flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-slate-200 truncate max-w-md">{viewResume.file_name}</h3>
                <p className="text-xs text-slate-500">Parsed text preview</p>
              </div>
              <button
                onClick={() => setViewResume(null)}
                className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="p-6 overflow-y-auto flex-1 font-mono text-xs text-slate-300 leading-relaxed whitespace-pre-wrap bg-slate-950/85 select-text">
              {viewResume.parsed_text || "No parsed text contents found."}
            </div>
            
            <div className="p-4 border-t border-slate-800 flex justify-end">
              <button
                onClick={() => setViewResume(null)}
                className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition-all"
              >
                Close Preview
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResumeUpload;
