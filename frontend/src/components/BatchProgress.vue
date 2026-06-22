<template>
  <div v-if="total > 0">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px">
      <el-progress :percentage="percentage" :stroke-width="16" style="flex: 1" />
      <span style="color: #999; font-size: 13px">{{ completed }}/{{ total }}</span>
    </div>
    <div v-for="(item, index) in results" :key="index" style="display: flex; align-items: center; gap: 8px; padding: 4px 0; font-size: 13px">
      <el-icon v-if="item.status === 'success'" color="#67C23A"><CircleCheck /></el-icon>
      <el-icon v-else-if="item.status === 'error'" color="#F56C6C"><CircleClose /></el-icon>
      <span>{{ item.label || item.model }}</span>
      <span v-if="item.error" style="color: #f56c6c; margin-left: 8px">{{ item.error }}</span>
    </div>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
const props = defineProps<{ completed: number; total: number; results: any[] }>()
const percentage = computed(() => Math.round((props.completed / props.total) * 100))
</script>
