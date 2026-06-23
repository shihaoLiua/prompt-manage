<template>
  <div v-loading="loading">
    <el-page-header content="提示词详情" @back="router.push('/prompts')" />

    <div v-if="prompt" style="margin-top: 20px">
      <!-- Info Card -->
      <el-card>
        <template #header>
          <div class="detail-header">
            <div class="detail-title-row">
              <el-icon
                :color="prompt.is_favorite ? '#FFD166' : '#CBD5E1'"
                :size="22"
                style="cursor: pointer; transition: transform 0.2s"
                @click="toggleFav"
              >
                <StarFilled v-if="prompt.is_favorite" />
                <Star v-else />
              </el-icon>
              <span class="detail-title">{{ prompt.title }}</span>
              <el-rate v-model="rating" :max="5" @change="updateRating" style="display: inline-block" />
              <span class="detail-version">v{{ prompt.current_version }}</span>
            </div>
            <div class="detail-actions">
              <el-button size="small" :icon="Edit" @click="router.push(`/prompts/${prompt.id}/edit`)">编辑</el-button>
              <el-button size="small" :icon="DataBoard" @click="router.push(`/prompts/${prompt.id}/batch-test`)">批量测试</el-button>
              <el-button size="small" type="danger" :icon="Delete" plain @click="handleDelete">删除</el-button>
            </div>
          </div>
        </template>

        <el-descriptions :column="2" border class="pm-descriptions">
          <el-descriptions-item label="描述" :span="2">{{ prompt.description || '-' }}</el-descriptions-item>
          <el-descriptions-item label="分类">{{ categoryName || '-' }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ formatDate(prompt.updated_at) }}</el-descriptions-item>
          <el-descriptions-item label="标签" :span="2">
            <el-tag v-for="tag in prompt.tags" :key="tag.id" size="small" style="margin-right: 6px; margin-bottom: 2px">
              {{ tag.name }}
            </el-tag>
            <span v-if="!prompt.tags?.length" style="color: var(--pm-text-muted)">-</span>
          </el-descriptions-item>
        </el-descriptions>

        <h4 style="margin: 20px 0 8px; font-size: 14px; font-weight: 600; color: var(--pm-text-primary)">提示词内容</h4>
        <div class="content-block">{{ prompt.content }}</div>
      </el-card>

      <!-- Single Test Card -->
      <el-card style="margin-top: 20px">
        <template #header>
          <div style="display: flex; align-items: center; gap: 8px">
            <el-icon :size="18" color="#4361EE"><VideoPlay /></el-icon>
            <span>单次流式测试</span>
          </div>
        </template>

        <el-form :model="testForm" label-width="100px" label-position="top">
          <div style="display: flex; gap: 12px; flex-wrap: wrap">
            <el-form-item label="API 配置" style="flex: 1; min-width: 200px">
              <el-select v-model="testForm.api_config_id" placeholder="选择 API 配置" style="width: 100%">
                <el-option-group v-if="configStore.items.length" label="我的配置">
                  <el-option v-for="cfg in configStore.items" :key="cfg.id" :label="cfg.name" :value="cfg.id" />
                </el-option-group>
                <el-option-group v-if="configStore.globalItems.length" label="全局配置">
                  <el-option v-for="cfg in configStore.globalItems" :key="cfg.id" :label="cfg.name" :value="cfg.id" />
                </el-option-group>
                <el-empty v-if="!configStore.items.length && !configStore.globalItems.length" description="暂无配置，请先在设置中添加" />
              </el-select>
            </el-form-item>
            <el-form-item label="模型" style="flex: 0 0 180px">
              <el-input v-model="testForm.model" placeholder="如 gpt-4o" />
            </el-form-item>
            <el-form-item label=" " style="flex: 0 0 auto; align-self: flex-end">
              <el-button
                type="primary"
                :icon="VideoPlay"
                :loading="testing"
                :disabled="!testForm.api_config_id || !testForm.model"
                @click="startTest"
              >
                {{ testing ? '测试中...' : '运行测试' }}
              </el-button>
            </el-form-item>
          </div>
        </el-form>

        <!-- Stream output -->
        <div v-if="streamStatus !== 'idle'" style="margin-top: 16px">
          <StreamOutput ref="streamRef" />
        </div>

        <!-- Empty state -->
        <div v-if="streamStatus === 'idle'" style="text-align: center; padding: 40px 0; color: var(--pm-text-muted)">
          <el-icon :size="48" color="#E2E8F0"><ChatLineSquare /></el-icon>
          <p style="margin-top: 12px; font-size: 14px">选择 API 配置和模型后点击"运行测试"</p>
        </div>
      </el-card>

      <!-- Test History Card -->
      <el-card style="margin-top: 20px">
        <template #header>
          <div style="display: flex; align-items: center; gap: 8px">
            <el-icon :size="18" color="#4361EE"><Timer /></el-icon>
            <span>测试历史</span>
          </div>
        </template>
        <el-table :data="testRuns" v-if="testRuns.length" stripe style="width: 100%">
          <el-table-column prop="model" label="模型" width="120" />
          <el-table-column label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.status === 'success' ? 'success' : row.status === 'running' ? 'warning' : 'danger'" size="small">
                {{ row.status === 'success' ? '成功' : row.status === 'running' ? '运行中' : '失败' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="latency_ms" label="延迟" width="100">
            <template #default="{ row }">{{ row.latency_ms ? `${row.latency_ms}ms` : '-' }}</template>
          </el-table-column>
          <el-table-column prop="created_at" label="时间" width="180">
            <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="80">
            <template #default="{ row }">
              <el-button size="small" text type="primary" @click="deleteRun(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-else description="暂无测试记录" />
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePromptsStore } from '@/stores/prompts'
import { useApiConfigsStore } from '@/stores/apiConfigs'
import { useCategoriesStore } from '@/stores/categories'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Edit, Delete, DataBoard, VideoPlay, Timer, ChatLineSquare } from '@element-plus/icons-vue'
import client from '@/api/client'
import StreamOutput from '@/components/StreamOutput.vue'

