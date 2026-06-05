<template>
  <div class="page-container">
    <div class="page-header">
      <n-space>
        <n-input
          v-model:value="searchForm.keyword"
          placeholder="搜索原料编号/名称"
          clearable
          style="width: 200px;"
          @keyup.enter="fetchMaterials"
        />
        <n-select
          v-model:value="searchForm.category_id"
          placeholder="选择分类"
          clearable
          :options="categoryOptions"
          style="width: 150px;"
        />
        <n-select
          v-model:value="searchForm.status"
          placeholder="选择状态"
          clearable
          :options="statusOptions"
          style="width: 150px;"
        />
        <n-button type="primary" @click="fetchMaterials">
          <template #icon>
            <n-icon><search-outline /></n-icon>
          </template>
          搜索
        </n-button>
        <n-button type="primary" @click="showModal = true">
          <template #icon>
            <n-icon><add-outline /></n-icon>
          </template>
          新增原料
        </n-button>
      </n-space>
    </div>
    
    <n-data-table
      :columns="columns"
      :data="materials"
      :loading="loading"
      :bordered="false"
    />
    
    <n-modal v-model:show="showModal" preset="card" :title="editingId ? '编辑原料' : '新增原料'" style="width: 600px;">
      <n-form :model="form" label-width="100px">
        <n-form-item label="原料编号" required>
          <n-input v-model:value="form.code" placeholder="请输入原料编号" :disabled="!!editingId" />
        </n-form-item>
        <n-form-item label="原料名称" required>
          <n-input v-model:value="form.name" placeholder="请输入原料名称" />
        </n-form-item>
        <n-form-item label="规格">
          <n-input v-model:value="form.specification" placeholder="请输入规格" />
        </n-form-item>
        <n-form-item label="分类">
          <n-select v-model:value="form.category_id" :options="categoryOptions" placeholder="请选择分类" />
        </n-form-item>
        <n-form-item label="保质期(天)">
          <n-input-number v-model:value="form.shelf_life_days" :min="1" placeholder="请输入保质期" />
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
import { useMessage, NTag, NButton } from 'naive-ui'
import { AddOutline, SearchOutline } from '@vicons/ionicons5'
import api from '@/utils/api'

interface Material {
  id: number
  code: string
  name: string
  specification: string
  category_id: number
  stock_quantity: number
  open_status: boolean
  open_date: string
  expiry_date: string
  current_status: string
  shelf_life_days: number
  category?: { name: string }
}

interface Category {
  id: number
  name: string
}

const message = useMessage()
const loading = ref(false)
const submitting = ref(false)
const showModal = ref(false)
const materials = ref<Material[]>([])
const categories = ref<Category[]>([])
const editingId = ref<number | null>(null)

const searchForm = ref({
  keyword: '',
  category_id: null as number | null,
  status: null as string | null
})

const form = ref({
  code: '',
  name: '',
  specification: '',
  category_id: null as number | null,
  shelf_life_days: 7
})

const statusOptions = [
  { label: '在库', value: 'in_stock' },
  { label: '已开封', value: 'opened' },
  { label: '已过期', value: 'expired' },
  { label: '缺货', value: 'out_of_stock' }
]

const statusMap: Record<string, { label: string; type: string }> = {
  in_stock: { label: '在库', type: 'success' },
  opened: { label: '已开封', type: 'warning' },
  expired: { label: '已过期', type: 'error' },
  out_of_stock: { label: '缺货', type: 'default' }
}

const categoryOptions = ref<{ label: string; value: number }[]>([])

const columns = [
  { title: 'ID', key: 'id', width: 80 },
  { title: '原料编号', key: 'code', width: 120 },
  { title: '原料名称', key: 'name' },
  { title: '规格', key: 'specification' },
  { title: '分类', key: 'category.name' },
  { title: '库存数量', key: 'stock_quantity', width: 100 },
  {
    title: '状态',
    key: 'current_status',
    width: 100,
    render: (row: Material) => {
      const status = statusMap[row.current_status] || { label: row.current_status, type: 'default' }
        return h(NTag, { type: status.type as any }, { default: () => status.label })
    }
  },
  { title: '开封日期', key: 'open_date', width: 120 },
  { title: '失效日期', key: 'expiry_date', width: 120 },
  {
    title: '操作',
    key: 'actions',
    render: (row: Material) => {
        return h('div', { style: 'display: flex; gap: 8px;' }, [
          h(NButton, {
            size: 'small',
            type: 'primary',
            quaternary: true,
            onClick: () => handleEdit(row)
          }, { default: () => '编辑' }),
          h(NButton, {
            size: 'small',
            type: 'error',
            quaternary: true,
            onClick: () => handleDelete(row.id)
          }, { default: () => '删除' })
        ])
    }
  }
]

async function fetchCategories() {
  try {
    const response = await api.get('/categories')
    categories.value = response.data
    categoryOptions.value = response.data.map((c: Category) => ({
      label: c.name,
      value: c.id
    }))
  } catch (error) {
    message.error('获取分类失败')
  }
}

async function fetchMaterials() {
  loading.value = true
  try {
    const params: Record<string, any> = {}
    if (searchForm.value.keyword) params.keyword = searchForm.value.keyword
    if (searchForm.value.category_id) params.category_id = searchForm.value.category_id
    if (searchForm.value.status) params.status = searchForm.value.status
    
    const response = await api.get('/materials', { params })
    materials.value = response.data
  } catch (error) {
    message.error('获取原料列表失败')
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  if (!form.value.code || !form.value.name) {
    message.warning('请填写必填项')
    return
  }
  submitting.value = true
  try {
    if (editingId.value) {
      await api.put(`/materials/${editingId.value}`, form.value)
    } else {
      await api.post('/materials', form.value)
    }
    message.success('保存成功')
    resetForm()
    fetchMaterials()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '保存失败')
  } finally {
    submitting.value = false
  }
}

function handleEdit(row: Material) {
  editingId.value = row.id
  form.value = {
    code: row.code,
    name: row.name,
    specification: row.specification,
    category_id: row.category_id,
    shelf_life_days: row.shelf_life_days || 7
  }
  showModal.value = true
}

function resetForm() {
  showModal.value = false
  editingId.value = null
  form.value = {
    code: '',
    name: '',
    specification: '',
    category_id: null,
    shelf_life_days: 7
  }
}

async function handleDelete(id: number) {
  try {
    await api.delete(`/materials/${id}`)
    message.success('删除成功')
    fetchMaterials()
  } catch (error) {
    message.error('删除失败')
  }
}

onMounted(() => {
  fetchCategories()
  fetchMaterials()
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
