import axios from 'axios';

// Create axios instance
const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1', // Adjust if backend runs on different port
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: Attach token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: Handle 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      localStorage.setItem('isAuthenticated', 'false');
      // Optional: Redirect to login or trigger a global event
      window.location.href = '/'; 
    }
    return Promise.reject(error);
  }
);

export default api;
