import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { authApi } from '@/api/auth'
import type { TokenPair, UserOut } from '@/types/api'

const ACCESS_KEY = 'diaryai.access_token'
const REFRESH_KEY = 'diaryai.refresh_token'
const DARK_KEY = 'diaryai.dark_mode'

export const useUserStore = defineStore('user', () => {
  const accessToken = ref<string | null>(localStorage.getItem(ACCESS_KEY))
  const refreshToken = ref<string | null>(localStorage.getItem(REFRESH_KEY))
  const me = ref<UserOut | null>(null)
  const darkMode = ref<boolean>(localStorage.getItem(DARK_KEY) === '1')

  const isAuthenticated = computed(() => !!accessToken.value)

  function setTokens(pair: TokenPair) {
    accessToken.value = pair.access_token
    refreshToken.value = pair.refresh_token
    localStorage.setItem(ACCESS_KEY, pair.access_token)
    localStorage.setItem(REFRESH_KEY, pair.refresh_token)
  }

  function clear() {
    accessToken.value = null
    refreshToken.value = null
    me.value = null
    localStorage.removeItem(ACCESS_KEY)
    localStorage.removeItem(REFRESH_KEY)
  }

  async function login(username: string, password: string) {
    const pair = await authApi.login({ username, password })
    setTokens(pair)
    await fetchMe()
  }

  async function fetchMe() {
    me.value = await authApi.me()
  }

  function logout() {
    clear()
  }

  function toggleDark() {
    darkMode.value = !darkMode.value
    localStorage.setItem(DARK_KEY, darkMode.value ? '1' : '0')
  }

  return {
    accessToken,
    refreshToken,
    me,
    darkMode,
    isAuthenticated,
    setTokens,
    clear,
    login,
    fetchMe,
    logout,
    toggleDark,
  }
})
