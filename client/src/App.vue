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

          <template v-if="isConsole">
          
            <v-list-tile @click="reloadClient()">
              <v-list-tile-title>Reload Client</v-list-tile-title>
              <v-list-tile-action>
                <v-icon>mdi-reload</v-icon>
              </v-list-tile-action>
            </v-list-tile>

            <v-list-tile @click="checkRestartX()">
              <v-list-tile-title>Restart X</v-list-tile-title>
              <v-list-tile-action>
                <v-icon>mdi-window-close</v-icon>
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
            
            <v-divider/>
            
            <v-list-tile @click="gotoAbout()">
              <v-list-tile-title>About</v-list-tile-title>
              <v-list-tile-action>
                <v-icon>mdi-information</v-icon>
              </v-list-tile-action>
            </v-list-tile>
          </template>
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

      <template v-if="isConsole">

        <v-btn
          v-if="alerts.length"
          icon
          @click="gotoAlerts()">
          <v-icon>mdi-alert</v-icon>
        </v-btn>      
      
        <v-icon v-if="dispenserGlass">mdi-glass-cocktail</v-icon>

        <template v-if="wifiState">
          <wifi-signal-icon :wifiOn="wifiState.ssid" :bars="wifiState.bars"/>
        </template>

        <volume-control/>
        
      </template>
          
      <v-btn v-if="user.name" icon @click="logout()">
        <v-icon>mdi-logout</v-icon>
      </v-btn>
      
    </v-toolbar>
    
    <v-content>
      <router-view
        @show-page="showPage"
      />
    </v-content>
    
    <connecting-dialog/>
    <error-dialog/>
    <notifier/>
    <confirm-dialog ref="confirmDialog"/>
    <login-dialog ref="loginDialog"/>
    <audio-player ref="audioPlayer"/>
    <keyboard-overlay v-if="isConsole"/>
    
  </v-app>
</template>

<script>

import { mapState } from 'vuex'
import bus from './bus'
import HTMLTitle from './components/HTMLTitle'
import ConfirmDialog from './components/ConfirmDialog'
import ConnectingDialog from './components/ConnectingDialog'
import ErrorDialog from './components/ErrorDialog'
import Notifier from './components/Notifier'
import LoginDialog from './components/LoginDialog'
import AudioPlayer from './components/AudioPlayer'
import KeyboardOverlay from './components/KeyboardOverlay'
import WifiSignalIcon from './components/WifiSignalIcon'
import VolumeControl from './components/VolumeControl'

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
    ConfirmDialog,
    ConnectingDialog,
    ErrorDialog,
    Notifier,
    LoginDialog,
    AudioPlayer,
    KeyboardOverlay,
    WifiSignalIcon,
    VolumeControl,
  },
  
  computed: {
    title () {
      return this.settings.appTitle + (this.pageTitle ? (": " + this.pageTitle) : "");
    },
    ...mapState([
      'settings',
      'isConsole',
      'user',
    ]),
    ...mapState({
      wifiState: state => state.wifi.state,
      dispenserGlass: state => state.dispenser.glass,
      alerts: state => state.alerts.alerts,
    }),
  },
  
  methods: {
  
    goBack() {
      window.history.length > 1
        ? this.$router.go(-1)
        : this.$router.push('/')
    },
    
    gotoAlerts() {
      this.$router.push({name: 'alerts'})
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
      this.checkAdmin('dispenserSetupRequiresAdmin').then(() => {
        this.$router.push({name: 'pumps'})
      }, ()=>{})
    },
    
    gotoSettings() {
      this.drawer = false
      this.checkAdmin('settingsRequiresAdmin').then(() => {
        this.$router.push({name: 'settings'})
      }, ()=>{})
    },

    gotoAbout() {
      this.drawer = false
      this.$router.push({name: 'about'})
    },
    
    checkRestartX() {
      this.drawer = false
      this.checkAdmin('restartXRequiresAdmin').then(this.restartX, ()=>{})
    },

    checkRestart() {
      this.drawer = false
      this.checkAdmin('restartRequiresAdmin').then(this.restart, ()=>{})
    },

    checkShutdown() {
      this.drawer = false
      this.checkAdmin('shutdownRequiresAdmin').then(this.shutdown, ()=>{})
    },

    reloadClient() {
      window.location.reload(true);
    },
    
    restartX() {
      this.$socket.emit('core_restartX', (res) => {
        if (res.error) {
            this.$store.commit('setError', res.error)
        }
      })
    },
    
    restart() {
      this.$refs.confirmDialog.open('Restart', 'Are you sure you want to restart the system?').then(() => {
        this.$socket.emit('core_restart', (res) => {
          if (res.error) {
              this.$store.commit('setError', res.error)
          }
        })
      }, ()=>{})
    },
    
    shutdown() {
      this.$refs.confirmDialog.open('Shutdown', 'Are you sure you want to shutdown the system?').then(() => {
        this.$socket.emit('core_shutdown', (res) => {
          if (res.error) {
              this.$store.commit('setError', res.error)
          }
        })
      }, ()=>{})
    },
    
    logout() {
      this.$refs.loginDialog.logout().then(() => {
        bus.$emit('logout')
      }, ()=>{})
    },
    
    showPage(pageTitle) {
      this.pageTitle = pageTitle
      this.showBack = !!pageTitle
    },
    
    checkAdmin(opt) {
      if ((! this.settings[opt]) || this.user.isAdmin)
        return new Promise((res) => { res() })
      return this.$refs.loginDialog.open()
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
  
}
</script>
