<template>
  <v-card flat>
        
    <v-toolbar
      v-if="title"
      clipped-left
      color="primary"
      dark
      dense
    >
      <v-toolbar-title>{{title}}</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn icon @click="addItem()">
        <v-icon>mdi-plus</v-icon>
      </v-btn>      
    </v-toolbar>
      
    <v-list
      avatar
      dense
    >
      <v-list-tile
        v-for="item in sortedItems"
        :key="item.id"
      >
      
        <v-list-tile-avatar>
          <alcoholic-icon :alcoholic="item.alternative.isAlcoholic"/>
        </v-list-tile-avatar>
        
        <v-list-tile-content>
          <v-list-tile-title>{{item.alternative.name}}</v-list-tile-title>
        </v-list-tile-content>
        
        <v-list-tile-action>
          <v-btn
            icon
            @click="deleteItem(item)"
          >
            <v-icon>mdi-delete</v-icon>
          </v-btn>
        </v-list-tile-action>
    
      </v-list-tile>
    </v-list>
    
    <v-dialog v-model="dialog" persistent scrollable @keydown.esc="closeDialog" @keydown.enter.prevent="saveItem">
      <v-card>
        <v-card-title>
          <span
            class="headline"
          >Add Alternative</span>
        </v-card-title>
        
        <v-card-text>
          <v-form ref="form" v-model="valid" lazy-validation>
            <v-container grid-list-md>
              <v-layout wrap>
              
                <v-flex xs12>
                  <select-ingredient
                    :manageIngredientsStore="false"
                    v-model="item.alternative_id"
                    required
                    autofocus
                    :rules="[v => !!v || 'Ingredient is required']"
                    tabindex="1"
                  ></select-ingredient>
                
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

  </v-card>
          
</template>

<script>

import SelectIngredient from '../components/SelectIngredient'
import AlcoholicIcon from '../components/AlcoholicIcon'
import bus from '../bus'


export default {
  name: 'IngredientAlternatives',
  
  props: {
    title: {
      type: String,
      default: 'Alternatives'
    },
    ingredient: {
      type: Object,
      required: true,
    },
    value: {}
  },
  
  data: function() {
    return {
      items: this.value, // only sets initial value!
      item: {},
      dialog: false,
      valid: true,
    }
  },
  
  components: {
    SelectIngredient,
    AlcoholicIcon,
  },
  
  watch: {
    value: function(v) {
      this.items = v  // update when prop changes!
    }
  },
  
  computed: {
  
    sortedItems() {
      if (! this.items) return []
      return this.items.slice().sort((a, b) => {
        return a.alternative.name.localeCompare(b.alternative.name, 'en', {'sensitivity': 'base'})
      })
    },
    
  },
  
  methods: {

    addItem() {
      this.$refs.form.reset()
      this.item = {
        id: null,
        alternative_id: undefined,
      }
      this.editIndex = -1
      bus.$emit('keyboard-install', this.$refs.form)
      this.dialog = true
    },
  
    closeDialog() {
      this.dialog = false
      bus.$emit('keyboard-remove', this.$refs.form)
      this.item = {}
    },

    saveItem() {
      if (! this.$refs.form.validate()) return

      // don't allow ingredient to be it's own alternative
      if (this.ingredient.id == this.item.alternative_id) {
        this.$store.commit('setError', 'An ingredient can\'t be it\'s own alternative!')
        return
      }
      
      // don't allow duplicate ingredients
      if (this.items.find(item => item.alternative_id === this.item.alternative_id)) {
        this.$store.commit('setError', 'This ingredient is already an alternative!')
        return
      }
        
      this.item['alternative'] = this.$store.getters['ingredients/getById'](this.item['alternative_id'])
      this.items.push(JSON.parse(JSON.stringify(this.item)))
      this.closeDialog()
      this.$emit('input', this.items)
   },
   
    deleteItem(item) {
      let idx = this.items.indexOf(item)
      if (idx == -1) return
      this.items.splice(idx, 1)
      this.$emit('input', this.items)
    },
    
  },

}
</script>
