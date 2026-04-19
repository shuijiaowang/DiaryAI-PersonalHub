import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

import { useUserStore } from '@/stores/user'

const routes: RouteRecordRaw[] = [
  { path: '/login', name: 'login', component: () => import('@/views/LoginView.vue'), meta: { public: true } },
  { path: '/register', name: 'register', component: () => import('@/views/RegisterView.vue'), meta: { public: true } },
  {
    path: '/',
    component: () => import('@/views/MainLayout.vue'),
    children: [
      { path: '', redirect: '/dashboard' },
      { path: 'dashboard', name: 'dashboard', component: () => import('@/views/DashboardView.vue') },
      { path: 'diary', name: 'diary', component: () => import('@/views/DiaryView.vue') },
      { path: 'diary/:id', name: 'diary-detail', component: () => import('@/views/DiaryDetailView.vue'), props: true },
      { path: 'modules/:code', name: 'module', component: () => import('@/views/ModuleView.vue'), props: true },
      { path: 'profile', name: 'profile', component: () => import('@/views/ProfileView.vue') },
      { path: 'chat', name: 'chat', component: () => import('@/views/ChatView.vue') },
      { path: 'settings', name: 'settings', component: () => import('@/views/SettingsView.vue') },
    ],
  },
  { path: '/:catchAll(.*)*', redirect: '/dashboard' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const userStore = useUserStore()
  if (!to.meta.public && !userStore.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.meta.public && userStore.isAuthenticated) {
    return { name: 'dashboard' }
  }
})

export default router
