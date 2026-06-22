import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import client from '@/api/client'
import type { User } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const isLoggedIn = computed(() => !!localStorage.getItem('access_token'))

  async function login(username: string, password: string) {
    const res = await client.post('/auth/login', { username, password })
    localStorage.setItem('access_token', res.data.access_token)
    localStorage.setItem('refresh_token', res.data.refresh_token)
    await fetchUser()
  }

  async function register(username: string, email: string, password: string) {
    await client.post('/auth/register', { username, email, password })
  }

  async function fetchUser() {
    try { user.value = (await client.get('/user/me')).data }
    catch { user.value = null }
  }

  function logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    user.value = null
    window.location.href = '/login'
  }

  return { user, isLoggedIn, login, register, fetchUser, logout }
})
