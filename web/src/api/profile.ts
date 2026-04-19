import { getJSON, putJSON } from '@/api/request'
import type { ProfileSectionOut, ProfileSectionUpsert } from '@/types/api'

export const profileApi = {
  list: () => getJSON<ProfileSectionOut[]>('/api/v1/profile'),
  upsert: (payload: ProfileSectionUpsert) =>
    putJSON<ProfileSectionOut>('/api/v1/profile', payload),
}
