<template>
  <div class="page-container">
    <div class="page-header">
      <n-button type="primary" @click="showModal = true">
        <template #icon>
          <n-icon><add-outline /></n-icon>
        </template>
        新增分类
      </n-button>
    </div>
    
    <n-data-table
      :columns="columns"
      :data="categories"
      :loading="loading"
      :bordered="false"
    />
    
    <n-modal v-model:show="showModal" preset="card" :title="editingId ? '编辑分类' : '新增分类'" style="width: 500px;">
      <n-form :model="form" label-width="80px">
        <n-form-item label="分类名称" required>
          <n-input v-model:value="form.name" placeholder="请输入分类名称" />
        </n-form-item>
        <n-form-item label="描述">
          <n-input v-model:value="form.description" type="textarea" placeholder="请输入描述" />
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
import api from '@/utils/api'

interface Category {
  id: number
  name: string
  description: string
}

const message = useMessage()
const loading = ref(false)
const submitting = ref(false)
const showModal = ref(false)
const categories = ref<Category[]>([])
const editingId = ref<number | null>(null)

const form = ref({
  name: '',
  description: ''
})

const columns = [
  { title: 'ID', key: 'id', width: 80 },
  { title: '分类名称', key: 'name' },
  { title: '描述', key: 'description' },
  {
    title: '操作',
    key: 'actions',
    render: (row: Category) => {
      return h('div', { style: 'display: flex; gap: 8px;' }, [
        h('n-button', {
          size: 'small',
          type: 'primary',
          quaternary: true,
          onClick: () => handleEdit(row)
        }, { default: () => '编辑' }),
        h('n-button', {
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
  loading.value = true
  try {
    const response = await api.get('/categories')
    categories.value = response.data
  } catch (error) {
    message.error('获取分类列表失败')
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  if (!form.value.name) {
    message.warning('请输入分类名称')
    return
  }
  submitting.value = true
  try {
    if (editingId.value) {
      await api.put(`/categories/${editingId.value}`, form.value)
    } else {
      await api.post('/categories', form.value)
    }
    message.success('保存成功')
    resetForm()
    fetchCategories()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '保存失败')
  } finally {
    submitting.value = false
  }
}

function handleEdit(row: Category) {
  editingId.value = row.id
  form.value = { name: row.name, description: row.description }
  showModal.value = true
}

function resetForm() {
  showModal.value = false
  editingId.value = null
  form.value = { name: '', description: '' }
}

async function handleDelete(id: number) {
  try {
    await api.delete(`/categories/${id}`)
    message.success('删除成功')
    fetchCategories()
  } catch (error) {
    message.error('删除失败')
  }
}

onMounted(() => {
  fetchCategories()
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
