import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { useMessage } from 'naive-ui'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = useMessage()
    if (error.response?.status === 401) {
      const authStore = useAuthStore()
      authStore.logout()
      window.location.href = '/login'
    }
    if (error.response?.data?.detail) {
      message.error(error.response.data.detail)
    } else if (error.message) {
      message.error(error.message)
    }
    return Promise.reject(error)
  }
)

export default api
