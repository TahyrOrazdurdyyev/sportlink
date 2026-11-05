import axios from 'axios'
import { useAuthStore } from '../stores/authStore'

// Always use relative path. In dev Vite proxies `/api` to the backend,
// and in prod the reverse proxy (Nginx) serves `/api`.
const getBaseURL = () => '/api/v1'

const apiClient = axios.create({
  baseURL: getBaseURL(),
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout()
      window.location.href = '/admin/login'
    }
    return Promise.reject(error)
  }
)

export default apiClient

