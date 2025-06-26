import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import PrimeVue from 'primevue/config';
import Aura from '@primeuix/themes/aura';
import 'primeicons/primeicons.css'
import axiosInstance from '@/utils/axios';
import ToastService from 'primevue/toastservice';
import Ripple from 'primevue/ripple';




const app = createApp(App)
app.directive('ripple', Ripple);
app.config.globalProperties.$axios = axiosInstance
app.use(ToastService);
app.use(router)
app.use(PrimeVue, {
    theme: {
        preset: Aura,
        options: {
            darkModeSelector: 'system',
            cssLayer: false,
            ripple: true
        }
    }
 });

app.mount('#app')

