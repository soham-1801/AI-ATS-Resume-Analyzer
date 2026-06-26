import api from "./api";

const authService = {
  register: (name, email, password) => {
    return api.post("/auth/register", { name, email, password });
  },
  
  login: (email, password) => {
    return api.post("/auth/login", { email, password });
  },
  
  getMe: () => {
    return api.get("/auth/me");
  },
  
  changePassword: (oldPassword, newPassword) => {
    return api.post("/auth/change-password", { old_password: oldPassword, new_password: newPassword });
  },
  
  oauthLogin: (provider, oauthData) => {
    return api.post("/auth/oauth", {
      provider,
      oauth_id: oauthData.oauth_id,
      email: oauthData.email,
      name: oauthData.name
    });
  },

  exchangeOAuthCode: (provider, code, redirectUri = null, idToken = null) => {
    return api.post(`/auth/oauth/${provider}`, { code, redirect_uri: redirectUri, id_token: idToken });
  }
};

export default authService;
