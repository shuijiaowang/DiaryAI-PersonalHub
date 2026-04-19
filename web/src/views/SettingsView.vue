<script setup lang="ts">
import { NCard, NList, NListItem, NSwitch, NTag, useMessage } from 'naive-ui'
import { onMounted, ref } from 'vue'

import { modulesApi } from '@/api/modules'
import type { ModuleOut } from '@/types/api'

const message = useMessage()
const modules = ref<ModuleOut[]>([])

async function load() {
  modules.value = await modulesApi.list()
}

async function toggle(m: ModuleOut, v: boolean) {
  await modulesApi.toggle(m.code, v)
  message.success(`${m.name} 已${v ? '启用' : '禁用'}`)
  await load()
}

onMounted(load)
</script>

<template>
  <NCard title="模块管理">
    <NList>
      <NListItem v-for="m in modules" :key="m.code">
        <div style="display: flex; justify-content: space-between; align-items: center">
          <div>
            <strong>{{ m.name }}</strong> <NTag size="small" style="margin-left: 8px">{{ m.code }}</NTag>
            <div style="color: #888; font-size: 12px; margin-top: 4px">{{ m.description }}</div>
          </div>
          <NSwitch :value="m.enabled" @update:value="(v: boolean) => toggle(m, v)" />
        </div>
      </NListItem>
    </NList>
  </NCard>
</template>
