import client from './client'
export async function fetchTestRuns(promptId: string) { return (await client.get(`/prompts/${promptId}/test-runs`)).data }
export async function fetchBatchTests() { return (await client.get('/batch-tests')).data }
export async function fetchBatchDetail(id: string) { return (await client.get(`/batch-tests/${id}`)).data }
export async function deleteBatchTest(id: string) { await client.delete(`/batch-tests/${id}`) }
