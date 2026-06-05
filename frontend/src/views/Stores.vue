<template>
  <div class="page-container">
    <div class="page-header">
      <n-button type="primary" @click="showModal = true">
        <template #icon>
          <n-icon><add-outline /></n-icon>
        </template>
        新增门店
      </n-button>
    </div>
    
    <n-data-table
      :columns="columns"
      :data="stores"
      :loading="loading"
      :bordered="false"
    />
    
    <n-modal v-model:show="showModal" preset="card" title="新增门店" style="width: 500px;">
      <n-form :model="form" label-width="80px">
        <n-form-item label="门店名称" required>
          <n-input v-model:value="form.name" placeholder="请输入门店名称" />
        </n-form-item>
        <n-form-item label="地址">
          <n-input v-model:value="form.address" placeholder="请输入地址" />
        </n-form-item>
        <n-form-item label="电话">
          <n-input v-model:value="form.phone" placeholder="请输入电话" />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showModal = false">取消</n-button>
          <n-button type="primary" :loading="submitting" @click="handleSubmit">保存</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
import { useMessage } from 'naive-ui'
import { AddOutline, CreateOutline, TrashOutline } from '@vicons/ionicons5'
import api from '@/utils/api'

interface Store {
  id: number
  name: string
  address: string
  phone: string
}

const message = useMessage()
const loading = ref(false)
const submitting = ref(false)
const showModal = ref(false)
const stores = ref<Store[]>([])

const form = ref({
  name: '',
  address: '',
  phone: ''
})

const columns = [
  { title: 'ID', key: 'id', width: 80 },
  { title: '门店名称', key: 'name' },
  { title: '地址', key: 'address' },
  { title: '电话', key: 'phone' },
  {
    title: '操作',
    key: 'actions',
    render: (row: Store) => {
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

async function fetchStores() {
  loading.value = true
  try {
    const response = await api.get('/stores')
    stores.value = response.data
  } catch (error) {
    message.error('获取门店列表失败')
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  if (!form.value.name) {
    message.warning('请输入门店名称')
    return
  }
  submitting.value = true
  try {
    await api.post('/stores', form.value)
    message.success('保存成功')
    showModal.value = false
    fetchStores()
    form.value = { name: '', address: '', phone: '' }
  } catch (error) {
    message.error('保存失败')
  } finally {
    submitting.value = false
  }
}

function handleEdit(row: Store) {
  form.value = { name: row.name, address: row.address, phone: row.phone }
  showModal.value = true
}

async function handleDelete(id: number) {
  try {
    await api.delete(`/stores/${id}`)
    message.success('删除成功')
    fetchStores()
  } catch (error) {
    message.error('删除失败')
  }
}

onMounted(() => {
  fetchStores()
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
