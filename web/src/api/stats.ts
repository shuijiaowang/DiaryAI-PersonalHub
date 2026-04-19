import { getJSON } from '@/api/request'

export const statsApi = {
  expenseByDay: (start?: string, end?: string) =>
    getJSON<{ date: string; total: number }[]>('/api/v1/stats/expense/by-day', { start, end }),
  eventsByModule: () =>
    getJSON<{ module_code: string; count: number }[]>('/api/v1/stats/events/by-module'),
}
