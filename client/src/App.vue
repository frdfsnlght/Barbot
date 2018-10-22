<template>
  <v-app>
    <html-title :title="title"/>
    
    <v-navigation-drawer
      persistent
      clipped
      v-model="drawer"
      enable-resize-watcher
      fixed
      app
    >
      <v-list>
        <v-list-tile @click="gotoDrinks()">
          <v-list-tile-action>
            <v-icon>mdi-cup-water</v-icon>
          </v-list-tile-action>
          <v-list-tile-title>Drinks</v-list-tile-title>
        </v-list-tile>
      
        <v-list-tile @click="gotoIngredients()">
          <v-list-tile-action>
            <v-icon>mdi-cart</v-icon>
          </v-list-tile-action>
          <v-list-tile-title>Ingredients</v-list-tile-title>
        </v-list-tile>
      
        <v-list-tile @click="gotoGlasses()">
          <v-list-tile-action>
            <v-icon>mdi-glass-cocktail</v-icon>
          </v-list-tile-action>
          <v-list-tile-title>Glasses</v-list-tile-title>
        </v-list-tile>
      
        <v-list-tile @click="gotoPumps()">
          <v-list-tile-action>
            <v-icon>mdi-gas-station</v-icon>
          </v-list-tile-action>
          <v-list-tile-title>Pumps</v-list-tile-title>
        </v-list-tile>
      
        <v-divider/>
        
        <v-list-group
          prepend-icon="mdi-settings"
          no-action
        >
          <v-list-tile slot="activator">
            <v-list-tile-title>System</v-list-tile-title>
          </v-list-tile>

          <v-list-tile @click="gotoSettings()">
            <v-list-tile-title>Settings</v-list-tile-title>
            <v-list-tile-action>
              <v-icon>mdi-settings</v-icon>
            </v-list-tile-action>
          </v-list-tile>

          <v-list-tile @click="checkRestart()">
            <v-list-tile-title>Restart</v-list-tile-title>
            <v-list-tile-action>
              <v-icon>mdi-restart</v-icon>
            </v-list-tile-action>
          </v-list-tile>

          <v-list-tile @click="checkShutdown()">
            <v-list-tile-title>Shutdown</v-list-tile-title>
            <v-list-tile-action>
              <v-icon>mdi-power</v-icon>
            </v-list-tile-action>
          </v-list-tile>
        </v-list-group>
        
      </v-list>
    </v-navigation-drawer>
    
    <v-toolbar
      app
      clipped-left
      color="primary"
      dark
    >
      <v-toolbar-side-icon
        v-if="!showBack"
        @click.stop="drawer = !drawer"
      ></v-toolbar-side-icon>
      
      <v-btn
        v-if="showBack"
        icon
        @click="goBack()">
        <v-icon>mdi-arrow-left</v-icon>
      </v-btn>      
      
      <v-toolbar-title>{{title}}</v-toolbar-title>
      <v-spacer></v-spacer>

      <template v-if="isConsole && wifiState">
        <v-icon v-if="!wifiState.ssid">mdi-wifi-off</v-icon>
        <v-icon v-else-if="wifiState.bars === 0">mdi-wifi-strength-outline</v-icon>
        <v-icon v-else-if="wifiState.bars === 1">mdi-wifi-strength-1</v-icon>
        <v-icon v-else-if="wifiState.bars === 2">mdi-wifi-strength-2</v-icon>
        <v-icon v-else-if="wifiState.bars === 3">mdi-wifi-strength-3</v-icon>
        <v-icon v-else-if="wifiState.bars === 4">mdi-wifi-strength-4</v-icon>
      </template>

      <v-menu
        v-if="isConsole"
        bottom left
        offset-y
        :close-on-content-click="false"
      >
        <v-btn
          slot="activator"
          dark
          icon
        >
          <v-icon v-if="volume < 0.33">mdi-volume-low</v-icon>
          <v-icon v-else-if="volume >= 0.33 && volume < 0.66">mdi-volume-medium</v-icon>
          <v-icon v-else>mdi-volume-high</v-icon>
        </v-btn>
        <v-list>
          <v-list-tile>
            <v-slider
              v-model="volume"
              min="0"
              max="1"
              step="0.05"
              prepend-icon="mdi-minus"              
              append-icon="mdi-plus"
              @end="changeVolume"
            ></v-slider>
          </v-list-tile>
        </v-list>
      </v-menu>
          
      <v-btn v-if="user.name" icon @click="logout()">
        <v-icon>mdi-logout</v-icon>
      </v-btn>
      
    </v-toolbar>
    
    <v-content>
      <router-view
        @show-page="showPage"/>
    </v-content>
    
    <v-dialog
      v-model="connectingDialog"
      persistent
      max-width="400"
    >
      <v-card
        color="primary"
        dark
      >
        <v-card-text>
          Attempting to connect...
          <v-progress-linear
            indeterminate
            color="white"
            class="mb-0"
          ></v-progress-linear>
        </v-card-text>
      </v-card>
    </v-dialog>
    
    <v-dialog
      v-model="error"
      persistent
      max-width="400"
    >
      <v-card
        color="red"
      >
        <v-card-title>
          <span class="headline">Error</span>
        </v-card-title>
      
        <v-card-text>
          {{errorMsg}}
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
            <v-btn
              flat
              @click="clearError()">ok</v-btn>
        </v-card-actions>
        
      </v-card>
    </v-dialog>
    
    <confirm ref="confirm"></confirm>
    <login ref="login"></login>
    <audio-player ref="audioPlayer"></audio-player>
    
    <v-snackbar
      v-model="snackbar"
      :color="snackbarColor"
      :timeout="4000"
    >
      {{ snackbarText }}
      <v-btn
        dark
        flat
        @click="snackbar = false"
      >
        Close
      </v-btn>
    </v-snackbar>
    
  </v-app>
