<script setup lang="ts">
import { NButton, NCard, NDatePicker, NInput, NList, NListItem, NSpace, NTag, useMessage } from 'naive-ui'
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { diaryApi } from '@/api/diary'
import type { DiaryOut } from '@/types/api'

const router = useRouter()
const message = useMessage()

const list = ref<DiaryOut[]>([])
const loading = ref(false)
const text = ref('')
const date = ref<number>(Date.now())

async function refresh() {
  list.value = await diaryApi.list()
}

async function create() {
  if (!text.value.trim()) {
    message.warning('日记内容不能为空')
    return
  }
  loading.value = true
  try {
    const d = new Date(date.value)
    const iso = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
    const created = await diaryApi.create({ date: iso, raw_text: text.value })
    message.success('已提交，AI 解析中…')
    text.value = ''
    await refresh()
    router.push({ name: 'diary-detail', params: { id: created.id } })
  } catch (e: unknown) {
    const err = e as { response?: { data?: { message?: string } } }
    message.error(err.response?.data?.message ?? '创建失败')
  } finally {
    loading.value = false
  }
}

const statusType = (s: string) =>
  s === 'parsed' ? 'success' : s === 'failed' ? 'error' : s === 'parsing' ? 'warning' : 'default'

onMounted(refresh)
</script>

<template>
  <NCard title="新写日记">
    <NSpace vertical>
      <NDatePicker v-model:value="date" type="date" />
      <NInput
        v-model:value="text"
        type="textarea"
        :autosize="{ minRows: 8, maxRows: 20 }"
        placeholder="今天发生了什么？随便写，AI 会帮你结构化。"
      />
      <NButton type="primary" :loading="loading" @click="create">提交并 AI 解析</NButton>
    </NSpace>
  </NCard>

  <NCard title="历史日记" style="margin-top: 16px">
    <NList v-if="list.length">
      <NListItem v-for="d in list" :key="d.id">
        <div style="display: flex; justify-content: space-between; align-items: center">
          <div>
            <strong>{{ d.date }}</strong>
            <span style="margin-left: 12px; color: #888">
              {{ d.raw_text.slice(0, 60) }}{{ d.raw_text.length > 60 ? '…' : '' }}
            </span>
          </div>
          <NSpace>
            <NTag :type="statusType(d.status)" size="small">{{ d.status }}</NTag>
            <NButton size="small" text @click="router.push({ name: 'diary-detail', params: { id: d.id } })">
              查看
            </NButton>
          </NSpace>
        </div>
      </NListItem>
    </NList>
    <p v-else style="color: #999">还没有日记。</p>
  </NCard>
</template>
