<template>

  <v-card flat>
    
    <loading v-if="loading"></loading>
    
    <template v-else>
    
      <h1 class="pa-3">{{item.name}}</h1>
      
      <p
        v-if="item.isAlcoholic"
        class="px-3 subheading">Alcoholic</p>
      <p
        v-else
        class="px-3 subheading">Non-alcoholic</p>

      <p
        v-if="item.isFavorite"
        class="px-3 subheading">This drink is a favorite</p>

      <p
        v-if="item.isOnMenu"
        class="px-3 subheading">This drink is on the menu</p>

      <p class="px-3 subheading">Times dispensed: {{timesDispensed}}</p>
        
      <p class="px-3 subheading">Glass: {{glassName}}</p>
        
      <h2 class="px-3">Ingredients</h2>

      <v-list>

        <v-list-tile
          v-for="di in sortedIngredients"
          :key="di.ingredient.id"
          ripple
          avatar
          @click="gotoIngredientDetail(di.ingredientId)"
        >
          <v-list-tile-avatar>
            <v-icon v-if="di.ingredient.isAlcoholic">mdi-flash</v-icon>
            <v-icon v-else>mdi-baby-buggy</v-icon>
            <v-icon v-if="di.ingredient.isAvailable">mdi-gas-station</v-icon>
          </v-list-tile-avatar>

          <v-list-tile-content>
            <v-list-tile-title>{{di.ingredient.amount}} {{di.ingredient.units}} {{di.ingredient.name}}</v-list-tile-title>
          </v-list-tile-content>
          
        </v-list-tile>
        
      </v-list>

      <template v-if="item.isOnMenu">
      
        <order-drink ref="orderDrink"></order-drink>

        <v-btn
          fab
          fixed
          bottom right
          color="primary"
          @click="orderDrink"
        >
          <v-icon dark>mdi-plus</v-icon>
        </v-btn>
        
      </template>
      
    </template>
    
  </v-card>
        
</template>

<script>

import { mapState } from 'vuex'
import Loading from '../components/Loading'
import OrderDrink from '../components/OrderDrink'

export default {
  name: 'DrinkDetail',
  props: {
    id: {},
    locationHistory: {
      default: false
    }
  }, 
  data() {
    return {
    }
  },
  
  components: {
    Loading,
    OrderDrink,
  },
  
  created() {
    this.$emit('show-page', 'Drinks')
  },
  
  computed: {
    timesDispensed() {
      return this.item.timesDispensed || 0
    },
    glassName() {
      return this.item.glass ? this.item.glass.name : ''
    },
    hasIngredients() {
      return this.item.ingredients && this.item.ingredients.length > 0
    },
    sortedIngredients() {
      if (! this.hasIngredients) return []
      return this.item.ingredients.slice().sort((a, b) => {
        if (a.ingredient.step < b.ingredient.step) return -1
        if (a.ingredient.step > b.ingredient.step) return 1
        return a.ingredient.name.localeCompare(b.ingredient.name, 'en', {'sensitivity': 'base'})
      })
    },
    ...mapState({
      loading: state => state.drinks.loading,
      item: state => state.drinks.item,
    })
  },
  
  methods: {
    
    gotoIngredientDetail(id) {
      this.$router.push({name: 'ingredientDetail', params: {id: id}})
    },
    
    orderDrink() {
      this.$refs.orderDrink.open(this.item).then(() => {
        if (this.locationHistory)
          this.$router.go(-2)
      })
    },
    
  },
  
  beforeRouteEnter(to, from, next) {
    next(t => {
      t.$store.dispatch('drinks/loadById', t.id)
    });
  },
  
  beforeRouteLeave(to, from, next) {
    this.$store.commit('drinks/destroy')
    next()
  },
  
  sockets: {
    drinkDeleted(item) {
      if (this.item.id && (item.id === this.item.id)) {
        window.history.length > 1 ? this.$router.go(-1) : this.$router.push('/')
      }
    }
  },  
  
}

</script>
