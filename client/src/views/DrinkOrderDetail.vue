<template>

  <v-card flat>
    
    <loading v-if="loading"></loading>
    
    <template v-else>
    
      <h1 class="pa-3">{{drinkName}}</h1>
      
      <p
        v-if="item.name"
        class="px-3 subheading">For: {{item.name}}</p>
      
      <p
        v-if="item.userHold"
        class="px-3 subheading">This order is on hold.</p>
      <p
        v-if="item.ingredientHold"
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
      return this.item.drink ? this.item.drink.name : ''
    },
    createdDate() {
      return this.$formatDateTimeString(this.item.createdDate)
    },
    ...mapState({
      loading: state => state.drinkOrders.loading,
      item: state => state.drinkOrders.item,
    })
  },
  
  methods: {
    
  },
  
  beforeRouteEnter(to, from, next) {
    next(t => {
      t.$store.dispatch('drinkOrders/loadById', t.$route.params.id)
    });
  },
  
  beforeRouteLeave(to, from, next) {
    this.$store.commit('drinkOrders/destroy')
    next()
  },
  
  sockets: {
    drinkOrderCancelled(item) {
      if (this.item.id && (item.id === this.item.id)) {
        window.history.length > 1 ? this.$router.go(-1) : this.$router.push('/')
      }
    },
    drinkOrderStarted(item) {
      if (this.item.id && (item.id === this.item.id)) {
        window.history.length > 1 ? this.$router.go(-1) : this.$router.push('/')
      }
    }
  },  
  
}

</script>
