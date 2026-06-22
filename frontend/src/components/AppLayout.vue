<template>
  <el-container style="min-height: 100vh">
    <el-aside width="220px" style="background: #304156">
      <div style="height: 60px; display: flex; align-items: center; justify-content: center; color: #fff; font-size: 18px; font-weight: bold; border-bottom: 1px solid rgba(255,255,255,0.1)">Prompt Manager</div>
      <el-menu :default-active="currentRoute" background-color="#304156" text-color="#bfcbd9" active-text-color="#409EFF" router>
        <el-menu-item index="/dashboard"><el-icon><DataBoard /></el-icon><span>仪表盘</span></el-menu-item>
        <el-menu-item index="/prompts"><el-icon><Document /></el-icon><span>提示词</span></el-menu-item>
        <el-menu-item index="/settings"><el-icon><Setting /></el-icon><span>设置</span></el-menu-item>
        <el-menu-item v-if="auth.user?.is_admin" index="/admin/api-configs"><el-icon><Tools /></el-icon><span>全局 API 配置</span></el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="background: #fff; border-bottom: 1px solid #e6e6e6; display: flex; align-items: center; justify-content: flex-end; padding: 0 20px">
        <el-dropdown trigger="click">
          <span style="cursor: pointer; display: flex; align-items: center; gap: 8px">{{ auth.user?.username || '用户' }}<el-icon><ArrowDown /></el-icon></span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="router.push('/settings')">个人设置</el-dropdown-item>
              <el-dropdown-item @click="auth.logout()">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-header>
      <el-main style="background: #f0f2f5; padding: 20px"><router-view /></el-main>
    </el-container>
  </el-container>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const currentRoute = computed(() => route.path)
</script>
