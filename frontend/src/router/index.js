import { createRouter, createWebHistory } from 'vue-router'
import EditorPage from '../views/EditorPage.vue'

const routes = [
  {
    path: '/',
    name: 'Editor',
    component: EditorPage,
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes, 
})

export default router
