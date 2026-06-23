<template>
  <header class="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-8">
    <h1 class="text-xl font-semibold text-[#111827]">{{ title }}</h1>
    <div class="flex items-center gap-3">
      <div class="w-8 h-8 rounded-full bg-brand-500 flex items-center justify-center text-white text-sm font-bold">
        {{ initial }}
      </div>
      <span class="text-sm font-medium text-gray-700">{{ username }}</span>
    </div>
  </header>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  username: string
  initial: string
}>()
</script>
