<template>
  <aside class="w-[220px] min-h-screen bg-sidebar-bg flex flex-col flex-shrink-0">
    <!-- Logo -->
    <div class="h-16 flex items-center px-4 border-b border-sidebar-border gap-3">
      <div class="w-8 h-8 rounded-lg bg-brand-500 flex items-center justify-center">
        <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
          <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm0 6a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6z" opacity="0.7"/>
          <path d="M15 9a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6a1 1 0 011-1h2z"/>
        </svg>
      </div>
      <span class="text-white font-semibold text-base">Prompt Manager</span>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 py-4 px-3 space-y-1">
      <router-link
        v-for="item in menuItems"
        :key="item.path"
        :to="item.path"
        class="nav-item"
        :class="{ 'nav-item-active': currentRoute === item.path }"
      >
        <div class="active-indicator" :class="{ 'active-indicator-visible': currentRoute === item.path }" />
        <component :is="item.icon" class="w-5 h-5 flex-shrink-0" />
        <span>{{ item.label }}</span>
      </router-link>
    </nav>

    <!-- Version -->
    <div class="px-6 py-4">
      <span class="text-[11px] text-gray-500">v0.1.0</span>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  Squares2X2Icon,
  DocumentTextIcon,
  Cog6ToothIcon,
  ShieldCheckIcon,
} from '@heroicons/vue/24/outline'

const route = useRoute()
const currentRoute = computed(() => route.path)

const menuItems = [
  { path: '/dashboard', label: '仪表盘', icon: Squares2X2Icon },
  { path: '/prompts', label: '提示词', icon: DocumentTextIcon },
  { path: '/settings', label: '设置', icon: Cog6ToothIcon },
  { path: '/admin/api-configs', label: '全局 API 配置', icon: ShieldCheckIcon },
]
</script>

<style scoped>
.nav-item {
  @apply flex items-center h-11 px-4 gap-3 rounded-lg text-sm font-medium relative;
  color: #9CA3AF;
  transition: all 0.15s;
}

.nav-item:hover {
  background: #1F2937;
  color: #FFFFFF;
}

.nav-item-active {
  background: #1F2937;
  color: #FFFFFF;
}

.active-indicator {
  @apply absolute left-0 w-[3px] h-5 rounded-r-full;
  background: transparent;
  transition: all 0.15s;
}

.active-indicator-visible {
  background: #3B82F6;
}
</style>
