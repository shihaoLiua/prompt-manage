<template>
  <el-container style="min-height: 100vh">
    <!-- Sidebar -->
    <el-aside width="240px" class="pm-sidebar">
      <div class="pm-sidebar-header">
        <div class="pm-logo">
          <el-icon :size="22" color="#4361EE"><MagicStick /></el-icon>
          <span>Prompt Manager</span>
        </div>
      </div>
      <el-menu
        :default-active="currentRoute"
        :collapse="false"
        class="pm-sidebar-menu"
        router
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataBoard /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/prompts">
          <el-icon><Document /></el-icon>
          <span>提示词</span>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <span>设置</span>
        </el-menu-item>
        <el-menu-item v-if="auth.user?.is_admin" index="/admin/api-configs">
          <el-icon><Tools /></el-icon>
          <span>全局 API 配置</span>
        </el-menu-item>
      </el-menu>
      <div class="pm-sidebar-footer">
        <div class="pm-version">v0.1.0</div>
      </div>
    </el-aside>

    <!-- Main area -->
    <el-container>
      <!-- Header -->
      <el-header class="pm-header">
        <div class="pm-header-left">
          <el-icon :size="18" color="#A3AED0"><Search /></el-icon>
          <span class="pm-header-path">{{ currentRoute === '/dashboard' ? '仪表盘' : currentRoute }}</span>
        </div>
        <div class="pm-header-right">
          <el-dropdown trigger="click">
            <span class="pm-user-dropdown">
              <el-avatar :size="32" style="background: var(--pm-primary-gradient); font-weight: 600;">
                {{ (auth.user?.username || 'U')[0].toUpperCase() }}
              </el-avatar>
              <span class="pm-username">{{ auth.user?.username || '用户' }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="router.push('/settings')">
                  <el-icon><Setting /></el-icon>个人设置
                </el-dropdown-item>
                <el-dropdown-item divided @click="auth.logout()">
                  <el-icon><SwitchButton /></el-icon>退出登录
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

onMounted(() => {
  if (!auth.user) auth.fetchUser()
})
</script>

<style scoped>
.pm-sidebar {
  background: var(--pm-sidebar-bg);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.pm-sidebar-header {
  height: 64px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.pm-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #fff;
  font-size: 17px;
  font-weight: 700;
  letter-spacing: -0.3px;
}

.pm-sidebar-menu {
  flex: 1;
  border-right: none !important;
  padding: 12px 0;
}

.pm-sidebar-menu .el-menu-item {
  height: 44px;
  line-height: 44px;
  margin: 2px 8px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--pm-sidebar-text) !important;
}

.pm-sidebar-menu .el-menu-item:hover {
  background: var(--pm-sidebar-hover) !important;
  color: #fff !important;
}

.pm-sidebar-menu .el-menu-item.is-active {
  background: var(--pm-primary) !important;
  color: #fff !important;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(67, 97, 238, 0.3);
}

.pm-sidebar-menu .el-menu-item .el-icon {
  margin-right: 10px;
  font-size: 18px;
}

.pm-sidebar-footer {
  padding: 16px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.pm-version {
  color: rgba(255, 255, 255, 0.2);
  font-size: 12px;
  text-align: center;
}

/* Header */
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
  gap: 10px;
}

.pm-header-path {
  color: var(--pm-text-muted);
  font-size: 13px;
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
  transition: background 0.2s;
}

.pm-user-dropdown:hover {
  background: var(--pm-border-light);
}

.pm-username {
  font-size: 14px;
  font-weight: 500;
  color: var(--pm-text-primary);
}

/* Content */
.pm-content {
  background: var(--pm-page-bg);
  padding: 24px !important;
}
</style>
