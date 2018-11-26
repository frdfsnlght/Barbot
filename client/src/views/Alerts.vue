<template>

  <v-card flat>
    
    <template v-if="!alerts.length">
      <v-card flat>
        <v-card-text>
          <p class="text-xs-center">No alerts.</p>
        </v-card-text>
      </v-card>
    </template>
    
    <template v-else>

      <div class="py-3">
        <p
          class="px-3 subheading"
          v-for="alert in alerts"
          :key="alert"
        >{{alert}}</p>
      </div>
    </template>
    
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
      })
    },
    
  },
  
}

</script>
