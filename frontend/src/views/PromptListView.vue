<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px">
      <h2 style="margin: 0">提示词</h2>
      <el-button type="primary" @click="router.push('/prompts/new')">新建提示词</el-button>
    </div>
    <el-card style="margin-bottom: 16px">
      <el-form :model="filters" inline>
        <el-form-item label="搜索"><el-input v-model="filters.search" placeholder="标题/描述" clearable @clear="search" @keyup.enter="search" /></el-form-item>
        <el-form-item label="收藏">
          <el-select v-model="filters.is_favorite" placeholder="全部" clearable @change="search" style="width: 120px">
            <el-option label="已收藏" :value="true" /><el-option label="未收藏" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item><el-button @click="search">搜索</el-button></el-form-item>
      </el-form>
    </el-card>
    <div v-loading="store.loading">
      <PromptCard v-for="p in store.items" :key="p.id" :prompt="p" />
      <el-empty v-if="!store.loading && store.items.length === 0" description="暂无提示词" />
    </div>
    <div style="display: flex; justify-content: center; margin-top: 16px">
      <el-pagination v-model:current-page="page" :page-size="pageSize" :total="store.total" layout="prev, pager, next" @current-change="load" />
    </div>
  </div>
</template>
<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePromptsStore } from '@/stores/prompts'
import PromptCard from '@/components/PromptCard.vue'
const router = useRouter()
const store = usePromptsStore()
const page = ref(1)
const pageSize = 20
const filters = reactive({ search: '', is_favorite: undefined as boolean | undefined })
async function load() {
  const params: Record<string, any> = { page: page.value, page_size: pageSize }
  if (filters.search) params.search = filters.search
  if (filters.is_favorite !== undefined) params.is_favorite = filters.is_favorite
  await store.fetchList(params)
}
function search() { page.value = 1; load() }
onMounted(() => load())
</script>
