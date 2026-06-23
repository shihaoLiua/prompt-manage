<template>
  <header class="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-8">
    <h1 class="text-xl font-semibold text-[#111827]">{{ title }}</h1>
    <el-dropdown trigger="click">
      <div class="flex items-center gap-3 cursor-pointer hover:bg-gray-50 rounded-lg px-3 py-2 transition-colors">
        <div class="w-8 h-8 rounded-full bg-brand-500 flex items-center justify-center text-white text-sm font-bold">
          {{ initial }}
        </div>
        <span class="text-sm font-medium text-gray-700">{{ username }}</span>
        <el-icon class="text-gray-400 text-xs"><ArrowDown /></el-icon>
      </div>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item @click="router.push('/settings')">
            <el-icon><Setting /></el-icon> 个人设置
          </el-dropdown-item>
          <el-dropdown-item divided @click="authStore.logout()">
            <el-icon><SwitchButton /></el-icon> 退出登录
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </header>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

defineProps<{
  title: string
  username: string
  initial: string
}>()

const router = useRouter()
const authStore = useAuthStore()
</script>
