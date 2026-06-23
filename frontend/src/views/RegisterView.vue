<template>
  <div class="auth-page">
    <div class="auth-bg">
      <div class="auth-bg-shape shape-1"></div>
      <div class="auth-bg-shape shape-2"></div>
    </div>
    <el-card class="auth-card" shadow="never">
      <div class="auth-header">
        <div class="auth-logo">
          <el-icon :size="28" color="#4361EE"><MagicStick /></el-icon>
          <span>Prompt Manager</span>
        </div>
        <p class="auth-tagline">创建你的账号</p>
      </div>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="0" class="auth-form">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" size="large">
            <template #prefix><el-icon><User /></el-icon></template>
          </el-input>
        </el-form-item>
        <el-form-item prop="email">
          <el-input v-model="form.email" placeholder="邮箱" size="large">
            <template #prefix><el-icon><Message /></el-icon></template>
          </el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码（至少 6 位）" size="large" show-password>
            <template #prefix><el-icon><Lock /></el-icon></template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" style="width: 100%" :loading="loading" @click="handleRegister">
            注册
          </el-button>
        </el-form-item>
      </el-form>
      <div class="auth-footer">
        已有账号？<router-link to="/login">登录</router-link>
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
const form = reactive({ username: '', email: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [{ required: true, type: 'email', message: '请输入有效邮箱', trigger: 'blur' }],
  password: [{ required: true, min: 6, message: '密码至少 6 位', trigger: 'blur' }],
}
async function handleRegister() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try { await auth.register(form.username, form.email, form.password); ElMessage.success('注册成功，请登录'); router.push('/login') }
  catch (e: any) { ElMessage.error(e.response?.data?.detail || '注册失败') }
  finally { loading.value = false }
}
</script>

<style scoped>
.auth-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #F5F6FA; position: relative; overflow: hidden; }
.auth-bg { position: absolute; inset: 0; pointer-events: none; }
.auth-bg-shape { position: absolute; border-radius: 50%; }
.shape-1 { width: 400px; height: 400px; background: linear-gradient(135deg, rgba(67, 97, 238, 0.08), rgba(108, 99, 255, 0.05)); top: -100px; right: -100px; }
.shape-2 { width: 300px; height: 300px; background: linear-gradient(135deg, rgba(67, 97, 238, 0.06), rgba(6, 214, 160, 0.04)); bottom: -80px; left: -80px; }
.auth-card { width: 400px; padding: 8px; position: relative; border-radius: 16px !important; box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06) !important; }
.auth-header { text-align: center; margin-bottom: 32px; margin-top: 8px; }
.auth-logo { display: flex; align-items: center; justify-content: center; gap: 10px; font-size: 22px; font-weight: 700; color: var(--pm-text-primary); }
.auth-tagline { color: var(--pm-text-muted); font-size: 13px; margin: 8px 0 0 0; }
.auth-form { margin-bottom: 16px; }
.auth-footer { text-align: center; font-size: 13px; color: var(--pm-text-muted); }
.auth-footer a { color: var(--pm-primary); text-decoration: none; font-weight: 600; }
</style>
