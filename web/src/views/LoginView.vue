<script setup lang="ts">
import { NButton, NCard, NForm, NFormItem, NInput, useMessage } from 'naive-ui'
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const router = useRouter()
const message = useMessage()

const form = reactive({ username: '', password: '' })
const loading = ref(false)

async function submit() {
  if (!form.username || !form.password) {
    message.warning('请填写用户名和密码')
    return
  }
  loading.value = true
  try {
    await userStore.login(form.username, form.password)
    message.success('登录成功')
    router.push({ name: 'dashboard' })
  } catch (e: unknown) {
    const err = e as { response?: { data?: { message?: string } } }
    message.error(err.response?.data?.message ?? '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div style="height: 100vh; display: flex; align-items: center; justify-content: center; background: #f5f5f5">
    <NCard title="DiaryAI · 登录" style="width: 360px">
      <NForm @submit.prevent="submit">
        <NFormItem label="用户名">
          <NInput v-model:value="form.username" placeholder="username" />
        </NFormItem>
        <NFormItem label="密码">
          <NInput v-model:value="form.password" type="password" show-password-on="click" placeholder="password" />
        </NFormItem>
        <NButton type="primary" block :loading="loading" @click="submit">登录</NButton>
        <div style="margin-top: 12px; text-align: center; font-size: 12px">
          还没账号？<router-link to="/register" style="color: #18a058">去注册</router-link>
        </div>
      </NForm>
    </NCard>
  </div>
</template>
