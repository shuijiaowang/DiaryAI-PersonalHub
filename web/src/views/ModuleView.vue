<script setup lang="ts">
import { NCard, NEmpty, NTag } from 'naive-ui'
import { onMounted, ref, watch } from 'vue'

import { eventApi } from '@/api/diary'
import type { EventOut } from '@/types/api'

const props = defineProps<{ code: string }>()
const events = ref<EventOut[]>([])

async function load() {
  events.value = await eventApi.listByModule(props.code)
}

onMounted(load)
watch(() => props.code, load)
</script>

<template>
  <NCard :title="`模块 · ${props.code}`">
    <NEmpty v-if="!events.length" description="暂无事件" />
    <div v-else>
      <div
        v-for="ev in events"
        :key="ev.id"
        style="margin-bottom: 12px; padding: 12px; border: 1px solid #eee; border-radius: 6px"
      >
        <div style="display: flex; justify-content: space-between">
          <div style="color: #666">{{ ev.created_at }}</div>
          <NTag v-if="ev.locked" size="small" type="warning">已锁定</NTag>
        </div>
        <div style="margin-top: 4px">{{ ev.ai_processed_text || ev.raw_text }}</div>
        <pre style="margin-top: 6px; background: #fafafa; padding: 8px; border-radius: 4px; overflow-x: auto">{{ JSON.stringify(ev.data, null, 2) }}</pre>
      </div>
    </div>
  </NCard>
</template>
