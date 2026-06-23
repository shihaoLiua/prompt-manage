<template>
  <div>
    <!-- Page header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-xl font-semibold text-gray-900 m-0">提示词</h1>
        <p class="text-sm text-gray-500 mt-1 m-0">管理和测试你的提示词模板</p>
      </div>
      <el-button type="primary" size="large" @click="router.push('/prompts/new')">
        + 新建提示词
      </el-button>
    </div>

    <!-- Search & filters -->
    <div class="bg-white border border-gray-200 rounded-xl p-5 mb-5">
      <div class="flex flex-wrap gap-3 items-end">
        <!-- Search -->
        <div class="flex-1 min-w-[240px]">
          <label class="text-xs font-medium text-gray-500 mb-1 block">搜索</label>
          <el-input
            v-model="filters.search"
            placeholder="搜索标题或描述..."
            clearable
            @clear="search"
            @keyup.enter="search"
          >
            <template #prefix><el-icon :size="16"><Search /></el-icon></template>
          </el-input>
        </div>

        <!-- Category filter -->
        <div style="width: 160px">
          <label class="text-xs font-medium text-gray-500 mb-1 block">分类</label>
          <el-select v-model="filters.category_id" placeholder="全部分类" clearable @change="search">
            <el-option v-for="c in flatCategories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </div>

        <!-- Favorite filter -->
        <div style="width: 120px">
          <label class="text-xs font-medium text-gray-500 mb-1 block">收藏</label>
          <el-select v-model="filters.is_favorite" placeholder="全部" clearable @change="search">
            <el-option label="⭐ 已收藏" :value="true" />
            <el-option label="未收藏" :value="false" />
          </el-select>
        </div>

        <!-- Sort -->
        <div style="width: 130px">
          <label class="text-xs font-medium text-gray-500 mb-1 block">排序</label>
          <el-select v-model="sortBy" @change="search">
            <el-option label="最近更新" value="updated_at" />
            <el-option label="最近创建" value="created_at" />
            <el-option label="标题排序" value="title" />
            <el-option label="评分排序" value="rating" />
          </el-select>
        </div>

        <el-button @click="search" style="margin-bottom: 1px">搜索</el-button>
      </div>
    </div>

    <!-- Results count -->
    <div class="flex items-center justify-between mb-4">
      <span class="text-sm text-gray-500">共 <strong class="text-gray-700">{{ store.total }}</strong> 个提示词</span>
    </div>

    <!-- Grid -->
    <div v-if="!store.loading && store.items.length === 0" class="flex flex-col items-center justify-center py-20 text-gray-400">
      <svg class="w-16 h-16 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <p class="text-base font-medium text-gray-500 mb-1">暂无提示词</p>
      <p class="text-sm text-gray-400 mb-4">创建你的第一个提示词开始使用</p>
      <el-button type="primary" @click="router.push('/prompts/new')">+ 新建提示词</el-button>
    </div>

    <!-- Loading -->
    <div v-if="store.loading" class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div v-for="i in 4" :key="i" class="bg-white border border-gray-200 rounded-xl p-5 animate-pulse">
        <div class="h-5 bg-gray-100 rounded w-3/4 mb-3"></div>
        <div class="h-4 bg-gray-100 rounded w-1/2 mb-4"></div>
        <div class="flex gap-2 mb-4">
          <div class="h-5 bg-gray-100 rounded w-16"></div>
          <div class="h-5 bg-gray-100 rounded w-14"></div>
        </div>
        <div class="h-4 bg-gray-100 rounded w-1/3"></div>
      </div>
    </div>

    <!-- Cards grid -->
    <div v-else-if="store.items.length" class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <PromptCard
        v-for="p in store.items"
        :key="p.id"
        :prompt="p"
        @toggle-fav="handleToggleFav"
      />
    </div>

    <!-- Pagination -->
    <div v-if="store.total > pageSize" class="flex justify-center mt-6">
      <el-pagination
        v-model:current-page="page"
        :page-size="pageSize"
        :total="store.total"
        layout="prev, pager, next"
        @current-change="load"
        background
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePromptsStore } from '@/stores/prompts'
import { useCategoriesStore } from '@/stores/categories'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import PromptCard from '@/components/PromptCard.vue'

const router = useRouter()
const store = usePromptsStore()
const catStore = useCategoriesStore()
const page = ref(1)
const pageSize = ref(20)
const sortBy = ref('updated_at')

const filters = reactive({
  search: '',
  category_id: '' as string | undefined,
  is_favorite: undefined as boolean | undefined,
})

const flatCategories = computed(() => {
  function flatten(list: any[]): any[] {
    const result: any[] = []
    for (const item of list) {
      result.push(item)
      if (item.children?.length) result.push(...flatten(item.children))
    }
    return result
  }
  return flatten(catStore.tree)
})

async function load() {
  const params: Record<string, any> = {
    page: page.value,
    page_size: pageSize.value,
    sort_by: sortBy.value,
    sort_order: 'desc',
  }
  if (filters.search) params.search = filters.search
  if (filters.category_id) params.category_id = filters.category_id
  if (filters.is_favorite !== undefined) params.is_favorite = filters.is_favorite
  await store.fetchList(params)
}

function search() { page.value = 1; load() }

async function handleToggleFav(id: string) {
  try {
    const isFav = await store.toggleFavorite(id)
    ElMessage.success(isFav ? '已收藏' : '已取消收藏')
    load()
  } catch {
    ElMessage.error('操作失败')
  }
}

onMounted(() => {
  catStore.fetchTree()
  load()
})
</script>
