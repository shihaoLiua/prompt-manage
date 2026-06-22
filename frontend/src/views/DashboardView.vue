<template>
  <div>
    <h2>仪表盘</h2>
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="6"><el-card shadow="hover"><div style="text-align: center"><div style="font-size: 36px; color: #409EFF">{{ promptCount }}</div><div style="color: #999; margin-top: 8px">提示词总数</div></div></el-card></el-col>
      <el-col :span="6"><el-card shadow="hover"><div style="text-align: center"><div style="font-size: 36px; color: #67C23A">{{ batchCount }}</div><div style="color: #999; margin-top: 8px">测试批次</div></div></el-card></el-col>
    </el-row>
    <el-card style="margin-top: 24px">
      <template #header>最近更新</template>
      <el-table :data="recentPrompts" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column prop="updated_at" label="更新时间" width="180"><template #default="{ row }">{{ formatDate(row.updated_at) }}</template></el-table-column>
      </el-table>
    </el-card>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { fetchPrompts } from '@/api/prompts'
import { fetchBatchTests } from '@/api/tests'
const promptCount = ref(0)
const batchCount = ref(0)
const recentPrompts = ref<any[]>([])
const loading = ref(true)
function formatDate(iso: string) { return new Date(iso).toLocaleString('zh-CN') }
onMounted(async () => {
  try { const [p, b] = await Promise.all([fetchPrompts({ page: 1, page_size: 10 }), fetchBatchTests()]); recentPrompts.value = p.items; promptCount.value = p.total; batchCount.value = b.length }
  finally { loading.value = false }
})
</script>
