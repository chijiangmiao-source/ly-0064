<template>
  <n-layout has-sider>
    <n-layout-sider
      :collapsed-width="64"
      :width="240"
      :collapsed="collapsed"
      show-trigger
      @collapse="collapsed = true"
      @expand="collapsed = false"
    >
      <div class="logo">
        <n-icon size="28" :depth="3">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 8h1a4 4 0 0 1 0 8h-1"/>
            <path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"/>
            <line x1="6" y1="1" x2="6" y2="4"/>
            <line x1="10" y1="1" x2="10" y2="4"/>
            <line x1="14" y1="1" x2="14" y2="4"/>
          </svg>
        </n-icon>
        <span v-if="!collapsed" class="logo-text">原料管理系统</span>
      </div>
      <n-menu
        :collapsed="collapsed"
        :collapsed-width="64"
        :collapsed-icon-size="22"
        :options="menuOptions"
        :value="activeMenu"
        @update:value="handleMenuClick"
      />
    </n-layout-sider>
    <n-layout>
      <n-layout-header>
        <div class="header">
          <div class="header-left">
            <n-text strong>{{ pageTitle }}</n-text>
          </div>
          <div class="header-right">
            <n-dropdown :options="userOptions" @select="handleUserAction">
              <n-button quaternary>
                <template #icon>
                  <n-icon><person-outline /></n-icon>
                </template>
                {{ authStore.user?.full_name || authStore.user?.username }}
              </n-button>
            </n-dropdown>
          </div>
        </div>
      </n-layout-header>
      <n-layout-content content-style="padding: 24px;">
        <router-view />
      </n-layout-content>
    </n-layout>
  </n-layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { NIcon } from 'naive-ui'
import {
  BarChartOutline,
  StorefrontOutline,
  ListOutline,
  CubeOutline,
  AddCircleOutline,
  OpenOutline,
  TrashOutline,
  ArrowRedoOutline,
  SwapHorizontalOutline,
  PersonOutline,
  LogOutOutline
} from '@vicons/ionicons5'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const collapsed = ref(false)
const activeMenu = ref('dashboard')

const menuOptions = [
  {
    label: '数据看板',
    key: 'dashboard',
    icon: () => h(NIcon, null, { default: () => h(BarChartOutline) })
  },
  {
    label: '门店管理',
    key: 'stores',
    icon: () => h(NIcon, null, { default: () => h(StorefrontOutline) })
  },
  {
    label: '原料分类',
    key: 'categories',
    icon: () => h(NIcon, null, { default: () => h(ListOutline) })
  },
  {
    label: '原料档案',
    key: 'materials',
    icon: () => h(NIcon, null, { default: () => h(CubeOutline) })
  },
  {
    label: '入库登记',
    key: 'stock-ins',
    icon: () => h(NIcon, null, { default: () => h(AddCircleOutline) })
  },
  {
    label: '开封登记',
    key: 'open-records',
    icon: () => h(NIcon, null, { default: () => h(OpenOutline) })
  },
  {
    label: '报损登记',
    key: 'damage-records',
    icon: () => h(NIcon, null, { default: () => h(TrashOutline) })
  },
  {
    label: '领用登记',
    key: 'usage-records',
    icon: () => h(NIcon, null, { default: () => h(ArrowRedoOutline) })
  },
  {
    label: '原料调拨',
    key: 'transfer-records',
    icon: () => h(NIcon, null, { default: () => h(SwapHorizontalOutline) })
  }
]

const userOptions = [
  {
    label: '退出登录',
    key: 'logout',
    icon: () => h(NIcon, null, { default: () => h(LogOutOutline) })
  }
]

const pageTitle = computed(() => {
  const menu = menuOptions.find(m => m.key === activeMenu.value)
  return menu?.label || ''
})

function handleMenuClick(key: string) {
  activeMenu.value = key
  router.push(`/${key}`)
}

function handleUserAction(key: string) {
  if (key === 'logout') {
    authStore.logout()
    router.push('/login')
  }
}

onMounted(() => {
  const path = route.path.replace('/', '')
  if (path && menuOptions.find(m => m.key === path)) {
    activeMenu.value = path
  }
  if (authStore.token && !authStore.user) {
    authStore.fetchUser()
  }
})
</script>

<style scoped>
.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 16px;
}

.logo-text {
  margin-left: 12px;
  font-size: 16px;
  font-weight: bold;
}

.header {
  height: 64px;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}
</style>
