<template>

  <v-card flat style="height: 93vh; overflow-y: auto;">
    
    <loading v-if="loading"></loading>
    
    <template v-else>
    
      <div class="pa-3">
    
        <h1 class="mb-3">{{glass.name}}</h1>
        <p class="subheading">{{glass.description}}</p>

        <h2>Drinks</h2>

        <p
          v-if="!hasDrinks"
          class="subheading"
        >No drinks use this glass.</p>
        
        <v-list v-else>

          <v-list-tile
            v-for="drink in sortedDrinks"
            :key="drink.id"
            ripple
            avatar
            @click="gotoDrinkDetail(drink.id)"
          >
            <v-list-tile-avatar>
              <v-icon v-if="drink.isFavorite">mdi-heart</v-icon>
              <alcoholic-icon :alcoholic="drink.isAlcoholic"/>
            </v-list-tile-avatar>

            <v-list-tile-content>
              <v-list-tile-title>{{drink.name}}</v-list-tile-title>
            </v-list-tile-content>
            
          </v-list-tile>
          
        </v-list>

      </div>
      
    </template>
    
  </v-card>
        
</template>

<script>

import { mapState } from 'vuex'
import Loading from '../components/Loading'
import AlcoholicIcon from '../components/AlcoholicIcon'

export default {
  name: 'GlassDetail',
  data() {
    return {
    }
  },
  
  components: {
    Loading,
    AlcoholicIcon,
  },
  
  created() {
    this.$emit('show-page', 'Glasses')
  },
  
  computed: {
    hasDrinks() {
      return this.glass.drinks && this.glass.drinks.length > 0
    },
    sortedDrinks() {
      if (! this.hasDrinks) return []
      return this.glass.drinks.slice().sort((a, b) => {
        return a.name.localeCompare(b.name, 'en', {'sensitivity': 'base'})
      })
    },
    ...mapState({
      loading: state => state.glasses.loading,
      glass: state => state.glasses.glass,
    })
  },
  
  methods: {
    
    gotoDrinkDetail(id) {
      this.$router.push({name: 'drinkDetail', params: {id: id}})
    },
    
  },
  
  beforeRouteEnter(to, from, next) {
    next(t => {
      t.$store.dispatch('glasses/getOne', t.$route.params.id)
    });
  },
  
  beforeRouteLeave(to, from, next) {
    this.$store.commit('glasses/destroy')
    next()
  },
  
  sockets: {
    glass_deleted(glass) {
      if (this.glass.id && (glass.id === this.glass.id)) {
        window.history.length > 1 ? this.$router.go(-1) : this.$router.push('/')
      }
    }
  },  
  
}

</script>
