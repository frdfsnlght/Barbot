<template>
  <v-card flat>
        
    <v-toolbar
      clipped-left
      color="secondary"
      dark
      dense
    >
      <v-toolbar-title>Orders</v-toolbar-title>
    </v-toolbar>
      
    <loading v-if="loading"></loading>
    
    <p
      v-else-if="!drinkOrders.length"
      class="title text-xs-center pa-3"
    >
      Place an order by clicking the "+" button below.
    </p>
    
    <template v-else>
    
      <div style="max-height: 47vh; overflow-y: auto;">
        <v-list two-line>
          <v-list-tile
            v-for="drinkOrder in drinkOrders"
            :key="drinkOrder.id"
            avatar
            ripple
            @click="gotoDetail(drinkOrder)"
          >
            
            <v-list-tile-avatar>
              <v-icon v-if="drinkOrder.userHold">mdi-pause</v-icon>
              <v-icon v-else-if="drinkOrder.ingredientHold">mdi-pause-octagon</v-icon>
              <v-icon v-else>mdi-play</v-icon>
            </v-list-tile-avatar>
            
            <v-list-tile-content>
              <v-list-tile-title>{{drinkOrder.drink.name}}</v-list-tile-title>
              <v-list-tile-sub-title>{{drinkOrder.name}}</v-list-tile-sub-title>
            </v-list-tile-content>
            
            <v-list-tile-action>
              <v-btn
                icon
                @click.stop="showMenu(drinkOrder, $event)"
              >
                <v-icon>mdi-dots-vertical</v-icon>
              </v-btn>
            </v-list-tile-action>
            
          </v-list-tile>
        </v-list>
      </div>

      <v-menu
        v-model="menu"
        :position-x="menuX"
        :position-y="menuY"
        absolute
        offset-y
      >
        <v-list>
        
          <v-list-tile ripple @click="toggleHold()">
            <v-list-tile-content>
              <v-list-tile-title v-if="drinkOrder.userHold">Dispense</v-list-tile-title>
              <v-list-tile-title v-else>Hold</v-list-tile-title>
            </v-list-tile-content>
            <v-list-tile-action>
              <v-icon v-if="drinkOrder.userHold">mdi-play</v-icon>
              <v-icon v-else>mdi-pause</v-icon>
            </v-list-tile-action>
          </v-list-tile>
          
          <v-list-tile ripple @click="cancel()">
            <v-list-tile-content>
              <v-list-tile-title>Cancel</v-list-tile-title>
            </v-list-tile-content>
            <v-list-tile-action>
              <v-icon>mdi-delete</v-icon>
            </v-list-tile-action>
          </v-list-tile>
          
        </v-list>
      </v-menu>
      
    </template>

    <v-btn
      fab
      fixed
      bottom right
      color="primary"
      @click="add"
    >
      <v-icon dark>mdi-plus</v-icon>
    </v-btn>
    
    <confirm-dialog ref="confirmDialog"/>
    
  </v-card>
          
</template>

<script>

import { mapState, mapGetters } from 'vuex'
import Loading from './Loading'
import ConfirmDialog from './ConfirmDialog'


export default {
  name: 'DrinkOrders',
  data() {
    return {
      drinkOrder: {},
      menu: false,
      menuX: 0,
      menuY: 0,
    }
  },
  
  components: {
    Loading,
    ConfirmDialog
  },
  
  computed: {
    ...mapGetters({
      drinkOrders: 'drinkOrders/sortedDrinkOrders'
    }),
    ...mapState({
      loading: state => state.drinkOrders.loading,
    })
  },
  
  created() {
    this.$store.dispatch('drinkOrders/getWaiting')
  },
  
  destroyed() {
    this.$store.commit('drinkOrders/destroy')
  },
  
  methods: {
  
    gotoDetail(drinkOrder) {
      this.$router.push({name: 'drinkOrderDetail', params: {id: drinkOrder.id}})
    },

    showMenu(drinkOrder, e) {
      this.drinkOrder = JSON.parse(JSON.stringify(drinkOrder))
      this.menuX = e.clientX
      this.menuY = e.clientY
      this.menu = true
    },
  
    add() {
      this.$router.push({name: 'drinksMenu'})
    },
  
    toggleHold() {
      this.$socket.emit('drinkOrder_toggleHold', this.drinkOrder.id, (res) => {
        if (res.error) {
          this.$store.commit('setError', res.error)
        }
      })
    },
    
    cancel() {
      this.$refs.confirmDialog.open('Cancel', 'Are you sure you want to cancel this order?', {rejectText: 'No'}).then(() => {
        this.$socket.emit('drinkOrder_cancel', this.drinkOrder.id, (res) => {
          if (res.error) {
            this.$store.commit('setError', res.error)
          }
        })
      }, ()=>{})
    },
    
  },

  sockets: {
    connect() {
      this.$store.dispatch('drinkOrders/getWaiting')
    },
  },
  
}
</script>
