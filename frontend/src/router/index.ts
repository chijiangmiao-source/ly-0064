import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/dashboard'
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue')
      },
      {
        path: 'stores',
        name: 'Stores',
        component: () => import('@/views/Stores.vue')
      },
      {
        path: 'categories',
        name: 'Categories',
        component: () => import('@/views/Categories.vue')
      },
      {
        path: 'materials',
        name: 'Materials',
        component: () => import('@/views/Materials.vue')
      },
      {
        path: 'stock-ins',
        name: 'StockIns',
        component: () => import('@/views/StockIns.vue')
      },
      {
        path: 'open-records',
        name: 'OpenRecords',
        component: () => import('@/views/OpenRecords.vue')
      },
      {
        path: 'damage-records',
        name: 'DamageRecords',
        component: () => import('@/views/DamageRecords.vue')
      },
      {
        path: 'usage-records',
        name: 'UsageRecords',
        component: () => import('@/views/UsageRecords.vue')
      },
      {
        path: 'transfer-records',
        name: 'TransferRecords',
        component: () => import('@/views/TransferRecords.vue')
      },
      {
        path: 'return-records',
        name: 'ReturnRecords',
        component: () => import('@/views/ReturnRecords.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth !== false)
  
  if (requiresAuth && !authStore.token) {
    next('/login')
  } else if (to.path === '/login' && authStore.token) {
    next('/')
  } else {
    next()
  }
})

export default router
