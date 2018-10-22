<template>

  <v-dialog v-model="dialog" persistent scrollable max-width="480px">
    <v-card>
      <v-card-title>
        <span class="headline">Order Drink</span>
      </v-card-title>
      
      <v-card-text>
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
                ></v-text-field>
              </v-flex>
              
              <v-flex xs12>
                <v-checkbox
                  label="Submit the order on hold?"
                  v-model="order.userHold"
                  required
                ></v-checkbox>
              </v-flex>
              
              <v-flex xs12  v-if="drink.isAlcoholic && parentalLock">
                <v-text-field
                  label="Code"
                  v-model="order.parentalCode"
                  hint="You must enter the parental code to order an alcoholic drink"
                  :append-icon="showCode ? 'mdi-eye-off' : 'mdi-eye'"
                  :type="showCode ? 'text' : 'password'"
                  required
                  @click:append="showCode = !showCode"
                  :rules="[v => !!v || 'Code is required']"
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

export default {
  name: 'OrderDrink',
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
      parentalLock: state => state.parentalLock,
    })
  },
  
  methods: {

    open(drink) {
      this.$refs.form.reset()
      this.drink = drink
      this.order.drinkId = drink.id
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
    },
    
    submit() {
      if (! this.$refs.form.validate()) return
      this.$socket.emit('submitDrinkOrder', this.order, (res) => {
        if (res.error) {
          this.$store.commit('setError', res.error)
        } else {
          this.dialog = false
          this.resolve()
        }
      })
    },

    cancel() {
      this.reject()
      this.dialog = false
    },
    
  },
  
}

</script>
