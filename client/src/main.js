import '@babel/polyfill'
import Vue from 'vue'
import './plugins/vuetify'
import './plugins/vue-socket.io-extended'
import App from './App.vue'
import router from './router'
import store from './store/store'

import '@mdi/font/css/materialdesignicons.css'
import 'typeface-roboto/index.css'

import './assets/custom.css'

window.App = new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')

Vue.prototype.$formatDateTimeString = function(d) {
    return new Date(Date.parse(d)).toLocaleDateString(
        undefined, {
            year: 'numeric',
            month: 'numeric',
            day: 'numeric',
            hour: 'numeric',
            minute: 'numeric',
            second: 'numeric'
        })
}
