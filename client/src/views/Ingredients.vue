<template>

  <v-card flat>
    
    <loading v-if="loading"></loading>
    
    <template v-else>
    
      <v-list>
        <v-list-tile
          v-for="item in items"
          :key="item.id"
          avatar
          ripple
          @click="itemDetail(item)"
        >
          <v-list-tile-avatar>
            <v-icon v-if="item.isAlcoholic">mdi-flash</v-icon>
            <v-icon v-else>mdi-baby-buggy</v-icon>
            <v-icon v-if="item.isAvailable">mdi-gas-station</v-icon>
          </v-list-tile-avatar>
          
          <v-list-tile-content>
            <v-list-tile-title>{{item.name}}</v-list-tile-title>
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
      
      <v-btn
        fab
        fixed
        bottom right
        color="primary"
        @click="addItem"
      >
        <v-icon dark>mdi-plus</v-icon>
      </v-btn>

      <v-dialog v-model="dialog" persistent scrollable max-width="480px">
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
                      v-model="item.name"
                      :rules="[v => !!v || 'Name is required']"
                      required
                      autofocus
                    ></v-text-field>
                  </v-flex>
                  
                  <v-flex xs12>
                    <v-checkbox
                      label="Is this ingredient alcoholic?"
                      v-model="item.isAlcoholic"
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
              @click="saveItem()">save</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <confirm ref="confirm"></confirm>
      
    </template>
    
  </v-card>
        
</template>

<script>

import { mapState, mapGetters } from 'vuex'
import Loading from '../components/Loading'
import Confirm from '../components/Confirm'

export default {
  name: 'Ingredients',
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
    Confirm
  },
  created() {
    this.$emit('show-page', 'Ingredients')
  },
  
  computed: {
    ...mapGetters({
      items: 'ingredients/sortedItems'
    }),
    ...mapState({
      loading: state => state.ingredients.loading,
    })
  },
  
  methods: {
  
    itemDetail(item) {
      this.$router.push({name: 'ingredientDetail', params: {id: item.id}})
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
        name: undefined
      }
      this.edit = false
      this.dialog = true
    },
    
    editItem() {
      this.edit = true
      this.dialog = true
    },
    
    closeDialog() {
      this.dialog = false
      this.item = {}
    },
    
    saveItem() {
      if (! this.$refs.form.validate()) return
      this.$socket.emit('saveIngredient', this.item, (res) => {
        if (res.error) {
          this.$store.commit('setError', res.error)
        } else {
          this.closeDialog()
        }
      })
    },
    
    deleteItem() {
      this.$refs.confirm.open('Delete', 'Are you sure you want to delete "' + this.item.name + '"?').then(() => {
        this.$socket.emit('deleteIngredient', this.item.id, (res) => {
          if (res.error) {
            this.$store.commit('setError', res.error)
          }
        })
      })
    },
    
  },
  
  beforeRouteEnter(to, from, next) {
    next(t => {
      t.$store.dispatch('ingredients/loadAll')
    });
  },
  
  beforeRouteLeave(to, from, next) {
    this.$store.commit('ingredients/destroy')
    next()
  }
  
}

</script>
