<template>
  <div v-loading="loading">
    <el-page-header :content="batch?.name || '批量测试详情'" @back="router.push('/dashboard')" />
    <el-card v-if="batch" style="margin-top: 20px">
      <template #header>{{ batch.name }} <el-tag :type="statusType" style="margin-left: 12px">{{ batch.status }}</el-tag></template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="总数">{{ batch.total_count }}</el-descriptions-item>
        <el-descriptions-item label="完成">{{ batch.completed_count }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDate(batch.created_at) }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import client from '@/api/client'
const route = useRoute()
const router = useRouter()
const loading = ref(true)
const batch = ref<any>(null)
const statusType = computed(() => ({ pending: 'info', running: 'warning', completed: 'success', partial: 'warning', failed: 'danger' } as any)[batch.value?.status] || 'info')
function formatDate(iso: string) { return new Date(iso).toLocaleString('zh-CN') }
onMounted(async () => {
  try { batch.value = (await client.get(`/batch-tests/${route.params.id}`)).data } catch {}
  finally { loading.value = false }
})
</script>
