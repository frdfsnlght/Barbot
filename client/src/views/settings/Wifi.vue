<template>

  <v-card flat>
    
    <v-list two-line>
      
      <v-list-tile
        avatar
        ripple
        @click="addNetwork()"
      >
        <v-list-tile-avatar>
          <v-icon>mdi-plus</v-icon>
        </v-list-tile-avatar>
        <v-list-tile-content>
          <v-list-tile-title>Add network</v-list-tile-title>
        </v-list-tile-content>
      </v-list-tile>
      
      <template v-if="!networksLoading">
      
        <v-list-tile
          avatar
          ripple
          @click="refreshNetworks()"
        >
          <v-list-tile-avatar>
            <v-icon>mdi-refresh</v-icon>
          </v-list-tile-avatar>
          <v-list-tile-content>
            <v-list-tile-title>Refresh</v-list-tile-title>
            <v-list-tile-sub-title
              v-if="!networks.length && !wifiState.ssid">No networks found</v-list-tile-sub-title>
          </v-list-tile-content>
        </v-list-tile>
      
      <v-divider></v-divider>
      
        <v-list-tile
          v-for="net in networks"
          :key="net.ssid"
          avatar
          ripple
          @click="selectNetwork(net)"
        >
          <v-list-tile-avatar>
            <v-icon v-if="net.bars === 0">mdi-wifi-strength-outline</v-icon>
            <v-icon v-else-if="net.bars === 1">mdi-wifi-strength-1</v-icon>
            <v-icon v-else-if="net.bars === 2">mdi-wifi-strength-2</v-icon>
            <v-icon v-else-if="net.bars === 3">mdi-wifi-strength-3</v-icon>
            <v-icon v-else-if="net.bars === 4">mdi-wifi-strength-4</v-icon>
          </v-list-tile-avatar>
          <v-list-tile-content>
            <v-list-tile-title>{{net.ssid}}</v-list-tile-title>
            <v-list-tile-sub-title>{{networkSubtitle(net)}}</v-list-tile-sub-title>
          </v-list-tile-content>
          <v-list-tile-action>
            <v-icon v-if="net.secured">mdi-lock</v-icon>
          </v-list-tile-action>
        </v-list-tile>
      
      </template>
      
    </v-list>
    
    <v-dialog v-model="connectDialog" persistent scrollable max-width="400px" @keydown.esc="connectDialog = false">
      <v-card>
        <v-card-title>
          <span v-if="!network.scanned" class="headline">Add Network</span>
          <span v-else class="headline">{{network.ssid}}</span>
        </v-card-title>
        <v-card-text>
          <v-form ref="connectForm" v-model="valid" lazy-validation>
            <v-container grid-list-md>
              <v-layout wrap>
              
                <template v-if="!network.scanned">
                  <v-flex xs12>
                    <v-text-field
                      label="Network name"
                      v-model="network.ssid"
                      hint="Enter the SSID"
                      :rules="[v => !!v || 'Network name is required']"
                      required
                      autofocus
                    ></v-text-field>
                  </v-flex>
                  
                  <v-select
                    :items="['None', 'WEP', 'WPA/WPA2 PSK']"
                    label="Security"
                    v-model="network.security"
                    required
                    :rules="[v => !!v || 'Security is required']"
                  ></v-select>
                </template>
                
                <v-text-field
                  v-show="network.security != 'None'"
                  label="Password"
                  v-model="network.password"
                  :append-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                  :type="showPassword ? 'text' : 'password'"
                  required
                  autofocus
                  @click:append="showPassword = !showPassword"
                  :rules="[v => network.security == 'None' || !!v || 'Password is required']"
                ></v-text-field>

              </v-layout>
            </v-container>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            flat
            @click="connectDialog = false">cancel</v-btn>
          <v-btn
            v-show="network.saved"
            flat
            @click="forgetNetwork()">forget</v-btn>
          <v-btn
            :disabled="!valid"
            flat
            @click="connectToNetwork()">{{network.scanned ? 'connect' : 'save'}}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="disconnectDialog" max-width="400px" @keydown.esc="disconnectDialog = false">
      <v-card>
        <v-toolbar dark color="primary" dense flat>
          <v-toolbar-title class="white--text">{{network.ssid}}</v-toolbar-title>
        </v-toolbar>
        <v-card-text>Disconnect from this network?</v-card-text>
        <v-card-actions class="pt-0">
          <v-spacer></v-spacer>
          <v-btn flat @click="disconnectDialog = false">cancel</v-btn>
          <v-btn flat @click="forgetNetwork()">forget</v-btn>
          <v-btn flat @click="disconnectFromNetwork()">disconnect</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <loading v-if="networksLoading"></loading>
    <confirm ref="confirm"></confirm>

  </v-card>
        
