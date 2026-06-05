<template>
  <div class="page-container">
    <div class="page-header">
      <n-button type="primary" @click="showModal = true">
        <template #icon>
          <n-icon><add-outline /></n-icon>
        </template>
        新增开封
      </n-button>
    </div>
    
    <n-data-table
      :columns="columns"
      :data="records"
      :loading="loading"
      :bordered="false"
    />
    
    <n-modal v-model:show="showModal" preset="card" title="新增开封" style="width: 500px;">
      <n-form :model="form" label-width="100px">
        <n-form-item label="原料" required>
          <n-select
            v-model:value="form.material_id"
            :options="materialOptions"
            placeholder="请选择原料"
            filterable
          />
        </n-form-item>
        <n-form-item label="开封日期" required>
          <n-date-picker v-model:value="form.open_date" type="date" />
        </n-form-item>
        <n-form-item label="失效日期" required>
          <n-date-picker v-model:value="form.expiry_date" type="date" />
        </n-form-item>
        <n-form-item label="备注">
          <n-input v-model:value="form.remark" type="textarea" placeholder="请输入备注" />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="resetForm">取消</n-button>
          <n-button type="primary" :loading="submitting" @click="handleSubmit">保存</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
import { useMessage } from 'naive-ui'
import { AddOutline } from '@vicons/ionicons5'
import { format } from 'date-fns'
import api from '@/utils/api'

interface OpenRecord {
  id: number
  material_id: number
  open_date: string
  expiry_date: string
  remark: string
  material?: { name: string; code: string }
}

interface Material {
  id: number
  name: string
  code: string
  stock_quantity: number
}

const message = useMessage()
const loading = ref(false)
const submitting = ref(false)
const showModal = ref(false)
const records = ref<OpenRecord[]>([])
const materials = ref<Material[]>([])

const form = ref({
  material_id: null as number | null,
  open_date: null as number | null,
  expiry_date: null as number | null,
  remark: ''
})

const materialOptions = ref<{ label: string; value: number }[]>([])

const columns = [
  { title: 'ID', key: 'id', width: 80 },
  { title: '原料', key: 'material.name' },
  { title: '开封日期', key: 'open_date', width: 120 },
  { title: '失效日期', key: 'expiry_date', width: 120 },
  { title: '备注', key: 'remark' },
  {
    title: '操作',
    key: 'actions',
    render: (row: OpenRecord) => {
      return h('n-button', {
        size: 'small',
        type: 'error',
        quaternary: true,
        onClick: () => handleDelete(row.id)
      }, { default: () => '删除' })
    }
  }
]

async function fetchMaterials() {
  try {
    const response = await api.get('/materials')
    materials.value = response.data.filter((m: Material) => m.stock_quantity > 0)
    materialOptions.value = materials.value.map((m: Material) => ({
      label: `${m.code} - ${m.name}`,
      value: m.id
    }))
  } catch (error) {
    message.error('获取原料列表失败')
  }
}

async function fetchRecords() {
  loading.value = true
  try {
    const response = await api.get('/open-records')
    records.value = response.data
  } catch (error) {
    message.error('获取开封记录失败')
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  if (!form.value.material_id || !form.value.open_date || !form.value.expiry_date) {
    message.warning('请填写必填项')
    return
  }
  submitting.value = true
  try {
    const data = {
      ...form.value,
      open_date: format(form.value.open_date!, 'yyyy-MM-dd'),
      expiry_date: format(form.value.expiry_date!, 'yyyy-MM-dd')
    }
    await api.post('/open-records', data)
    message.success('保存成功')
    resetForm()
    fetchRecords()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '保存失败')
  } finally {
    submitting.value = false
  }
}

function resetForm() {
  showModal.value = false
  form.value = {
    material_id: null,
    open_date: null,
    expiry_date: null,
    remark: ''
  }
}

async function handleDelete(id: number) {
  try {
    await api.delete(`/open-records/${id}`)
    message.success('删除成功')
    fetchRecords()
  } catch (error) {
    message.error('删除失败')
  }
}

onMounted(() => {
  fetchMaterials()
  fetchRecords()
})
</script>

<style scoped>
.page-container {
  padding: 24px;
  background: #fff;
  border-radius: 8px;
}

.page-header {
  margin-bottom: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
