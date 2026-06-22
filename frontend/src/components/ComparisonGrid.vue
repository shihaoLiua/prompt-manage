<template>
  <div v-if="results.length > 0">
    <h4>对比结果</h4>
    <el-table :data="results" border stripe style="width: 100%" max-height="600">
      <el-table-column label="配置" min-width="120"><template #default="{ row }"><strong>{{ row.label || row.model }}</strong></template></el-table-column>
      <el-table-column label="模型" width="120" prop="model" />
      <el-table-column label="状态" width="80"><template #default="{ row }"><el-tag :type="row.status === 'success' ? 'success' : 'danger'" size="small">{{ row.status === 'success' ? '成功' : '失败' }}</el-tag></template></el-table-column>
      <el-table-column label="延迟" width="100"><template #default="{ row }">{{ row.latency_ms ? `${row.latency_ms}ms` : '-' }}</template></el-table-column>
      <el-table-column label="响应内容" min-width="300"><template #default="{ row }"><div style="max-height: 200px; overflow-y: auto; white-space: pre-wrap; font-size: 13px; background: #f5f7fa; padding: 8px; border-radius: 4px">{{ row.response_text || row.error || '-' }}</div></template></el-table-column>
    </el-table>
  </div>
</template>
<script setup lang="ts">
defineProps<{ results: any[] }>()
</script>
