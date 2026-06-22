import { defineStore } from 'pinia'
import { ref } from 'vue'
import client from '@/api/client'
import type { Prompt, PromptListItem } from '@/types'

export const usePromptsStore = defineStore('prompts', () => {
  const items = ref<PromptListItem[]>([])
  const total = ref(0)
  const current = ref<Prompt | null>(null)
  const loading = ref(false)
  async function fetchList(params?: Record<string, any>) {
    loading.value = true
    try { const res = await client.get('/prompts', { params }); items.value = res.data.items; total.value = res.data.total }
    finally { loading.value = false }
  }
  async function fetchOne(id: string) { current.value = (await client.get(`/prompts/${id}`)).data }
  async function create(data: Partial<Prompt>) { return (await client.post('/prompts', data)).data }
  async function update(id: string, data: Partial<Prompt>) { current.value = (await client.put(`/prompts/${id}`, data)).data }
  async function remove(id: string) { await client.delete(`/prompts/${id}`) }
  async function toggleFavorite(id: string) { return (await client.put(`/prompts/${id}/favorite`)).data.is_favorite }
  async function setRating(id: string, rating: number) { await client.put(`/prompts/${id}/rating`, { rating }) }
  return { items, total, current, loading, fetchList, fetchOne, create, update, remove, toggleFavorite, setRating }
})
