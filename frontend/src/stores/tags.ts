import { defineStore } from 'pinia'
import { ref } from 'vue'
import client from '@/api/client'
import type { Tag } from '@/types'
export const useTagsStore = defineStore('tags', () => {
  const items = ref<Tag[]>([])
  const loading = ref(false)
  async function fetchAll() { loading.value = true; try { items.value = (await client.get('/tags')).data } finally { loading.value = false } }
  async function create(data: { name: string; color?: string }) { const r = await client.post('/tags', data); await fetchAll(); return r.data }
  async function remove(id: string) { await client.delete(`/tags/${id}`); await fetchAll() }
  return { items, loading, fetchAll, create, remove }
})
