<script setup lang="ts">
import type { FormInst, FormRules } from 'naive-ui'
import { NButton, NCard, NForm, NFormItem, NInput, useMessage } from 'naive-ui'
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { authApi } from '@/api/auth'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const message = useMessage()
const userStore = useUserStore()

const formRef = ref<FormInst | null>(null)
const form = reactive({ username: '', password: '', email: '' })
const loading = ref(false)

function utf8ByteLength(s: string): number {
  return new TextEncoder().encode(s).length
}

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: ['input', 'blur'] },
    { min: 3, max: 50, message: '用户名长度需在 3–50 个字符', trigger: ['blur'] },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: ['input', 'blur'] },
    { min: 6, max: 128, message: '密码长度需在 6–128 个字符', trigger: ['blur'] },
    {
      validator: (_rule, value: string) => {
        if (!value) return true
        if (utf8ByteLength(value) > 72) {
          return new Error(
            '密码 UTF-8 编码不能超过 72 字节（中文等字符占多字节，会更早达到上限）',
          )
        }
        return true
      },
      trigger: ['blur', 'change'],
    },
  ],
  email: [
    {
      validator: (_rule, value: string) => {
        const v = (value ?? '').trim()
        if (!v) return true
        const ok = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)
        return ok || new Error('邮箱格式不正确')
      },
      trigger: ['blur'],
    },
  ],
}

async function submit() {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }
  loading.value = true
  try {
    await authApi.register({
      username: form.username,
      password: form.password,
      email: form.email || null,
    })
    await userStore.login(form.username, form.password)
    message.success('注册成功')
    router.push({ name: 'dashboard' })
  } catch (e: unknown) {
    const err = e as { response?: { data?: { message?: string } } }
    message.error(err.response?.data?.message ?? '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div style="height: 100vh; display: flex; align-items: center; justify-content: center; background: #f5f5f5">
    <NCard title="DiaryAI · 注册" style="width: 400px">
      <NForm ref="formRef" :model="form" :rules="rules" @submit.prevent="submit">
        <NFormItem path="username" label="用户名">
          <NInput v-model:value="form.username" placeholder="3–50 个字符" />
        </NFormItem>
        <NFormItem path="password" label="密码">
          <NInput v-model:value="form.password" type="password" show-password-on="click" />
        </NFormItem>
        <div style="font-size: 12px; color: #888; margin: -8px 0 16px; line-height: 1.45">
          至少 6 个字符、至多 128 个字符；无大小写或数字强制要求。后端使用 bcrypt，密码 UTF-8 编码不得超过 72 字节（纯英文数字约可 72 位）。
        </div>
        <NFormItem path="email" label="邮箱（可选）">
          <NInput v-model:value="form.email" placeholder="留空可不填" />
        </NFormItem>
        <NButton type="primary" block :loading="loading" @click="submit">创建账号</NButton>
        <div style="margin-top: 12px; text-align: center; font-size: 12px">
          已有账号？<router-link to="/login" style="color: #18a058">去登录</router-link>
        </div>
      </NForm>
    </NCard>
  </div>
</template>
