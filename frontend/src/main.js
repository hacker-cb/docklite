import { createApp } from 'vue'
import PrimeVue from 'primevue/config'
import router from './router'
import App from './App.vue'

// PrimeVue components
import Button from 'primevue/button'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Toast from 'primevue/toast'
import ToastService from 'primevue/toastservice'
import ConfirmDialog from 'primevue/confirmdialog'
import ConfirmationService from 'primevue/confirmationservice'
import Tag from 'primevue/tag'
import InputNumber from 'primevue/inputnumber'
import Card from 'primevue/card'
import Chip from 'primevue/chip'
import Skeleton from 'primevue/skeleton'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'

// PrimeVue CSS
import 'primevue/resources/themes/lara-light-blue/theme.css'
import 'primevue/resources/primevue.min.css'
import 'primeicons/primeicons.css'

const app = createApp(App)

app.use(PrimeVue)
app.use(ToastService)
app.use(ConfirmationService)
app.use(router)

// Register components
app.component('Button', Button)
app.component('DataTable', DataTable)
app.component('Column', Column)
app.component('Dialog', Dialog)
app.component('InputText', InputText)
app.component('Textarea', Textarea)
app.component('Toast', Toast)
app.component('ConfirmDialog', ConfirmDialog)
app.component('Tag', Tag)
app.component('InputNumber', InputNumber)
app.component('Card', Card)
app.component('Chip', Chip)
app.component('Skeleton', Skeleton)
app.component('TabView', TabView)
app.component('TabPanel', TabPanel)

app.mount('#app')

