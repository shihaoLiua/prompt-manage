<template>
  <div class="bg-white border border-gray-200 rounded-xl p-6 flex-1 min-w-[200px]">
    <div class="flex items-start justify-between">
      <div>
        <div class="text-[32px] font-bold text-[#111827] leading-none">{{ value }}</div>
        <div class="text-sm text-gray-500 mt-1">{{ label }}</div>
      </div>
      <span
        v-if="trend"
        class="inline-flex items-center px-2 py-[2px] rounded-full text-xs font-medium bg-brand-50 text-brand-700"
      >
        ↑ {{ trend }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  value: string | number
  label: string
  trend?: string
}>()
</script>
