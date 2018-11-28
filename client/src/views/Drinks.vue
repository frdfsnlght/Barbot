<template>

  <v-card flat>
    
    <loading v-if="loading"></loading>
    
    <p
      v-else-if="!items.length"
      class="title text-xs-center ma-3"
    >
      No drinks are currently available.
    </p>
    
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
            <v-icon v-if="item.isOnMenu">mdi-cup-water</v-icon>
            <v-icon v-if="item.isFavorite">mdi-heart</v-icon>
            <alcoholic-icon :alcoholic="item.isAlcoholic"/>
          </v-list-tile-avatar>

          <v-list-tile-content>
            <v-list-tile-title>{{item.primaryName}}</v-list-tile-title>
            <v-list-tile-sub-title>{{item.secondaryName}}</v-list-tile-sub-title>
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

      <v-menu
        v-model="menu"
        :position-x="menuX"
        :position-y="menuY"
        absolute
        offset-y
      >
        <v-list>
        
          <v-list-tile ripple @click="editItem()">
            <v-list-tile-content>
              <v-list-tile-title>Edit</v-list-tile-title>
            </v-list-tile-content>
            <v-list-tile-action>
              <v-icon>mdi-pencil</v-icon>
            </v-list-tile-action>
          </v-list-tile>
          
          <v-list-tile ripple @click="deleteItem()">
            <v-list-tile-content>
              <v-list-tile-title>Delete</v-list-tile-title>
            </v-list-tile-content>
            <v-list-tile-action>
              <v-icon>mdi-delete</v-icon>
            </v-list-tile-action>
          </v-list-tile>
          
        </v-list>
      </v-menu>
      
    </template>
    
    <template v-if="!loading">
      <v-btn
        fab
        fixed
        bottom right
        color="primary"
        @click="addItem"
      >
        <v-icon dark>mdi-plus</v-icon>
      </v-btn>
    </template>
    
    <confirm ref="confirm"></confirm>
    <drink-dialog ref="drinkDialog"/>
    
  </v-card>
        
</template>

<script>

import { mapState, mapGetters } from 'vuex'
import Loading from '../components/Loading'
import Confirm from '../components/Confirm'
import AlcoholicIcon from '../components/AlcoholicIcon'
import DrinkDialog from '../components/DrinkDialog'

export default {
  name: 'Drinks',
  data() {
    return {
      item: {},
      edit: false,
      valid: true,
      menu: false,
      menuX: 0,
      menuY: 0,
    }
  },
  
  components: {
    Loading,
    Confirm,
    AlcoholicIcon,
    DrinkDialog,
  },
  
  created() {
    this.$emit('show-page', 'Drinks')
  },
  
  computed: {
    ...mapGetters({
      items: 'drinks/sortedItems',
    }),
    ...mapState({
      loading: state => state.drinks.loadingAll,
    })
  },
  
  methods: {
  
    itemDetail(item) {
      this.$router.push({name: 'drinkDetail', params: {id: item.id}})
    },
  
    showMenu(item, e) {
      this.item = JSON.parse(JSON.stringify(item))
      this.menuX = e.clientX
      this.menuY = e.clientY
      this.menu = true
    },
  
    addItem() {
      this.$refs.drinkDialog.open({
        id: undefined,
        primaryName: undefined,
        secondaryName: undefined,
        instructions: undefined,
        glassId: undefined,
        ingredients: []
      })
    },
    
    editItem() {
      this.$refs.drinkDialog.open(this.item, true)
    },
    
    deleteItem() {
      this.$refs.confirm.open('Delete', 'Are you sure you want to delete "' + this.item.name + '"?').then(() => {
        this.$socket.emit('deleteDrink', this.item.id, (res) => {
          if (res.error) {
            this.$store.commit('setError', res.error)
          }
        })
      })
    },
    
  },
  
  beforeRouteEnter(to, from, next) {
    next(t => {
      t.$store.dispatch('drinks/loadAll')
    });
  },
  
  beforeRouteLeave(to, from, next) {
    this.$store.commit('drinks/destroy')
    next()
  }
  
}

</script>
