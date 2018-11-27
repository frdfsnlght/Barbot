<template>

  <v-card
    flat
    class="pa-3"
  >

    <p
      v-if="!dispenserGlassReady"
      class="headline red--text text-xs-center mb-3"
    >
      Place a glass in the dispensing area.
    </p>
    
    <p
      v-if="!pumps.length"
      class="headline text-xs-center mb-3"
    >
      There are no pumps ready.
    </p>
    
    <div
      class="text-xs-center"
    >
      <v-btn
        v-for="pump in pumps"
        :key="pump.id"
        ripple
        large
        block
        class="mb-3"
        :disabled="!dispenserGlassReady || (anyPumpRunning && dispensingId != pump.id)"
        @mousedown="startPump(pump.id)"
        @mouseup="stopPump()"
      >
        {{pump.ingredient.name}}
      </v-btn>
    </div>
    
  </v-card>
        
</template>

<script>

import { mapGetters, mapState } from 'vuex'

export default {
  name: 'MakeMyOwn',
  data() {
    return {
      dispensingId: null,
      captureId: null,
    }
  },
  
  components: {
  },
  
  created() {
    this.$emit('show-page', 'Make My Own')
  },
  
  computed: {
    ...mapGetters({
      pumps: 'pumps/sortedReadyPumps',
      anyPumpReady: 'pumps/anyPumpReady',
      anyPumpRunning: 'pumps/anyPumpRunning',
    }),
    ...mapState({
      isConsole: state => state.isConsole,
      dispenserGlassReady: state => state.dispenser.glassReady,
    })
  },
  
  watch: {
  
    dispenserGlassReady(v) {
      if (v && this.dispensingId) {
        this.$socket.emit('dispenser_stopPump', (res) => {
          if (res.error) {
              this.$store.commit('setError', res.error)
          } else
            this.dispensingId = null
        })
      }
    },
    
  },
  
  methods: {
    
    startPump(id) {
      if (this.dispensingId != id) {
        if (this.dispensingId != null)
          this.stopDispense(this.dispensingId)
        this.$socket.emit('dispenser_startPump', id, (res) => {
          if (res.error) {
              this.$store.commit('setError', res.error)
          } else
            this.dispensingId = id
        })
      }
    },
    
    stopPump() {
      if (this.dispensingId != null) {
        this.captureId = this.dispensingId
        this.$socket.emit('dispenser_stopPump', (res) => {
          if (res.error) {
              this.$store.commit('setError', res.error)
          } else
            this.dispensingId = null
        })
       }
    },
    
  },
  
  beforeRouteEnter(to, from, next) {
    next(t => {
      if (t.isConsole) {
        t.$socket.emit('dispenser_startDispense', (res) => {
          if (res.error) {
            t.$store.commit('setError', res.error)
          }
        })
      }
    })
  },
  
  sockets: {
    pumpSaved(pump) {
      if (this.captureId && (this.captureId == pump.id)) {
        console.log('dispensed ' + pump.lastAmount + ' mL of ' + pump.ingredient.name)
        this.captureId = null
      }
    }
  },  
  
}

</script>
