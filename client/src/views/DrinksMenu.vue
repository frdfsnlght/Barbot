<template>

  <v-card flat>
    
    <template v-if="isConsole && anyPumpReady">
    
      <v-list>
        <v-list-tile
          avatar
          ripple
          @click="gotoMakeMyOwn()"
        >
          <v-list-tile-action>
            <v-icon>mdi-account</v-icon>
          </v-list-tile-action>
          <v-list-tile-title>Make My Own</v-list-tile-title>
        </v-list-tile>
      </v-list>
      <v-divider/>
      
    </template>
    
    <loading v-if="loading"></loading>
    
    <p
      v-else-if="!drinks.length"
      class="title text-xs-center ma-3"
    >
      No menu items are currently available. Try loading some ingredients or adding more recipes.
    </p>
    
    <template v-else>
    
      <v-list two-line>
        <v-list-tile
          v-for="drink in drinks"
          :key="drink.id"
          avatar
          ripple
          @click="gotoDetail(drink)"
        >
          <v-list-tile-avatar>
            <v-icon v-if="drink.isFavorite">mdi-heart</v-icon>
            <alcoholic-icon :alcoholic="drink.isAlcoholic"/>
          </v-list-tile-avatar>

          <v-list-tile-content>
            <v-list-tile-title>{{drink.primaryName}}</v-list-tile-title>
            <v-list-tile-sub-title>{{drink.secondaryName}}</v-list-tile-sub-title>
          </v-list-tile-content>
          
          <v-list-tile-action>
            <v-btn
              icon
              @click.stop="orderDrink(drink)"
            >
              <v-icon>mdi-plus</v-icon>
            </v-btn>
          </v-list-tile-action>
      
        </v-list-tile>
      </v-list>

      <order-drink-dialog ref="orderDrinkDialog"/>

    </template>
    
  </v-card>
        
</template>

<script>

import { mapState, mapGetters } from 'vuex'
import Loading from '../components/Loading'
import OrderDrinkDialog from '../components/OrderDrinkDialog'
import AlcoholicIcon from '../components/AlcoholicIcon'

export default {
  name: 'DrinksMenu',
  data() {
    return {
      drink: {},
      dialog: false,
      valid: true,
    }
  },
  
  components: {
    Loading,
    OrderDrinkDialog,
    AlcoholicIcon,
  },
  
  created() {
    this.$emit('show-page', 'Drinks Menu')
  },
  
  computed: {
    ...mapGetters({
      drinks: 'drinksMenu/sortedDrinks',
      anyPumpReady: 'pumps/anyPumpReady',
    }),
    ...mapState([
      'isConsole',
    ]),
    ...mapState({
      loading: state => state.drinksMenu.loading,
      dispenserState: state => state.dispenser.state,
    })
  },
  
  methods: {
  
    gotoMakeMyOwn() {
      this.$router.push({name: 'makeMyOwn'})
    },
  
    gotoDetail(drink) {
      this.$router.push({name: 'drinkDetail', params: {id: drink.id, locationHistory: -2}})
    },
  
    orderDrink(drink) {
      this.$refs.orderDrinkDialog.open(drink).then(() => {
        window.history.length > 1 ? this.$router.go(-1) : this.$router.push('/')
      }, ()=>{})
    },
    
  },
  
  beforeRouteEnter(to, from, next) {
    next(t => {
      t.$store.dispatch('drinksMenu/getAll')
      if (t.isConsole && t.dispenserState == 'manual') {
        t.$socket.emit('dispenser_stopManual', (res) => {
          if (res.error) {
            t.$store.commit('setError', res.error)
          }
        })
      }
    });
  },
  
  beforeRouteLeave(to, from, next) {
    this.$store.commit('drinksMenu/destroy')
    next()
  }
  
}

</script>
