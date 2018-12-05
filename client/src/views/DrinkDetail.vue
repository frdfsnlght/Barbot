<template>

  <v-card flat>
    
    <loading v-if="loading"></loading>
    
    <template v-else>
    
      <div class="pa-3">
      
        <h1 class="mb-3">{{drink.name}}</h1>
        
        <p
          v-if="drink.isAlcoholic"
          class="subheading">Alcoholic</p>
        <p
          v-else
          class="subheading">Non-alcoholic</p>

        <p
          v-if="drink.isFavorite"
          class="subheading">This drink is a favorite</p>

        <p
          v-if="drink.isOnMenu"
          class="subheading">This drink is on the menu</p>

        <p class="subheading">Times dispensed: {{timesDispensed}}</p>
          
        <p class="subheading">Glass: {{glassName}}</p>
          
        <h2>Ingredients</h2>

        <v-list>

          <v-list-tile
            v-for="di in sortedIngredients"
            :key="di.ingredient.id"
            ripple
            avatar
            @click="gotoIngredientDetail(di.ingredient_id)"
          >
            <v-list-tile-avatar>
              <alcoholic-icon :alcoholic="di.ingredient.isAlcoholic"/>
              <v-icon v-if="di.ingredient.isAvailable">mdi-gas-station</v-icon>
              <v-icon>mdi-numeric-{{di.step}}-box-outline</v-icon>
            </v-list-tile-avatar>
            
            <v-list-tile-content>
              <v-list-tile-title>{{ingredientAmount(di)}} {{di.ingredient.name}}</v-list-tile-title>
            </v-list-tile-content>

          </v-list-tile>
          
        </v-list>

        <p class="subheading">{{drink.instructions}}</p>
        
        <template v-if="drink.isOnMenu">
        
          <order-drink-dialog ref="orderDrinkDialog"></order-drink-dialog>

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
        
      </div>
      
    </template>
    
  </v-card>
        
</template>

<script>

import { mapState } from 'vuex'
import Loading from '../components/Loading'
import OrderDrinkDialog from '../components/OrderDrinkDialog'
import AlcoholicIcon from '../components/AlcoholicIcon'
import units from '../units'

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
    OrderDrinkDialog,
    AlcoholicIcon,
  },
  
  created() {
    this.$emit('show-page', 'Drinks')
  },
  
  computed: {
    timesDispensed() {
      return this.drink.timesDispensed || 0
    },
    glassName() {
      return this.drink.glass ? this.drink.glass.name : ''
    },
    hasIngredients() {
      return this.drink.ingredients && this.drink.ingredients.length > 0
    },
    sortedIngredients() {
      if (! this.hasIngredients) return []
      return this.drink.ingredients.slice().sort((a, b) => {
        if (a.ingredient.step < b.ingredient.step) return -1
        if (a.ingredient.step > b.ingredient.step) return 1
        return a.ingredient.name.localeCompare(b.ingredient.name, 'en', {'sensitivity': 'base'})
      })
    },
    ...mapState({
      loading: state => state.drinks.loading,
      drink: state => state.drinks.drink,
    })
  },
  
  methods: {

    ingredientAmount(drinkIngredient) {
      return units.format(drinkIngredient.amount, drinkIngredient.units)
    },
  
    gotoIngredientDetail(id) {
      this.$router.push({name: 'ingredientDetail', params: {id: id}})
    },
    
    orderDrink() {
      this.$refs.orderDrinkDialog.open(this.drink).then(() => {
        if (this.locationHistory)
          this.$router.go(-2)
      }, ()=>{})
    },
    
  },
  
  beforeRouteEnter(to, from, next) {
    next(t => {
      t.$store.dispatch('drinks/getOne', t.id)
    });
  },
  
  beforeRouteLeave(to, from, next) {
    this.$store.commit('drinks/destroy')
    next()
  },
  
  sockets: {
    drinkDeleted(drink) {
      if (this.drink.id && (drink.id === this.drink.id)) {
        window.history.length > 1 ? this.$router.go(-1) : this.$router.push('/')
      }
    }
  },  
  
}

</script>
