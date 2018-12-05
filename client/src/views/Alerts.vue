<template>

  <v-card
    flat
    class="ma-3"
  >
    
    <p
      v-if="!alerts.length"
      class="title text-xs-center"
    >
      No alerts.
    </p>
    
    <div
      v-else
    >
      <p
        class="subheading"
        v-for="alert in alerts"
        :key="alert"
      >{{alert}}</p>
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
    
    <confirm ref="confirm"></confirm>
      
  </v-card>
        
</template>

<script>

import { mapState } from 'vuex'
import Confirm from '../components/Confirm'

export default {
  name: 'Alerts',
  data() {
    return {
    }
  },
  
  components: {
    Confirm,
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
      this.$refs.confirm.open('Clear', 'Are you sure you want to clear all the alerts?').then(() => {
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
