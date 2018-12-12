<template>

  <v-card flat style="height: 93vh; overflow-y: auto;">
    
    <loading v-if="loading"></loading>
    
    <template v-else>
    
      <h1 class="pa-3">{{drinkName}}</h1>
      
      <p
        v-if="drinkOrder.name"
        class="px-3 subheading">For: {{drinkOrder.name}}</p>
      
      <p
        v-if="drinkOrder.userHold"
        class="px-3 subheading">This order is on hold.</p>
      <p
        v-if="drinkOrder.ingredientHold"
        class="px-3 subheading">This order cannot be made because of one or more missing ingredients.</p>
      
      <p class="px-3 subheading">Placed: {{createdDate}}</p>
        
    </template>
    
  </v-card>
        
</template>

<script>

import { mapState } from 'vuex'
import Loading from '../components/Loading'

export default {
  name: 'DrinkOrderDetail',
  data() {
    return {
    }
  },
  
  components: {
    Loading,
  },
  
  created() {
    this.$emit('show-page', 'Drink Order')
  },
  
  computed: {
    drinkName() {
      return this.drinkOrder.drink ? this.drinkOrder.drink.name : ''
    },
    createdDate() {
      return this.$formatDateTimeString(this.drinkOrder.createdDate)
    },
    ...mapState({
      loading: state => state.drinkOrders.loading,
      drinkOrder: state => state.drinkOrders.drinkOrder,
    })
  },
  
  methods: {
    
  },
  
  beforeRouteEnter(to, from, next) {
    next(t => {
      t.$store.dispatch('drinkOrders/getOne', t.$route.params.id)
    });
  },
  
  beforeRouteLeave(to, from, next) {
    this.$store.commit('drinkOrders/destroy')
    next()
  },
  
  sockets: {
  
    drinkOrder_cancelled(drinkOrder) {
      if (this.drinkOrder.id && (drinkOrder.id === this.drinkOrder.id)) {
        window.history.length > 1 ? this.$router.go(-1) : this.$router.push('/')
      }
    },
    
    drinkOrder_changed(drinkOrder) {
      if (drinkOrder.startedDate && this.drinkOrder.id && (drinkOrder.id === this.drinkOrder.id)) {
        window.history.length > 1 ? this.$router.go(-1) : this.$router.push('/')
      }
    }
  },  
  
}

</script>
