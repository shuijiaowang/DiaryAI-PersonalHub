<script setup lang="ts">
import {
  NButton,
  NCard,
  NDataTable,
  NDatePicker,
  NEmpty,
  NForm,
  NFormItem,
  NGrid,
  NGridItem,
  NInput,
  NInputNumber,
  NModal,
  NRadioButton,
  NRadioGroup,
  NSelect,
  NSpace,
  NStatistic,
  NTag,
  useMessage,
  type DataTableColumns,
} from 'naive-ui'
import { computed, h, onMounted, reactive, ref, watch } from 'vue'
import VChart from 'vue-echarts'
import { BarChart, HeatmapChart, LineChart, PieChart } from 'echarts/charts'
import {
  CalendarComponent,
  GridComponent,
  LegendComponent,
  TitleComponent,
  TooltipComponent,
  VisualMapComponent,
} from 'echarts/components'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'

import { eventApi, type EventManualCreate } from '@/api/diary'
import {
  statsApi,
  type ExpenseByPeriodRow,
  type ExpenseCategoryRow,
  type ExpenseGranularity,
  type ExpenseItemRow,
  type ExpenseSummary,
} from '@/api/stats'

use([
  BarChart,
  LineChart,
  PieChart,
  HeatmapChart,
  CalendarComponent,
  GridComponent,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  VisualMapComponent,
  CanvasRenderer,
])

// ---------------------------------------------------------------- state

const message = useMessage()

const granularity = ref<ExpenseGranularity>('day')
const range = ref<[number, number]>(defaultRange('day'))

const summary = ref<ExpenseSummary | null>(null)
const periodRows = ref<ExpenseByPeriodRow[]>([])
const categoryRows = ref<ExpenseCategoryRow[]>([])
const items = ref<ExpenseItemRow[]>([])
const loading = ref(false)

const showManualModal = ref(false)
const manualSubmitting = ref(false)
const manualForm = reactive<ManualExpenseForm>(initialManualForm())

// ---------------------------------------------------------------- helpers

function defaultRange(g: ExpenseGranularity): [number, number] {
  const end = new Date()
  end.setHours(23, 59, 59, 999)
  const start = new Date(end)
  const spans: Record<ExpenseGranularity, number> = {
    day: 30,
    week: 7 * 12,
    month: 31 * 12,
    year: 365 * 5,
  }
  start.setDate(start.getDate() - spans[g])
  start.setHours(0, 0, 0, 0)
  return [start.getTime(), end.getTime()]
}

function toISO(ts: number): string {
  const d = new Date(ts)
  const y = d.getFullYear()
  const m = `${d.getMonth() + 1}`.padStart(2, '0')
  const day = `${d.getDate()}`.padStart(2, '0')
  return `${y}-${m}-${day}`
}

function queryRange() {
  return { start: toISO(range.value[0]), end: toISO(range.value[1]) }
}

// ---------------------------------------------------------------- data load

async function loadAll() {
  loading.value = true
  try {
    const r = queryRange()
    const [s, p, c, it] = await Promise.all([
      statsApi.expenseSummary(r),
      statsApi.expenseByPeriod(granularity.value, r),
      statsApi.expenseByCategory(r),
      statsApi.expenseItems(r, 200, 0),
    ])
    summary.value = s
    periodRows.value = p
    categoryRows.value = c
    items.value = it
  } catch (e) {
    message.error(`加载失败：${(e as Error).message ?? e}`)
  } finally {
    loading.value = false
  }
}

function onGranularityChange(g: ExpenseGranularity) {
  granularity.value = g
  range.value = defaultRange(g)
  loadAll()
}

onMounted(loadAll)
watch(range, loadAll)

// ---------------------------------------------------------------- charts

