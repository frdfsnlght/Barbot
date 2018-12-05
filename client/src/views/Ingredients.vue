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
    
    <v-dialog v-model="dialog" persistent scrollable @keydown.esc="closeDialog" @keydown.enter.prevent="saveIngredient">
      <v-card>
        <v-card-title>
          <span
            v-if="edit"
            class="headline"
          >Edit Ingredient</span>
          <span
            v-else
            class="headline"
          >Add Ingredient</span>
        </v-card-title>
        <v-card-text>
          <v-form ref="form" v-model="valid" lazy-validation>
            <v-container grid-list-md>
              <v-layout wrap>
              
                <v-flex xs12>
                  <v-text-field
                    label="Name"
                    v-model="ingredient.name"
                    :rules="[v => !!v || 'Name is required']"
                    required
                    autofocus
                    :data-kbUCWords="true"
                    tabindex="1"
                  ></v-text-field>
                </v-flex>
                
                <v-flex xs12>
                  <v-checkbox
                    label="Is this ingredient alcoholic?"
                    v-model="ingredient.isAlcoholic"
                    required
                  ></v-checkbox>
                </v-flex>
                
              </v-layout>
            </v-container>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            flat
            @click="closeDialog()">close</v-btn>
          <v-btn
            :disabled="!valid"
            flat
            @click="saveIngredient()">save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <confirm ref="confirm"></confirm>
      
  </v-card>
        
</template>

<script>

import { mapState, mapGetters } from 'vuex'
import Loading from '../components/Loading'
import Confirm from '../components/Confirm'
import AlcoholicIcon from '../components/AlcoholicIcon'
import bus from '../bus'

export default {
  name: 'Ingredients',
  data() {
    return {
      ingredient: {},
      dialog: false,
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
      this.$refs.form.reset()
      this.ingredient = JSON.parse(JSON.stringify(ingredient))
      this.menuX = e.clientX
      this.menuY = e.clientY
      this.menu = true
    },
  
    addIngredient() {
      this.$refs.form.reset()
      this.ingredient = {
        id: undefined,
        name: undefined
      }
      this.edit = false
      bus.$emit('keyboard-install', this.$refs.form)
      this.dialog = true
    },
    
    editIngredient() {
      this.edit = true
      bus.$emit('keyboard-install', this.$refs.form)
      this.dialog = true
    },
    
    closeDialog() {
      this.dialog = false
      this.ingredient = {}
      bus.$emit('keyboard-remove', this.$refs.form)
    },
    
    saveIngredient() {
      if (! this.$refs.form.validate()) return
      this.$socket.emit('ingredient_save', this.ingredient, (res) => {
        if (res.error) {
          this.$store.commit('setError', res.error)
        } else {
          this.closeDialog()
        }
      })
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
