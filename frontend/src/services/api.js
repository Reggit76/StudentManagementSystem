import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Enable sending cookies with requests
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add CSRF token from cookie if available
    const cookies = document.cookie.split(';').reduce((acc, cookie) => {
      const [key, value] = cookie.trim().split('=');
      acc[key] = value;
      return acc;
    }, {});
    
    // Try different possible CSRF token cookie names
    const csrfToken = cookies['csrf_token'] || cookies['csrftoken'] || cookies['CSRF-TOKEN'];
    
    if (csrfToken) {
      config.headers['X-CSRF-Token'] = csrfToken;
      config.headers['X-CSRFToken'] = csrfToken; 
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

// Обновляем Groups API
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
  getStudents: (id) =>  // Добавляем новый метод
    api.get(`/groups/${id}/students`),
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

// Добавляем в конец файла

// Audit Logs API
export const auditLogsAPI = {
  getAll: (params) =>
    api.get('/audit-logs', { params }),
  getActions: () =>
    api.get('/audit-logs/actions'),
  getTables: () =>
    api.get('/audit-logs/tables'),
};


// Для обратной совместимости
export const divisionsAPI = subdivisionsAPI;

export default api;