</template>

<script>

import { mapState, mapGetters } from 'vuex'
import Loading from '../../components/Loading'
import Confirm from '../../components/Confirm'
import store from '../../store/store'
import bus from '../../bus'

export default {
  name: 'Wifi',
  data() {
    return {
      valid: true,
      network: {
        ssid: undefined,
        security: undefined,
        password: undefined,
        scanned: undefined,
      },
      showPassword: false,
      connectDialog: false,
      disconnectDialog: false,
    }
  },
  
  components: {
    Loading,
    Confirm,
  },
  
  created() {
    this.$emit('show-page', 'Wifi')
    bus.$on('logout', this.onLogout)
  },
  
  beforeDestroy: function () {
    bus.$off('logout', this.onLogout)
  },
  
  computed: {
    ...mapGetters({
      networks: 'wifi/sortedNetworks',
    }),
    ...mapState({
      networksLoading: state => state.wifi.networksLoading,
      wifiState: state => state.wifi.state,
    })
  },
  
  methods: {
    
    networkSubtitle(net) {
      let out = []
      if (net.connected) out.push('Connected')
      if (net.saved) out.push('Saved')
      if (net.auth) out.push(...net.auth)
      return out.join(', ')    
    },
    
    addNetwork() {
      this.$refs.connectForm.reset()
      this.network.ssid = undefined
      this.network.security = 'None'
      this.network.password = undefined
      this.network.scanned = false
      this.connectDialog = true
    },
    
    selectNetwork(network) {
      if (network.connected) {
        this.network.ssid = network.ssid
        this.disconnectDialog = true
        
      } else if (network.scanned) {
        this.$refs.connectForm.reset()
        this.network.ssid = network.ssid
        this.network.password = undefined
        this.network.scanned = true
        this.network.saved = network.saved
        
        if (network.secured) {
          this.network.security = 'not none'
          this.connectDialog = true
        } else {
          this.network.security = 'None'
          this.connectToNetwork()
        }
        
      } else if (network.saved) {
        this.network.ssid = network.ssid
        this.forgetNetwork()
      }
    },

    forgetNetwork() {
      this.$refs.confirm.open(this.network.ssid, 'Forget this network?').then(() => {
        this.$socket.emit('forgetWifiNetwork', this.network.ssid, (res) => {
          if (res.error) {
              this.$store.commit('setError', res.error)
          } else {
            this.refreshNetworks()
            this.connectDialog = false
            this.disconnectDialog = false
          }
        })
      })
    },
    
    connectToNetwork() {
      if (! this.$refs.connectForm.validate()) return
      let params = {
        ssid: this.network.ssid,
      }
      if (this.network.security != 'None')
        params['password'] = this.network.password
      this.$socket.emit('connectToWifiNetwork', params, (res) => {
        if (res.error) {
            this.$store.commit('setError', res.error)
        } else {
          this.connectDialog = false
          this.refreshNetworks()
        }
      })
    },
    
    disconnectFromNetwork() {
      this.$socket.emit('disconnectFromWifiNetwork', this.network.ssid, (res) => {
        if (res.error) {
            this.$store.commit('setError', res.error)
        } else {
          this.disconnectDialog = false
          this.refreshNetworks()
        }
      })
    },
    
    refreshNetworks() {
      this.$store.dispatch('wifi/loadNetworks')
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
      next(t => {
        t.refreshNetworks()
      })
  },
  
  beforeRouteLeave(to, from, next) {
    this.$store.commit('wifi/destroyNetworks')
    next()
  },
  
}

</script>
