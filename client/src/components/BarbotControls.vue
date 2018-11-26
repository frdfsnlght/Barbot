<template>

  <v-card flat height="40vh">
  
    <v-layout column justify-space-between fill-height>
      <v-layout column justify-center fill-height class="text-xs-center pa-3">
  
        <div v-if="pumpsSetup || dispenserState == 'pause' || dispenserState == 'dispense'">
          <p class="display-1">
            Please wait...
          </p>
        </div>
        
        <div v-else-if="dispenserState == 'hold'">
          <p class="display-1">
            Drink orders are on hold
          </p>
        </div>
        
        <div v-else-if="dispenserState == 'wait'">
          <p class="display-1">
            Waiting for a drink order
          </p>
          <v-btn
            v-if="isConsole && anyPumpReady"
            color="primary"
            large
            class="px-5"
            @click="gotoMakeMyOwn()"
          >
            make my own
          </v-btn>
        </div>
        
        <div v-if="dispenserDrinkOrder" class="mb-3">
          <p class="headline mb-0">
            {{dispenserDrinkOrder.drink.primaryName}}
          </p>
          <p v-if="dispenserDrinkOrder.drink.secondaryName" class="subheading mb-0">
            {{dispenserDrinkOrder.drink.secondaryName}}
          </p>
          <p v-if="dispenserDrinkOrder.name" class="title mt-1 mb-0">
            For {{dispenserDrinkOrder.name}}
          </p>
        </div>
        
        <template v-if="isConsole">
        
          <div v-if="dispenserState == 'start'">
            <p :class="'subheading ' + (dispenserGlassReady ? '' : 'red--text')">
              Insert a {{dispenserDrinkOrder.drink.glass.name}} glass.
              <v-icon v-if="dispenserGlassReady" class="green--text">mdi-check</v-icon>
            </p>
            <v-btn
              color="green"
              large
              class="px-5"
              :loading="!dispenserGlassReady"
              :disabled="!dispenserGlassReady || clicked"
              @click="dispenserControl('start')"
            >
              start
              <span slot="loader">Waiting...</span>
            </v-btn>
            <v-btn
              color="red"
              large
              class="px-5"
              :disabled="clicked"
              @click="dispenserControl('cancel')"
            >
              cancel
            </v-btn>
          </div>

          <div v-if="dispenserState == 'run'">
            <p class="title">
              Dispensing...
            </p>
            <v-btn
              color="red"
              large
              class="px-5"
              :disabled="clicked"
              @click="dispenserControl('cancel')"
            >
              cancel
            </v-btn>
          </div>
          
          <div v-if="dispenserState == 'clear_glass'">
            <p class="title">
              The glass was removed.
            </p>
            <p class="title">
              The drink order has been put on hold.
            </p>
            <v-btn
              color="primary"
              large
              class="px-5"
              @click="dispenserControl('ok')"
            >
              ok
            </v-btn>
          </div>

          <div v-if="dispenserState == 'clear_cancel'">
            <p class="title">
              Dispensing was cancelled.
            </p>
            <p class="title">
              The drink order has been put on hold.
            </p>
            <p class="title">
              Please remove the glass.
            </p>
          </div>

          <div v-if="dispenserState == 'pickup'">
            <p class="title">
              Drink is complete.
            </p>
            <p class="title">
              Please remove the glass.
            </p>
          </div>
          
        </template>
        
        <template v-else>

          <div v-if="dispenserState == 'run' || dispenserState == 'dispense'">
            <p class="title">
              Dispensing...
            </p>
          </div>
        
          <div v-if="dispenserState == 'pickup'">
            <p class="title">
              Drink is complete.
            </p>
          </div>
        
        </template>
        
      </v-layout>

      <v-flex>
          <v-card flat class="text-xs-center py-3">
              <span
                v-for="p in pumps"
                :key="p.id"
              >
                <v-icon v-if="p.running" class="green--text">mdi-refresh</v-icon>
                <v-icon v-else-if="!p.state">mdi-close-circle-outline</v-icon>
                <v-icon v-else-if="p.state=='loaded'">mdi-close-circle-outline</v-icon>
                <v-icon v-else-if="p.state=='ready'">mdi-circle-outline</v-icon>
                <v-icon v-else-if="p.state=='empty'" class="red--text">mdi-alert-circle-outline</v-icon>
                <v-icon v-else-if="p.state=='dirty'">mdi-close-circle-outline</v-icon>
              </span>
          </v-card>
      </v-flex>
        
    </v-layout>
  </v-card>
    
</template>

<script>

import { mapState, mapGetters } from 'vuex'
import Confirm from './Confirm'


export default {
  name: 'BarbotControls',
  data() {
    return {
      clicked: false,
    }
  },
  
  components: {
    Confirm
  },
  
  computed: {
    ...mapGetters({
      pumps: 'pumps/sortedItems',
      anyPumpReady: 'pumps/anyPumpReady',
    }),
    ...mapState([
      'isConsole',
    ]),
    ...mapState({
      pumpsSetup: state => state.pumps.setup,
      dispenserState: state => state.dispenser.state,
      dispenserDrinkOrder: state => state.dispenser.drinkOrder,
      dispenserGlassReady: state => state.dispenser.glassReady,
    }),
  },
  
  watch: {
    dispenserState: function() {
      this.clicked = false
    },
  },
  
  methods: {
  
    dispenseControl(ctl) {
      this.clicked = true
      this.$socket.emit('dispenserControl', ctl, (res) => {
        if (res.error) {
            this.$store.commit('setError', res.error)
        }
        this.clicked = false
      })
    },
  
    gotoMakeMyOwn() {
      this.$router.push({name: 'makeMyOwn'})
    },
    
  },

}
</script>
