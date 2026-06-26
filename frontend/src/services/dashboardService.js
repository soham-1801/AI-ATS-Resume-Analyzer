import api from "./api";

const dashboardService = {
  getAnalytics: () => {
    return api.get("/dashboard/analytics");
  },
  
  getStats: () => {
    return api.get("/dashboard/stats");
  }
};

export default dashboardService;
