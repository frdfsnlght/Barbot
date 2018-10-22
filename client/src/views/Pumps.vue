<template>

  <v-card flat>
    
    <loading v-if="loading"></loading>
    
    <template v-else>
    
      <v-list two-line>
        <v-list-tile
          v-for="item in items"
          :key="item.id"
          avatar
          ripple
        >
          <v-list-tile-avatar>
            <v-icon v-if="item.running">mdi-run</v-icon>
            <v-icon v-else-if="!item.state">mdi-power-off</v-icon>
            <v-icon v-else-if="item.state=='loaded'">mdi-plus</v-icon>
            <v-icon v-else-if="item.state=='ready'">mdi-check</v-icon>
            <v-icon v-else-if="item.state=='empty'">mdi-battery-outline</v-icon>
            <v-icon v-else-if="item.state=='dirty'">mdi-spray-bottle</v-icon>
          </v-list-tile-avatar>
          
          <v-list-tile-content>
            <v-list-tile-title>{{item.name}} : {{itemIngredient(item)}}</v-list-tile-title>
            <v-list-tile-sub-title>{{itemState(item)}}</v-list-tile-sub-title>
          </v-list-tile-content>
          
          <v-list-tile-action>
            <v-btn
              icon
              :disabled="disableActions()"
              @click.stop="showMenu(item, $event)"
            >
              <v-icon>mdi-dots-vertical</v-icon>
            </v-btn>
          </v-list-tile-action>
          
        </v-list-tile>
      </v-list>

      <v-menu
        v-model="menu"
        :position-x="menuX"
        :position-y="menuY"
        absolute
        offset-y
      >
        <v-list>
        
          <v-list-tile
            v-if="!item.state"
            ripple
            @click="openLoadPump()"
          >
            <v-list-tile-content>
              <v-list-tile-title>Load</v-list-tile-title>
            </v-list-tile-content>
            <v-list-tile-action>
              <v-icon>mdi-plus</v-icon>
            </v-list-tile-action>
          </v-list-tile>

          <v-list-tile
            v-if="item.state=='loaded'"
            ripple
            @click="openPrimePump()"
          >
            <v-list-tile-content>
              <v-list-tile-title>Prime</v-list-tile-title>
            </v-list-tile-content>
            <v-list-tile-action>
              <v-icon>mdi-autorenew</v-icon>
            </v-list-tile-action>
          </v-list-tile>

          <v-list-tile
            v-if="item.state=='loaded'"
            ripple
            @click="unloadPump()"
          >
            <v-list-tile-content>
              <v-list-tile-title>Unload</v-list-tile-title>
            </v-list-tile-content>
            <v-list-tile-action>
              <v-icon>mdi-minus</v-icon>
            </v-list-tile-action>
          </v-list-tile>

          <v-list-tile
            v-if="item.state=='ready' || item.state=='empty'"
            ripple
            @click="openLoadPump()"
          >
            <v-list-tile-content>
              <v-list-tile-title>Reload</v-list-tile-title>
            </v-list-tile-content>
            <v-list-tile-action>
              <v-icon>mdi-recycle</v-icon>
            </v-list-tile-action>
          </v-list-tile>

          <v-list-tile
            v-if="item.state=='ready' || item.state=='empty'"
            ripple
            @click="drainPump()"
          >
            <v-list-tile-content>
              <v-list-tile-title>Drain</v-list-tile-title>
            </v-list-tile-content>
            <v-list-tile-action>
              <v-icon>mdi-backup-restore</v-icon>
            </v-list-tile-action>
          </v-list-tile>

          <v-list-tile
            v-if="item.state=='ready'"
            ripple
            @click="openPrimePump()"
          >
            <v-list-tile-content>
              <v-list-tile-title>Prime</v-list-tile-title>
            </v-list-tile-content>
            <v-list-tile-action>
              <v-icon>mdi-autorenew</v-icon>
            </v-list-tile-action>
          </v-list-tile>
          
          <v-list-tile
            v-if="!item.state || item.state=='dirty'"
            ripple
            @click="openCleanPump()"
          >
            <v-list-tile-content>
              <v-list-tile-title>Clean</v-list-tile-title>
            </v-list-tile-content>
            <v-list-tile-action>
              <v-icon>mdi-spray-bottle</v-icon>
            </v-list-tile-action>
          </v-list-tile>

        </v-list>
      </v-menu>
      
      <pump-wizard ref="pumpWizard" :pump="item"></pump-wizard>
      
    </template>
    
  </v-card>
        
</template>

<script>

import { mapState, mapGetters } from 'vuex'
import store from '../store/store'
import bus from '../bus'
import Loading from '../components/Loading'
import PumpWizard from '../components/PumpWizard'

export default {
  name: 'Ingredients',
  data() {
    return {
      item: {},
      menu: false,
      menuX: 0,
      menuY: 0,
    }
  },
  components: {
    Loading,
    PumpWizard,
  },
  
  created() {
    this.$emit('show-page', 'Pumps')
    bus.$on('logout', this.onLogout)
  },
  
  beforeDestroy: function () {
    bus.$off('logout', this.onLogout)
  },
  
  computed: {
    ...mapGetters({
      items: 'pumps/sortedItems',
      anyPumpRunning: 'pumps/anyPumpRunning',
    }),
    ...mapState({
      loading: state => state.pumps.loading,
      isConsole: state => state.isConsole,
      pumpSetup: state => state.pumpSetup,
    })
  },
  
  methods: {
  
    itemIngredient(item) {
      if (! item.ingredient) return '<no ingredient>'
      return item.amount.toFixed() + ' ' + item.units + ' ' + item.ingredient.name + ' (' + Math.round((item.amount / item.containerAmount) * 100)   + '%)'
    },
    
    itemState(item) {
      if (! item.state) return '<unused>'
      return item.state
    },
    
    disableActions() {
      return !(this.isConsole && this.pumpSetup) || this.anyPumpRunning
    },

    showMenu(item, e) {
      this.item = item
      this.menuX = e.clientX
      this.menuY = e.clientY
      this.menu = true
    },
  
    openLoadPump() {
      this.$refs.pumpWizard.openLoad()
    },
  
    unloadPump() {
      this.$socket.emit('unloadPump', this.item.id, (res) => {
        if (res.error) {
            this.$store.commit('setError', res.error)
        }
      })
    },
  
    openPrimePump() {
      this.$refs.pumpWizard.openPrime()
    },
  
    drainPump() {
      this.$socket.emit('drainPump', this.item.id, (res) => {
        if (res.error) {
            this.$store.commit('setError', res.error)
        }
      })
    },
  
    openCleanPump() {
      this.$refs.pumpWizard.openClean()
    },
  
    onLogout() {
      if (! ((store.state.options.pumpSetupRequiresAdmin == false) || store.state.user.isAdmin))
        this.$router.replace({name: 'home'})
    },
    
  },
  
  beforeRouteEnter(to, from, next) {
    if (! ((store.state.options.pumpSetupRequiresAdmin == false) || store.state.user.isAdmin))
      next({name: 'home'})
    else
      next(t => {
        if (t.isConsole) {
          t.$socket.emit('startPumpSetup', (res) => {
            if (res.error) {
              t.$store.commit('setError', res.error)
            }
          })
        }
      })
  },
  
  beforeRouteLeave(to, from, next) {
    next()
  },
  
}

</script>
