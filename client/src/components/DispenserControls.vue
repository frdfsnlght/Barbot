<template>

  <v-card flat height="40vh">
  
    <v-layout column justify-space-between fill-height>
      <v-layout column justify-center fill-height class="text-xs-center pa-3">
  
        <div v-if="dispenserState == 'setup' || dispenserState == 'pause' || dispenserState == 'dispense'">
          <p class="display-1">
            Please wait...
          </p>
        </div>
        
        <div v-else-if="dispenserState == 'hold'">
          <p class="display-1">
            Drink orders are on hold
          </p>
          <div>
            <v-btn
              color="primary"
              fab
              large
              icon
              @click="toggleDispenserHold()"
            >
              <v-icon>mdi-play</v-icon>
            </v-btn>
          </div>
        </div>
        
        <div v-else-if="dispenserState == 'wait'">
          <p class="display-1">
            Waiting for a drink order
          </p>
          <div>
            <v-btn
              color="primary"
              fab
              large
              icon
              @click="toggleDispenserHold()"
            >
              <v-icon>mdi-pause</v-icon>
            </v-btn>
          </div>
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
            <p :class="'subheading ' + (dispenserGlass ? '' : 'red--text')">
              Insert a {{dispenserDrinkOrder.drink.glass.name}} glass.
              <v-icon v-if="dispenserGlass" class="green--text">mdi-check</v-icon>
            </p>
            <v-btn
              color="green"
              large
              class="px-5"
              :loading="!dispenserGlass"
              :disabled="!dispenserGlass || clicked"
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
        <div class="text-xs-center py-3">
            <span
              v-for="p in pumps"
              :key="p.id"
            >
              <pump-icon :pump="p"/>
            </span>
        </div>
      </v-flex>
        
    </v-layout>
  </v-card>
    
</template>

<script>

import { mapState, mapGetters } from 'vuex'
import Confirm from './Confirm'
import PumpIcon from './PumpIcon'


export default {
  name: 'DispenserControls',
  data() {
    return {
      clicked: false,
    }
  },
  
  components: {
    Confirm,
    PumpIcon,
  },
  
  computed: {
    ...mapGetters({
      pumps: 'pumps/sortedItems',
    }),
    ...mapState([
      'isConsole',
    ]),
    ...mapState({
      dispenserState: state => state.dispenser.state,
      dispenserDrinkOrder: state => state.dispenser.drinkOrder,
      dispenserGlass: state => state.dispenser.glass,
    }),
  },
  
  watch: {
    dispenserState: function() {
      this.clicked = false
    },
  },
  
  methods: {
  
    dispenserControl(ctl) {
      this.clicked = true
      this.$socket.emit('dispenser_setControl', ctl, (res) => {
        if (res.error) {
            this.$store.commit('setError', res.error)
        }
        this.clicked = false
      })
    },
  
    toggleDispenserHold() {
      if (this.dispenserState == 'hold') {
        this.$socket.emit('dispenser_stopHold', (res) => {
            if (res.error) {
                this.$store.commit('setError', res.error)
            }
        })
      } else {
        this.$socket.emit('dispenser_startHold', (res) => {
            if (res.error) {
                this.$store.commit('setError', res.error)
            }
        })
      }
    },
  
  },

}
</script>
