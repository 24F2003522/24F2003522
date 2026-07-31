import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Register from './view/RegisterPage.vue'
import Login from './view/LoginPage.vue'
import Home from './view/HomePage.vue'
import Admin from './view/AdminDashboard.vue'
import Staff from './view/StaffDashboard.vue'
import Trekker from './view/TrekkersDashboard.vue'
import AssignStaff from './view/AssignStaff.vue'
import Bookings from './view/Bookings.vue'


const routes = [
    { path: '/', component: Home },
    { path: '/register', component: Register },
    { path: '/login', component: Login },
    { path: '/home', component: Home },
    { path: '/admin', component: Admin },
    { path: '/staff', component: Staff },
    { path: '/trekkers', component: Trekker },
    {path: '/assign-staff', component: AssignStaff},
    {path: '/bookings', component: Bookings},
   
    { path: '/:pathMatch(.*)*', redirect: '/home' },
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

const app = createApp(App)
app.use(router)
app.mount('#app')

export default router