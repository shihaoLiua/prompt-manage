<template>
  <div v-loading="loading">
    <el-page-header :content="isNew ? '新建提示词' : '编辑提示词'" @back="router.push('/prompts')" />
    <el-card style="margin-top: 20px; max-width: 800px">
      <PromptForm v-if="!loading" :prompt="store.current" :submit-text="isNew ? '创建' : '保存'" @save="handleSave" @cancel="router.push('/prompts')" />
    </el-card>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePromptsStore } from '@/stores/prompts'
import { ElMessage } from 'element-plus'
import PromptForm from '@/components/PromptForm.vue'
const route = useRoute()
const router = useRouter()
const store = usePromptsStore()
const loading = ref(!!route.params.id)
const isNew = computed(() => route.name === 'PromptNew')
async function handleSave(data: any) {
  try {
    if (isNew.value) { await store.create(data); ElMessage.success('创建成功') }
    else { await store.update(route.params.id as string, data); ElMessage.success('保存成功') }
    router.push('/prompts')
  } catch (e: any) { ElMessage.error(e.response?.data?.detail || '操作失败') }
}
onMounted(async () => { if (route.params.id) { await store.fetchOne(route.params.id as string); loading.value = false } })
</script>