const periodChartOption = computed(() => {
  const xs = periodRows.value.map((r) => formatBucket(r.bucket, granularity.value))
  const totals = periodRows.value.map((r) => Number(r.total.toFixed(2)))
  const counts = periodRows.value.map((r) => r.count)
  return {
    tooltip: { trigger: 'axis' },
    legend: { data: ['金额（元）', '笔数'] },
    grid: { top: 48, right: 48, bottom: 40, left: 48 },
    xAxis: { type: 'category', data: xs },
    yAxis: [
      { type: 'value', name: '金额', axisLabel: { formatter: '{value} 元' } },
      { type: 'value', name: '笔数', position: 'right' },
    ],
    series: [
      {
        name: '金额（元）',
        type: 'bar',
        data: totals,
        itemStyle: { color: '#18a058' },
      },
      {
        name: '笔数',
        type: 'line',
        yAxisIndex: 1,
        data: counts,
        smooth: true,
        itemStyle: { color: '#f0a020' },
      },
    ],
  }
})

const categoryChartOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c} 元 ({d}%)' },
  legend: { bottom: 0 },
  series: [
    {
      name: '消费类型',
      type: 'pie',
      radius: ['45%', '72%'],
      avoidLabelOverlap: true,
      label: { formatter: '{b}\n{d}%' },
      data: categoryRows.value.map((r) => ({
        name: r.category || '其他',
        value: Number(r.total.toFixed(2)),
      })),
    },
  ],
}))

const calendarChartOption = computed(() => {
  // Render last 1 year of daily totals as a calendar heatmap.
  const map = new Map<string, number>()
  for (const row of periodRows.value) {
    if (!row.bucket) continue
    map.set(row.bucket, (map.get(row.bucket) ?? 0) + row.total)
  }
  // If granularity != 'day' we reaggregate from items for finer view.
  if (granularity.value !== 'day') {
    map.clear()
    for (const it of items.value) {
      const day = (it.created_at || '').slice(0, 10)
      if (!day) continue
      const price = Number((it.data as { 价格?: number | string })['价格'] ?? 0)
      map.set(day, (map.get(day) ?? 0) + price)
    }
  }
  const values = [...map.entries()].map(([d, v]) => [d, Number(v.toFixed(2))])
  const endDay = toISO(range.value[1])
  const startDay = toISO(range.value[0])
  const year = endDay.slice(0, 4)
  // ECharts calendar only supports one year per range; use explicit range string.
  const calendarRange = isSameYear(startDay, endDay) ? year : [startDay, endDay]
  const max = values.length ? Math.max(...values.map((v) => v[1] as number)) : 0
  return {
    tooltip: {
      formatter: (p: { value: [string, number] }) => `${p.value[0]}：${p.value[1]} 元`,
    },
    visualMap: {
      min: 0,
      max: Math.max(max, 100),
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: 0,
      inRange: { color: ['#e8f5e9', '#66bb6a', '#1b5e20'] },
    },
    calendar: {
      range: calendarRange,
      cellSize: ['auto', 18],
      top: 32,
      left: 48,
      right: 32,
      dayLabel: { nameMap: 'ZH' },
      monthLabel: { nameMap: 'ZH' },
      itemStyle: { borderColor: '#fff' },
    },
    series: [{ type: 'heatmap', coordinateSystem: 'calendar', data: values }],
  }
})

function isSameYear(a: string, b: string) {
  return a.slice(0, 4) === b.slice(0, 4)
}

function formatBucket(b: string | null, g: ExpenseGranularity): string {
  if (!b) return ''
  if (g === 'year') return b.slice(0, 4)
  if (g === 'month') return b.slice(0, 7)
  return b
}

function granularityLabel(g: ExpenseGranularity): string {
  return ({ day: '日', week: '周', month: '月', year: '年' } as const)[g]
}

// ---------------------------------------------------------------- table

