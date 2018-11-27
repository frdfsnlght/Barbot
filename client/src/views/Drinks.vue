<template>

  <v-card flat>
    
    <loading v-if="loading"></loading>
    
    <p
      v-else-if="!items.length"
      class="title text-xs-center ma-3"
    >
      No drinks are currently available.
    </p>
    
    <template v-else>
    
      <v-list two-line>
        <v-list-tile
          v-for="item in items"
          :key="item.id"
          avatar
          ripple
          @click="itemDetail(item)"
        >
          <v-list-tile-avatar>
            <v-icon v-if="item.isOnMenu">mdi-cup-water</v-icon>
            <v-icon v-if="item.isFavorite">mdi-heart</v-icon>
            <v-icon v-if="item.isAlcoholic">mdi-flash</v-icon>
            <v-icon v-else>mdi-baby-buggy</v-icon>
          </v-list-tile-avatar>

          <v-list-tile-content>
            <v-list-tile-title>{{item.primaryName}}</v-list-tile-title>
            <v-list-tile-sub-title>{{item.secondaryName}}</v-list-tile-sub-title>
          </v-list-tile-content>
          
          <v-list-tile-action>
            <v-btn
              icon
              @click.stop="showMenu(item, $event)"
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
        
          <v-list-tile ripple @click="editItem()">
            <v-list-tile-content>
              <v-list-tile-title>Edit</v-list-tile-title>
            </v-list-tile-content>
            <v-list-tile-action>
              <v-icon>mdi-pencil</v-icon>
            </v-list-tile-action>
          </v-list-tile>
          
          <v-list-tile ripple @click="deleteItem()">
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
        @click="addItem"
      >
        <v-icon dark>mdi-plus</v-icon>
      </v-btn>
    </template>
    
    <v-dialog v-model="dialog" persistent scrollable max-width="480px" @keydown.esc="closeDialog" @keydown.enter.prevent="saveItem">
      <v-card>
        <v-card-title>
          <span
            v-if="edit"
            class="headline"
          >Edit Drink</span>
          <span
            v-else
            class="headline"
          >Add Drink</span>
        </v-card-title>
        
        <v-card-text>
          <v-form ref="form" v-model="valid" lazy-validation>
            <v-container grid-list-md>
              <v-layout wrap>
              
                <v-flex xs12>
                  <v-text-field
                    label="Primary name"
                    v-model="item.primaryName"
                    :rules="[v => !!v || 'Primary name is required']"
                    required
                    autofocus
                    :data-kbUCWords="true"
                    tabindex="1"
                  ></v-text-field>
                </v-flex>
                
                <v-flex xs12>
                  <v-text-field
                    label="Secondary name"
                    v-model="item.secondaryName"
                    hint="This is not required but can help distinguish similar drinks"
                    :data-kbUCWords="true"
                    tabindex="2"
                    ></v-text-field>
                </v-flex>
                
                <v-flex xs12>
                  <v-checkbox
                    label="Is this drink a favorite?"
                    v-model="item.isFavorite"
                    required
                    tabindex="3"
                  ></v-checkbox>
                </v-flex>
                
                <v-flex xs12>
                  <v-select
                    :items="glasses"
                    item-text="name"
                    item-value="id"
                    label="Glass"
                    v-model="item.glassId"
                    :rules="[v => !!v || 'Glass is required']"
                    required
                    tabindex="4"
                  ></v-select>
                </v-flex>

                <v-flex xs12>
                  <drink-ingredients
                    title="Ingredients"
                    v-model="item.ingredients"></drink-ingredients>
                </v-flex>
                
                <v-flex xs12>
                  <v-textarea
                    label="Instructions"
                    auto-grow
                    v-model="item.instructions"
                    :data-kbUCFirst="true"
                    tabindex="5"
                  ></v-textarea>
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
            @click="saveItem()">save</v-btn>
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
import DrinkIngredients from '../components/DrinkIngredients'
import bus from '../bus'

export default {
  name: 'Drinks',
  data() {
    return {
      item: {},
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
    DrinkIngredients
  },
  
  created() {
    this.$emit('show-page', 'Drinks')
  },
  
  computed: {
    ...mapGetters({
      items: 'drinks/sortedItems',
      glasses: 'glasses/sortedItems',
    }),
    ...mapState({
      loading: state => state.drinks.loadingAll,
    })
  },
  
  methods: {
  
    itemDetail(item) {
      this.$router.push({name: 'drinkDetail', params: {id: item.id}})
    },
  
    showMenu(item, e) {
      this.$refs.form.reset()
      this.item = JSON.parse(JSON.stringify(item))
      this.menuX = e.clientX
      this.menuY = e.clientY
      this.menu = true
    },
  
    addItem() {
      this.$refs.form.reset()
      this.item = {
        id: undefined,
        primaryName: undefined,
        secondaryName: undefined,
        instructions: undefined,
        glassId: undefined,
        ingredients: []
      }
      this.edit = false
      this.$store.dispatch('glasses/loadAll')
      bus.$emit('keyboard-install', this.$refs.form)
      this.dialog = true
    },
    
    editItem() {
      this.edit = true
      this.$store.dispatch('glasses/loadAll')
      bus.$emit('keyboard-install', this.$refs.form)
      this.dialog = true
    },
    
    closeDialog() {
      this.dialog = false
      this.item = {}
      bus.$emit('keyboard-remove', this.$refs.form)
    },
    
    saveItem() {
      if (! this.$refs.form.validate()) return
      if ((! this.item.ingredients) || (this.item.ingredients.length == 0)) {
        this.$store.commit('setError', 'At least one ingredient is required!')
        return
      }
      this.$socket.emit('saveDrink', this.item, (res) => {
        if (res.error) {
          this.$store.commit('setError', res.error)
        } else {
          this.closeDialog()
        }
      })
    },
    
    deleteItem() {
      this.$refs.confirm.open('Delete', 'Are you sure you want to delete "' + this.item.name + '"?').then(() => {
        this.$socket.emit('deleteDrink', this.item.id, (res) => {
          if (res.error) {
            this.$store.commit('setError', res.error)
          }
        })
      })
    },
    
  },
  
  beforeRouteEnter(to, from, next) {
    next(t => {
      t.$store.dispatch('drinks/loadAll')
    });
  },
  
  beforeRouteLeave(to, from, next) {
    this.$store.commit('drinks/destroy')
    this.$store.commit('glasses/destroy')
    next()
  }
  
}

</script>
