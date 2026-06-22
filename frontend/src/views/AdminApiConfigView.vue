<template>
  <div>
    <h2>全局 API 配置</h2>
    <p style="color: #999; font-size: 13px">全局配置对所有用户可见可用，仅管理员可管理。</p>
    <el-card style="margin-top: 16px">
      <el-table :data="configStore.globalItems" stripe style="width: 100%">
        <el-table-column prop="name" label="名称" min-width="120" />
        <el-table-column prop="api_base" label="API 地址" min-width="200" />
        <el-table-column prop="default_model" label="默认模型" width="140" />
        <el-table-column label="状态" width="80"><template #default="{ row }"><el-tag :type="row.is_active ? 'success' : 'info'" size="small">{{ row.is_active ? '启用' : '禁用' }}</el-tag></template></el-table-column>
      </el-table>
    </el-card>
  </div>
</template>
<script setup lang="ts">
import { onMounted } from 'vue'
import { useApiConfigsStore } from '@/stores/apiConfigs'
const configStore = useApiConfigsStore()
onMounted(() => configStore.fetchGlobal())
</script>
