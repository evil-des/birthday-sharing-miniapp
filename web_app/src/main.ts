import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ApiService from '@/services/api'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.provide('apiService', new ApiService(import.meta.env.VITE_API_URL))

app.mount('#app')
