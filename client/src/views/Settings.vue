<template>

  <v-card flat style="height: 92.5vh; overflow-y: auto;">
    
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
        @click="setParentalCode()"
      >
        <v-list-tile-avatar>
          <v-icon v-if="settings.parentalCode">mdi-lock</v-icon>
          <v-icon v-else>mdi-lock-open</v-icon>
        </v-list-tile-avatar>
        <v-list-tile-content>
          <v-list-tile-title>Parental lock</v-list-tile-title>
          <v-list-tile-sub-title v-if="settings.parentalCode">Active</v-list-tile-sub-title>
          <v-list-tile-sub-title v-else>Disabled</v-list-tile-sub-title>
        </v-list-tile-content>
        <v-list-tile-action>
          <v-switch v-model="settings.parentalCode" readonly></v-switch>
        </v-list-tile-action>
      </v-list-tile>
      
      <v-list-tile
        avatar
        ripple
        @click="toggleSetting('enableLocalAudio')"
      >
        <v-list-tile-avatar>
          <v-icon v-if="settings.enableLocalAudio">mdi-lock</v-icon>
          <v-icon v-else>mdi-lock-open</v-icon>
        </v-list-tile-avatar>
        <v-list-tile-content>
          <v-list-tile-title>Local audio</v-list-tile-title>
          <v-list-tile-sub-title v-if="settings.enableLocalAudio">Active</v-list-tile-sub-title>
          <v-list-tile-sub-title v-else>Disabled</v-list-tile-sub-title>
        </v-list-tile-content>
        <v-list-tile-action>
          <v-switch v-model="settings.enableLocalAudio" readonly></v-switch>
        </v-list-tile-action>
      </v-list-tile>
      
      <v-list-tile
        avatar
        ripple
        @click="toggleSetting('enableRemoteAudio')"
      >
        <v-list-tile-avatar>
          <v-icon v-if="settings.enableRemoteAudio">mdi-lock</v-icon>
          <v-icon v-else>mdi-lock-open</v-icon>
        </v-list-tile-avatar>
        <v-list-tile-content>
          <v-list-tile-title>Remote audio</v-list-tile-title>
          <v-list-tile-sub-title v-if="settings.enableRemoteAudio">Active</v-list-tile-sub-title>
          <v-list-tile-sub-title v-else>Disabled</v-list-tile-sub-title>
        </v-list-tile-content>
        <v-list-tile-action>
          <v-switch v-model="settings.enableRemoteAudio" readonly></v-switch>
        </v-list-tile-action>
      </v-list-tile>
      
      <v-list-tile
        avatar
        ripple
        @click="toggleSetting('enableIdleAudio')"
      >
        <v-list-tile-avatar>
          <v-icon v-if="settings.enableIdleAudio">mdi-lock</v-icon>
          <v-icon v-else>mdi-lock-open</v-icon>
        </v-list-tile-avatar>
        <v-list-tile-content>
          <v-list-tile-title>Idle audio</v-list-tile-title>
          <v-list-tile-sub-title v-if="settings.enableIdleAudio">Active</v-list-tile-sub-title>
          <v-list-tile-sub-title v-else>Disabled</v-list-tile-sub-title>
        </v-list-tile-content>
        <v-list-tile-action>
          <v-switch v-model="settings.enableIdleAudio" readonly></v-switch>
        </v-list-tile-action>
      </v-list-tile>
      
      <v-list-tile
        avatar
        ripple
        @click="toggleSetting('restartRequiresAdmin')"
      >
        <v-list-tile-avatar>
          <v-icon v-if="settings.restartRequiresAdmin">mdi-lock</v-icon>
          <v-icon v-else>mdi-lock-open</v-icon>
        </v-list-tile-avatar>
        <v-list-tile-content>
          <v-list-tile-title>Restart requires admin</v-list-tile-title>
          <v-list-tile-sub-title v-if="settings.restartRequiresAdmin">Active</v-list-tile-sub-title>
          <v-list-tile-sub-title v-else>Disabled</v-list-tile-sub-title>
        </v-list-tile-content>
        <v-list-tile-action>
          <v-switch v-model="settings.restartRequiresAdmin" readonly></v-switch>
        </v-list-tile-action>
      </v-list-tile>
      
      <v-list-tile
        avatar
        ripple
        @click="toggleSetting('restartXRequiresAdmin')"
      >
        <v-list-tile-avatar>
          <v-icon v-if="settings.restartXRequiresAdmin">mdi-lock</v-icon>
          <v-icon v-else>mdi-lock-open</v-icon>
        </v-list-tile-avatar>
        <v-list-tile-content>
          <v-list-tile-title>Restart X requires admin</v-list-tile-title>
          <v-list-tile-sub-title v-if="settings.restartXRequiresAdmin">Active</v-list-tile-sub-title>
          <v-list-tile-sub-title v-else>Disabled</v-list-tile-sub-title>
        </v-list-tile-content>
        <v-list-tile-action>
          <v-switch v-model="settings.restartXRequiresAdmin" readonly></v-switch>
        </v-list-tile-action>
      </v-list-tile>
      
      <v-list-tile
        avatar
        ripple
        @click="toggleSetting('shutdownRequiresAdmin')"
      >
        <v-list-tile-avatar>
          <v-icon v-if="settings.shutdownRequiresAdmin">mdi-lock</v-icon>
          <v-icon v-else>mdi-lock-open</v-icon>
        </v-list-tile-avatar>
        <v-list-tile-content>
          <v-list-tile-title>Shutdown requires admin</v-list-tile-title>
          <v-list-tile-sub-title v-if="settings.shutdownRequiresAdmin">Active</v-list-tile-sub-title>
          <v-list-tile-sub-title v-else>Disabled</v-list-tile-sub-title>
        </v-list-tile-content>
        <v-list-tile-action>
          <v-switch v-model="settings.shutdownRequiresAdmin" readonly></v-switch>
        </v-list-tile-action>
      </v-list-tile>
      
      <v-list-tile
        avatar
        ripple
        @click="toggleSetting('settingsRequiresAdmin')"
      >
        <v-list-tile-avatar>
          <v-icon v-if="settings.settingsRequiresAdmin">mdi-lock</v-icon>
          <v-icon v-else>mdi-lock-open</v-icon>
        </v-list-tile-avatar>
        <v-list-tile-content>
          <v-list-tile-title>Settings requires admin</v-list-tile-title>
          <v-list-tile-sub-title v-if="settings.settingsRequiresAdmin">Active</v-list-tile-sub-title>
          <v-list-tile-sub-title v-else>Disabled</v-list-tile-sub-title>
        </v-list-tile-content>
        <v-list-tile-action>
          <v-switch v-model="settings.settingsRequiresAdmin" readonly></v-switch>
        </v-list-tile-action>
      </v-list-tile>
      
      <v-list-tile
        avatar
        ripple
        @click="toggleSetting('dispenserSetupRequiresAdmin')"
      >
        <v-list-tile-avatar>
          <v-icon v-if="settings.dispenserSetupRequiresAdmin">mdi-lock</v-icon>
          <v-icon v-else>mdi-lock-open</v-icon>
        </v-list-tile-avatar>
        <v-list-tile-content>
          <v-list-tile-title>Pump setup requires admin</v-list-tile-title>
          <v-list-tile-sub-title v-if="settings.dispenserSetupRequiresAdmin">Active</v-list-tile-sub-title>
          <v-list-tile-sub-title v-else>Disabled</v-list-tile-sub-title>
        </v-list-tile-content>
        <v-list-tile-action>
          <v-switch v-model="settings.dispenserSetupRequiresAdmin" readonly></v-switch>
        </v-list-tile-action>
      </v-list-tile>
      
    </v-list>

    <parental-code-dialog ref="parentalCodeDialog"/>
    
  </v-card>
        
