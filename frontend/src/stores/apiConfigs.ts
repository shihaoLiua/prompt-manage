import { defineStore } from 'pinia'
import { ref } from 'vue'
import client from '@/api/client'
import type { ApiConfig } from '@/types'
export const useApiConfigsStore = defineStore('apiConfigs', () => {
  const items = ref<ApiConfig[]>([])
  const globalItems = ref<ApiConfig[]>([])
  const loading = ref(false)
  async function fetchMine() { loading.value = true; try { items.value = (await client.get('/user/api-configs')).data } finally { loading.value = false } }
  async function fetchGlobal() { globalItems.value = (await client.get('/user/api-configs/global')).data }
  async function create(data: { name: string; api_base: string; api_key: string; default_model: string }) { const r = await client.post('/user/api-configs', data); await fetchMine(); return r.data }
  async function update(id: string, data: Partial<ApiConfig & { api_key?: string }>) { const r = await client.put(`/user/api-configs/${id}`, data); await fetchMine(); return r.data }
  async function remove(id: string) { await client.delete(`/user/api-configs/${id}`); await fetchMine() }
  return { items, globalItems, loading, fetchMine, fetchGlobal, create, update, remove }
})