const columns: DataTableColumns<ExpenseItemRow> = [
  {
    title: '时间',
    key: 'created_at',
    width: 180,
    render: (row) => row.created_at.replace('T', ' ').slice(0, 19),
  },
  {
    title: '类型',
    key: 'category',
    width: 90,
    render: (row) => String((row.data as Record<string, unknown>)['消费类型'] ?? '其他'),
  },
  {
    title: '金额',
    key: 'price',
    width: 100,
    align: 'right',
    render: (row) => {
      const v = Number((row.data as Record<string, unknown>)['价格'] ?? 0)
      return h('span', { style: 'font-variant-numeric: tabular-nums' }, `${v.toFixed(2)} 元`)
    },
  },
  {
    title: '平台 / 店铺',
    key: 'place',
    render: (row) => {
      const d = row.data as Record<string, unknown>
      const parts = [d['平台'], d['店铺']].filter(Boolean)
      return parts.join(' · ') || '—'
    },
  },
  {
    title: '评价 / 原文',
    key: 'memo',
    render: (row) => {
      const comment = (row.data as Record<string, unknown>)['评价'] as string | undefined
      return comment || row.ai_processed_text || row.raw_text || '—'
    },
  },
  {
    title: '标记',
    key: 'locked',
    width: 110,
    render: (row) =>
      row.locked
        ? h(NTag, { size: 'small', type: 'warning' }, { default: () => '手动/已锁定' })
        : h(NTag, { size: 'small', type: 'info' }, { default: () => 'AI 提取' }),
  },
]

// ---------------------------------------------------------------- manual entry

interface ManualExpenseForm {
  date: number | null
  category: string
  platform: string
  shop: string
  comment: string
  price: number | null
  raw_text: string
}

const categoryOptions = [
  '日常',
  '饮食',
  '出行',
  '购物',
  '住房',
  '娱乐',
  '学习',
  '医疗',
  '其他',
].map((v) => ({ label: v, value: v }))

function initialManualForm(): ManualExpenseForm {
  return {
    date: Date.now(),
    category: '其他',
    platform: '',
    shop: '',
    comment: '',
    price: null,
    raw_text: '',
  }
}

function openManualModal() {
  Object.assign(manualForm, initialManualForm())
  showManualModal.value = true
}

async function submitManual() {
  if (manualForm.price == null || !(manualForm.price >= 0)) {
    message.warning('请填写价格')
    return
  }
  manualSubmitting.value = true
  try {
    const payload: EventManualCreate = {
      module_code: 'expense',
      date: manualForm.date ? toISO(manualForm.date) : null,
      raw_text: manualForm.raw_text || null,
      data: {
        消费类型: manualForm.category,
        平台: manualForm.platform,
        店铺: manualForm.shop,
        评价: manualForm.comment,
        价格: manualForm.price,
        其他: {},
      },
    }
    await eventApi.createManual(payload)
    message.success('已手动补录（不会修改日记原文）')
    showManualModal.value = false
    await loadAll()
  } catch (e) {
    message.error(`补录失败：${(e as Error).message ?? e}`)
  } finally {
    manualSubmitting.value = false
  }
}
</script>

