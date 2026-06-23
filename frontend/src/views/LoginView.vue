<template>
  <div class="auth-page">
    <div class="auth-grid-bg"></div>
    <div class="auth-glow glow-1"></div>
    <div class="auth-glow glow-2"></div>
    <el-card class="auth-card" shadow="never">
      <div class="auth-header">
        <div class="auth-logo">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#06B6D4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/>
          </svg>
          <span>Prompt Manager</span>
        </div>
        <p class="auth-tagline">提示词管理 · 测试 · 协作</p>
      </div>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="0" class="auth-form">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" size="large">
            <template #prefix><el-icon><User /></el-icon></template>
          </el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" size="large" show-password>
            <template #prefix><el-icon><Lock /></el-icon></template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" style="width: 100%" :loading="loading" @click="handleLogin">登录</el-button>
        </el-form-item>
      </el-form>
      <div class="auth-footer">
        还没有账号？<router-link to="/register">注册</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
const router = useRouter()
const auth = useAuthStore()
const formRef = ref()
const loading = ref(false)
const form = reactive({ username: '', password: '' })
const rules = { username: [{ required: true, message: '请输入用户名', trigger: 'blur' }], password: [{ required: true, message: '请输入密码', trigger: 'blur' }] }
async function handleLogin() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try { await auth.login(form.username, form.password); ElMessage.success('登录成功'); router.push('/') }
  catch (e: any) { ElMessage.error(e.response?.data?.detail || '登录失败') }
  finally { loading.value = false }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--pm-bg-base);
  position: relative;
  overflow: hidden;
}

.auth-grid-bg {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
  background-size: 48px 48px;
}

.auth-glow {
  position: absolute;
  width: 400px;
  height: 400px;
  border-radius: 50%;
  filter: blur(100px);
  pointer-events: none;
}

.glow-1 {
  background: rgba(6, 182, 212, 0.08);
  top: -150px;
  right: -100px;
}

.glow-2 {
  background: rgba(6, 182, 212, 0.05);
  bottom: -150px;
  left: -100px;
}

.auth-card {
  width: 380px;
  padding: 8px;
  position: relative;
  background: var(--pm-bg-surface) !important;
  border: 1px solid var(--pm-border) !important;
  border-radius: 16px !important;
}

.auth-header {
  text-align: center;
  margin-bottom: 32px;
  margin-top: 8px;
}

.auth-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-size: 22px;
  font-weight: 700;
  color: var(--pm-text-primary);
}

.auth-tagline {
  color: var(--pm-text-tertiary);
  font-size: 13px;
  margin: 8px 0 0 0;
}

.auth-form {
  margin-bottom: 16px;
}

.auth-footer {
  text-align: center;
  font-size: 13px;
  color: var(--pm-text-tertiary);
}

.auth-footer a {
  color: var(--pm-accent);
  text-decoration: none;
  font-weight: 600;
}

.auth-footer a:hover {
  text-decoration: underline;
}
</style>
