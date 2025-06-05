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
    api.get('/students/list', { params }),
  getAllPaginated: (params) =>
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
  getAll: (params) => {
    // Если нужна пагинация, используем основной эндпоинт
    if (params && (params.page || params.size)) {
      return api.get('/groups', { params });
    }
    // Иначе используем простой список
    return api.get('/groups/list', { params });
  },
  getById: (id) =>
    api.get(`/groups/${id}`),
  create: (data) =>
    api.post('/groups', data),
  update: (id, data) =>
    api.put(`/groups/${id}`, data),
  delete: (id) =>
    api.delete(`/groups/${id}`),
};

// Subdivisions API (исправлено с divisions на subdivisions)
export const subdivisionsAPI = {
  getAll: (params) => {
    // Если нужна пагинация, используем основной эндпоинт
    if (params && (params.page || params.size)) {
      return api.get('/subdivisions', { params });
    }
    // Иначе используем простой список
    return api.get('/subdivisions/list');
  },
  getById: (id) =>
    api.get(`/subdivisions/${id}`),
  create: (data) =>
    api.post('/subdivisions', data),
  update: (id, data) =>
    api.put(`/subdivisions/${id}`, data),
  delete: (id) =>
    api.delete(`/subdivisions/${id}`),
};

// Users API
export const usersAPI = {
  getAll: (params) =>
    api.get('/users', { params }),
  getById: (id) =>
    api.get(`/users/${id}`),
  create: (data) =>
    api.post('/users', data),
  update: (id, data) =>
    api.put(`/users/${id}`, data),
  delete: (id) =>
    api.delete(`/users/${id}`),
  changePassword: (data) =>
    api.post('/users/change-password', data),
  addRole: (userId, roleId) =>
    api.post(`/users/${userId}/roles/${roleId}`),
  removeRole: (userId, roleId) =>
    api.delete(`/users/${userId}/roles/${roleId}`),
};

// Roles API
export const rolesAPI = {
  getAll: () =>
    api.get('/roles'),
  getById: (id) =>
    api.get(`/roles/${id}`),
  create: (data) =>
    api.post('/roles', data),
  update: (id, data) =>
    api.put(`/roles/${id}`, data),
  delete: (id) =>
    api.delete(`/roles/${id}`),
};

// Для обратной совместимости
export const divisionsAPI = subdivisionsAPI;

export default api;