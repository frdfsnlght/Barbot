<template>
  <v-dialog
    v-model="visible"
    persistent
    max-width="400"
    style="z-index: 800"
  >
    <v-card
      color="red"
    >
      <v-card-title>
        <span class="headline">Error</span>
      </v-card-title>
    
      <v-card-text>
        {{error}}
      </v-card-text>
      
      <v-card-actions>
        <v-spacer></v-spacer>
          <v-btn
            flat
            @click="clearError()">ok</v-btn>
      </v-card-actions>
      
    </v-card>
  </v-dialog>
</template>

<script>

import { mapState } from 'vuex'

export default {
  name: 'ErrorDialog',
  
  computed: {
    visible: {
      get() {
        return !! this.error
      },
      set() {}
    },
    ...mapState([
      'error'
    ]),
  },

  methods: {
    clearError() {
      this.$store.commit('clearError')
    },
  },
  
}

</script>
