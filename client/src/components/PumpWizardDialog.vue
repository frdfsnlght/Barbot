<template>
  <div>
  
    <v-dialog v-model="loadDialog" persistent scrollable>
      <v-card>
        <v-card-title>
          <span v-if="!isReload" class="headline">Load Pump {{pump.name}}</span>
          <span v-else class="headline">Reload Pump {{pump.name}}</span>
        </v-card-title>
        
        <v-card-text @keydown.esc.prevent="closeLoad" @keydown.enter.prevent="submitLoad">
          <v-form ref="loadForm" v-model="valid" lazy-validation>
            <v-container grid-list-md>
              <v-layout wrap>
              
                <v-flex xs12>
                  <select-ingredient
                    :autofocus="!isReload"
                    v-model="loadParams.ingredient_id"
                    required
                    :disabled="isReload"
                    :rules="[v => !!v || 'Ingredient is required']"
                  ></select-ingredient>
                </v-flex>
                
                <v-flex xs12 v-if="ingredientHasNoDrinks">
                  <p>This ingredient is not used in any drinks!</p>
                </v-flex>
                
                <v-flex xs6>
                  <v-text-field
                    label="Container size"
                    v-model="loadParams.containerAmount"
                    :autofocus="isReload"
                    :rules="[v => !!v || 'Container size is required']"
                    required
                    data-kbType="positiveNumber"
                  ></v-text-field>
                </v-flex>
                  
                <v-flex xs6>
                  <select-units
                    v-model="loadParams.units"
                    required
                    :rules="[v => !!v || 'Units is required']"
                  ></select-units>
                </v-flex>
                
                <v-flex xs12>
                  <v-slider
                    v-model="loadParams.percent"
                    min="1"
                    max="100"
                    step="1"
                    thumb-label="always"
                    always-dirty
                    required
                    prepend-icon="mdi-minus"
                    @click:prepend="loadParams.percent -= 1"
                    append-icon="mdi-plus"
                    @click:append="loadParams.percent += 1"
                  ></v-slider>
                </v-flex>
                
                <v-flex xs12>
                  Amount: {{loadParamsAmount}}
                </v-flex>
                
              </v-layout>
            </v-container>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            flat
            @click="closeAll()">cancel</v-btn>
          <v-btn
            v-if="!isReload"
            flat
            :disabled="!valid"
            @click="submitLoad()">next</v-btn>
          <v-btn
            v-else
            flat
            :disabled="!valid"
            @click="submitLoad()">load</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="primeDialog" persistent scrollable @keydown.esc.prevent="closePrime">
      <v-card>
        <v-card-title>
          <span class="headline">Prime Pump {{pump.name}}</span>
        </v-card-title>
        
        <v-card-text>
        
          <v-container fluid>
            <v-layout column>
        
              <v-flex class="text-xs-center mb-3">
                <p v-if="isAutoPrime">Insert the pump tube into the ingredient container.</p>
                <p v-if="!dispenserGlass" class="red--text">Place a glass in the dispensing area.</p>
              </v-flex>
              
              <v-flex class="text-xs-center">
              
                <v-btn
                  v-if="isAutoPrime"
                  color="green"
                  large
                  class="px-5"
                  :loading="!dispenserGlass || pump.running"
                  :disabled="!dispenserGlass || pump.running"
                  @click="primePump()"
                >
                  autoprime
                  <span slot="loader">Waiting...</span>
                </v-btn>
                
                <v-btn
                  v-else
                  color="green"
                  large
                  class="px-5"
                  :loading="!dispenserGlass"
                  :disabled="!dispenserGlass"
                  @mousedown="startPump()"
                  @touchstart="startPump()"
                  @mouseup="stopPump()"
                  @touchend="stopPump()"
                >
                  prime
                  <span slot="loader">Waiting...</span>
                </v-btn>
                
              </v-flex>
                
            </v-layout>
          </v-container>
                
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            flat
            @click="closeAll()">close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="cleanDialog" persistent scrollable @keydown.esc.prevent="closeClean">
      <v-card>
        <v-card-title>
          <span class="headline">Clean Pump {{pump.name}}</span>
        </v-card-title>
        
        <v-card-text>
        
          <v-container fluid>
            <v-layout column>
        
              <v-flex class="text-xs-center mb-3">
                <p>Insert the pump tube into a container of clean water.</p>
                <p v-if="!dispenserGlass" class="red--text">Place a glass in the dispensing area.</p>
              </v-flex>
              
              <v-flex class="text-xs-center">
                <v-btn
                  color="green"
                  large
                  :loading="!dispenserGlass || pump.running"
                  :disabled="!dispenserGlass || pump.running"
                  @click="cleanPump()"
                >
                  clean
                  <span slot="loader">Waiting...</span>
                </v-btn>
                <v-btn
                  color="green"
                  large
                  :loading="!dispenserGlass || pump.running"
                  :disabled="!dispenserGlass || pump.running"
                  @click="drainPump()"
                >
                  drain
                  <span slot="loader">Waiting...</span>
                </v-btn>
              </v-flex>
              
              <v-flex class="text-xs-center">
                <v-btn
                  v-if="!pump.running"
                  color="green"
                  large
                  @click="startPump()"
                >
                  flush
                </v-btn>
                <v-btn
                  v-else
                  color="red"
                  large
                  @click="stopPump()"
                >
                  stop
                </v-btn>
              </v-flex>
        
            </v-layout>
          </v-container>
                
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            flat
            @click="closeAll()">close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

  </div>
