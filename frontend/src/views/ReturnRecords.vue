<template>
  <div class="page-container">
    <div class="page-header">
      <n-form :model="queryForm" inline label-placement="left" label-width="80px">
        <n-form-item label="门店">
          <n-select
            v-model:value="queryForm.store_id"
            :options="storeOptions"
            placeholder="请选择门店"
            clearable
            style="width: 180px;"
          />
        </n-form-item>
        <n-form-item label="原料">
          <n-select
            v-model:value="queryForm.material_id"
            :options="queryMaterialOptions"
            placeholder="请选择原料"
            filterable
            clearable
            style="width: 220px;"
          />
        </n-form-item>
        <n-form-item label="批次">
          <n-input
            v-model:value="queryForm.batch_number"
            placeholder="请输入批次号"
            clearable
            style="width: 160px;"
          />
        </n-form-item>
        <n-form-item label="日期范围">
          <n-date-picker
            v-model:value="queryForm.date_range"
            type="daterange"
            clearable
          />
        </n-form-item>
        <n-form-item>
          <n-space>
            <n-button type="primary" @click="fetchRecords">
              <template #icon>
                <n-icon><search-outline /></n-icon>
              </template>
              查询
            </n-button>
            <n-button @click="resetQuery">重置</n-button>
          </n-space>
        </n-form-item>
      </n-form>
      <n-button type="primary" @click="openModal">
        <template #icon>
          <n-icon><add-outline /></n-icon>
        </template>
        新增退货
      </n-button>
    </div>

    <n-data-table
      :columns="columns"
      :data="records"
      :loading="loading"
      :bordered="false"
    />

    <n-modal v-model:show="showModal" preset="card" title="新增采购退货" style="width: 600px;">
      <n-form :model="form" label-width="110px">
        <n-form-item label="门店" required>
          <n-select
            v-model:value="form.store_id"
            :options="storeOptions"
            placeholder="请选择门店"
            @update:value="handleFormStoreChange"
          />
        </n-form-item>
        <n-form-item label="原料" required>
          <n-select
            v-model:value="form.material_id"
            :options="formMaterialOptions"
            placeholder="请先选择门店"
            filterable
            :disabled="!form.store_id"
            @update:value="handleMaterialSelect"
          />
        </n-form-item>
        <n-form-item label="批次号" required>
          <n-input
            v-model:value="form.batch_number"
            placeholder="请输入批次号"
            :disabled="!form.material_id"
          />
          <span v-if="selectedMaterial && selectedMaterial.batch_number" class="stock-tip">
            当前批次: {{ selectedMaterial.batch_number }}
          </span>
        </n-form-item>
        <n-form-item label="退货数量" required>
          <n-input-number
            v-model:value="form.quantity"
            :min="0.01"
            :max="maxQuantity"
            step="0.01"
            placeholder="请输入数量"
            :disabled="!form.material_id"
          />
          <span v-if="selectedMaterial" class="stock-tip">当前库存: {{ selectedMaterial.stock_quantity }}</span>
        </n-form-item>
        <n-form-item label="退货日期" required>
          <n-date-picker v-model:value="form.return_date" type="date" />
        </n-form-item>
        <n-form-item label="退货原因" required>
          <n-input v-model:value="form.reason" placeholder="请输入退货原因" />
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
import { ref, computed, onMounted, h } from 'vue'
import { useMessage, NButton } from 'naive-ui'
import { AddOutline, SearchOutline } from '@vicons/ionicons5'
import { format } from 'date-fns'
import api from '@/utils/api'

interface ReturnRecord {
  id: number
  material_id: number
  store_id: number
  quantity: number
  batch_number: string
  return_date: string
  reason: string
  remark: string
  material?: { name: string; code: string }
  store?: { name: string }
}

interface Material {
  id: number
  name: string
  code: string
  stock_quantity: number
  open_status: boolean
  expiry_date: string | null
  current_status: string
  store_id: number | null
  batch_number: string
}

interface Store {
  id: number
  name: string
}

const message = useMessage()
const loading = ref(false)
const submitting = ref(false)
const showModal = ref(false)
const records = ref<ReturnRecord[]>([])
const materials = ref<Material[]>([])
const stores = ref<Store[]>([])

const queryForm = ref({
  store_id: null as number | null,
  material_id: null as number | null,
  batch_number: '',
  date_range: null as [number, number] | null
})

const form = ref({
  store_id: null as number | null,
  material_id: null as number | null,
  quantity: null as number | null,
  batch_number: '',
  return_date: null as number | null,
  reason: '',
  remark: ''
})

function statusLabel(status: string): string {
  const map: Record<string, string> = {
    in_stock: '在库',
    opened: '已开封',
    expired: '已过期',
    out_of_stock: '无库存'
  }
  return map[status] || status
}

