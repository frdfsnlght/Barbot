<template>

  <v-card flat>
    
    <loading v-if="loading"></loading>
    
    <template v-else>
    
      <div class="pa-3">
      
        <h1 class="mb-3">{{ingredient.name}}</h1>
        
        <p
          v-if="ingredient.isAlcoholic"
          class="subheading">Alcoholic</p>
        <p
          v-else
          class="subheading">Non-alcoholic</p>

        <p
          v-if="ingredient.isAvailable"
          class="subheading">This ingredient is currently available.</p>
        <p
          v-else
          class="subheading">Last available: {{lastAvailable}}</p>

        <p class="subheading">Amount dispensed: {{amountDispensedML}} ml / {{amountDispensedOZ}} oz</p>
        <p class="subheading">Times dispensed: {{timesDispensed}}</p>
        
        <h2>Alternatives</h2>

        <p
          v-if="!hasAlternatives"
          class="subheading"
        >This ingredient has no alternatives.</p>
        
        <v-list dense v-else>

          <v-list-tile
            v-for="ia in sortedAlternatives"
            :key="ia.alternative.id"
            ripple
            avatar
            @click="gotoIngredientDetail(ia.alternative_id)"
          >
            <v-list-tile-avatar>
              <alcoholic-icon :alcoholic="ia.alternative.isAlcoholic"/>
            </v-list-tile-avatar>
            
            <v-list-tile-content>
              <v-list-tile-title>{{ia.alternative.name}}</v-list-tile-title>
            </v-list-tile-content>

          </v-list-tile>
          
        </v-list>
        
        <h2>Drinks</h2>

        <p
          v-if="!hasDrinks"
          class="subheading"
        >No drinks use this ingredient.</p>
        
        <v-list v-else>

          <v-list-tile
            v-for="di in sortedDrinks"
            :key="di.drink.id"
            ripple
            avatar
            @click="gotoDrinkDetail(di.drink_id)"
          >
            <v-list-tile-avatar>
              <v-icon v-if="di.drink.isFavorite">mdi-heart</v-icon>
              <alcoholic-icon :alcoholic="di.drink.isAlcoholic"/>
            </v-list-tile-avatar>

            <v-list-tile-content>
              <v-list-tile-title>{{di.drink.name}}</v-list-tile-title>
            </v-list-tile-content>
            
          </v-list-tile>
          
        </v-list>

      </div>
      
    </template>
    
  </v-card>
        
</template>

<script>

import { mapState } from 'vuex'
import Loading from '../components/Loading'
import AlcoholicIcon from '../components/AlcoholicIcon'
import units from '../units'

export default {
  name: 'IngredientDetail',
  data() {
    return {
    }
  },
  
  components: {
    Loading,
    AlcoholicIcon,
  },
  
  created() {
    this.$emit('show-page', 'Ingredients')
  },
  
  computed: {
    amountDispensedML() {
      let a = this.ingredient.amountDispensed || 0
      return a.toFixed(0)
    },
    amountDispensedOZ() {
      let a = this.ingredient.amountDispensed || 0
      return (a * 0.033814).toFixed(2)
    },
    timesDispensed() {
      return this.ingredient.timesDispensed || 0
    },
    lastAvailable() {
      if (! this.ingredient.lastContainerAmount)
        return '<never>'
      return units.format(this.ingredient.lastContainerAmount, this.ingredient.lastUnits) + ' container, ' +
            ((this.ingredient.lastAmount / this.ingredient.lastContainerAmount) * 100).toFixed() + '% full ' +
            '(' + units.format(this.ingredient.lastAmount, this.ingredient.lastUnits) + ')'
    },
    hasAlternatives() {
      return this.ingredient.alternatives && this.ingredient.alternatives.length > 0
    },
    sortedAlternatives() {
      if (! this.hasAlternatives) return []
      return this.ingredient.alternatives.slice().sort((a, b) => {
        return a.alternative.name.localeCompare(b.alternative.name, 'en', {'sensitivity': 'base'})
      })
    },
    hasDrinks() {
      return this.ingredient.drinks && this.ingredient.drinks.length > 0
    },
    sortedDrinks() {
      if (! this.hasDrinks) return []
      return this.ingredient.drinks.slice().sort((a, b) => {
        return a.drink.name.localeCompare(b.drink.name, 'en', {'sensitivity': 'base'})
      })
    },
    ...mapState({
      loading: state => state.ingredients.loading,
      ingredient: state => state.ingredients.ingredient,
    })
  },
  
  methods: {
    
    gotoIngredientDetail(id) {
      this.$router.push({name: 'ingredientDetail', params: {id: id}})
    },
    
    
    gotoDrinkDetail(id) {
      this.$router.push({name: 'drinkDetail', params: {id: id}})
    },
    
  },
  
  beforeRouteEnter(to, from, next) {
    next(t => {
      t.$store.dispatch('ingredients/getOne', t.$route.params.id)
    });
  },
  
  beforeRouteUpdate(to, from, next) {
    this.$store.dispatch('ingredients/getOne', to.params.id)
    next()
  },
  
  beforeRouteLeave(to, from, next) {
    this.$store.commit('ingredients/destroy')
    next()
  },
  
  sockets: {
    ingredient_deleted(ingredient) {
      if (this.ingredient.id && (ingredient.id === this.ingredient.id)) {
        window.history.length > 1 ? this.$router.go(-1) : this.$router.push('/')
      }
    }
  },  
  
}

</script>
