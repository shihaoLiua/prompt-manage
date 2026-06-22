<template>
  <div>
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px">
      <span style="font-weight: 600">变量定义</span>
      <el-button size="small" type="primary" plain @click="add">添加变量</el-button>
    </div>
    <div v-for="(v, i) in modelValue" :key="i" style="display: flex; gap: 8px; align-items: center; margin-bottom: 8px">
      <el-input v-model="v.name" placeholder="变量名" size="small" style="width: 120px" />
      <el-input v-model="v.label" placeholder="标签" size="small" style="width: 100px" />
      <el-input v-model="v.default" placeholder="默认值" size="small" style="width: 100px" />
      <el-button size="small" type="danger" :icon="Delete" circle @click="remove(i)" />
    </div>
    <div v-if="modelValue.length === 0" style="color: #999; font-size: 13px">暂无变量</div>
  </div>
</template>
<script setup lang="ts">
import { Delete } from '@element-plus/icons-vue'
defineProps<{ modelValue: any[] }>()
const emit = defineEmits<{ 'update:modelValue': [value: any[]] }>()
function add() { emit('update:modelValue', [...(arguments.length ? [] : []), { name: '', label: '', default: '', type: 'text' }]) }
function add() { const list = [...(null as any || [])]; let l = [...((null as any) || [])]; l.push({ name: '', label: '', default: '', type: 'text' }); emit('update:modelValue', l) }
function remove(i: number) { emit('update:modelValue', (null as any || []).filter((_: any, idx: number) => idx !== i)) }
</script>
