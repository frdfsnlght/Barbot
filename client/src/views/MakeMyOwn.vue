<template>

  <v-container fluid fill-height pa-0>
    <v-layout column justify-start fill-height>
    
      <v-flex style="height: 60vh; overflow-y: auto">
      
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
            :disabled="!dispenserGlass || (anyPumpRunning && !runningPumps.includes(pump.id))"
            @mousedown="startPump(pump.id)"
            @touchstart="startPump(pump.id)"
            @mouseup="stopPump(pump.id)"
            @touchend="stopPump(pump.id)"
          >
            <alcoholic-icon :alcoholic="pump.ingredient.isAlcoholic" class="mr-3"/>
            {{pump.ingredient.name}}
          </v-btn>
        </div>
      </v-flex>
      
      <v-flex style="height: 30vh;">
      
        <v-card flat>
              
          <v-toolbar
            clipped-left
            color="secondary"
            dark
            dense
          >
            <v-toolbar-title>Ingredients</v-toolbar-title>
            <v-spacer></v-spacer>
            <v-btn
              v-if="ingredients"
              :disabled="anyPumpRunning"
              icon
              @click="clearIngredients()"
            >
              <v-icon>mdi-delete</v-icon>
            </v-btn>      
            <v-btn
              v-if="ingredients"
              :disabled="anyPumpRunning"
              icon
              @click="addDrink()"
            >
              <v-icon>mdi-cup-water</v-icon>
            </v-btn>      
          </v-toolbar>
      
          <div style="max-height: 25vh; overflow-y: auto">
            <v-list
              avatar
              dense
            >
              <v-list-tile
                v-for="ingredient in sortedIngredients"
                :key="ingredient.id"
              >
                <v-list-tile-avatar>
                  <v-icon>mdi-numeric-{{ingredient.step}}-box-outline</v-icon>
                </v-list-tile-avatar>
                
                <v-list-tile-content>
                  <v-list-tile-title>{{ingredientAmount(ingredient)}} {{ingredient.units}} {{ingredient.ingredient.name}}</v-list-tile-title>
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
import units from '../units'


export default {
  name: 'MakeMyOwn',
  data() {
    return {
      runningPumps: [],
      ingredients: [],
      parentalCodeValidated: false,
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
      parentalCode: state => state.settings.parentalCode,
    })
  },
  
  watch: {
  
    dispenserState(v) {
      if (v != 'manual')
        this.$router.replace({name: 'home'})
    },
  
  },
  
  methods: {
    
    ingredientAmount(ingredient) {
      return units.format(ingredient.amount, ingredient.units)
    },
    
    startPump(id) {
      if (this.runningPumps.includes(id)) return
      
      let pump = this.getPump(id)
      if (this.parentalCode && pump.ingredient.isAlcoholic && ! this.parentalCodeValidated) {
        this.$refs.parentalCodeDialog.open().then(() => {
          this.parentalCodeValidated = true
        }, ()=>{})
      } else {
        this.$socket.emit('dispenser_startPump', {id: id, parentalCode: this.parentalCode}, (res) => {
          if (res.error) {
              this.$store.commit('setError', res.error)
          }
        })
      }
    },
    
    stopPump(id) {
      if (! this.runningPumps.includes(id)) return
      this.$socket.emit('dispenser_stopPump', id, (res) => {
        if (res.error) {
          this.$store.commit('setError', res.error)
        }
      })
    },
    
    clearIngredients() {
      this.ingredients = []
    },
    
    captureIngredient(ingredient, amount) {
      amount = Math.round(units.toOther(amount, units.defaultUnits()) * 1000) / 1000
      
      // find max step
      let maxStep = 1
      for (var i = 0; i < this.ingredients.length; i++)
        if (this.ingredients[i].step > maxStep) maxStep = this.ingredients[i].step
      // find number of ingredients with maxStep
      let stepIngs = this.ingredients.filter(function(i) { return i.step == maxStep })
      if (stepIngs.length >= 4) maxStep++
      
      let ing = this.ingredients.find((e) => { return e.ingredient_id === ingredient.id })
      if (! ing) {
        this.ingredients.push({
          id: null,
          ingredient: ingredient,
          ingredient_id: ingredient.id,
          amount: amount,
          units: units.defaultUnits(),
          step: maxStep,
        })
      } else {
        ing.amount += amount
      }
    },
    
    addDrink() {
      this.$refs.drinkDialog.open({
        id: undefined,
        primaryName: undefined,
        secondaryName: undefined,
        instructions: undefined,
        glass_id: undefined,
        ingredients: this.ingredients,
      }).then(() => {
        this.ingredients = []
      }, ()=>{})
    },
    
  },
  
  beforeRouteEnter(to, from, next) {
    next(t => {
      if (t.isConsole) {
        t.$socket.emit('dispenser_startManual', (res) => {
          if (res.error) {
            t.$store.commit('setError', res.error)
          }
        })
      }
    })
  },
  
  sockets: {
  
    pump_changed(pump) {
      if (pump.running) {
        if (! this.runningPumps.includes(pump.id))
          this.runningPumps.push(pump.id)
      } else {
        if (this.runningPumps.includes(pump.id)) {
          this.runningPumps = this.runningPumps.filter(function(id) { return id != pump.id })
          this.captureIngredient(pump.ingredient, pump.lastAmount)
        }
      }
    }
    
  },  
  
}

</script>
