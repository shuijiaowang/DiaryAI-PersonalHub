<script setup lang="ts">
import { NConfigProvider, NMessageProvider, darkTheme } from 'naive-ui'
import { computed } from 'vue'

import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const theme = computed(() => (userStore.darkMode ? darkTheme : null))
</script>

<template>
  <NConfigProvider :theme="theme">
    <NMessageProvider>
      <router-view />
    </NMessageProvider>
  </NConfigProvider>
</template>
