import Vue from 'vue'
import Router from 'vue-router'
import Home from './views/Home.vue'

Vue.use(Router)

export default new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [{
    path: '/',
    name: 'home',
    component: Home,
  }, {
    path: '/drinks',
    name: 'drinks',
    component: () => import(/* webpackChunkName: "drinks" */ './views/Drinks.vue'),
  }, {
    path: '/drinkDetail/:id',
    name: 'drinkDetail',
    props: true,
    component: () => import(/* webpackChunkName: "drinkDetail" */ './views/DrinkDetail.vue'),
  }, {
    path: '/ingredients',
    name: 'ingredients',
    component: () => import(/* webpackChunkName: "ingredients" */ './views/Ingredients.vue'),
  }, {
    path: '/ingredientDetail/:id',
    name: 'ingredientDetail',
    component: () => import(/* webpackChunkName: "ingredientDetail" */ './views/IngredientDetail.vue'),
  }, {
    path: '/glasses',
    name: 'glasses',
    component: () => import(/* webpackChunkName: "glasses" */ './views/Glasses.vue'),
  }, {
    path: '/glassDetail/:id',
    name: 'glassDetail',
    component: () => import(/* webpackChunkName: "glassDetail" */ './views/GlassDetail.vue'),
  }, {
    path: '/drinkOrderDetail/:id',
    name: 'drinkOrderDetail',
    component: () => import(/* webpackChunkName: "drinkOrderDetail" */ './views/DrinkOrderDetail.vue'),
  }, {
    path: '/drinksMenu',
    name: 'drinksMenu',
    component: () => import(/* webpackChunkName: "drinksMenu" */ './views/DrinksMenu.vue'),
  }, {
    path: '/pumps',
    name: 'pumps',
    component: () => import(/* webpackChunkName: "pumps" */ './views/Pumps.vue'),
  }, {
    path: '/settings',
    name: 'settings',
    component: () => import(/* webpackChunkName: "settings" */ './views/Settings.vue'),
  }, {
    path: '/settings/wifi',
    name: 'settings/wifi',
    component: () => import(/* webpackChunkName: "settingsWifi" */ './views/settings/Wifi.vue'),
  }]
})
