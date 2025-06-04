import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (username, password) =>
    api.post('/auth/login', { username, password }),
  register: (userData) =>
    api.post('/auth/register', userData),
  me: () =>
    api.get('/auth/me'),
};

// Students API
export const studentsAPI = {
  getAll: (params) =>
    api.get('/students', { params }),
  getById: (id) =>
    api.get(`/students/${id}`),
  create: (data) =>
    api.post('/students', data),
  update: (id, data) =>
    api.put(`/students/${id}`, data),
  delete: (id) =>
    api.delete(`/students/${id}`),
  getContributions: (id) =>
    api.get(`/students/${id}/contributions`),
  getHostel: (id) =>
    api.get(`/students/${id}/hostel`),
};

// Groups API
export const groupsAPI = {
  getAll: (params) =>
    api.get('/groups', { params }),
  getById: (id) =>
    api.get(`/groups/${id}`),
  create: (data) =>
    api.post('/groups', data),
  update: (id, data) =>
    api.put(`/groups/${id}`, data),
  delete: (id) =>
    api.delete(`/groups/${id}`),
};

// Divisions API
export const divisionsAPI = {
  getAll: (params) =>
    api.get('/divisions', { params }),
  getById: (id) =>
    api.get(`/divisions/${id}`),
  create: (data) =>
    api.post('/divisions', data),
  update: (id, data) =>
    api.put(`/divisions/${id}`, data),
  delete: (id) =>
    api.delete(`/divisions/${id}`),
};

export default api; 