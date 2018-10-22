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
          @click="itemDetail(item)"
        >
          <v-list-tile-avatar>
            <v-icon v-if="item.isFavorite">mdi-heart</v-icon>
            <v-icon v-if="item.isAlcoholic">mdi-flash</v-icon>
            <v-icon v-else>mdi-baby-buggy</v-icon>
          </v-list-tile-avatar>

          <v-list-tile-content>
            <v-list-tile-title>{{item.primaryName}}</v-list-tile-title>
            <v-list-tile-sub-title>{{item.secondaryName}}</v-list-tile-sub-title>
          </v-list-tile-content>
          
          <v-list-tile-action>
            <v-btn
              icon
              @click.stop="orderDrink(item)"
            >
              <v-icon>mdi-plus</v-icon>
            </v-btn>
          </v-list-tile-action>
      
        </v-list-tile>
      </v-list>

      <order-drink ref="orderDrink"></order-drink>

    </template>
    
  </v-card>
        
</template>

<script>

import { mapState, mapGetters } from 'vuex'
import Loading from '../components/Loading'
import OrderDrink from '../components/OrderDrink'

export default {
  name: 'DrinksMenu',
  data() {
    return {
      item: {},
      dialog: false,
      valid: true,
    }
  },
  
  components: {
    Loading,
    OrderDrink,
  },
  
  created() {
    this.$emit('show-page', 'Drinks Menu')
  },
  
  computed: {
    ...mapGetters({
      items: 'drinksMenu/sortedItems',
    }),
    ...mapState({
      loading: state => state.drinksMenu.loading,
    })
  },
  
  methods: {
  
    itemDetail(item) {
      this.$router.push({name: 'drinkDetail', params: {id: item.id, locationHistory: -2}})
    },
  
    orderDrink(item) {
      this.$refs.orderDrink.open(item).then(() => {
        window.history.length > 1 ? this.$router.go(-1) : this.$router.push('/')
      })
    },
    
  },
  
  beforeRouteEnter(to, from, next) {
    next(t => {
      t.$store.dispatch('drinksMenu/loadAll')
    });
  },
  
  beforeRouteLeave(to, from, next) {
    this.$store.commit('drinksMenu/destroy')
    next()
  }
  
}

</script>
