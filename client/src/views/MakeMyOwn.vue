<template>

  <v-container fluid fill-height pa-0>
    <v-layout column justify-start fill-height>
    
      <v-flex style="min-height: 60vh; overflow-y: auto">
      
        <p
          v-if="!dispenserGlass"
          class="headline red--text text-xs-center mb-3"
        >
          Place a glass in the dispensing area.
        </p>
        
        <p
          v-if="!pumps.length"
          class="headline text-xs-center mb-3"
        >
          There are no pumps ready.
        </p>
        
        <div
          class="text-xs-center"
        >
          <v-btn
            v-for="pump in pumps"
            :key="pump.id"
            ripple
            large
            block
            class="mb-3"
            :disabled="!dispenserGlass || (anyPumpRunning && dispensingId != pump.id)"
            @mousedown="startPump(pump.id)"
            @mouseup="stopPump()"
          >
            <alcoholic-icon :alcoholic="pump.ingredient.isAlcoholic" class="mr-3"/>
            {{pump.ingredient.name}}
          </v-btn>
        </div>
      </v-flex>
      
      <v-flex fill-height>
      
        <v-card flat>
              
          <v-toolbar
            clipped-left
            color="secondary"
            dark
            dense
          >
            <v-toolbar-title>Ingredients</v-toolbar-title>
            <v-spacer></v-spacer>
            <v-btn v-if="ingredients" icon @click="addDrink()">
              <v-icon>mdi-cup-water</v-icon>
            </v-btn>      
          </v-toolbar>
      
          <div style="max-height: 27vh; overflow-y: auto">
            <v-list
              avatar
              dense
            >
              <v-list-tile
                v-for="item in sortedIngredients"
                :key="item.id"
              >
                <v-list-tile-avatar>
                  <v-icon>mdi-numeric-{{item.step}}-box-outline</v-icon>
                </v-list-tile-avatar>
                
                <v-list-tile-content>
                  <v-list-tile-title>{{item.amount | fixedAmount}} {{item.units}} {{item.ingredient.name}}</v-list-tile-title>
                </v-list-tile-content>
                
              </v-list-tile>
            </v-list>
          </div>
          
        </v-card>
        
      </v-flex>
      
    </v-layout>
    <parental-code-dialog ref="parentalCodeDialog" :validate="true"/>
    <drink-dialog ref="drinkDialog"/>
  </v-container>
        
</template>

<script>

import { mapGetters, mapState } from 'vuex'
import AlcoholicIcon from '../components/AlcoholicIcon'
import ParentalCodeDialog from '../components/ParentalCodeDialog'
import DrinkDialog from '../components/DrinkDialog'
import utils from '../utils'


export default {
  name: 'MakeMyOwn',
  data() {
    return {
      dispensingId: null,
      captureId: null,
      cachedParentalCode: false,
      ingredients: [],
    }
  },
  
  components: {
    AlcoholicIcon,
    ParentalCodeDialog,
    DrinkDialog,
  },
  
  created() {
    this.$emit('show-page', 'Make My Own')
  },
  
  computed: {
    sortedIngredients() {
      return this.ingredients.slice().sort((a, b) => {
        if (a.step < b.step) return -1
        if (a.step > b.step) return 1
        return a.ingredient.name.localeCompare(b.ingredient.name, 'en', {'sensitivity': 'base'})
      })
    },
    ...mapGetters({
      pumps: 'pumps/sortedReadyPumps',
      getPump: 'pumps/getPump',
      anyPumpReady: 'pumps/anyPumpReady',
      anyPumpRunning: 'pumps/anyPumpRunning',
    }),
    ...mapState({
      isConsole: state => state.isConsole,
      dispenserState: state => state.dispenser.state,
      dispenserGlass: state => state.dispenser.glass,
      dispenserParentalCode: state => state.dispenser.parentalCode,
      defaultUnits: state => state.options.defaultUnits,
    })
  },
  
  watch: {
  
    dispenserState(v) {
      if (v != 'dispense')
        this.$router.replace({name: 'home'})
    },
  
    dispenserGlass(v) {
      if (v && this.dispensingId) {
        this.$socket.emit('dispenser_stopPump', (res) => {
          if (res.error) {
              this.$store.commit('setError', res.error)
          } else
            this.dispensingId = null
        })
      }
    },
    
  },
  
  methods: {
    
    startPump(id) {
      if (this.dispensingId != id) {
        if (this.dispensingId != null)
          this.stopDispense(this.dispensingId)
      }
      let pump = this.getPump(id)
      if (this.dispenserParentalCode && pump.ingredient.isAlcoholic && ! this.cachedParentalCode) {
        this.$refs.parentalCodeDialog.open().then(() => {
          this.cachedParentalCode = this.$refs.parentalCodeDialog.code
          console.log('code is ' + this.cachedParentalCode)
        })
      } else {
        this.$socket.emit('dispenser_startPump', {id: id, parentalCode: this.cachedParentalCode}, (res) => {
          if (res.error) {
              this.$store.commit('setError', res.error)
          } else
            this.dispensingId = id
        })
      }
    },
    
    stopPump() {
      if (this.dispensingId != null) {
        this.captureId = this.dispensingId
        this.$socket.emit('dispenser_stopPump', (res) => {
          if (res.error) {
              this.$store.commit('setError', res.error)
          } else
            this.dispensingId = null
        })
       }
    },
    
    captureIngredient(ingredient, amount) {
      amount = Math.round(utils.convertUnits(amount, 'ml', this.defaultUnits) * 10) / 10
      
      // find max step
      let maxStep = 1
      for (var i = 0; i < this.ingredients.length; i++)
        if (this.ingredients[i].step > maxStep) maxStep = this.ingredients[i].step
      // find number of ingredients with maxStep
      let stepIngs = this.ingredients.filter(function(i) { return i.step == maxStep })
      if (stepIngs.length >= 4) maxStep++
      
      let ing = this.ingredients.find((e) => { return e.ingredientId === ingredient.id })
      if (! ing) {
        this.ingredients.push({
          id: null,
          ingredient: ingredient,
          ingredientId: ingredient.id,
          amount: amount,
          units: this.defaultUnits,
          step: maxStep,
        })
      } else {
        ing.amount += amount
      }
      
      console.dir(this.ingredients)
    },
    
    addDrink() {
      this.$refs.drinkDialog.open({
        id: undefined,
        primaryName: undefined,
        secondaryName: undefined,
        instructions: undefined,
        glassId: undefined,
        ingredients: this.ingredients,
      }).then(() => {
        this.ingredients = []
      })
    },
    
  },
  
  beforeRouteEnter(to, from, next) {
    next(t => {
      if (t.isConsole) {
        t.$socket.emit('dispenser_startDispense', (res) => {
          if (res.error) {
            t.$store.commit('setError', res.error)
          }
        })
      }
    })
  },
  
  sockets: {
    pumpSaved(pump) {
      if (this.captureId && (this.captureId == pump.id)) {
        this.captureIngredient(pump.ingredient, pump.lastAmount)
        this.captureId = null
      }
    }
  },  
  
}

</script>
