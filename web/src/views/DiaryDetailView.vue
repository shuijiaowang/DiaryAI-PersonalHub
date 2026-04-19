<script setup lang="ts">
import { NButton, NCard, NEmpty, NSpace, NTag, useMessage } from 'naive-ui'
import { onMounted, ref, watch } from 'vue'

import { diaryApi } from '@/api/diary'
import type { DiaryDetail } from '@/types/api'

const props = defineProps<{ id: string | number }>()
const message = useMessage()
const detail = ref<DiaryDetail | null>(null)

async function load() {
  detail.value = await diaryApi.get(Number(props.id))
}

async function reparse() {
  await diaryApi.parse(Number(props.id), true)
  message.info('已重新提交解析')
  setTimeout(load, 1500)
}

onMounted(load)
watch(() => props.id, load)
</script>

<template>
  <div v-if="detail">
    <NCard :title="`${detail.date} · 状态 ${detail.status}`">
      <template #header-extra>
        <NSpace>
          <NTag :type="detail.status === 'parsed' ? 'success' : 'warning'">{{ detail.status }}</NTag>
          <NButton size="small" type="primary" @click="reparse">重新解析</NButton>
        </NSpace>
      </template>
      <p style="white-space: pre-wrap">{{ detail.raw_text }}</p>
      <div v-if="detail.ai_processed_text" style="margin-top: 16px; padding-top: 16px; border-top: 1px dashed #ddd">
        <strong>AI 规范化：</strong>
        <p style="white-space: pre-wrap; color: #555">{{ detail.ai_processed_text }}</p>
      </div>
      <p v-if="detail.parse_error" style="color: red">解析错误：{{ detail.parse_error }}</p>
    </NCard>

    <NCard title="提取的事件" style="margin-top: 16px">
      <NEmpty v-if="!detail.events.length" description="暂无事件" />
      <div v-else>
        <div v-for="ev in detail.events" :key="ev.id" style="margin-bottom: 16px; padding: 12px; border: 1px solid #eee; border-radius: 6px">
          <NSpace align="center" style="margin-bottom: 6px">
            <NTag type="info">{{ ev.module_code }}</NTag>
            <NTag v-if="ev.locked" size="small" type="warning">已锁定</NTag>
          </NSpace>
          <div style="color: #666; font-size: 13px">原文：{{ ev.raw_text }}</div>
          <pre style="margin-top: 6px; background: #fafafa; padding: 8px; border-radius: 4px; overflow-x: auto">{{ JSON.stringify(ev.data, null, 2) }}</pre>
        </div>
      </div>
    </NCard>
  </div>
</template>
