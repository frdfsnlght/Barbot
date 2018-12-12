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
    
      <draggable v-model="alternatives">
    
        <v-list-tile
          v-for="alternative in alternatives"
          :key="alternative.id"
        >
        
          <v-list-tile-avatar>
            <v-icon>mdi-reorder-horizontal</v-icon>
            <alcoholic-icon :alcoholic="alternative.isAlcoholic"/>
          </v-list-tile-avatar>
          
          <v-list-tile-content>
            <v-list-tile-title>{{alternative.name}}</v-list-tile-title>
          </v-list-tile-content>
          
          <v-list-tile-action>
            <v-btn
              icon
              @click="deleteAlternative(alternative)"
            >
              <v-icon>mdi-delete</v-icon>
            </v-btn>
          </v-list-tile-action>
      
        </v-list-tile>
      
      </draggable>
    
    </v-list>
    
    <v-dialog v-model="dialog" persistent scrollable>
      <v-card>
        <v-card-title>
          <span
            class="headline"
          >Add Alternative</span>
        </v-card-title>
        
        <v-card-text @keydown.esc.prevent="closeDialog" @keydown.enter.prevent="saveAlternative">
          <v-form ref="form" v-model="valid" lazy-validation>
            <v-container grid-list-md>
              <v-layout wrap>
              
                <v-flex xs12>
                  <select-ingredient
                    :manageIngredientsStore="false"
                    v-model="alternative.id"
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
            @click="saveAlternative()">save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

  </v-card>
          
</template>

<script>

import SelectIngredient from '../components/SelectIngredient'
import AlcoholicIcon from '../components/AlcoholicIcon'
import draggable from 'vuedraggable';
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
      alternatives: this.value, // only sets initial value!
      alternative: {},
      dialog: false,
      valid: true,
      targetAlternativeId: null,
    }
  },
  
  components: {
    SelectIngredient,
    AlcoholicIcon,
    draggable,
  },
  
  watch: {
  
    value: function(v) {
      this.alternatives = v  // update when prop changes!
    },
    
    alternatives: function(v) {
      this.$emit('input', v)
    },
    
  },
  
  methods: {

    addItem() {
      this.$refs.form.reset()
      this.alternative = {
        id: null
      }
      bus.$emit('keyboard-install', this.$refs.form)
      this.dialog = true
    },
  
    closeDialog() {
      this.dialog = false
      bus.$emit('keyboard-remove', this.$refs.form)
      this.alternative = {}
    },

    saveAlternative() {
      if (! this.$refs.form.validate()) return

      // don't allow ingredient to be it's own alternative
      if (this.ingredient.id == this.alternative.id) {
        this.$store.commit('setError', 'An ingredient can\'t be it\'s own alternative!')
        return
      }
      
      // don't allow duplicate ingredients
      if (this.alternatives.find(alternative => alternative.id === this.alternative.id)) {
        this.$store.commit('setError', 'This ingredient is already an alternative!')
        return
      }
        
      let alt = this.$store.getters['ingredients/getById'](this.alternative.id)
      this.alternatives.push(JSON.parse(JSON.stringify(alt)))
      this.closeDialog()
    },
   
    deleteAlternative(alternative) {
      let idx = this.alternatives.indexOf(alternative)
      if (idx == -1) return
      this.alternatives.splice(idx, 1)
    },
    
  },

}
</script>
