import { defineStore } from 'pinia'
import { ref } from 'vue'
import client from '@/api/client'
import type { Category } from '@/types'
export const useCategoriesStore = defineStore('categories', () => {
  const tree = ref<Category[]>([])
  const loading = ref(false)
  async function fetchTree() { loading.value = true; try { tree.value = (await client.get('/categories')).data } finally { loading.value = false } }
  async function create(data: { name: string; parent_id?: string | null; sort_order?: number }) { const r = await client.post('/categories', data); await fetchTree(); return r.data }
  async function remove(id: string) { await client.delete(`/categories/${id}`); await fetchTree() }
  return { tree, loading, fetchTree, create, remove }
})
