import api from "./api";

const atsService = {
  // Job Description endpoints
  createJd: (description) => {
    return api.post("/job-description/", { description });
  },
  
  getAllJds: () => {
    return api.get("/job-description/all");
  },
  
  deleteJd: (id) => {
    return api.delete(`/job-description/${id}`);
  },
  
  // Analysis endpoints
  analyze: (resumeId, jdId) => {
    return api.post("/ats/analyze", { resume_id: resumeId, job_description_id: jdId });
  },
  
  getResults: (resumeId) => {
    return api.get(`/ats/results/${resumeId}`);
  },
  
  // PDF download
  downloadPdfUrl: (resultId) => {
    return `${api.defaults.baseURL}/ats/results/${resultId}/pdf`;
  },
  
  downloadPdf: (resultId) => {
    return api.get(`/ats/results/${resultId}/pdf`, { responseType: "blob" });
  },
  
  // AI Rewrite endpoints
  rewriteSection: (section, content) => {
    return api.post("/ai/rewrite", { section, content });
  }
};

export default atsService;