</template>

<script>

import { mapState } from 'vuex'
import bus from './bus'
import HTMLTitle from './components/HTMLTitle'
import Confirm from './components/Confirm'
import Login from './components/Login'
import AudioPlayer from './components/AudioPlayer'

export default {
  name: 'App',
  data () {
    return {
      pageTitle: false,
      drawer: false,
      showBack: false,
    }
  },
  
  components: {
    'html-title': HTMLTitle,
    Confirm,
    Login,
    AudioPlayer,
  },
  
  computed: {
    title () {
      return this.options.appTitle + (this.pageTitle ? (": " + this.pageTitle) : "");
    },
    connectingDialog() {
      return !this.$store.state.connected
    },
    snackbar: {
      get: function() {
        return this.$store.state.snackbar
      },
      set: function(newValue) {
        this.$store.commit('setSnackbar', newValue)
      },
    },
    volume: {
      get: function() {
        return this.$store.state.volume
      },
      set: function() {
        // nop
      },
    },
    ...mapState([
      'options',
      'isConsole',
      'error',
      'errorMsg',
      'snackbarColor',
      'snackbarText',
      'user',
    ]),
    ...mapState({
      wifiState: state => state.wifi.state
    }),
  },
  
  methods: {
  
    goBack() {
      window.history.length > 1
        ? this.$router.go(-1)
        : this.$router.push('/')
    },
    
    gotoDrinks() {
      this.drawer = false
      this.$router.push({name: 'drinks'})
    },
    
    gotoIngredients() {
      this.drawer = false
      this.$router.push({name: 'ingredients'})
    },
    
    gotoGlasses() {
      this.drawer = false
      this.$router.push({name: 'glasses'})
    },
    
    gotoPumps() {
      this.drawer = false
      this.checkAdmin('pumpSetupRequiresAdmin').then(() => {
        this.$router.push({name: 'pumps'})
      })
    },
    
    gotoSettings() {
      this.drawer = false
      this.checkAdmin('settingsRequiresAdmin').then(() => {
        this.$router.push({name: 'settings'})
      })
    },

    checkRestart() {
      this.drawer = false
      this.checkAdmin('restartRequiresAdmin').then(this.restart)
    },

    checkShutdown() {
      this.drawer = false
      this.checkAdmin('shutdownRequiresAdmin').then(this.shutdown)
    },

    restart() {
      this.$refs.confirm.open('Restart', 'Are you sure you want to restart the system?').then(() => {
        this.$socket.emit('restart', (res) => {
          if (res.error) {
              this.$store.commit('setError', res.error)
          }
        })
      })
    },
    
    shutdown() {
      this.$refs.confirm.open('Shutdown', 'Are you sure you want to shutdown the system?').then(() => {
        this.$socket.emit('shutdown', (res) => {
          if (res.error) {
              this.$store.commit('setError', res.error)
          }
        })
      })
    },
    
    logout() {
      this.$refs.login.logout().then(() => {
        bus.$emit('logout')
      })
    },
    
    showPage(pageTitle) {
      this.pageTitle = pageTitle
      this.showBack = !!pageTitle
    },
    
    clearError() {
      this.$store.commit('clearError')
    },
    
    changeVolume: function(v) {
      this.$refs.audioPlayer.setVolume(v)
    },
    
    checkAdmin(opt) {
      if ((! this.$store.state.options[opt]) || this.$store.state.user.isAdmin)
        return new Promise((res) => { res() })
      return this.$refs.login.open()
    },
    
  },
  
  sockets: {
    shutdownRequest() {
      if (this.isConsole)
        this.shutdown()
    }
  },  
  
  created() {
    if (this.isConsole)
      console.log('Client is running as console.')
    else
      console.log('Client is running as remote.')
  },
  
  mounted() {
    this.$store.dispatch('pumps/loadAll')
  },
  
}
</script>
