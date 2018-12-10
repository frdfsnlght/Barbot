<template>

  <v-card flat>
    
    <loading v-if="loading"></loading>
    
    <p
      v-else-if="!ingredients.length"
      class="title text-xs-center ma-3"
    >
      No ingredients are currently available.
    </p>
    
    <template v-else>
    
      <v-list>
        <v-list-tile
          v-for="ingredient in ingredients"
          :key="ingredient.id"
          avatar
          ripple
          @click="gotoDetail(ingredient)"
        >
          <v-list-tile-avatar>
            <alcoholic-icon :alcoholic="ingredient.isAlcoholic"/>
            <v-icon v-if="ingredient.isAvailable">mdi-gas-station</v-icon>
          </v-list-tile-avatar>
          
          <v-list-tile-content>
            <v-list-tile-title>{{ingredient.name}}</v-list-tile-title>
          </v-list-tile-content>
          
          <v-list-tile-action>
            <v-btn
              icon
              @click.stop="showMenu(ingredient, $event)"
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
        
          <v-list-tile ripple @click="editIngredient()">
            <v-list-tile-content>
              <v-list-tile-title>Edit</v-list-tile-title>
            </v-list-tile-content>
            <v-list-tile-action>
              <v-icon>mdi-pencil</v-icon>
            </v-list-tile-action>
          </v-list-tile>
          
          <v-list-tile ripple @click="deleteIngredient()">
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
        @click="addIngredient"
      >
        <v-icon dark>mdi-plus</v-icon>
      </v-btn>
    </template>
    
    <confirm ref="confirm"></confirm>
    <ingredient-dialog ref="ingredientDialog"/>
      
  </v-card>
        
</template>

<script>

import { mapState, mapGetters } from 'vuex'
import Loading from '../components/Loading'
import Confirm from '../components/Confirm'
import AlcoholicIcon from '../components/AlcoholicIcon'
import IngredientDialog from '../components/IngredientDialog'

export default {
  name: 'Ingredients',
  
  data() {
    return {
      ingredient: {},
      menu: false,
      menuX: 0,
      menuY: 0,
    }
  },
  
  components: {
    Loading,
    Confirm,
    AlcoholicIcon,
    IngredientDialog,
  },
  
  created() {
    this.$emit('show-page', 'Ingredients')
  },
  
  computed: {
    ...mapGetters({
      ingredients: 'ingredients/sortedIngredients'
    }),
    ...mapState({
      loading: state => state.ingredients.loading,
    })
  },
  
  methods: {
  
    gotoDetail(ingredient) {
      this.$router.push({name: 'ingredientDetail', params: {id: ingredient.id}})
    },
  
    showMenu(ingredient, e) {
      this.ingredient = JSON.parse(JSON.stringify(ingredient))
      this.menuX = e.clientX
      this.menuY = e.clientY
      this.menu = true
    },
  
    addIngredient() {
      this.$refs.ingredientDialog.open({
        id: undefined,
        name: undefined,
        isAlcoholic: false,
        alternatives: []
      }).then(()=>{},()=>{})
    },
    
    editIngredient() {
      this.$refs.ingredientDialog.open(this.ingredient, true).then(()=>{},()=>{})
    },
    
    deleteIngredient() {
      this.$refs.confirm.open('Delete', 'Are you sure you want to delete "' + this.ingredient.name + '"?').then(() => {
        this.$socket.emit('ingredient_delete', this.ingredient.id, (res) => {
          if (res.error) {
            this.$store.commit('setError', res.error)
          }
        })
      }, ()=>{})
    },
    
  },
  
  beforeRouteEnter(to, from, next) {
    next(t => {
      t.$store.dispatch('ingredients/getAll')
    });
  },
  
  beforeRouteLeave(to, from, next) {
    this.$store.commit('ingredients/destroy')
    next()
  }
  
}

</script>
