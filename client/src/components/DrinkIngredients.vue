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
          <v-icon>mdi-numeric-{{item.step}}-box-outline</v-icon>
        </v-list-tile-avatar>
        
        <v-list-tile-content>
          <v-list-tile-title>{{item.amount | fixedAmount}} {{item.units}} {{item.ingredient.name}}</v-list-tile-title>
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
    
    <v-dialog v-model="dialog" persistent scrollable max-width="480px" @keydown.esc="closeDialog" @keydown.enter.prevent="saveItem">
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
                    required
                    autofocus
                    data-kbType="positiveInteger"
                    tabindex="1"
                  ></v-text-field>
                </v-flex>

                <v-flex xs6>
                  <v-text-field
                    label="Amount"
                    v-model="item.amount"
                    :rules="[v => !!v || 'Amount is required']"
                    required
                    data-kbType="positiveNumber"
                    tabindex="2"
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
                    v-model="item.ingredient_id"
                    required
                    :rules="[v => !!v || 'Ingredient is required']"
                    tabindex="3"
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
import units from '../units'
import bus from '../bus'


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
        ingredient_id: undefined,
        amount: undefined,
        units: units.defaultUnits(),
        step: maxStep,
      }
      this.editIndex = -1
      bus.$emit('keyboard-install', this.$refs.form)
      this.dialog = true
    },
  
    editItem(item) {
      this.$refs.form.reset()
      this.item = JSON.parse(JSON.stringify(item))
      this.editIndex = this.items.indexOf(item)
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
      if (this.editIndex != -1) {
        this.items.splice(this.editIndex, 1)
      }

      let amount = +(this.item.amount)
      if (isNaN(amount)) {
        this.$store.commit('setError', 'Invalid amount!')
        return
      }
      let step = Math.trunc(+(this.item.step))
      if (isNaN(step)) {
        this.$store.commit('setError', 'Invalid step!')
        return
      }
      
      // don't allow duplicate ingredients
      if (this.items.find(item => item.ingredient_id === this.item.ingredient_id)) {
        this.$store.commit('setError', 'This ingredient is already in the drink!')
        return
      }
        
      // don't allow more than 4 ingredients in the same step
      let stepIngs = this.items.filter(function(i) { return i.step == step })
      if (stepIngs.length >= 4) {
        this.$store.commit('setError', 'There are already 4 ingredients in the same step!')
        return
      }
        
      // don't allow more ingredients than configured
      let totalMLs = units.toML(amount, this.item.units)
      this.items.forEach((i) => { totalMLs += units.toML(i.amount, i.units) })
      if (totalMLs > this.drinkSizeLimit) {
        this.$store.commit('setError',
          'Drink ingredients exceed configured limit of ' +
            units.format(units.toOther(this.drinkSizeLimit, units.defaultUnits()), units.defaultUnits()) + '.')
        return
      }
      
      this.item['ingredient'] = this.$store.getters['ingredients/getOne'](this.item['ingredient_id'])
      this.item.amount = amount
      this.item.step = step
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
