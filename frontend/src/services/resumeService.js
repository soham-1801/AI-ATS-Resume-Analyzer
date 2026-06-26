import api from "./api";

const resumeService = {
  upload: (formData, onProgress) => {
    return api.post("/resume/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      onUploadProgress: onProgress,
    });
  },
  
  getAll: () => {
    return api.get("/resume/all");
  },
  
  delete: (id) => {
    return api.delete(`/resume/${id}`);
  }
};

export default resumeService;
