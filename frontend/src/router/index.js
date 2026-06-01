import { createRouter, createWebHistory } from 'vue-router'
import Home from '../pages/Home.vue'
import Plan from '../pages/Plan.vue'
import Coach from '../pages/Coach.vue'
import Data from '../pages/Data.vue'
import Mine from '../pages/Mine.vue'

const routes = [
  { path: '/', redirect: '/home' },
  { path: '/home', name: 'home', component: Home, meta: { title: '驾驶舱' } },
  { path: '/plan', name: 'plan', component: Plan, meta: { title: '计划' } },
  { path: '/coach', name: 'coach', component: Coach, meta: { title: 'AI教练' } },
  { path: '/data', name: 'data', component: Data, meta: { title: '数据' } },
  { path: '/mine', name: 'mine', component: Mine, meta: { title: '我的' } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
