<template>

  <v-dialog v-model="dialog" persistent scrollable max-width="480px" @keydown.esc="cancel" @keydown.enter.prevent="submit">
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
                  v-model="drink.primaryName"
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
                  v-model="drink.secondaryName"
                  hint="This is not required but can help distinguish similar drinks"
                  :data-kbUCWords="true"
                  tabindex="2"
                  ></v-text-field>
              </v-flex>
              
              <v-flex xs12>
                <v-checkbox
                  label="Is this drink a favorite?"
                  v-model="drink.isFavorite"
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
                  v-model="drink.glass_id"
                  :rules="[v => !!v || 'Glass is required']"
                  required
                  tabindex="4"
                ></v-select>
              </v-flex>

              <v-flex xs12>
                <drink-ingredients
                  title="Ingredients"
                  v-model="drink.ingredients"></drink-ingredients>
              </v-flex>
              
              <v-flex xs12>
                <v-textarea
                  label="Instructions"
                  auto-grow
                  v-model="drink.instructions"
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

import { mapGetters } from 'vuex'
import DrinkIngredients from './DrinkIngredients'
import bus from '../bus'

export default {
  name: 'OrderDrinkDialog',
  
  data() {
    return {
      valid: true,
      resolve: undefined,
      reject: undefined,
      dialog: false,
      drink: {},
      edit: false,
    }
  },
  
  components: {
    DrinkIngredients,
  },
  
  computed: {
    ...mapGetters({
      glasses: 'glasses/sortedGlasses',
    }),
  },
  
  methods: {

    open(drink, edit = false) {
      this.$store.dispatch('glasses/getAll')
      bus.$emit('keyboard-install', this.$refs.form)
      this.$refs.form.reset()
      this.edit = edit
      this.drink = drink
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
      if ((! this.drink.ingredients) || (this.drink.ingredients.length == 0)) {
        this.$store.commit('setError', 'At least one ingredient is required!')
        return
      }
      this.$socket.emit('drink_save', this.drink, (res) => {
        if (res.error) {
          this.$store.commit('setError', res.error)
        } else {
          this.close()
          this.resolve()
        }
      })
    },
    
    cancel() {
      this.reject()
      this.close()
    },
    
  },
  
  destroy() {
    this.$store.commit('glasses/destroy')
  },
  
}

</script>
