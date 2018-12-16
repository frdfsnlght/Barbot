<template>

  <v-card flat style="height: 92.5vh; overflow-y: auto;">
    
    <loading v-if="loading"></loading>
    
    <p
      v-else-if="!drinks.length"
      class="title text-xs-center ma-3"
    >
      No drinks are currently available.
    </p>
    
    <template v-else>
    
      <v-list>
      
        <v-list-group
          prepend-icon="mdi-sort"
          v-model="showSort"
          no-action
        >
          <v-list-tile slot="activator">
            <v-list-tile-content>
              <v-list-tile-title>Sort by ...</v-list-tile-title>
            </v-list-tile-content>
          </v-list-tile>

          <v-list-tile @click="sortByName">
            <v-list-tile-content>
              <v-list-tile-title>Name</v-list-tile-title>
            </v-list-tile-content>
            <v-list-tile-action>
              <v-icon v-if="sortBy == 'name'">mdi-check</v-icon>
            </v-list-tile-action>
          </v-list-tile>
          
          <v-list-tile @click="sortByMissingIngredients">
            <v-list-tile-content>
              <v-list-tile-title>Missing ingredients</v-list-tile-title>
            </v-list-tile-content>
            <v-list-tile-action>
              <v-icon v-if="sortBy == 'missingIngredients'">mdi-check</v-icon>
            </v-list-tile-action>
          </v-list-tile>
          
        </v-list-group>

      </v-list>
        
      <v-divider v-if="!showSort"/>
        
      <v-list two-line>
        
        <v-list-tile
          v-for="drink in drinks"
          :key="drink.id"
          avatar
          ripple
          @click="gotoDetail(drink)"
        >
          <v-list-tile-avatar>
            <v-icon v-if="drink.isOnMenu">mdi-cup-water</v-icon>
            <v-icon v-if="drink.isFavorite">mdi-heart</v-icon>
            <alcoholic-icon :alcoholic="drink.isAlcoholic"/>
          </v-list-tile-avatar>

          <v-list-tile-content>
            <v-list-tile-title>{{drinkTitle(drink)}}</v-list-tile-title>
            <v-list-tile-sub-title>{{drinkSubtitle(drink)}}</v-list-tile-sub-title>
          </v-list-tile-content>
          
          <v-list-tile-action>
            <v-btn
              icon
              @click.stop="showMenu(drink, $event)"
            >
              <v-icon>mdi-dots-vertical</v-icon>
            </v-btn>
          </v-list-tile-action>
      
        </v-list-tile>
      </v-list>

      <v-menu
        v-model="menu"
        :position-x="menuX"
        :position-y="menuY"
        absolute
        offset-y
      >
        <v-list>

          <v-list-tile
            v-if="drink.missingIngredients == 0"
            ripple @click="orderDrink()">
            <v-list-tile-content>
              <v-list-tile-title>Order</v-list-tile-title>
            </v-list-tile-content>
            <v-list-tile-action>
              <v-icon>mdi-cup-water</v-icon>
            </v-list-tile-action>
          </v-list-tile>
          
          <v-list-tile ripple @click="editDrink()">
            <v-list-tile-content>
              <v-list-tile-title>Edit</v-list-tile-title>
            </v-list-tile-content>
            <v-list-tile-action>
              <v-icon>mdi-pencil</v-icon>
            </v-list-tile-action>
          </v-list-tile>
          
          <v-list-tile ripple @click="deleteDrink()">
            <v-list-tile-content>
              <v-list-tile-title>Delete</v-list-tile-title>
            </v-list-tile-content>
            <v-list-tile-action>
              <v-icon>mdi-delete</v-icon>
            </v-list-tile-action>
          </v-list-tile>
          
        </v-list>
      </v-menu>
      
    </template>
    
    <template v-if="!loading">
      <v-btn
        fab
        fixed
        bottom right
        color="primary"
        @click="addDrink"
      >
        <v-icon dark>mdi-plus</v-icon>
      </v-btn>
    </template>
    
    <confirm-dialog ref="confirmDialog"/>
    <drink-dialog ref="drinkDialog"/>
    <order-drink-dialog ref="orderDrinkDialog"/>

  </v-card>
        
</template>

<script>

import { mapState, mapGetters } from 'vuex'
import Loading from '../components/Loading'
import ConfirmDialog from '../components/ConfirmDialog'
import AlcoholicIcon from '../components/AlcoholicIcon'
import DrinkDialog from '../components/DrinkDialog'
import OrderDrinkDialog from '../components/OrderDrinkDialog'

export default {
  name: 'Drinks',
  
  data() {
    return {
      drink: {},
      menu: false,
      menuX: 0,
      menuY: 0,
      showSort: false,
    }
  },
  
  components: {
    Loading,
    ConfirmDialog,
    AlcoholicIcon,
    DrinkDialog,
    OrderDrinkDialog,
  },
  
  created() {
    this.$emit('show-page', 'Drinks')
  },
  
  computed: {
  
    ...mapGetters({
      drinks: 'drinks/sortedDrinks',
    }),
    ...mapState({
      loading: state => state.drinks.loading,
      sortBy: state => state.drinks.sortBy,
    })
  },
  
  methods: {

    sortByName() {
      this.$store.commit('drinks/setSortBy', 'name')
      this.showSort = false
    },
    
    sortByMissingIngredients() {
      this.$store.commit('drinks/setSortBy', 'missingIngredients')
      this.showSort = false
    },
    
    drinkTitle(drink) {
      let title = drink.primaryName
      if (drink.secondaryName)
        title += ', ' + drink.secondaryName
      return title
    },
    
    drinkSubtitle(drink) {
      if (drink.missingIngredients == 0) return 'available to order'
      let subtitle = 'missing ' + drink.missingIngredients + ' of ' + drink.numIngredients + ' ingredient'
      if (drink.numIngredients > 1) subtitle += 's'
      return subtitle
    },
    
    gotoDetail(drink) {
      this.$router.push({name: 'drinkDetail', params: {id: drink.id}})
    },
  
    showMenu(drink, e) {
      this.drink = JSON.parse(JSON.stringify(drink))
      this.menuX = e.clientX
      this.menuY = e.clientY
      this.menu = true
    },
  
    addDrink() {
      this.$refs.drinkDialog.open({
        id: undefined,
        primaryName: undefined,
        secondaryName: undefined,
        instructions: undefined,
        glass_id: undefined,
        ingredients: []
      }).then(()=>{},()=>{})
    },
    
    editDrink() {
      this.$refs.drinkDialog.open(this.drink, true).then(()=>{},()=>{})
    },
    
    deleteDrink() {
      this.$refs.confirmDialog.open('Delete', 'Are you sure you want to delete "' + this.drink.name + '"?').then(() => {
        this.$socket.emit('drink_delete', this.drink.id, (res) => {
          if (res.error) {
            this.$store.commit('setError', res.error)
          }
        })
      }, ()=>{})
    },
    
    orderDrink() {
      this.$refs.orderDrinkDialog.open(this.drink).then(()=>{}, ()=>{})
    },
    
  },
  
  beforeRouteEnter(to, from, next) {
    next(t => {
      t.$store.dispatch('drinks/getAll')
    });
  },
  
  beforeRouteLeave(to, from, next) {
    this.$store.commit('drinks/destroy')
    next()
  },
  
  sockets: {
    connect() {
      this.$store.dispatch('drinks/getAll')
    },
  },
  
}

</script>
