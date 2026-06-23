<template>
  <div
    class="bg-white border border-gray-200 rounded-xl p-5 cursor-pointer transition-all duration-150 hover:border-brand-500 hover:shadow-sm group"
    @click="router.push(`/prompts/${prompt.id}`)"
  >
    <!-- Top row: title + favorite -->
    <div class="flex items-start justify-between gap-3">
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-2">
          <el-icon
            :size="16"
            :color="prompt.is_favorite ? '#F59E0B' : '#D1D5DB'"
            class="flex-shrink-0 transition-colors cursor-pointer hover:text-yellow-500"
            @click.stop="emit('toggleFav', prompt.id)"
          >
            <StarFilled v-if="prompt.is_favorite" />
            <Star v-else />
          </el-icon>
          <h3 class="text-base font-semibold text-gray-900 truncate m-0">{{ prompt.title }}</h3>
          <span
            v-if="prompt.current_version"
            class="flex-shrink-0 text-[11px] font-medium text-brand-600 bg-brand-50 px-1.5 py-0.5 rounded leading-none"
          >
            v{{ prompt.current_version }}
          </span>
        </div>
        <p v-if="prompt.description" class="text-sm text-gray-500 mt-1.5 line-clamp-2 leading-relaxed m-0">
          {{ prompt.description }}
        </p>
      </div>
    </div>

    <!-- Tags row -->
    <div v-if="prompt.tags?.length" class="flex flex-wrap gap-1.5 mt-3">
      <span
        v-for="tag in prompt.tags.slice(0, 4)"
        :key="tag.id"
        class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
        :style="{ background: (tag.color || '#3B82F6') + '15', color: tag.color || '#3B82F6' }"
      >
        {{ tag.name }}
      </span>
      <span v-if="prompt.tags.length > 4" class="text-xs text-gray-400 ml-1">+{{ prompt.tags.length - 4 }}</span>
    </div>

    <!-- Bottom row: meta -->
    <div class="flex items-center justify-between mt-3 pt-3 border-t border-gray-100">
      <div class="flex items-center gap-3 text-xs text-gray-400">
        <span v-if="prompt.rating" class="flex items-center gap-0.5">
          <StarFilled style="color: #F59E0B; width: 12px; height: 12px;" />
          {{ prompt.rating }}/5
        </span>
        <span>{{ timeAgo(prompt.updated_at) }}</span>
      </div>
      <div class="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity" @click.stop>
        <el-button size="small" text :icon="Edit" @click="router.push(`/prompts/${prompt.id}/edit`)">编辑</el-button>
        <el-button size="small" text type="primary" :icon="VideoPlay" @click="router.push(`/prompts/${prompt.id}`)">测试</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { StarFilled, Star, Edit, VideoPlay } from '@element-plus/icons-vue'

const props = defineProps<{ prompt: any }>()
const emit = defineEmits<{ toggleFav: [id: string] }>()
const router = useRouter()

function timeAgo(iso: string): string {
  if (!iso) return ''
  const diff = Date.now() - new Date(iso).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return '刚刚'
  if (mins < 60) return `${mins} 分钟前`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours} 小时前`
  const days = Math.floor(hours / 24)
  if (days < 7) return `${days} 天前`
  return new Date(iso).toLocaleDateString('zh-CN')
}
</script>
