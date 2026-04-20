import { getJSON } from '@/api/request'

export type ExpenseGranularity = 'day' | 'week' | 'month' | 'year'

export interface ExpenseByPeriodRow {
  bucket: string
  total: number
  count: number
}

export interface ExpenseSummary {
  total: number
  count: number
  avg: number
  max: number
  start: string
  end: string
}

export interface ExpenseCategoryRow {
  category: string
  total: number
  count: number
}

export interface ExpenseItemRow {
  id: number
  diary_id: number
  created_at: string
  raw_text: string
  ai_processed_text: string | null
  locked: boolean
  data: Record<string, unknown>
}

export type StatsDateRange = {
  start?: string
  end?: string
} & Record<string, unknown>

export const statsApi = {
  expenseByDay: (start?: string, end?: string) =>
    getJSON<{ date: string; total: number }[]>('/api/v1/stats/expense/by-day', { start, end }),
  expenseByPeriod: (granularity: ExpenseGranularity, range: StatsDateRange = {}) =>
    getJSON<ExpenseByPeriodRow[]>('/api/v1/stats/expense/by-period', {
      granularity,
      ...range,
    }),
  expenseSummary: (range: StatsDateRange = {}) =>
    getJSON<ExpenseSummary>('/api/v1/stats/expense/summary', range),
  expenseByCategory: (range: StatsDateRange = {}) =>
    getJSON<ExpenseCategoryRow[]>('/api/v1/stats/expense/by-category', range),
  expenseItems: (range: StatsDateRange = {}, limit = 200, offset = 0) =>
    getJSON<ExpenseItemRow[]>('/api/v1/stats/expense/items', {
      ...range,
      limit,
      offset,
    }),
  eventsByModule: () =>
    getJSON<{ module_code: string; count: number }[]>('/api/v1/stats/events/by-module'),
}