</template>

<script>

import { mapState } from 'vuex'
import store from '../store/store'
import bus from '../bus'
import ParentalCodeDialog from '../components/ParentalCodeDialog'

export default {
  name: 'Settings',
  data() {
    return {
    }
  },
  
  components: {
    ParentalCodeDialog
  },
  
  created() {
    this.$emit('show-page', 'Settings')
    bus.$on('logout', this.onLogout)
  },
  
  beforeDestroy: function () {
    bus.$off('logout', this.onLogout)
  },
  
  computed: {
    ...mapState([
      'settings',
    ]),
    ...mapState({
      wifiState: state => state.wifi.state,
    })
  },
  
  methods: {
  
    gotoWifi() {
      this.$router.push({name: 'settings/wifi'})
    },
  
    setParentalCode() {
      if (this.settings.parentalCode) {
        this.$socket.emit('settings_set', {'key': 'parentalCode', 'value': ''}, (res) => {
          if (res.error)
            this.$store.commit('setError', res.error)
        })
      } else {
        this.$refs.parentalCodeDialog.open()
      }
    },
  
    toggleSetting(key) {
      this.$socket.emit('settings_set', {'key': key, 'value': !this.settings[key]}, (res) => {
        if (res.error)
          this.$store.commit('setError', res.error)
      })
    },
    
    onLogout() {
      if (! ((store.state.settings.settingsRequiresAdmin == false) || store.state.user.isAdmin))
        this.$router.replace({name: 'home'})
    },
    
  },
  
  beforeRouteEnter(to, from, next) {
    if (! ((store.state.settings.settingsRequiresAdmin == false) || store.state.user.isAdmin))
      next({name: 'home'})
    else
      next(true)
  },
  
}

</script>
