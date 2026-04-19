import axios, { type AxiosInstance, type InternalAxiosRequestConfig } from 'axios'

import { useUserStore } from '@/stores/user'

const baseURL = import.meta.env.VITE_API_BASE || ''

export const http: AxiosInstance = axios.create({
  baseURL,
  timeout: 30_000,
})

http.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const userStore = useUserStore()
  if (userStore.accessToken) {
    config.headers = config.headers ?? {}
    ;(config.headers as Record<string, string>).Authorization = `Bearer ${userStore.accessToken}`
  }
  return config
})

http.interceptors.response.use(
  (resp) => resp,
  (error) => {
    if (error.response?.status === 401) {
      const userStore = useUserStore()
      userStore.clear()
      // simple redirect; real apps would attempt /auth/refresh first
      if (location.pathname !== '/login') location.href = '/login'
    }
    return Promise.reject(error)
  },
)

export async function getJSON<T>(url: string, params?: Record<string, unknown>): Promise<T> {
  const { data } = await http.get<T>(url, { params })
  return data
}

export async function postJSON<T>(url: string, body?: unknown): Promise<T> {
  const { data } = await http.post<T>(url, body)
  return data
}

export async function patchJSON<T>(url: string, body?: unknown): Promise<T> {
  const { data } = await http.patch<T>(url, body)
  return data
}

export async function putJSON<T>(url: string, body?: unknown): Promise<T> {
  const { data } = await http.put<T>(url, body)
  return data
}

export async function deleteJSON<T>(url: string): Promise<T> {
  const { data } = await http.delete<T>(url)
  return data
}
