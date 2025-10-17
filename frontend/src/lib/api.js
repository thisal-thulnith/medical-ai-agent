import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: async (data) => {
    const response = await api.post('/auth/register', data);
    return response.data;
  },

  login: async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },
};

// Chat API
export const chatAPI = {
  sendMessage: async (data) => {
    const response = await api.post('/chat/message', data);
    return response.data;
  },

  getConversations: async () => {
    const response = await api.get('/chat/conversations');
    return response.data;
  },

  getConversation: async (id) => {
    const response = await api.get(`/chat/conversations/${id}`);
    return response.data;
  },

  deleteConversation: async (id) => {
    await api.delete(`/chat/conversations/${id}`);
  },
};

// Dashboard API
export const dashboardAPI = {
  getStats: async () => {
    const response = await api.get('/dashboard/stats');
    return response.data;
  },

  getHealthData: async () => {
    const response = await api.get('/dashboard/health-data');
    return response.data;
  },
};

// Upload API
export const uploadAPI = {
  uploadReport: async (formData) => {
    const token = localStorage.getItem('auth_token');
    const response = await axios.post(`${API_URL}/upload/report`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  },

  getReports: async () => {
    const response = await api.get('/upload/reports');
    return response.data;
  },
};

export default api;
