<template>

  <v-card flat style="height: 92.5vh; overflow-y: auto;">
  
    <div class="pa-3 text-xs-center">

      <img src="../assets/logo.png"/>
      
      <p class="headline">{{settings.appTitle}}</p>
    
      <div class="ma-3" v-if="wifiState">
        <p>Connect with any of the following URLs:</p>
        <ul>
          <li v-if="wifiState.shortHostname">http://{{wifiState.shortHostname}}:{{serverPort}}/</li>
          <li v-if="wifiState.shortHostname">http://{{wifiState.shortHostname}}.local:{{serverPort}}/</li>
          <li v-for="addr in wifiState.ipAddresses" :key="addr">http://{{addr}}:{{serverPort}}/</li>
        </ul>
      </div>
    
      <p class="mb-0">{{statistics.drinks}} drinks</p>
      <p class="mb-0">{{statistics.ingredients}} ingredients</p>
      <p class="mb-0">{{statistics.glasses}} glasses</p>
      <p class="mb-0">{{statistics.menuDrinks}} drinks on the menu</p>
      <p>{{statistics.drinksServed}} drinks served since startup</p>
    
      <p>Storage: {{statistics.diskFree}}%</p>
      
      <p class="mb-0">Git: {{gitVersion}}/{{gitBranch}}</p>
      <p>Built: {{buildDate}}</p>

    </div>
    
    <v-footer absolute>
      <v-layout justify-center row>
        <div>&copy; {{new Date().getFullYear()}}</div>
      </v-layout>
    </v-footer>
    
  </v-card>
        
</template>

<style>

li {
  list-style-type: none;
}

</style>

<script>

import { mapState } from 'vuex'
import build from '../build'

export default {
  name: 'About',
  data() {
    return {
      statistics: {},
    }
  },
  
  created() {
    this.$emit('show-page', 'About')
  },
  
  computed: {
    gitVersion() {
      return build.gitVersion
    },
    gitBranch() {
      return build.gitBranch
    },
    buildDate() {
      return build.buildDate
    },
    serverPort() {
      return document.location.port
    },
    ...mapState({
      settings: state => state.settings,
      wifiState: state => state.wifi.state,
    }),
  },
  
  methods: {
  
  },
  
  beforeRouteEnter(to, from, next) {
    next(t => {
      t.$socket.emit('core_statistics', (res) => {
        if (res.error) {
            t.$store.commit('setError', res.error)
        } else {
          t.statistics = res
        }
      })
    });
  },
  
}

</script>