const selectedMaterial = computed<Material | null>(() => {
  if (!form.value.material_id) return null
  return materials.value.find(m => m.id === form.value.material_id) || null
})

const maxQuantity = computed(() => {
  return selectedMaterial.value?.stock_quantity || undefined
})

const storeOptions = computed(() => {
  return stores.value.map(s => ({ label: s.name, value: s.id }))
})

const queryMaterialOptions = computed(() => {
  let list = materials.value
  if (queryForm.value.store_id) {
    list = list.filter(m => m.store_id === queryForm.value.store_id || m.store_id === null)
  }
  return list.map(m => ({
    label: `${m.code} - ${m.name}`,
    value: m.id
  }))
})

const formMaterialOptions = computed(() => {
  if (!form.value.store_id) return []
  const list = materials.value.filter(m => {
    if (m.store_id !== form.value.store_id && m.store_id !== null) return false
    if (m.stock_quantity <= 0) return false
    return true
  })
  return list.map(m => ({
    label: `${m.code} - ${m.name} (库存: ${m.stock_quantity}, 状态: ${statusLabel(m.current_status)})`,
    value: m.id
  }))
})

const columns = [
  { title: 'ID', key: 'id', width: 80 },
  { title: '门店', key: 'store.name', width: 120 },
  { title: '原料', key: 'material.name' },
  { title: '批次号', key: 'batch_number', width: 140 },
  { title: '退货数量', key: 'quantity', width: 120 },
  { title: '退货日期', key: 'return_date', width: 120 },
  { title: '退货原因', key: 'reason' },
  { title: '备注', key: 'remark' },
  {
    title: '操作',
    key: 'actions',
    render: (row: ReturnRecord) => {
      return h(NButton, {
        size: 'small',
        type: 'error',
        quaternary: true,
        onClick: () => handleDelete(row.id)
      }, { default: () => '删除' })
    }
  }
]

async function fetchStores() {
  try {
    const response = await api.get('/stores')
    stores.value = response.data
  } catch (error) {
    message.error('获取门店列表失败')
  }
}

async function fetchMaterials() {
  try {
    const response = await api.get('/materials')
    materials.value = response.data
  } catch (error) {
    message.error('获取原料列表失败')
  }
}

async function fetchRecords() {
  loading.value = true
  try {
    const params: Record<string, any> = {}
    if (queryForm.value.store_id) params.store_id = queryForm.value.store_id
    if (queryForm.value.material_id) params.material_id = queryForm.value.material_id
    if (queryForm.value.batch_number) params.batch_number = queryForm.value.batch_number
    if (queryForm.value.date_range) {
      params.start_date = format(queryForm.value.date_range[0], 'yyyy-MM-dd')
      params.end_date = format(queryForm.value.date_range[1], 'yyyy-MM-dd')
    }
    const response = await api.get('/return-records', { params })
    records.value = response.data
  } catch (error) {
    message.error('获取退货记录失败')
  } finally {
    loading.value = false
  }
}

function handleFormStoreChange() {
  form.value.material_id = null
  form.value.quantity = null
  form.value.batch_number = ''
}

function handleMaterialSelect() {
  if (selectedMaterial.value) {
    form.value.batch_number = selectedMaterial.value.batch_number || ''
    if (form.value.quantity && form.value.quantity > selectedMaterial.value.stock_quantity) {
      form.value.quantity = selectedMaterial.value.stock_quantity
    }
  }
}

function openModal() {
  resetForm()
  showModal.value = true
}

function resetQuery() {
  queryForm.value = {
    store_id: null,
    material_id: null,
    batch_number: '',
    date_range: null
  }
  fetchRecords()
}

async function handleSubmit() {
  if (!form.value.store_id || !form.value.material_id || !form.value.quantity || !form.value.return_date || !form.value.reason || !form.value.batch_number) {
    message.warning('请填写必填项')
    return
  }
  submitting.value = true
  try {
    const data: Record<string, any> = { ...form.value }
    if (form.value.return_date) {
      data.return_date = format(form.value.return_date, 'yyyy-MM-dd')
    }
    await api.post('/return-records', data)
    message.success('保存成功')
    resetForm()
    fetchRecords()
    fetchMaterials()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '保存失败')
  } finally {
    submitting.value = false
  }
}

function resetForm() {
  showModal.value = false
  form.value = {
    store_id: null,
    material_id: null,
    quantity: null,
    batch_number: '',
    return_date: null,
    reason: '',
    remark: ''
  }
}

async function handleDelete(id: number) {
  try {
    await api.delete(`/return-records/${id}`)
    message.success('删除成功')
    fetchRecords()
    fetchMaterials()
  } catch (error) {
    message.error('删除失败')
  }
}

onMounted(() => {
  fetchStores()
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
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  flex-wrap: wrap;
}

.stock-tip {
  margin-left: 8px;
  font-size: 12px;
  color: #999;
}
</style>
