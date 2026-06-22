<template>
  <el-form :model="form" label-width="80px">
    <el-form-item label="标题" required><el-input v-model="form.title" /></el-form-item>
    <el-form-item label="描述"><el-input v-model="form.description" type="textarea" :rows="2" /></el-form-item>
    <el-form-item label="内容" required><el-input v-model="form.content" type="textarea" :rows="12" placeholder="使用 {{variable}} 语法" /></el-form-item>
    <el-form-item label="变量"><VariableForm v-model="form.variables" /></el-form-item>
    <el-form-item>
      <el-button type="primary" @click="$emit('save', form)">{{ submitText || '保存' }}</el-button>
      <el-button @click="$emit('cancel')">取消</el-button>
    </el-form-item>
  </el-form>
</template>
<script setup lang="ts">
import { reactive, watch } from 'vue'
import VariableForm from './VariableForm.vue'
const props = defineProps<{ prompt?: any; submitText?: string }>()
const emit = defineEmits<{ save: [data: any]; cancel: [] }>()
const form = reactive({ title: '', description: '', content: '', variables: [] as any[] })
watch(() => props.prompt, (p) => { if (p) { form.title = p.title; form.description = p.description || ''; form.content = p.content; form.variables = p.variables || [] } }, { immediate: true })
</script>
