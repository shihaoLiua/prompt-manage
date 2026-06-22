<template>
  <div v-loading="loading">
    <el-page-header :content="prompt?.title" @back="router.push('/prompts')" />
    <div v-if="prompt" style="margin-top: 20px">
      <el-card>
        <template #header>
          <div style="display: flex; align-items: center; gap: 12px">
            <span style="font-size: 18px; font-weight: 600">{{ prompt.title }}</span>
            <el-icon v-if="prompt.is_favorite" color="#E6A23C" style="cursor: pointer" @click="toggleFav"><StarFilled /></el-icon>
            <el-icon v-else color="#999" style="cursor: pointer" @click="toggleFav"><Star /></el-icon>
            <el-rate v-model="rating" :max="5" @change="updateRating" style="display: inline-block" />
            <el-button size="small" @click="router.push(`/prompts/${prompt.id}/edit`)">编辑</el-button>
            <el-button size="small" @click="router.push(`/prompts/${prompt.id}/batch-test`)">批量测试</el-button>
            <el-button size="small" type="danger" @click="handleDelete">删除</el-button>
          </div>
        </template>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="描述">{{ prompt.description || '-' }}</el-descriptions-item>
          <el-descriptions-item label="版本">v{{ prompt.current_version }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ formatDate(prompt.updated_at) }}</el-descriptions-item>
        </el-descriptions>
        <h4 style="margin: 16px 0 8px">内容</h4>
        <pre style="background: #f5f7fa; padding: 16px; border-radius: 4px; white-space: pre-wrap">{{ prompt.content }}</pre>
      </el-card>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePromptsStore } from '@/stores/prompts'
import { ElMessage, ElMessageBox } from 'element-plus'
const route = useRoute()
const router = useRouter()
const store = usePromptsStore()
const loading = ref(true)
const prompt = computed(() => store.current)
const rating = ref(0)
function formatDate(iso: string) { return new Date(iso).toLocaleString('zh-CN') }
async function toggleFav() { if (!prompt.value) return; await store.toggleFavorite(prompt.value.id); await store.fetchOne(prompt.value.id) }
async function updateRating() { if (!prompt.value) return; await store.setRating(prompt.value.id, rating.value) }
async function handleDelete() {
  if (!prompt.value) return
  await ElMessageBox.confirm('确认删除？', '警告')
  await store.remove(prompt.value.id); ElMessage.success('已删除'); router.push('/prompts')
}
onMounted(async () => { await store.fetchOne(route.params.id as string); rating.value = prompt.value?.rating || 0; loading.value = false })
</script>
