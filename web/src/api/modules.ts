import { getJSON, patchJSON } from '@/api/request'
import type { ModuleOut } from '@/types/api'

export const modulesApi = {
  list: () => getJSON<ModuleOut[]>('/api/v1/modules'),
  toggle: (code: string, enabled: boolean) =>
    patchJSON<ModuleOut>(`/api/v1/modules/${code}`, { enabled }),
}
