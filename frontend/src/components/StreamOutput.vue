<template>
  <div>
    <div v-if="status" style="margin-bottom: 8px">
      <el-tag v-if="status === 'running'" type="warning">测试中...</el-tag>
      <el-tag v-else-if="status === 'success'" type="success">完成</el-tag>
      <el-tag v-else-if="status === 'error'" type="danger">错误</el-tag>
    </div>
    <div v-if="errorMessage" style="color: #f56c6c; margin-bottom: 8px">{{ errorMessage }}</div>
    <div v-if="output" style="background: #1e1e1e; color: #d4d4d4; padding: 16px; border-radius: 4px; min-height: 100px; white-space: pre-wrap; font-family: 'Courier New', monospace; font-size: 13px">
      {{ output }}<span v-if="status === 'running'" class="cursor">▊</span>
    </div>
    <div v-if="usage && status === 'success'" style="margin-top: 8px; color: #999; font-size: 13px">
      输入 {{ usage.prompt_tokens }} tokens · 输出 {{ usage.completion_tokens }} tokens · {{ latency }}ms
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref } from 'vue'
const output = ref('')
const status = ref<'idle' | 'running' | 'success' | 'error'>('idle')
const errorMessage = ref('')
const usage = ref<{ prompt_tokens: number; completion_tokens: number } | null>(null)
const latency = ref(0)
function connect(es: EventSource) {
  disconnect(); output.value = ''; status.value = 'running'; errorMessage.value = ''; usage.value = null
  es.addEventListener('token', (e: MessageEvent) => { output.value += JSON.parse(e.data).data })
  es.addEventListener('done', (e: MessageEvent) => { const d = JSON.parse(e.data); usage.value = d.usage; latency.value = d.latency_ms; status.value = 'success'; disconnect() })
  es.addEventListener('error', (e: MessageEvent) => { errorMessage.value = JSON.parse(e.data).message; status.value = 'error'; disconnect() })
  es.onerror = () => { if (status.value === 'running') { errorMessage.value = '连接中断'; status.value = 'error' }; disconnect() }
}
function disconnect() { eventSource?.close(); eventSource = null }
let eventSource: EventSource | null = null
defineExpose({ connect, disconnect })
</script>
<style scoped>
.cursor { animation: blink 1s step-end infinite }
@keyframes blink { 50% { opacity: 0 } }
</style>
