// NOTE: keep these in sync with server/app/schemas/*.py manually for now.
// In a real project we'd generate this from FastAPI's /openapi.json.

export interface UserCreate {
  username: string
  password: string
  email?: string | null
}
export interface UserLogin {
  username: string
  password: string
}
export interface UserOut {
  id: number
  username: string
  email: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}
export interface TokenPair {
  access_token: string
  refresh_token: string
  token_type: string
}

export type DiaryStatus = 'draft' | 'parsing' | 'parsed' | 'failed'

export interface DiaryCreate {
  date: string
  raw_text: string
}
export interface DiaryUpdate {
  raw_text?: string | null
}
export interface DiaryOut {
  id: number
  user_id: number
  date: string
  raw_text: string
  ai_processed_text: string | null
  status: DiaryStatus
  parse_error: string | null
  created_at: string
  updated_at: string
}
export interface DiaryDetail extends DiaryOut {
  events: EventOut[]
}

export interface EventOut {
  id: number
  diary_id: number
  user_id: number
  module_code: string
  raw_text: string
  ai_processed_text: string | null
  data: Record<string, unknown>
  locked: boolean
  created_at: string
  updated_at: string
}
export interface EventUpdate {
  raw_text?: string
  ai_processed_text?: string
  data?: Record<string, unknown>
  locked?: boolean
}

export interface ModuleOut {
  id: number
  code: string
  name: string
  description: string | null
  schema: Record<string, unknown>
  prompt_fragment: string
  actions: string[]
  is_builtin: boolean
  enabled: boolean
  created_at: string
  updated_at: string
}

export type Privacy = 'public' | 'ai_only' | 'private'
export interface ProfileSectionUpsert {
  module_code: string
  content: Record<string, unknown>
  privacy: Privacy
}
export interface ProfileSectionOut {
  id: number
  user_id: number
  module_code: string
  content: Record<string, unknown>
  privacy: Privacy
  updated_by_event_id: number | null
  created_at: string
  updated_at: string
}

export interface Message {
  message: string
}