<template>
  <div>
    <NCard title="消费统计" style="margin-bottom: 16px">
      <template #header-extra>
        <NSpace>
          <NRadioGroup
            :value="granularity"
            size="small"
            @update:value="(v: ExpenseGranularity) => onGranularityChange(v)"
          >
            <NRadioButton value="day">日</NRadioButton>
            <NRadioButton value="week">周</NRadioButton>
            <NRadioButton value="month">月</NRadioButton>
            <NRadioButton value="year">年</NRadioButton>
          </NRadioGroup>
          <NDatePicker
            v-model:value="range"
            type="daterange"
            clearable
            size="small"
            style="width: 260px"
          />
          <NButton size="small" @click="loadAll" :loading="loading">刷新</NButton>
          <NButton size="small" type="primary" @click="openManualModal">+ 手动补录</NButton>
        </NSpace>
      </template>

      <NGrid :cols="4" x-gap="12">
        <NGridItem>
          <NCard size="small" embedded>
            <NStatistic label="总支出" :value="(summary?.total ?? 0).toFixed(2)" tabular-nums>
              <template #suffix>元</template>
            </NStatistic>
          </NCard>
        </NGridItem>
        <NGridItem>
          <NCard size="small" embedded>
            <NStatistic label="笔数" :value="summary?.count ?? 0" />
          </NCard>
        </NGridItem>
        <NGridItem>
          <NCard size="small" embedded>
            <NStatistic label="单笔均值" :value="(summary?.avg ?? 0).toFixed(2)" tabular-nums>
              <template #suffix>元</template>
            </NStatistic>
          </NCard>
        </NGridItem>
        <NGridItem>
          <NCard size="small" embedded>
            <NStatistic label="最大单笔" :value="(summary?.max ?? 0).toFixed(2)" tabular-nums>
              <template #suffix>元</template>
            </NStatistic>
          </NCard>
        </NGridItem>
      </NGrid>
    </NCard>

    <NGrid :cols="3" x-gap="16" style="margin-bottom: 16px">
      <NGridItem :span="2">
        <NCard :title="`按${granularityLabel(granularity)}分布`">
          <div v-if="!periodRows.length" style="padding: 24px 0"><NEmpty description="没有数据" /></div>
          <VChart v-else :option="periodChartOption" autoresize style="height: 320px" />
        </NCard>
      </NGridItem>
      <NGridItem>
        <NCard title="按类型分布">
          <div v-if="!categoryRows.length" style="padding: 24px 0"><NEmpty description="没有数据" /></div>
          <VChart v-else :option="categoryChartOption" autoresize style="height: 320px" />
        </NCard>
      </NGridItem>
    </NGrid>

    <NCard title="日历热力图" style="margin-bottom: 16px">
      <div v-if="!items.length && !periodRows.length" style="padding: 24px 0">
        <NEmpty description="没有数据" />
      </div>
      <VChart v-else :option="calendarChartOption" autoresize style="height: 240px" />
    </NCard>

    <NCard title="消费明细">
      <NDataTable
        :columns="columns"
        :data="items"
        :pagination="{ pageSize: 20 }"
        :bordered="false"
        size="small"
        striped
      />
    </NCard>

    <NModal
      v-model:show="showManualModal"
      preset="card"
      title="手动补录消费"
      style="width: 520px"
      :mask-closable="!manualSubmitting"
    >
      <NForm :model="manualForm" label-placement="left" label-width="80">
        <NFormItem label="日期">
          <NDatePicker v-model:value="manualForm.date" type="date" clearable style="width: 100%" />
        </NFormItem>
        <NFormItem label="类型">
          <NSelect v-model:value="manualForm.category" :options="categoryOptions" />
        </NFormItem>
        <NFormItem label="金额">
          <NInputNumber v-model:value="manualForm.price" :min="0" :precision="2" style="width: 100%">
            <template #suffix>元</template>
          </NInputNumber>
        </NFormItem>
        <NFormItem label="平台">
          <NInput v-model:value="manualForm.platform" placeholder="美团 / 淘宝 / 现金 ..." />
        </NFormItem>
        <NFormItem label="店铺">
          <NInput v-model:value="manualForm.shop" />
        </NFormItem>
        <NFormItem label="备注">
          <NInput v-model:value="manualForm.comment" placeholder="评价、用途等" />
        </NFormItem>
        <NFormItem label="原文片段">
          <NInput
            v-model:value="manualForm.raw_text"
            type="textarea"
            :autosize="{ minRows: 2, maxRows: 4 }"
            placeholder="可选。此处只写在 event 表，不会修改日记原文"
          />
        </NFormItem>
      </NForm>
      <p style="color: #999; font-size: 12px; margin: 0 0 12px">
        手动补录不会修改日记原文（ADR-007）。这条记录会打上"已锁定"标记，AI 重解析时不会被覆盖或删除。
      </p>
      <NSpace justify="end">
        <NButton @click="showManualModal = false" :disabled="manualSubmitting">取消</NButton>
        <NButton type="primary" :loading="manualSubmitting" @click="submitManual">保存</NButton>
      </NSpace>
    </NModal>
  </div>
</template>
