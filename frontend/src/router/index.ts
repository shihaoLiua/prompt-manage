import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  { path: '/login', name: 'Login', component: () => import('@/views/LoginView.vue'), meta: { noAuth: true } },
  { path: '/register', name: 'Register', component: () => import('@/views/RegisterView.vue'), meta: { noAuth: true } },
  {
    path: '/',
    component: () => import('@/components/AppLayout.vue'),
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', name: 'Dashboard', component: () => import('@/views/DashboardView.vue') },
      { path: 'prompts', name: 'PromptList', component: () => import('@/views/PromptListView.vue') },
      { path: 'prompts/new', name: 'PromptNew', component: () => import('@/views/PromptEditView.vue') },
      { path: 'prompts/:id', name: 'PromptDetail', component: () => import('@/views/PromptDetailView.vue') },
      { path: 'prompts/:id/edit', name: 'PromptEdit', component: () => import('@/views/PromptEditView.vue') },
      { path: 'prompts/:id/batch-test', name: 'BatchTest', component: () => import('@/views/BatchTestView.vue') },
      { path: 'batch-tests/:id', name: 'BatchResult', component: () => import('@/views/BatchResultView.vue') },
      { path: 'settings', name: 'Settings', component: () => import('@/views/SettingsView.vue') },
      { path: 'admin/api-configs', name: 'AdminApiConfig', component: () => import('@/views/AdminApiConfigView.vue') },
    ],
  },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('access_token')
  if (!to.meta.noAuth && !token) next('/login')
  else if (to.meta.noAuth && token && to.name === 'Login') next('/')
  else next()
})

export default router
