<template>

  <v-container fluid fill-height pa-0>
    <v-layout column justify-start fill-height>
    
      <v-flex>
        <dispenser-controls ref="dispenserControls"></dispenser-controls>
      </v-flex>
      
      <v-flex fill-height>
        <drink-orders></drink-orders>
      </v-flex>
      
    </v-layout>
      
  </v-container>
  
</template>

<script>

import { mapState } from 'vuex'

import DispenserControls from '../components/DispenserControls'
import DrinkOrders from '../components/DrinkOrders'

export default {
  name: 'Home',
  data() {
    return {}
  },
  
  components: {
    DispenserControls,
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
      dispenserState: state => state.dispenser.state,
    }),
  },
  
  beforeRouteEnter(to, from, next) {
    next(t => {
      if (t.isConsole && t.dispenserState == 'setup') {
        t.$socket.emit('dispenser_stopSetup', (res) => {
          if (res.error) {
            t.$store.commit('setError', res.error)
          }
        })
      }
      if (t.isConsole && t.dispenserState == 'manual') {
        t.$socket.emit('dispenser_stopManual', (res) => {
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
