<template>
  <div>
    <h2>个人设置</h2>
    <el-card style="margin-top: 16px">
      <template #header>我的 API 配置</template>
      <el-button size="small" type="primary" style="margin-bottom: 12px" @click="showDialog = true; isEdit = false">新建配置</el-button>
      <el-table :data="configStore.items" v-loading="configStore.loading" stripe style="width: 100%">
        <el-table-column prop="name" label="名称" min-width="120" />
        <el-table-column prop="api_base" label="API 地址" min-width="200" />
        <el-table-column prop="default_model" label="默认模型" width="140" />
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button size="small" @click="edit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="remove(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    <el-dialog v-model="showDialog" :title="isEdit ? '编辑配置' : '新建配置'" width="500px">
      <el-form :model="dialogForm" label-width="100px">
        <el-form-item label="名称"><el-input v-model="dialogForm.name" /></el-form-item>
        <el-form-item label="API 地址"><el-input v-model="dialogForm.api_base" placeholder="https://api.openai.com/v1" /></el-form-item>
        <el-form-item label="API Key"><el-input v-model="dialogForm.api_key" type="password" show-password /></el-form-item>
        <el-form-item label="默认模型"><el-input v-model="dialogForm.default_model" placeholder="gpt-4o" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="saveConfig">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { useApiConfigsStore } from '@/stores/apiConfigs'
import { ElMessage, ElMessageBox } from 'element-plus'
const configStore = useApiConfigsStore()
const showDialog = ref(false)
const isEdit = ref(false)
const editId = ref<string | null>(null)
const dialogForm = reactive({ name: '', api_base: '', api_key: '', default_model: '' })
function edit(item: any) { isEdit.value = true; editId.value = item.id; dialogForm.name = item.name; dialogForm.api_base = item.api_base; dialogForm.api_key = ''; dialogForm.default_model = item.default_model; showDialog.value = true }
async function saveConfig() {
  try {
    if (isEdit.value && editId.value) { await configStore.update(editId.value, dialogForm); ElMessage.success('已更新') }
    else { await configStore.create(dialogForm); ElMessage.success('已创建') }
    showDialog.value = false
  } catch (e: any) { ElMessage.error(e.response?.data?.detail || '保存失败') }
}
async function remove(id: string) { await ElMessageBox.confirm('确认删除？', '警告'); await configStore.remove(id); ElMessage.success('已删除') }
onMounted(() => configStore.fetchMine())
</script>
