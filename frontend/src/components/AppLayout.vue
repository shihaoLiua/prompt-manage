<template>
  <el-container class="pm-root">
    <!-- Sidebar -->
    <el-aside width="240px" class="pm-sidebar">
      <div class="pm-sidebar-header">
        <div class="pm-logo">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#06B6D4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/>
          </svg>
          <span>Prompt Manager</span>
        </div>
      </div>
      <el-menu
        :default-active="currentRoute"
        class="pm-sidebar-menu"
        router
      >
        <el-menu-item index="/dashboard">
          <el-icon><Grid /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/prompts">
          <el-icon><FileText /></el-icon>
          <span>提示词</span>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Settings /></el-icon>
          <span>设置</span>
        </el-menu-item>
        <el-menu-item v-if="auth.user?.is_admin" index="/admin/api-configs">
          <el-icon><Shield /></el-icon>
          <span>全局 API 配置</span>
        </el-menu-item>
      </el-menu>
      <div class="pm-sidebar-footer">
        <div class="pm-version">v0.1.0</div>
      </div>
    </el-aside>

    <!-- Main -->
    <el-container>
      <!-- Header -->
      <el-header class="pm-header">
        <div class="pm-header-left">
          <span class="pm-header-path">{{ routeName }}</span>
        </div>
        <div class="pm-header-right">
          <el-dropdown trigger="click">
            <span class="pm-user-dropdown">
              <el-avatar :size="30" style="background: var(--pm-accent); color: #09090B; font-weight: 700; font-size: 13px">
                {{ (auth.user?.username || 'U')[0].toUpperCase() }}
              </el-avatar>
              <span class="pm-username">{{ auth.user?.username || '用户' }}</span>
              <el-icon class="pm-chevron"><ChevronDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="router.push('/settings')">
                  <el-icon><Settings /></el-icon> 个人设置
                </el-dropdown-item>
                <el-dropdown-item divided @click="auth.logout()">
                  <el-icon><LogOut /></el-icon> 退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- Content -->
      <el-main class="pm-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const currentRoute = computed(() => route.path)

const routeName = computed(() => {
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

<style scoped>
.pm-root {
  min-height: 100vh;
  background: var(--pm-bg-base);
}

/* === Sidebar === */
.pm-sidebar {
  background: var(--pm-sidebar-bg);
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--pm-sidebar-border);
  overflow: hidden;
}

.pm-sidebar-header {
  height: 64px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  border-bottom: 1px solid var(--pm-sidebar-border);
}

.pm-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--pm-text-primary);
  font-size: 16px;
  font-weight: 700;
  letter-spacing: -0.3px;
}

.pm-sidebar-menu {
  flex: 1;
  border-right: none !important;
  padding: 12px 8px;
  background: transparent !important;
}

.pm-sidebar-menu .el-menu-item {
  height: 42px;
  line-height: 42px;
  margin: 2px 0;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--pm-sidebar-text) !important;
  background: transparent !important;
  transition: all 0.12s;
}

.pm-sidebar-menu .el-menu-item:hover {
  background: var(--pm-bg-hover) !important;
  color: var(--pm-text-primary) !important;
}

.pm-sidebar-menu .el-menu-item.is-active {
  background: var(--pm-accent-bg) !important;
  color: var(--pm-accent) !important;
  font-weight: 600;
}

.pm-sidebar-menu .el-menu-item .el-icon {
  margin-right: 10px;
  font-size: 18px;
}

.pm-sidebar-footer {
  padding: 16px 20px;
  border-top: 1px solid var(--pm-sidebar-border);
}

.pm-version {
  color: var(--pm-text-tertiary);
  font-size: 11px;
  text-align: center;
  letter-spacing: 0.5px;
}

/* === Header === */
.pm-header {
  background: var(--pm-header-bg);
  border-bottom: 1px solid var(--pm-header-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px !important;
  height: 64px !important;
}

.pm-header-left {
  display: flex;
  align-items: center;
}

.pm-header-path {
  font-size: 14px;
  font-weight: 500;
  color: var(--pm-text-secondary);
}

.pm-header-right {
  display: flex;
  align-items: center;
}

.pm-user-dropdown {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 8px;
  transition: background 0.12s;
}

.pm-user-dropdown:hover {
  background: var(--pm-bg-hover);
}

.pm-username {
  font-size: 14px;
  font-weight: 500;
  color: var(--pm-text-primary);
}

.pm-chevron {
  color: var(--pm-text-tertiary);
  font-size: 14px;
}

/* === Content === */
.pm-content {
  background: var(--pm-bg-base);
  padding: 24px !important;
}
</style>
