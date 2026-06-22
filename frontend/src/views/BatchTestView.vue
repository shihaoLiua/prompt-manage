<template>
  <div v-loading="loading">
    <el-page-header :content="`批量测试: ${prompt?.title}`" @back="router.push(`/prompts/${route.params.id}`)" />
    <el-card style="margin-top: 20px; max-width: 800px">
      <template #header>配置</template>
      <el-form :model="form" label-width="100px">
        <el-form-item label="批次名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="测试配置">
          <div v-for="(cfg, index) in form.configs" :key="index" style="display: flex; gap: 8px; margin-bottom: 8px; align-items: center">
            <el-input v-model="cfg.model" placeholder="模型" style="width: 150px" />
            <el-input v-model="cfg.label" placeholder="标签" style="width: 100px" />
            <el-button type="danger" :icon="Delete" circle @click="removeConfig(index)" />
          </div>
          <el-button size="small" @click="addConfig">+ 添加配置</el-button>
        </el-form-item>
        <el-form-item><el-button type="primary" :loading="running" @click="startBatch">开始测试</el-button></el-form-item>
      </el-form>
    </el-card>
    <el-card v-if="batchId" style="margin-top: 16px">
      <template #header>进度</template>
      <BatchProgress :completed="bp.completed" :total="bp.total" :results="bp.results" />
      <ComparisonGrid v-if="bp.completed === bp.total && bp.results.length > 0" :results="bp.results" />
    </el-card>
  </div>
</template>
<script setup lang="ts">
import { reactive, ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePromptsStore } from '@/stores/prompts'
import { ElMessage } from 'element-plus'
import client from '@/api/client'
import BatchProgress from '@/components/BatchProgress.vue'
import ComparisonGrid from '@/components/ComparisonGrid.vue'
import { Delete } from '@element-plus/icons-vue'
const route = useRoute()
const router = useRouter()
const store = usePromptsStore()
const loading = ref(true)
const running = ref(false)
const batchId = ref<string | null>(null)
const prompt = computed(() => store.current)
const form = reactive({ name: '', configs: [{ model: 'gpt-4o', label: 'GPT-4o' }] })
const bp = reactive({ completed: 0, total: 0, results: [] as any[] })
function addConfig() { form.configs.push({ model: '', label: '' }) }
function removeConfig(i: number) { form.configs.splice(i, 1) }
async function startBatch() {
  if (!prompt.value) return
  running.value = true
  try {
    const res = await client.post(`/prompts/${prompt.value.id}/batch-test`, form)
    batchId.value = res.data.id
    ElMessage.success('批量测试已创建')
    const es = new EventSource(`/api/batch-tests/${batchId.value}/stream?token=${localStorage.getItem('access_token')}`)
    es.addEventListener('progress', (e: MessageEvent) => { const d = JSON.parse(e.data); bp.completed = d.completed; bp.total = d.total; if (d.result) bp.results.push(d.result) })
    es.addEventListener('complete', () => { es.close(); running.value = false; ElMessage.success('批量测试完成') })
    es.addEventListener('error', (e: MessageEvent) => { ElMessage.error(JSON.parse(e.data).message); running.value = false; es.close() })
  } catch (e: any) { ElMessage.error(e.response?.data?.detail || '创建失败'); running.value = false }
}
onMounted(async () => { await store.fetchOne(route.params.id as string); loading.value = false })
</script>
