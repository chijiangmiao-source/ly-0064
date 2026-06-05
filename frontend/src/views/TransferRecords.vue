<template>
  <div class="page-container">
    <div class="page-header">
      <n-form :model="queryForm" inline label-placement="left" label-width="80px">
        <n-form-item label="调出门店">
          <n-select
            v-model:value="queryForm.from_store_id"
            :options="storeOptions"
            placeholder="请选择调出门店"
            clearable
            style="width: 180px;"
          />
        </n-form-item>
        <n-form-item label="调入门店">
          <n-select
            v-model:value="queryForm.to_store_id"
            :options="storeOptions"
            placeholder="请选择调入门店"
            clearable
            style="width: 180px;"
          />
        </n-form-item>
        <n-form-item label="原料">
          <n-select
            v-model:value="queryForm.material_id"
            :options="allMaterialOptions"
            placeholder="请选择原料"
            filterable
            clearable
            style="width: 220px;"
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
        新增调拨
      </n-button>
    </div>

    <n-data-table
      :columns="columns"
      :data="records"
      :loading="loading"
      :bordered="false"
    />

    <n-modal v-model:show="showModal" preset="card" title="新增调拨" style="width: 640px;">
      <n-form :model="form" label-width="100px">
        <n-form-item label="调出门店" required>
          <n-select
            v-model:value="form.from_store_id"
            :options="storeOptions"
            placeholder="请选择调出门店"
            @update:value="handleFromStoreChange"
          />
        </n-form-item>
        <n-form-item label="调入门店" required>
          <n-select
            v-model:value="form.to_store_id"
            :options="toStoreOptions"
            placeholder="请选择调入门店"
            :disabled="!form.from_store_id"
          />
        </n-form-item>
        <n-form-item label="原料" required>
          <n-select
            v-model:value="form.material_id"
            :options="formMaterialOptions"
            placeholder="请先选择调出门店"
            filterable
            :disabled="!form.from_store_id"
            @update:value="handleMaterialSelect"
          />
        </n-form-item>
        <n-form-item label="调拨数量" required>
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
        <n-form-item label="调拨日期" required>
          <n-date-picker v-model:value="form.transfer_date" type="date" />
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

interface TransferRecord {
  id: number
  material_id: number
  from_store_id: number
  to_store_id: number
  quantity: number
  transfer_date: string
  batch_number: string
  remark: string
  material?: { name: string; code: string; batch_number: string }
  from_store?: { name: string }
  to_store?: { name: string }
}

interface Material {
  id: number
  name: string
  code: string
  stock_quantity: number
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
const records = ref<TransferRecord[]>([])
const materials = ref<Material[]>([])
const stores = ref<Store[]>([])

const queryForm = ref({
  from_store_id: null as number | null,
  to_store_id: null as number | null,
  material_id: null as number | null,
  date_range: null as [number, number] | null
})

const form = ref({
  from_store_id: null as number | null,
  to_store_id: null as number | null,
  material_id: null as number | null,
  quantity: null as number | null,
  transfer_date: null as number | null,
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

const toStoreOptions = computed(() => {
  if (!form.value.from_store_id) return storeOptions.value
  return stores.value
    .filter(s => s.id !== form.value.from_store_id)
    .map(s => ({ label: s.name, value: s.id }))
})

const allMaterialOptions = computed(() => {
  return materials.value.map(m => ({
    label: `${m.code} - ${m.name}`,
    value: m.id
  }))
})

const formMaterialOptions = computed(() => {
  if (!form.value.from_store_id) return []
  const list = materials.value.filter(m => {
    if (m.store_id !== form.value.from_store_id) return false
    if (m.stock_quantity <= 0) return false
    if (m.current_status === 'expired') return false
    return true
  })
  return list.map(m => {
    const batch = m.batch_number ? ` [批次: ${m.batch_number}]` : ''
    return {
      label: `${m.code} - ${m.name}${batch} (库存: ${m.stock_quantity}, 状态: ${statusLabel(m.current_status)})`,
      value: m.id
    }
  })
})

const columns = [
  { title: 'ID', key: 'id', width: 80 },
  { title: '调出门店', key: 'from_store.name', width: 120 },
  { title: '调入门店', key: 'to_store.name', width: 120 },
  { title: '原料', key: 'material.name' },
  { title: '批次号', key: 'batch_number', width: 140 },
  { title: '调拨数量', key: 'quantity', width: 120 },
  { title: '调拨日期', key: 'transfer_date', width: 120 },
  { title: '备注', key: 'remark' },
  {
    title: '操作',
    key: 'actions',
    width: 100,
    render: (row: TransferRecord) => {
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
    if (queryForm.value.from_store_id) params.from_store_id = queryForm.value.from_store_id
    if (queryForm.value.to_store_id) params.to_store_id = queryForm.value.to_store_id
    if (queryForm.value.material_id) params.material_id = queryForm.value.material_id
    if (queryForm.value.date_range) {
      params.start_date = format(queryForm.value.date_range[0], 'yyyy-MM-dd')
      params.end_date = format(queryForm.value.date_range[1], 'yyyy-MM-dd')
    }
    const response = await api.get('/transfer-records', { params })
    records.value = response.data
  } catch (error) {
    message.error('获取调拨记录失败')
  } finally {
    loading.value = false
  }
}

function handleFromStoreChange() {
  form.value.to_store_id = null
  form.value.material_id = null
  form.value.quantity = null
}

function openModal() {
  resetForm()
  showModal.value = true
}

function resetQuery() {
  queryForm.value = {
    from_store_id: null,
    to_store_id: null,
    material_id: null,
    date_range: null
  }
  fetchRecords()
}

function handleMaterialSelect() {
  if (form.value.quantity && selectedMaterial.value && form.value.quantity > selectedMaterial.value.stock_quantity) {
    form.value.quantity = selectedMaterial.value.stock_quantity
  }
}

async function handleSubmit() {
  if (!form.value.from_store_id || !form.value.to_store_id || !form.value.material_id || !form.value.quantity || !form.value.transfer_date) {
    message.warning('请填写必填项')
    return
  }
  if (form.value.from_store_id === form.value.to_store_id) {
    message.warning('调出门店和调入门店不能相同')
    return
  }
  submitting.value = true
  try {
    const data: Record<string, any> = { ...form.value }
    if (form.value.transfer_date) {
      data.transfer_date = format(form.value.transfer_date, 'yyyy-MM-dd')
    }
    await api.post('/transfer-records', data)
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
    from_store_id: null,
    to_store_id: null,
    material_id: null,
    quantity: null,
    transfer_date: null,
    remark: ''
  }
}

async function handleDelete(id: number) {
  try {
    await api.delete(`/transfer-records/${id}`)
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
