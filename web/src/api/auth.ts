import { getJSON, postJSON } from '@/api/request'
import type { TokenPair, UserCreate, UserLogin, UserOut } from '@/types/api'

export const authApi = {
  register: (payload: UserCreate) => postJSON<UserOut>('/api/v1/auth/register', payload),
  login: (payload: UserLogin) => postJSON<TokenPair>('/api/v1/auth/login', payload),
  refresh: (refresh_token: string) =>
    postJSON<TokenPair>('/api/v1/auth/refresh', { refresh_token }),
  me: () => getJSON<UserOut>('/api/v1/auth/me'),
}
