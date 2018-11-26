<template>

  <v-card flat>

    <p v-if="!dispenserGlassReady" class="headline red--text text-xs-center ma-3">
      Place a glass in the dispensing area.
    </p>
    
    <div class="text-xs-center pa-3">
      <v-btn
        v-for="pump in pumps"
        :key="pump.id"
        ripple
        large
        block
        :disabled="!dispenserGlassReady"
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
    }),
    ...mapState({
      isConsole: state => state.isConsole,
      dispenserGlassReady: state => state.dispenser.glassReady,
    })
  },
  
  methods: {
    
    startPump(id) {
      if (this.dispensingId != id) {
        if (this.dispensingId != null)
          this.stopDispense(this.dispensingId)
        console.log('start pump: ' + id)
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
        console.log('stop pump: ' + this.dispensingId)
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
      console.dir(pump);
    }
  },  
  
}

</script>
