import Vue from 'vue'
import Vuetify from 'vuetify'
import 'vuetify/dist/vuetify.min.css'
//import colors from 'vuetify/es5/util/colors'

Vue.use(Vuetify, {
  iconfont: 'mdi',
  theme:
{
  primary: "#B71C1C",
  secondary: "#757575",
  accent: "#000000",
  error: "#f44336",
  warning: "#ffeb3b",
  info: "#2196f3",
  success: "#4caf50"
}
})
