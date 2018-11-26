<template>

  <v-container fluid fill-height pa-0>
    <v-layout column justify-start fill-height color="pink">
    
      <v-flex>
        <barbot-controls ref="barbotControls"></barbot-controls>
      </v-flex>
      
      <v-flex fill-height>
        <drink-orders></drink-orders>
      </v-flex>
      
    </v-layout>
      
  </v-container>
</template>

<script>

import { mapState } from 'vuex'

import BarbotControls from '../components/BarbotControls'
import DrinkOrders from '../components/DrinkOrders'

export default {
  name: 'Home',
  data() {
    return {}
  },
  
  components: {
    BarbotControls,
    DrinkOrders
  },
  
  created() {
    this.$emit('show-page', false)
  },
  
  computed: {
    ...mapState([
        'isConsole',
    ]),
    ...mapState({
      pumpsSetup: state => state.pumps.setup,
      dispenserState: state => state.dispenser.state,
    }),
  },
  
  beforeRouteEnter(to, from, next) {
    next(t => {
      if (t.isConsole && t.pumpsSetup) {
        t.$socket.emit('core_stopPumpSetup', (res) => {
          if (res.error) {
            t.$store.commit('setError', res.error)
          }
        })
      }
      if (t.isConsole && t.dispenserState == 'dispense') {
        t.$socket.emit('dispenser_stopDispense', (res) => {
          if (res.error) {
            t.$store.commit('setError', res.error)
          }
        })
      }
    })
  },
  
  beforeRouteLeave(to, from, next) {
    next()
  }
  
}

</script>
