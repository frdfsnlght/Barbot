<template>

  <v-card flat>
    
    <loading v-if="loading"></loading>
    
    <p
      v-else-if="!drinks.length"
      class="title text-xs-center ma-3"
    >
      No drinks are currently available.
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
            <v-icon v-if="drink.isOnMenu">mdi-cup-water</v-icon>
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
    
    <confirm ref="confirm"></confirm>
    <drink-dialog ref="drinkDialog"/>
    
  </v-card>
        
</template>

<script>

import { mapState, mapGetters } from 'vuex'
import Loading from '../components/Loading'
import Confirm from '../components/Confirm'
import AlcoholicIcon from '../components/AlcoholicIcon'
import DrinkDialog from '../components/DrinkDialog'

export default {
  name: 'Drinks',
  data() {
    return {
      drink: {},
      edit: false,
      valid: true,
      menu: false,
      menuX: 0,
      menuY: 0,
    }
  },
  
  components: {
    Loading,
    Confirm,
    AlcoholicIcon,
    DrinkDialog,
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
    })
  },
  
  methods: {
  
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
      })
    },
    
    editDrink() {
      this.$refs.drinkDialog.open(this.drink, true)
    },
    
    deleteDrink() {
      this.$refs.confirm.open('Delete', 'Are you sure you want to delete "' + this.drink.name + '"?').then(() => {
        this.$socket.emit('drink_delete', this.drink.id, (res) => {
          if (res.error) {
            this.$store.commit('setError', res.error)
          }
        })
      })
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
  }
  
}

</script>
