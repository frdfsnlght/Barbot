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
      
    <v-list dense>
      <v-list-tile
        v-for="item in sortedItems"
        :key="item.id"
      >
        <v-list-tile-content>
          <v-list-tile-title>{{item.amount}} {{item.units}} {{item.ingredient.name}}</v-list-tile-title>
        </v-list-tile-content>
        
        <v-list-tile-action>
          <v-menu bottom left>
            <v-btn
              slot="activator"
              icon
            >
              <v-icon>mdi-dots-vertical</v-icon>
            </v-btn>
            <v-list>
            
              <v-list-tile ripple @click="editItem(item)">
                <v-list-tile-content>
                  <v-list-tile-title>Edit</v-list-tile-title>
                </v-list-tile-content>
                <v-list-tile-action>
                  <v-icon>mdi-pencil</v-icon>
                </v-list-tile-action>
              </v-list-tile>
              
              <v-list-tile ripple @click="deleteItem(item)">
                <v-list-tile-content>
                  <v-list-tile-title>Delete</v-list-tile-title>
                </v-list-tile-content>
                <v-list-tile-action>
                  <v-icon>mdi-delete</v-icon>
                </v-list-tile-action>
              </v-list-tile>
              
            </v-list>
          </v-menu>
        </v-list-tile-action>
    
      </v-list-tile>
    </v-list>
    
    <v-dialog v-model="dialog" persistent scrollable max-width="480px">
      <v-card>
        <v-card-title>
          <span
            v-if="editIndex >= 0"
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
              
                <v-flex xs8>
                  <v-text-field
                    label="Step"
                    v-model="item.step"
                    :rules="[v => !!v || 'Step is required']"
                    mask="##"
                    required
                    autofocus
                  ></v-text-field>
                </v-flex>

                <v-flex xs6>
                  <v-text-field
                    label="Amount"
                    v-model="item.amount"
                    :rules="[v => !!v || 'Amount is required']"
                    mask="###"
                    required
                  ></v-text-field>
                </v-flex>

                <v-flex xs6>
                  <select-units
                    v-model="item.units"
                    required
                    :rules="[v => !!v || 'Units is required']"
                  ></select-units>
                </v-flex>
                
                <v-flex xs12>
                  <select-ingredient
                    v-model="item.ingredientId"
                    required
                    :rules="[v => !!v || 'Ingredient is required']"
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

import { mapState } from 'vuex'
import SelectIngredient from '../components/SelectIngredient'
import SelectUnits from '../components/SelectUnits'
//import { toML, convertUnits } from '../utils'
import utils from '../utils'


export default {
  name: 'DrinkIngredients',
  
  props: {
    title: {
      type: String,
      default: 'Ingredients'
    },
    value: {}
  },
  
  data: function() {
    return {
      items: this.value, // only sets initial value!
      item: {},
      dialog: false,
      editIndex: -1,
      valid: true,
    }
  },
  
  components: {
    SelectIngredient,
    SelectUnits,
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
        if (a.step < b.step) return -1
        if (a.step > b.step) return 1
        return a.ingredient.name.localeCompare(b.ingredient.name, 'en', {'sensitivity': 'base'})
      })
    },
    ...mapState({
      defaultUnits: state => state.options.defaultUnits,
      drinkSizeLimit: state => state.options.drinkSizeLimit,
    }),
    
  },
  
  methods: {
  
    addItem() {
      this.$refs.form.reset()
      // find max step
      let maxStep = 1
      for (var i = 0; i < this.items.length; i++)
        if (this.items[i].step > maxStep) maxStep = this.items[i].step
      // find number of ingredients with maxStep
      let stepIngs = this.items.filter(function(i) { return i.step == maxStep })
      if (stepIngs.length >= 4) maxStep++
        
      this.item = {
        id: null,
        ingredientId: undefined,
        amount: undefined,
        units: this.defaultUnits,
        step: maxStep,
      }
      this.editIndex = -1
      this.dialog = true
    },
  
    editItem(item) {
      this.$refs.form.reset()
      this.item = JSON.parse(JSON.stringify(item))
      this.editIndex = this.items.indexOf(item)
      this.dialog = true
    },
  
    closeDialog() {
      this.dialog = false
      this.item = {}
    },

    saveItem() {
      if (! this.$refs.form.validate()) return
      if (this.editIndex != -1) {
        this.items.splice(this.editIndex, 1)
      }
        
      console.log('drinkSizeLimit: ' + this.drinkSizeLimit)
      
      // don't allow duplicate ingredients
      if (this.items.find(item => item.ingredientId === this.item.ingredientId)) {
        this.$store.commit('setError', 'This ingredient is already in the drink!')
        return
      }
        
      // don't allow more than 4 ingredients in the same step
      let step = this.item.step
      let stepIngs = this.items.filter(function(i) { return i.step == step })
      if (stepIngs.length >= 4) {
        this.$store.commit('setError', 'There are already 4 ingredients in the same step!')
        return
      }
        
      // don't allow more ingredients than configured
      let totalMLs = utils.toML(this.item.amount, this.item.units)
      this.items.forEach((i) => { totalMLs += utils.toML(i.amount, i.units) })
      if (totalMLs > this.drinkSizeLimit) {
        this.$store.commit('setError',
          'Drink ingredients exceed configured limit of ' +
            utils.convertUnits(this.drinkSizeLimit, 'ml', this.defaultUnits).toFixed() + ' ' +
            this.defaultUnits)
        return
      }
      
      this.item['ingredient'] = this.$store.getters['ingredients/getById'](this.item['ingredientId'])
      this.items.push(JSON.parse(JSON.stringify(this.item)))
      this.closeDialog()
      console.dir(this.items)
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
