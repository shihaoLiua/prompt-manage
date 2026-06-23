<template>
  <div v-loading="loading" element-loading-background="rgba(9, 9, 11, 0.7)">
    <el-page-header content="提示词详情" @back="router.push('/prompts')" />

    <div v-if="prompt" style="margin-top: 20px">
      <!-- Info Card -->
      <el-card>
        <template #header>
          <div class="detail-header">
            <div class="detail-title-row">
              <el-icon
                :color="prompt.is_favorite ? '#F59E0B' : '#3F3F46'"
                :size="20"
                style="cursor: pointer; transition: color 0.15s"
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
              <el-button size="small" type="danger" :icon="DeleteIcon" plain @click="handleDelete">删除</el-button>
            </div>
          </div>
        </template>

        <div class="detail-meta">
          <div class="meta-item">
            <span class="meta-label">描述</span>
            <span class="meta-value">{{ prompt.description || '—' }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">分类</span>
            <span class="meta-value">{{ categoryName || '—' }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">更新时间</span>
            <span class="meta-value">{{ formatDate(prompt.updated_at) }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">标签</span>
            <span class="meta-value">
              <el-tag v-for="tag in prompt.tags" :key="tag.id" size="small" style="margin-right: 4px">
                {{ tag.name }}
              </el-tag>
              <span v-if="!prompt.tags?.length" style="color: var(--pm-text-tertiary)">—</span>
            </span>
          </div>
        </div>

        <h4 class="section-title">提示词内容</h4>
        <div class="content-block">{{ prompt.content }}</div>
      </el-card>

      <!-- Single Test Card -->
      <el-card style="margin-top: 16px">
        <template #header>
          <div class="card-header-with-icon">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#06B6D4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3"/></svg>
            <span>单次流式测试</span>
          </div>
        </template>

        <div class="test-form-row">
          <div class="test-form-field" style="flex: 1; min-width: 200px">
            <label class="test-label">API 配置</label>
            <el-select v-model="testForm.api_config_id" placeholder="选择 API 配置" style="width: 100%">
              <el-option-group v-if="configStore.items.length" label="我的配置">
                <el-option v-for="cfg in configStore.items" :key="cfg.id" :label="cfg.name" :value="cfg.id" />
              </el-option-group>
              <el-option-group v-if="configStore.globalItems.length" label="全局配置">
                <el-option v-for="cfg in configStore.globalItems" :key="cfg.id" :label="cfg.name" :value="cfg.id" />
              </el-option-group>
              <template #empty>
                <div style="padding: 12px; color: var(--pm-text-tertiary); font-size: 13px">暂无配置，请在设置中添加</div>
              </template>
            </el-select>
          </div>
          <div class="test-form-field" style="flex: 0 0 160px">
            <label class="test-label">模型</label>
            <el-input v-model="testForm.model" placeholder="如 gpt-4o" />
          </div>
          <div class="test-form-field" style="flex: 0 0 auto; align-self: flex-end">
            <el-button
              type="primary"
              :icon="VideoPlay"
              :loading="testing"
              :disabled="!testForm.api_config_id || !testForm.model"
              size="large"
              @click="startTest"
            >
              {{ testing ? '运行中' : '运行测试' }}
            </el-button>
          </div>
        </div>

        <!-- Variable inputs -->
        <div v-if="prompt.variables?.length" class="test-vars-section">
          <label class="test-label" style="margin-bottom: 8px; display: block">变量</label>
          <div class="test-vars-grid">
            <div
              v-for="(v, i) in prompt.variables"
              :key="i"
              class="test-form-field"
            >
              <label class="test-var-label">{{ v.label || v.name }}</label>
              <el-input
                v-if="v.type === 'select' && v.options?.length"
                v-model="testVarValues[v.name]"
                :placeholder="v.default || v.name"
              >
                <template #append>
                  <el-select v-model="testVarValues[v.name]" style="width: 110px">
                    <el-option v-for="opt in v.options" :key="opt" :label="opt" :value="opt" />
                  </el-select>
                </template>
              </el-input>
              <el-input
                v-else
                v-model="testVarValues[v.name]"
                :placeholder="v.default || v.name"
              />
            </div>
          </div>
        </div>

        <div v-if="streamStatus !== 'idle'" style="margin-top: 16px">
          <StreamOutput ref="streamRef" />
        </div>

        <div v-if="streamStatus === 'idle'" class="test-empty-state">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#3F3F46" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="5 3 19 12 5 21 5 3"/>
          </svg>
          <p>选择 API 配置和模型后点击运行</p>
        </div>
      </el-card>

      <!-- Test History -->
      <el-card style="margin-top: 16px">
        <template #header>
          <div class="card-header-with-icon">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#06B6D4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            <span>测试历史</span>
          </div>
        </template>
        <el-table :data="testRuns" v-if="testRuns.length" stripe style="width: 100%">
          <el-table-column prop="model" label="模型" width="120" />
          <el-table-column label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="row.status === 'success' ? 'success' : row.status === 'running' ? 'warning' : 'danger'" size="small" effect="dark">
                {{ row.status === 'success' ? '成功' : row.status === 'running' ? '运行中' : '失败' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="延迟" width="100">
            <template #default="{ row }">{{ row.latency_ms ? `${row.latency_ms}ms` : '—' }}</template>
          </el-table-column>
          <el-table-column label="时间" width="170">
            <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="70">
            <template #default="{ row }">
              <el-button size="small" text type="danger" @click="deleteRun(row.id)">删除</el-button>
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
import { Edit, Delete as DeleteIcon, DataBoard, VideoPlay } from '@element-plus/icons-vue'
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
const testVarValues = ref<Record<string, string>>({})

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

function initVarValues() {
  const vars: Record<string, string> = {}
  if (prompt.value?.variables) {
    for (const v of prompt.value.variables) {
      vars[v.name] = v.default || ''
    }
  }
  testVarValues.value = vars
}

async function startTest() {
  if (!prompt.value || !testForm.value.api_config_id) return
  testing.value = true
  streamStatus.value = 'running'
  streamRef.value?.reset()
  try {
    const token = localStorage.getItem('access_token')
    const resp = await fetch(`/api/prompts/${prompt.value.id}/test`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        api_config_id: testForm.value.api_config_id,
        model: testForm.value.model,
        variables: testVarValues.value,
      }),
    })

    if (!resp.ok) {
      const err = await resp.json()
      ElMessage.error(err.detail || '测试启动失败')
      streamStatus.value = 'idle'
      testing.value = false
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
  initVarValues()
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
  font-size: 11px;
  font-weight: 600;
  color: var(--pm-accent);
  background: var(--pm-accent-bg);
  padding: 2px 8px;
  border-radius: 4px;
  letter-spacing: 0.3px;
}

.detail-actions {
  display: flex;
  gap: 8px;
}

.detail-meta {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
  border: 1px solid var(--pm-border);
  border-radius: 8px;
  overflow: hidden;
}

.meta-item {
  display: flex;
  border-bottom: 1px solid var(--pm-border-light);
  border-right: 1px solid var(--pm-border-light);
}

.meta-item:nth-child(even) {
  border-right: none;
}

.meta-item:nth-last-child(-n+2) {
  border-bottom: none;
}

.meta-label {
  flex: 0 0 80px;
  padding: 10px 12px;
  font-size: 13px;
  font-weight: 500;
  color: var(--pm-text-secondary);
  background: var(--pm-bg-elevated);
}

.meta-value {
  flex: 1;
  padding: 10px 12px;
  font-size: 13px;
  color: var(--pm-text-primary);
}

.section-title {
  margin: 20px 0 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--pm-text-primary);
}

.card-header-with-icon {
  display: flex;
  align-items: center;
  gap: 8px;
}

.test-form-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: flex-end;
}

.test-form-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.test-label {
  font-size: 12px;
  font-weight: 500;
  color: var(--pm-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.test-empty-state {
  text-align: center;
  padding: 40px 0;
  color: var(--pm-text-tertiary);
}

.test-empty-state p {
  margin-top: 12px;
  font-size: 14px;
}

.test-vars-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #E5E7EB;
}

.test-vars-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}

.test-var-label {
  font-size: 13px;
  font-weight: 500;
  color: #374151;
}
</style>
