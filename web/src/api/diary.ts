import { deleteJSON, getJSON, patchJSON, postJSON } from '@/api/request'
import type { DiaryCreate, DiaryDetail, DiaryOut, DiaryUpdate, EventOut, EventUpdate, Message } from '@/types/api'

export const diaryApi = {
  list: (limit = 50, offset = 0) =>
    getJSON<DiaryOut[]>('/api/v1/diaries', { limit, offset }),
  get: (id: number) => getJSON<DiaryDetail>(`/api/v1/diaries/${id}`),
  create: (payload: DiaryCreate) => postJSON<DiaryOut>('/api/v1/diaries', payload),
  update: (id: number, payload: DiaryUpdate) =>
    patchJSON<DiaryOut>(`/api/v1/diaries/${id}`, payload),
  remove: (id: number) => deleteJSON<Message>(`/api/v1/diaries/${id}`),
  parse: (id: number, force = false) =>
    postJSON<Message>(`/api/v1/diaries/${id}/parse`, { force }),
}

export const eventApi = {
  listByModule: (module_code: string, limit = 100, offset = 0) =>
    getJSON<EventOut[]>('/api/v1/events', { module_code, limit, offset }),
  update: (id: number, payload: EventUpdate) =>
    patchJSON<EventOut>(`/api/v1/events/${id}`, payload),
  remove: (id: number) => deleteJSON<Message>(`/api/v1/events/${id}`),
}
