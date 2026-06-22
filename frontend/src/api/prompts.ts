import client from './client'
export async function fetchPrompts(params?: Record<string, any>) { return (await client.get('/prompts', { params })).data }
export async function fetchPrompt(id: string) { return (await client.get(`/prompts/${id}`)).data }
export async function createPrompt(data: any) { return (await client.post('/prompts', data)).data }
export async function updatePrompt(id: string, data: any) { return (await client.put(`/prompts/${id}`, data)).data }
export async function deletePrompt(id: string) { await client.delete(`/prompts/${id}`) }