const route = useRoute()
const router = useRouter()
const store = usePromptsStore()
const configStore = useApiConfigsStore()
const catStore = useCategoriesStore()
const streamRef = ref()
const loading = ref(true)
const testing = ref(false)
const testRuns = ref<any[]>([])

const prompt = computed(() => store.current)
const rating = ref(0)
const streamStatus = ref<'idle' | 'running' | 'success' | 'error'>('idle')

const testForm = ref({ api_config_id: '', model: 'gpt-4o' })

const categoryName = computed(() => {
  if (!prompt.value?.category_id) return null
  function findCat(list: any[]): any {
    for (const c of list) {
      if (c.id === prompt.value?.category_id) return c
      if (c.children) { const found = findCat(c.children); if (found) return found }
    }
    return null
  }
  return findCat(catStore.tree)?.name
})

function formatDate(iso: string) {
  return new Date(iso).toLocaleString('zh-CN')
}

async function toggleFav() {
  if (!prompt.value) return
  await store.toggleFavorite(prompt.value.id)
  await store.fetchOne(prompt.value.id)
}

async function updateRating() {
  if (!prompt.value) return
  await store.setRating(prompt.value.id, rating.value)
}

async function handleDelete() {
  if (!prompt.value) return
  await ElMessageBox.confirm('确认删除此提示词？此操作不可撤销。', '删除确认', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning',
  })
  await store.remove(prompt.value.id)
  ElMessage.success('已删除')
  router.push('/prompts')
}

async function startTest() {
  if (!prompt.value || !testForm.value.api_config_id) return
  testing.value = true
  streamStatus.value = 'running'
  try {
    const token = localStorage.getItem('access_token')
    const resp = await fetch(`/api/prompts/${prompt.value.id}/test`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        api_config_id: testForm.value.api_config_id,
        model: testForm.value.model,
        variables: {},
      }),
    })

    if (!resp.ok) {
      const err = await resp.json()
      ElMessage.error(err.detail || '测试启动失败')
      streamStatus.value = 'idle'
      return
    }

    const reader = resp.body?.getReader()
    if (!reader) return

    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })

      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            streamRef.value?.handleEvent(data)
            if (data.type === 'done') {
              streamStatus.value = 'success'
              loadTestRuns()
            } else if (data.type === 'error') {
              streamStatus.value = 'error'
            }
          } catch {}
        }
      }
    }
  } catch (e: any) {
    streamStatus.value = 'idle'
    ElMessage.error(e.message || '连接失败')
  } finally {
    testing.value = false
  }
}

async function deleteRun(id: string) {
  await client.delete(`/test-runs/${id}`)
  ElMessage.success('已删除')
  loadTestRuns()
}

async function loadTestRuns() {
  if (!prompt.value) return
  try { testRuns.value = (await client.get(`/prompts/${prompt.value.id}/test-runs`)).data } catch {}
}

onMounted(async () => {
  const id = route.params.id as string
  await store.fetchOne(id)
  rating.value = prompt.value?.rating || 0
  await Promise.all([
    configStore.fetchMine(),
    configStore.fetchGlobal(),
    catStore.fetchTree(),
    loadTestRuns(),
  ])
  loading.value = false
})
</script>

<style scoped>
.detail-header {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.detail-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--pm-text-primary);
}

.detail-version {
  font-size: 12px;
  font-weight: 600;
  color: var(--pm-primary);
  background: var(--pm-primary-light);
  padding: 2px 8px;
  border-radius: 4px;
}

.detail-actions {
  display: flex;
  gap: 8px;
}

.pm-descriptions {
  margin-top: 4px;
}
</style>
