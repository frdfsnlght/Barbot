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
      v-else-if="!items.length"
      class="title text-xs-center pa-3"
    >
      Place an order by clicking the "+" button below.
    </p>
    
    <template v-else>
    
      <div style="max-height: 27vh; overflow-y: auto">
        <v-list two-line>
          <v-list-tile
            v-for="item in items"
            :key="item.id"
            avatar
            ripple
            @click="itemDetail(item)"
          >
            
            <v-list-tile-avatar>
              <v-icon v-if="item.userHold">mdi-pause</v-icon>
              <v-icon v-else-if="item.ingredientHold">mdi-pause-octagon</v-icon>
              <v-icon v-else>mdi-play</v-icon>
            </v-list-tile-avatar>
            
            <v-list-tile-content>
              <v-list-tile-title>{{item.drink.name}}</v-list-tile-title>
              <v-list-tile-sub-title>{{item.name}}</v-list-tile-sub-title>
            </v-list-tile-content>
            
            <v-list-tile-action>
              <v-btn
                icon
                @click.stop="showMenu(item, $event)"
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
        
          <v-list-tile ripple @click="toggleHoldItem()">
            <v-list-tile-content>
              <v-list-tile-title v-if="item.userHold">Dispense</v-list-tile-title>
              <v-list-tile-title v-else>Hold</v-list-tile-title>
            </v-list-tile-content>
            <v-list-tile-action>
              <v-icon v-if="item.userHold">mdi-play</v-icon>
              <v-icon v-else>mdi-pause</v-icon>
            </v-list-tile-action>
          </v-list-tile>
          
          <v-list-tile ripple @click="cancelItem()">
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
      @click="addItem"
    >
      <v-icon dark>mdi-plus</v-icon>
    </v-btn>
    
    <confirm ref="confirm"></confirm>
    
  </v-card>
          
</template>

<script>

import { mapState, mapGetters } from 'vuex'
import Loading from './Loading'
import Confirm from './Confirm'


export default {
  name: 'DrinkOrders',
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
    Confirm
  },
  
  computed: {
    ...mapGetters({
      items: 'drinkOrders/sortedItems'
    }),
    ...mapState({
      loading: state => state.drinkOrders.loading,
      dispenserState: state => state.dispenser.state,
    })
  },
  
  created() {
    this.$store.dispatch('drinkOrders/loadWaiting')
  },
  
  destroyed() {
    this.$store.commit('drinkOrders/destroy')
  },
  
  methods: {
  
    itemDetail(item) {
      this.$router.push({name: 'drinkOrderDetail', params: {id: item.id}})
    },

    showMenu(item, e) {
      this.item = JSON.parse(JSON.stringify(item))
      this.menuX = e.clientX
      this.menuY = e.clientY
      this.menu = true
    },
  
    addItem() {
      this.$router.push({name: 'drinksMenu'})
    },
  
    toggleHoldItem() {
      this.$socket.emit('core_toggleDrinkOrderHold', this.item.id, (res) => {
        if (res.error) {
          this.$store.commit('setError', res.error)
        }
      })
    },
    
    cancelItem() {
      this.$refs.confirm.open('Cancel', 'Are you sure you want to cancel this order?', {rejectText: 'No'}).then(() => {
        this.$socket.emit('core_cancelDrinkOrder', this.item.id, (res) => {
          if (res.error) {
            this.$store.commit('setError', res.error)
          }
        })
      })
    },
    
  },

}
</script>
