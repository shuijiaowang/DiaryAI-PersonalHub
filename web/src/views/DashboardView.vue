<script setup lang="ts">
import { NCard, NGrid, NGridItem, NStatistic } from 'naive-ui'
import { onMounted, ref } from 'vue'

import { statsApi } from '@/api/stats'

const expense = ref<{ date: string; total: number }[]>([])
const byModule = ref<{ module_code: string; count: number }[]>([])
const totalExpense = ref(0)

onMounted(async () => {
  try {
    expense.value = await statsApi.expenseByDay()
    byModule.value = await statsApi.eventsByModule()
    totalExpense.value = expense.value.reduce((s, x) => s + x.total, 0)
  } catch {
    // ignore for skeleton stage
  }
})
</script>

<template>
  <div>
    <NGrid :cols="3" x-gap="16">
      <NGridItem>
        <NCard title="近 30 天消费">
          <NStatistic :value="totalExpense.toFixed(2)" tabular-nums>
            <template #suffix>元</template>
          </NStatistic>
        </NCard>
      </NGridItem>
      <NGridItem>
        <NCard title="事件总数">
          <NStatistic :value="byModule.reduce((s, x) => s + x.count, 0)" />
        </NCard>
      </NGridItem>
      <NGridItem>
        <NCard title="启用模块数">
          <NStatistic :value="byModule.length" />
        </NCard>
      </NGridItem>
    </NGrid>

    <NCard title="按模块分布" style="margin-top: 16px">
      <ul>
        <li v-for="row in byModule" :key="row.module_code">
          <strong>{{ row.module_code }}</strong> · {{ row.count }} 条
        </li>
      </ul>
      <p v-if="!byModule.length" style="color: #999">暂无数据，去写一篇日记看看吧。</p>
    </NCard>
  </div>
</template>
