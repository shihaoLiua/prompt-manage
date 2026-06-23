<template>
  <div class="flex min-h-screen bg-[#F8FAFC]">
    <Sidebar />
    <div class="flex-1 flex flex-col">
      <Header
        :title="pageTitle"
        :username="auth.user?.username || '用户'"
        :initial="(auth.user?.username || 'U')[0].toUpperCase()"
      />
      <main class="flex-1 p-8">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Sidebar from './Sidebar.vue'
import Header from './Header.vue'

const route = useRoute()
const auth = useAuthStore()

const pageTitle = computed(() => {
  const map: Record<string, string> = {
    '/dashboard': '仪表盘',
    '/prompts': '提示词',
    '/settings': '设置',
    '/admin/api-configs': '全局 API 配置',
  }
  if (route.path.startsWith('/prompts/')) return '提示词'
  if (route.path.startsWith('/batch-tests/')) return '测试结果'
  return map[route.path] || 'Prompt Manager'
})

onMounted(() => {
  if (!auth.user) auth.fetchUser()
})
</script>
