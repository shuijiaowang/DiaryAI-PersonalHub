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
import { computed, h } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

function renderLink(name: string, label: string) {
  return () => h(RouterLink, { to: { name } }, { default: () => label })
}

const menuOptions = computed<MenuOption[]>(() => [
  { label: renderLink('dashboard', '总览'), key: 'dashboard' },
  { label: renderLink('diary', '日记'), key: 'diary' },
  { label: renderLink('profile', '我的画像'), key: 'profile' },
  {
    label: '统计',
    key: 'stats-group',
    children: [
      { label: renderLink('stats-expense', '消费统计'), key: 'stats-expense' },
    ],
  },
  {
    label: '模块明细',
    key: 'modules-group',
    children: [
      { label: renderLink('module', '消费'), key: 'module-expense', props: { onClick: () => router.push({ name: 'module', params: { code: 'expense' } }) } },
      { label: renderLink('module', '饮食'), key: 'module-meal', props: { onClick: () => router.push({ name: 'module', params: { code: 'meal' } }) } },
      { label: renderLink('module', '天气'), key: 'module-weather', props: { onClick: () => router.push({ name: 'module', params: { code: 'weather' } }) } },
      { label: renderLink('module', '备忘录'), key: 'module-memo', props: { onClick: () => router.push({ name: 'module', params: { code: 'memo' } }) } },
    ],
  },
  { label: renderLink('chat', '对话'), key: 'chat' },
  { label: renderLink('settings', '设置'), key: 'settings' },
])

const activeKey = computed(() => (route.name as string) || 'dashboard')

function logout() {
  userStore.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <NLayout has-sider style="height: 100vh">
    <NLayoutSider bordered collapse-mode="width" :collapsed-width="64" :width="220" show-trigger>
      <div style="padding: 18px; font-weight: 600; font-size: 15px">DiaryAI</div>
      <NMenu :options="menuOptions" :value="activeKey" />
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
