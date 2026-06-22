<template>
  <div style="min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #f0f2f5">
    <el-card style="width: 400px; padding: 20px">
      <h2 style="text-align: center; margin-bottom: 24px">注册账号</h2>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="0">
        <el-form-item prop="username"><el-input v-model="form.username" placeholder="用户名" prefix-icon="User" size="large" /></el-form-item>
        <el-form-item prop="email"><el-input v-model="form.email" placeholder="邮箱" prefix-icon="Message" size="large" /></el-form-item>
        <el-form-item prop="password"><el-input v-model="form.password" type="password" placeholder="密码" prefix-icon="Lock" size="large" show-password /></el-form-item>
        <el-form-item><el-button type="primary" size="large" style="width: 100%" :loading="loading" @click="handleRegister">注册</el-button></el-form-item>
      </el-form>
      <div style="text-align: center"><router-link to="/login">已有账号？登录</router-link></div>
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
const rules = { username: [{ required: true, message: '请输入用户名', trigger: 'blur' }], email: [{ required: true, type: 'email', message: '请输入有效邮箱', trigger: 'blur' }], password: [{ required: true, min: 6, message: '密码至少 6 位', trigger: 'blur' }] }
async function handleRegister() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try { await auth.register(form.username, form.email, form.password); ElMessage.success('注册成功，请登录'); router.push('/login') }
  catch (e: any) { ElMessage.error(e.response?.data?.detail || '注册失败') }
  finally { loading.value = false }
}
</script>
