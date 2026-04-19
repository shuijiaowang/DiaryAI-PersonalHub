<script setup lang="ts">
import { NButton, NCard, NEmpty, NInput, NSpace, useMessage } from 'naive-ui'
import { onMounted, ref } from 'vue'

import { profileApi } from '@/api/profile'
import type { ProfileSectionOut } from '@/types/api'

const message = useMessage()
const sections = ref<ProfileSectionOut[]>([])

const newCode = ref('')
const newJson = ref('{}')

async function load() {
  sections.value = await profileApi.list()
}

async function saveSection(code: string, json: string) {
  let content: Record<string, unknown>
  try {
    content = JSON.parse(json)
  } catch {
    message.error('JSON 解析失败')
    return
  }
  await profileApi.upsert({ module_code: code, content, privacy: 'ai_only' })
  message.success('已保存')
  await load()
}

async function addSection() {
  if (!newCode.value) return
  await saveSection(newCode.value, newJson.value)
  newCode.value = ''
  newJson.value = '{}'
}

onMounted(load)
</script>

<template>
  <NCard title="新增 / 编辑 模块">
    <NSpace vertical>
      <NInput v-model:value="newCode" placeholder="module_code，例如 basic / work / hobby / relation" />
      <NInput
        v-model:value="newJson"
        type="textarea"
        :autosize="{ minRows: 5, maxRows: 12 }"
        placeholder='{"key": "value"}'
      />
      <NButton type="primary" @click="addSection">保存</NButton>
    </NSpace>
  </NCard>

  <NCard title="已配置的画像模块" style="margin-top: 16px">
    <NEmpty v-if="!sections.length" description="还没配置任何画像模块" />
    <div v-for="s in sections" :key="s.id" style="margin-bottom: 16px">
      <h4>{{ s.module_code }} <span style="color: #999; font-weight: normal">({{ s.privacy }})</span></h4>
      <pre style="background: #fafafa; padding: 8px; border-radius: 4px">{{ JSON.stringify(s.content, null, 2) }}</pre>
    </div>
  </NCard>
</template>
