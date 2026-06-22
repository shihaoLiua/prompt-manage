import client from './client'
export async function loginApi(username: string, password: string) { return (await client.post('/auth/login', { username, password })).data }
export async function registerApi(username: string, email: string, password: string) { await client.post('/auth/register', { username, email, password }) }
