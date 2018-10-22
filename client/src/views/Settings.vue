<template>

  <v-card flat>
    
    <v-list two-line>
    
      <v-list-tile
        avatar
        ripple
        @click="gotoWifi()"
      >
        <v-list-tile-avatar>
          <v-icon v-if="!wifiState">mdi-wifi-off</v-icon>
          <v-icon v-else-if="!wifiState.ssid">mdi-wifi-off</v-icon>
          <v-icon v-else-if="wifiState.bars === 0">mdi-wifi-strength-outline</v-icon>
          <v-icon v-else-if="wifiState.bars === 1">mdi-wifi-strength-1</v-icon>
          <v-icon v-else-if="wifiState.bars === 2">mdi-wifi-strength-2</v-icon>
          <v-icon v-else-if="wifiState.bars === 3">mdi-wifi-strength-3</v-icon>
          <v-icon v-else-if="wifiState.bars === 4">mdi-wifi-strength-4</v-icon>
        </v-list-tile-avatar>
        <v-list-tile-content>
          <v-list-tile-title>WiFi</v-list-tile-title>
          <v-list-tile-sub-title v-if="!wifiState">Not available</v-list-tile-sub-title>
          <v-list-tile-sub-title v-else-if="!wifiState.ssid">Not connected</v-list-tile-sub-title>
          <v-list-tile-sub-title v-else>Connected to {{wifiState.ssid}}</v-list-tile-sub-title>
        </v-list-tile-content>
      </v-list-tile>
      
      <v-list-tile
        avatar
        ripple
        @click="setParentalLock()"
      >
        <v-list-tile-avatar>
          <v-icon>mdi-lock</v-icon>
        </v-list-tile-avatar>
        <v-list-tile-content>
          <v-list-tile-title>Parental lock</v-list-tile-title>
          <v-list-tile-sub-title v-if="parentalLock">Active</v-list-tile-sub-title>
          <v-list-tile-sub-title v-else>Disabled</v-list-tile-sub-title>
        </v-list-tile-content>
        <v-list-tile-action>
          <v-switch v-model="parentalLock" readonly></v-switch>
        </v-list-tile-action>
      </v-list-tile>
      
    </v-list>

    <parental-code ref="parentalCode"></parental-code>
    
  </v-card>
        
</template>

<script>

import { mapState } from 'vuex'
import store from '../store/store'
import bus from '../bus'
import ParentalCode from '../components/ParentalCode'

export default {
  name: 'Settings',
  data() {
    return {
    }
  },
  
  components: {
    ParentalCode
  },
  
  created() {
    this.$emit('show-page', 'Settings')
    bus.$on('logout', this.onLogout)
  },
  
  beforeDestroy: function () {
    bus.$off('logout', this.onLogout)
  },
  
  computed: {
    ...mapState({
      wifiState: state => state.wifi.state,
      parentalLock: state => state.parentalLock,
    })
  },
  
  methods: {
  
    gotoWifi() {
      this.$router.push({name: 'settings/wifi'})
    },
  
    setParentalLock() {
      if (this.parentalLock) {
        this.$socket.emit('setParentalLock', false, (res) => {
          if (res.error)
            this.$store.commit('setError', res.error)          
        })
      } else {
        this.$refs.parentalCode.open()
      }
    },
  
    onLogout() {
      if (! ((store.state.options.settingsRequiresAdmin == false) || store.state.user.isAdmin))
        this.$router.replace({name: 'home'})
    },
    
  },
  
  beforeRouteEnter(to, from, next) {
    if (! ((store.state.options.settingsRequiresAdmin == false) || store.state.user.isAdmin))
      next({name: 'home'})
    else
      next(true)
  },
  
}

</script>
