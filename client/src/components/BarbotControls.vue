<template>

  <v-card flat height="40vh">
  
    <v-layout column justify-space-between fill-height>
      <v-layout column justify-center fill-height class="text-xs-center pa-3">
  
        <div v-if="pumpSetup">
          <p class="display-1">
            Please wait...
          </p>
        </div>
        
        <div v-else-if="!dispenseState.state">
          <p class="display-1">
            Waiting for a drink order
          </p>
        </div>
        
        <div v-if="dispenseState.order" class="mb-3">
          <p class="headline mb-0">
            {{dispenseState.order.drink.primaryName}}
          </p>
          <p v-if="dispenseState.order.drink.secondaryName" class="subheading mb-0">
            {{dispenseState.order.drink.secondaryName}}
          </p>
          <p v-if="dispenseState.order.name" class="title mt-1 mb-0">
            For {{dispenseState.order.name}}
          </p>
        </div>
        
        <template v-if="isConsole">
        
          <div v-if="dispenseState.state == 'start'">
            <p :class="'subheading ' + (glassReady ? '' : 'red--text')">
              Insert a {{dispenseState.order.drink.glass.name}} glass.
              <v-icon v-if="glassReady" class="green--text">mdi-check</v-icon>
            </p>
            <v-btn
              color="green"
              large
              class="px-5"
              :loading="!glassReady"
              :disabled="!glassReady || clicked"
              @click="dispenseControl('start')"
            >
              start
              <span slot="loader">Waiting...</span>
            </v-btn>
            <v-btn
              color="red"
              large
              class="px-5"
              :disabled="clicked"
              @click="dispenseControl('cancel')"
            >
              cancel
            </v-btn>
          </div>

          <div v-if="dispenseState.state == 'dispense'">
            <p class="title">
              Dispensing...
            </p>
            <v-btn
              color="red"
              large
              class="px-5"
              :disabled="clicked"
              @click="dispenseControl('cancel')"
            >
              cancel
            </v-btn>
          </div>
          
          <div v-if="dispenseState.state == 'glassClear'">
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
              @click="dispenseControl('ok')"
            >
              ok
            </v-btn>
          </div>

          <div v-if="dispenseState.state == 'cancelClear'">
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

          <div v-if="dispenseState.state == 'pickup'">
            <p class="title">
              Drink is complete.
            </p>
            <p class="title">
              Please remove the glass.
            </p>
          </div>
          
        </template>
        
        <template v-else>

          <div v-if="dispenseState.state && dispenseState.state != 'pickup'">
            <p class="title">
              Dispensing...
            </p>
            <v-btn
              color="red"
              large
              class="px-5"
              :disabled="clicked"
              @click="dispenseControl('cancel')"
            >
              cancel
            </v-btn>
          </div>
        
          <div v-if="dispenseState.state == 'pickup'">
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
    }),
    ...mapState([
      'pumpSetup',
      'isConsole',
      'dispenseState',
      'glassReady',
    ])
  },
  
  watch: {
    dispenseState: function() {
      this.clicked = false
    },
  },
  
  methods: {
  
    dispenseControl(ctl) {
      this.clicked = true
      this.$socket.emit('dispenseControl', ctl, (res) => {
        if (res.error) {
            this.$store.commit('setError', res.error)
        }
        this.clicked = false
      })
    },
  
  },

}
</script>
