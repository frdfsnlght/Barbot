<template>

  <v-dialog v-model="dialog" persistent scrollable>
    <v-card>
      <v-card-title>
        <span class="headline">Order Drink</span>
      </v-card-title>
      
      <v-card-text @keydown.esc="cancel" @keydown.enter.prevent="submit">
        <v-form ref="form" v-model="valid" lazy-validation>
          <v-container grid-list-md>
            <v-layout wrap>
            
              <v-flex xs12>
                <h2 class="pb-3">{{drink.name}}</h2>
              </v-flex>
            
              <v-flex xs12>
                <v-text-field
                  label="Name"
                  v-model="order.name"
                  autofocus
                  :data-kbUCWords="true"
                  tabindex="1"
                ></v-text-field>
              </v-flex>
              
              <v-flex xs12>
                <v-checkbox
                  label="Submit the order on hold?"
                  v-model="order.userHold"
                  required
                ></v-checkbox>
              </v-flex>
              
              <v-flex xs12  v-if="drink.isAlcoholic && parentalCode">
                <v-text-field
                  label="Code"
                  v-model="order.parentalCode"
                  hint="You must enter the parental code to order this drink"
                  :append-icon="showCode ? 'mdi-eye-off' : 'mdi-eye'"
                  :type="showCode ? 'text' : 'password'"
                  required
                  @click:append="showCode = !showCode"
                  :rules="[v => !!v || 'Code is required']"
                  tabindex="2"
                ></v-text-field>
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
          flat
          @click="submit()">order</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

</template>

<script>

import { mapState } from 'vuex'
import bus from '../bus'

export default {
  name: 'OrderDrinkDialog',
  data() {
    return {
      valid: true,
      resolve: undefined,
      reject: undefined,
      drink: {},
      order: {},
      dialog: false,
      showCode: false,
    }
  },
  
  computed: {
    ...mapState({
      parentalCode: state => state.settings.parentalCode,
    })
  },
  
  methods: {

    open(drink) {
      bus.$emit('keyboard-install', this.$refs.form)
      this.$refs.form.reset()
      this.drink = drink
      this.order.drink_id = drink.id
      this.order.userHold = false
      this.order.name = undefined
      this.order.parentalCode = undefined
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
      this.$socket.emit('drinkOrder_submit', this.order, (res) => {
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
  
}

</script>
