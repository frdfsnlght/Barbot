<template>

  <v-card flat style="height: 93vh; overflow-y: auto;">
  
    <div class="pa-3 text-xs-center">

      <img src="../assets/logo.png"/>
      
      <p class="headline">{{settings.appTitle}}</p>
    
      <div class="ma-3" v-if="wifiState">
        <p>Connect with any of the following URLs:</p>
        <ul>
          <li v-if="wifiState.shortHostname">http://{{wifiState.shortHostname}}.local:{{serverPort}}/</li>
          <li v-if="wifiState.longHostname">http://{{wifiState.longHostname}}:{{serverPort}}/</li>
          <li v-for="addr in wifiState.ipAddresses" :key="addr">http://{{addr}}:{{serverPort}}/</li>
        </ul>
      </div>
    
      <p>Git: {{gitVersion}}/{{gitBranch}}</p>
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
  
}

</script>
