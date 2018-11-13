<template>

  <v-dialog v-model="dialog" persistent scrollable max-width="480px" @keydown.esc="close" @keydown.enter.prevent="">
    <v-card>
      <v-card-title>
        <span class="headline">Flush Pumps</span>
      </v-card-title>
      
      <v-card-text>
      
        <v-container fluid>
          <v-layout column>
      
            <v-flex class="text-xs-center mb-3">
              <p class="red--text">Make sure the flushing tube is secured to the dispenser funnel!</p>
            </v-flex>
            
            <v-flex class="text-xs-center">
              <v-btn
                :color="flushing ? 'red' : 'green'"
                large
                class="px-5"
                :disabled="selectedIds.length == 0 && !flushing"
                :loading="selectedIds.length == 0 && !flushing"
                @click="toggleFlush()"
              >
                <span v-if="flushing">stop</span>
                <span v-else>start</span>
                <span slot="loader">Select Pumps...</span>
              </v-btn>
            </v-flex>
            
            <v-list dense>
            
              <v-list-tile
                v-for="(pump, idx) in pumps"
                :key="pump.id"
              >
                <v-list-tile-action>
                  <v-checkbox
                    :value="pump.id"
                    :key="pump.id"
                    :label="pump.name"
                    :disabled="flushing"
                    v-model="selected[idx]"
                  />
                </v-list-tile-action>
            
              </v-list-tile>
            </v-list>

          </v-layout>
        </v-container>
              
      </v-card-text>
      
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn
          flat
          :disabled="flushing"
          @click="close()">close</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

</template>

<script>

import { mapGetters, mapState } from 'vuex'

export default {
  name: 'PumpFlushDialog',
  
  data() {
    return {
      dialog: false,
      selected: [],
    }
  },
  
  computed: {
    selectedIds() {
      let ids = []
      for (let i = 0; i < this.pumps.length; i++) {
        if (this.selected[i])
          ids.push(this.pumps[i].id)
      }
      return ids
    },
    ...mapGetters({
      pumps: 'pumps/sortedFlushablePumps',
    }),
    ...mapState({
      flushing: state => state.pumps.flushing,
    }),
  },

  methods: {

    open() {
      this.dialog = true
    },
    
    close() {
      this.dialog = false
    },

    toggleFlush() {
      if (this.flushing) {
        this.$socket.emit('stopFlushingPumps', (res) => {
          if (res.error)
              this.$store.commit('setError', res.error)
        })
      } else {
        this.$socket.emit('startFlushingPumps', this.selectedIds, (res) => {
          if (res.error)
              this.$store.commit('setError', res.error)
        })
      }
    },

  },

  created() {
    this.selected = this.pumps.map(() => { return false })
  },
  
}

</script>
