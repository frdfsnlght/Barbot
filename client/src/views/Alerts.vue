<template>

  <v-card flat style="height: 92.5vh; overflow-y: auto;">
    <div class="pa-3">
    
      <p
        v-if="!alerts.length"
        class="title text-xs-center"
      >
        No alerts.
      </p>
    
      <div v-else>
        <p
          class="subheading"
          v-for="alert in alerts"
          :key="alert"
        >{{alert}}</p>
      </div>
    
    </div>
    
    <v-btn
      fab
      fixed
      bottom right
      color="primary"
      @click="clearAlerts"
    >
      <v-icon dark>mdi-close</v-icon>
    </v-btn>
    
    <confirm-dialog ref="confirmDialog"/>
      
  </v-card>
        
</template>

<script>

import { mapState } from 'vuex'
import ConfirmDialog from '../components/ConfirmDialog'

export default {
  name: 'Alerts',
  data() {
    return {
    }
  },
  
  components: {
    ConfirmDialog,
  },
  
  created() {
    this.$emit('show-page', 'Alerts')
  },
  
  computed: {
    ...mapState({
      alerts: state => state.alerts.alerts,
    }),
  },
  
  methods: {
  
    clearAlerts() {
      this.$refs.confirmDialog.open('Clear', 'Are you sure you want to clear all the alerts?').then(() => {
        this.$socket.emit('alerts_clear', (res) => {
          if (res.error) {
            this.$store.commit('setError', res.error)
          } else {
            this.$router.go(-1)
          }
        })
      }, ()=>{})
    },
    
  },
  
}

</script>
