<template>
  <el-card shadow="hover" style="margin-bottom: 12px; cursor: pointer" @click="router.push(`/prompts/${prompt.id}`)">
    <div style="display: flex; align-items: center; justify-content: space-between">
      <div>
        <div style="font-size: 16px; font-weight: 600">
          <el-icon v-if="prompt.is_favorite" color="#E6A23C" style="margin-right: 4px"><StarFilled /></el-icon>{{ prompt.title }}
        </div>
        <div v-if="prompt.description" style="color: #999; font-size: 13px; margin-top: 4px">{{ prompt.description }}</div>
      </div>
      <div style="display: flex; gap: 4px">
        <el-tag v-for="tag in prompt.tags" :key="tag.id" :color="tag.color || '#409EFF'" style="color: #fff; border: none" size="small">{{ tag.name }}</el-tag>
      </div>
    </div>
  </el-card>
</template>
<script setup lang="ts">
import { useRouter } from 'vue-router'
defineProps<{ prompt: any }>()
const router = useRouter()
</script>
