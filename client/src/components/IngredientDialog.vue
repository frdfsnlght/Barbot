<template>

  <v-dialog v-model="dialog" persistent scrollable @keydown.esc="cancel" @keydown.enter.prevent="submit">
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

              <v-flex xs12>
                <ingredient-alternatives
                  title="Alternatives"
                  :ingredient="ingredient"
                  v-model="ingredient.alternatives"></ingredient-alternatives>
              </v-flex>
              
            </v-layout>
          </v-container>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn
          flat
          @click="cancel()">close</v-btn>
        <v-btn
          :disabled="!valid"
          flat
          @click="submit()">save</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

</template>

<script>

import IngredientAlternatives from './IngredientAlternatives'
import bus from '../bus'

export default {
  name: 'IngredientDialog',
  
  data() {
    return {
      valid: true,
      resolve: undefined,
      reject: undefined,
      dialog: false,
      ingredient: {},
      edit: false,
    }
  },
  
  components: {
    IngredientAlternatives,
  },
  
  methods: {

    open(ingredient, edit = false) {
      bus.$emit('keyboard-install', this.$refs.form)
      this.edit = edit
      this.ingredient = ingredient
      this.dialog = true
      return new Promise((resolve, reject) => {
        this.resolve = resolve
        this.reject = reject
      })
    },
    
    close() {
      this.dialog = false
      bus.$emit('keyboard-remove', this.$refs.form)
    },
    
    submit() {
      if (! this.$refs.form.validate()) return
      
      this.$socket.emit('ingredient_save', this.ingredient, (res) => {
        if (res.error) {
          this.$store.commit('setError', res.error)
        } else {
          this.close()
          this.resolve()
        }
      })
    },
    
    cancel() {
      this.close()
      this.reject()
    },
    
  },
  
}

</script>
