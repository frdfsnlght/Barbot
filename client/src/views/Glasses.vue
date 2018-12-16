<template>

  <v-card flat style="height: 92.5vh; overflow-y: auto;">
    
    <loading v-if="loading"></loading>
    
    <p
      v-else-if="!glasses.length"
      class="title text-xs-center ma-3"
    >
      No glasses are currently available.
    </p>
    
    <template v-else>
    
      <v-list two-line>
        <v-list-tile
          v-for="glass in glasses"
          :key="glass.id"
          ripple
          @click="gotoDetail(glass)"
        >
          <v-list-tile-content>
            <v-list-tile-title>{{glass.size}} {{glass.units}} {{glass.type}}</v-list-tile-title>
            <v-list-tile-sub-title>{{glass.description}}</v-list-tile-sub-title>
          </v-list-tile-content>
          
          <v-list-tile-action>
            <v-btn
              icon
              @click.stop="showMenu(glass, $event)"
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
          <v-list-tile ripple @click="editGlass()">
            <v-list-tile-content>
              <v-list-tile-title>Edit</v-list-tile-title>
            </v-list-tile-content>
            <v-list-tile-action>
              <v-icon>mdi-pencil</v-icon>
            </v-list-tile-action>
          </v-list-tile>
          
          <v-list-tile ripple @click="deleteGlass()">
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
        @click="addGlass"
      >
        <v-icon dark>mdi-plus</v-icon>
      </v-btn>
    </template>
    
    <v-dialog v-model="dialog" persistent scrollable @keydown.esc="closeDialog" @keydown.enter.prevent="saveGlass">
      <v-card>
        <v-card-title>
          <span
            v-if="edit"
            class="headline"
          >Edit Glass</span>
          <span
            v-else
            class="headline"
          >Add Glass</span>
        </v-card-title>
        <v-card-text>
          <v-form ref="form" v-model="valid" lazy-validation>
            <v-container grid-list-md>
              <v-layout wrap>
              
                <v-flex xs12>
                  <v-text-field
                    label="Type"
                    v-model="glass.type"
                    :rules="[v => !!v || 'Type is required']"
                    required
                    autofocus
                    :data-kbUCWords="true"
                    tabindex="1"
                  ></v-text-field>
                </v-flex>
                
                <v-flex xs6>
                  <v-text-field
                    label="Size"
                    mask="##"
                    v-model="glass.size"
                    :rules="[v => !!v || 'Size is required']"
                    required
                    data-kbType="positiveInteger"
                    tabindex="2"
                  ></v-text-field>
                </v-flex>
                
                <v-flex xs6>
                  <select-units
                    v-model="glass.units"
                    required
                    :rules="[v => !!v || 'Units is required']"
                  ></select-units>
                </v-flex>

                <v-flex xs12>
                  <v-textarea
                    label="Description"
                    auto-grow
                    v-model="glass.description"
                    :data-kbUCFirst="true"
                    tabindex="3"
                  ></v-textarea>
                </v-flex>
    
              </v-layout>
            </v-container>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            flat
            @click="closeDialog()">close</v-btn>
          <v-btn
            :disabled="!valid"
            flat
            @click="saveGlass()">save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <confirm-dialog ref="confirmDialog"/>
      
  </v-card>
        
</template>

<script>

import { mapState, mapGetters } from 'vuex'
import Loading from '../components/Loading'
import ConfirmDialog from '../components/ConfirmDialog'
import SelectUnits from '../components/SelectUnits'
import bus from '../bus'

export default {
  name: 'Glasses',
  data() {
    return {
      glass: {},
      dialog: false,
      edit: false,
      valid: true,
      menu: false,
      menuX: 0,
      menuY: 0,
    }
  },
  components: {
    Loading,
    ConfirmDialog,
    SelectUnits
  },
  created() {
    this.$emit('show-page', 'Glasses')
  },
  
  computed: {
    ...mapGetters({
      glasses: 'glasses/sortedGlasses'
    }),
    ...mapState({
      loading: state => state.glasses.loading,
    })
  },
  
  methods: {
  
    gotoDetail(glass) {
      this.$router.push({name: 'glassDetail', params: {id: glass.id}})
    },
  
    showMenu(glass, e) {
      this.$refs.form.reset()
      this.glass = JSON.parse(JSON.stringify(glass))
      this.menuX = e.clientX
      this.menuY = e.clientY
      this.menu = true
    },
    
    addGlass() {
      this.$refs.form.reset()
      this.glass = {
        id: undefined,
        type: undefined,
        size: undefined,
        units: 'oz',
        description: undefined
      }
      this.edit = false
      bus.$emit('keyboard-install', this.$refs.form)
      this.dialog = true
    },
    
    editGlass() {
      this.edit = true
      bus.$emit('keyboard-install', this.$refs.form)
      this.dialog = true
    },
    
    closeDialog() {
      this.dialog = false
      this.glass = {}
      bus.$emit('keyboard-remove', this.$refs.form)
    },
    
    saveGlass() {
      if (! this.$refs.form.validate()) return
//      glass = JSON.parse(JSON.stringify(this.glass))
      if (typeof(this.glass.size) == 'string')
        this.glass.size = parseInt(this.glass.size)
      this.$socket.emit('glass_save', this.glass, (res) => {
        if (res.error) {
          this.$store.commit('setError', res.error)
        } else {
          this.closeDialog()
        }
      })
    },
    
    deleteGlass() {
      this.$refs.confirmDialog.open('Delete', 'Are you sure you want to delete "' + this.glass.size + ' ' + this.glass.units + ' ' + this.glass.type + '"?').then(() => {
        this.$socket.emit('glass_delete', this.glass.id, (res) => {
          if (res.error) {
            this.$store.commit('setError', res.error)
          }
        })
      }, ()=>{})
    },
    
  },
  
  beforeRouteEnter(to, from, next) {
    next(t => {
      t.$store.dispatch('glasses/getAll')
    });
  },
  
  beforeRouteLeave(to, from, next) {
    this.$store.commit('glasses/destroy')
    next()
  }
  
}

</script>
