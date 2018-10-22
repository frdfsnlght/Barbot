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
        v-if="item.isAvailable"
        class="px-3 subheading">This ingredient is currently available.</p>

      <p class="px-3 subheading">Amount dispensed: {{amountDispensedML}} ml / {{amountDispensedOZ}} oz</p>
      <p class="px-3 subheading">Times dispensed: {{timesDispensed}}</p>
        
      <h2 class="px-3">Drinks</h2>

      <p
        v-if="!hasDrinks"
        class="pa-3 subheading"
      >No ingredients use this glass.</p>
      
      <v-list v-else>

        <v-list-tile
          v-for="di in sortedDrinks"
          :key="di.drink.id"
          ripple
          avatar
          @click="gotoDrinkDetail(di.drinkId)"
        >
          <v-list-tile-avatar>
            <v-icon v-if="di.drink.isFavorite">mdi-heart</v-icon>
            <v-icon v-if="di.drink.isAlcoholic">mdi-flash</v-icon>
            <v-icon v-else>mdi-baby-buggy</v-icon>
          </v-list-tile-avatar>

          <v-list-tile-content>
            <v-list-tile-title>{{di.drink.name}}</v-list-tile-title>
          </v-list-tile-content>
          
        </v-list-tile>
        
      </v-list>

    </template>
    
  </v-card>
        
</template>

<script>

import { mapState } from 'vuex'
import Loading from '../components/Loading'

export default {
  name: 'IngredientDetail',
  data() {
    return {
    }
  },
  
  components: {
    Loading,
  },
  
  created() {
    this.$emit('show-page', 'Ingredients')
  },
  
  computed: {
    amountDispensedML() {
      let a = this.item.amountDispensed || 0
      return a.toFixed(0)
    },
    amountDispensedOZ() {
      let a = this.item.amountDispensed || 0
      return (a * 0.033814).toFixed(2)
    },
    timesDispensed() {
      return this.item.timesDispensed || 0
    },
    hasDrinks() {
      return this.item.drinks && this.item.drinks.length > 0
    },
    sortedDrinks() {
      if (! this.hasDrinks) return []
      return this.item.drinks.slice().sort((a, b) => {
        return a.drink.name.localeCompare(b.drink.name, 'en', {'sensitivity': 'base'})
      })
    },
    ...mapState({
      loading: state => state.ingredients.loading,
      item: state => state.ingredients.item,
    })
  },
  
  methods: {
    
    gotoDrinkDetail(id) {
      this.$router.push({name: 'drinkDetail', params: {id: id}})
    },
    
  },
  
  beforeRouteEnter(to, from, next) {
    next(t => {
      t.$store.dispatch('ingredients/loadById', t.$route.params.id)
    });
  },
  
  beforeRouteLeave(to, from, next) {
    this.$store.commit('ingredients/destroy')
    next()
  },
  
  sockets: {
    ingredientDeleted(item) {
      if (this.item.id && (item.id === this.item.id)) {
        window.history.length > 1 ? this.$router.go(-1) : this.$router.push('/')
      }
    }
  },  
  
}

</script>