</template>

<script>

import { mapState } from 'vuex'
import SelectIngredient from '../components/SelectIngredient'
import SelectUnits from '../components/SelectUnits'
import bus from '../bus'
import units from '../units'

export default {
  name: 'PumpWizardDialog',
  props: ['pump'],
  
  data() {
    return {
      valid: false,
      
      loadDialog: false,
      ingredientHasNoDrinks: false,    
      loadParams: {},
      isReload: false,
      
      primeDialog: false,
      isAutoPrime: false,
      
      cleanDialog: false,
    }
  },
  
  components: {
    SelectIngredient,
    SelectUnits,
  },

  computed: {
    loadParamsIngredientId() {
      return this.loadParams.ingredient_id
    },
    loadParamsPercent() {
      return this.loadParams.percent
    },
    loadParamsContainerAmount() {
      return this.loadParams.containerAmount
    },
    loadParamsAmount() {
      if (this.loadParams.containerAmount)
        return units.format(this.loadParams.containerAmount * this.loadParams.percent / 100, this.loadParams.units)
      else
        return ''
    },
    pumpRunning() {
      return this.pump.running
    },
    ...mapState({
      dispenserGlass: state => state.dispenser.glass,
    }),
  },
  
  watch: {
    loadParamsIngredientId(v) {
      if (v && (! this.isReload)) {
        this.$store.dispatch('ingredients/getOne', v).then((i) => {
          if (i.lastContainerAmount) {
            this.loadParams.containerAmount = i.lastContainerAmount
            this.loadParams.units = i.lastUnits
            this.loadParams.amount = i.lastAmount
            this.loadParams.percent = Math.round((i.lastAmount / i.lastContainerAmount) * 100)
          }
          this.ingredientHasNoDrinks = i.drinks.length == 0
        })
      }
    },
    loadParamsContainerAmount() {
      this.loadParamsAmountRecalculate()
    },
    loadParamsPercent() {
      this.loadParamsAmountRecalculate()
    },
    pumpRunning(v) {
      if (!v && this.isAutoPrime)
        this.isAutoPrime = false
    },
  },
  
  methods: {

    openLoad() {
      bus.$emit('keyboard-install', this.$refs.loadForm)
      this.$refs.loadForm.reset()
      this.ingredientHasNoDrinks = false
      if (! this.pump.state) {
        this.isReload = false
        this.loadParams = {
          pump_id: this.pump.id,
          containerAmount: undefined,
          units: units.defaultUnits(),
          percent: 50,
          ingredient_id: undefined,
          amount: 0,
        }
      } else if ((this.pump.state == 'ready') || (this.pump.state == 'empty')) {
        this.isReload = true
        this.loadParams = {
          pump_id: this.pump.id,
          containerAmount: this.pump.containerAmount,
          units: this.pump.units,
          ingredient_id: this.pump.ingredient_id,
          amount: this.pump.containerAmount,
          percent: 100,
        }
      }
      this.loadDialog = true
    },
    
    closeLoad() {
      if (this.loadDialog) {
        this.$refs.loadForm.reset()
        this.loadParams = {}
        this.loadDialog = false
        bus.$emit('keyboard-remove', this.$refs.loadForm)
      }
    },
    
    submitLoad() {
      if (! this.$refs.loadForm.validate()) return
      
      let amount = +(this.loadParams.containerAmount)
      if (isNaN(amount)) {
        this.$store.commit('setError', 'Invalid container amount!')
        return
      }
      this.loadParams.containerAmount = amount
      
      this.$socket.emit('pump_load', this.loadParams, (res) => {
        if (res.error) {
            this.$store.commit('setError', res.error)
        } else {
          this.closeLoad()
          if (! this.isReload)
            this.openPrime()
        }
      })
    },

    loadParamsAmountRecalculate() {
      if (this.loadParams.containerAmount)
        this.loadParams.amount = this.loadParams.containerAmount * this.loadParams.percent / 100
      else
        this.loadParams.amount = 0
    },
    
    openPrime() {
      if (this.pump.state == 'loaded')
        this.isAutoPrime = true
      else
        this.isAutoPrime = false
      this.primeDialog = true
    },
    
    primePump() {
      this.$socket.emit('pump_prime', this.pump.id, (res) => {
        if (res.error) {
            this.$store.commit('setError', res.error)
        }
      })
    },

    closePrime() {
      this.primeDialog = false
    },

    openClean() {
      this.cleanDialog = true
    },
    
    closeClean() {
      this.cleanDialog = false
    },
    
    cleanPump() {
      this.$socket.emit('pump_clean', this.pump.id, (res) => {
        if (res.error) {
            this.$store.commit('setError', res.error)
        }
      })
    },
    
    drainPump() {
      this.$socket.emit('pump_drain', this.pump.id, (res) => {
        if (res.error) {
            this.$store.commit('setError', res.error)
        }
      })
    },

    startPump() {
      this.$socket.emit('dispenser_startPump', {'id': this.pump.id}, (res) => {
        if (res.error) {
            this.$store.commit('setError', res.error)
        }
      })
    },
    
    stopPump() {
      this.$socket.emit('dispenser_stopPump', this.pump.id, (res) => {
        if (res.error) {
            this.$store.commit('setError', res.error)
        }
      })
    },
    
    
    closeAll() {
      this.closeLoad()
      this.closePrime()
      this.closeClean()
    },
    
  },
  
}

</script>
