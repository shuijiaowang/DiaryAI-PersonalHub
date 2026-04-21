<script setup lang="ts">
import {
  NLayout,
  NLayoutHeader,
  NLayoutSider,
  NMenu,
  NButton,
  NSpace,
  type MenuOption,
} from 'naive-ui'
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const menuOptions = computed<MenuOption[]>(() => [
  { label: '总览', key: 'dashboard' },
  { label: '日记', key: 'diary' },
  { label: '我的画像', key: 'profile' },
  {
    label: '统计',
    key: 'stats-group',
    children: [
      { label: '消费统计', key: 'stats-expense' },
    ],
  },
  {
    label: '模块明细',
    key: 'modules-group',
    children: [
      { label: '消费', key: 'module-expense' },
      { label: '饮食', key: 'module-meal' },
      { label: '天气', key: 'module-weather' },
      { label: '备忘录', key: 'module-memo' },
    ],
  },
  { label: '对话', key: 'chat' },
  { label: '设置', key: 'settings' },
])

const activeKey = computed(() => {
  if (route.name === 'module') {
    return `module-${String(route.params.code || '')}`
  }
  return (route.name as string) || 'dashboard'
})

const menuRouteMap: Record<string, { name: string, params?: Record<string, string> }> = {
  dashboard: { name: 'dashboard' },
  diary: { name: 'diary' },
  profile: { name: 'profile' },
  'stats-expense': { name: 'stats-expense' },
  'module-expense': { name: 'module', params: { code: 'expense' } },
  'module-meal': { name: 'module', params: { code: 'meal' } },
  'module-weather': { name: 'module', params: { code: 'weather' } },
  'module-memo': { name: 'module', params: { code: 'memo' } },
  chat: { name: 'chat' },
  settings: { name: 'settings' },
}

function handleMenuSelect(key: string) {
  const target = menuRouteMap[key]
  if (!target) return
  router.push(target)
}

function logout() {
  userStore.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <NLayout has-sider style="height: 100vh">
    <NLayoutSider bordered collapse-mode="width" :collapsed-width="64" :width="220" show-trigger>
      <div style="padding: 18px; font-weight: 600; font-size: 15px">DiaryAI</div>
      <NMenu :options="menuOptions" :value="activeKey" @update:value="handleMenuSelect" />
    </NLayoutSider>
    <NLayout>
      <NLayoutHeader bordered style="padding: 12px 20px; display: flex; align-items: center; justify-content: space-between">
        <div>欢迎，{{ userStore.me?.username ?? '...' }}</div>
        <NSpace>
          <NButton size="small" @click="userStore.toggleDark()">
            {{ userStore.darkMode ? '浅色' : '深色' }}
          </NButton>
          <NButton size="small" type="error" ghost @click="logout">登出</NButton>
        </NSpace>
      </NLayoutHeader>
      <NLayout style="padding: 20px">
        <router-view />
      </NLayout>
    </NLayout>
  </NLayout>
</template>
