<template>

  <v-dialog v-model="dialog" persistent scrollable>
    <v-card>
      <v-card-title>
        Keyboard Test
      </v-card-title>
      
      <v-card-text>
        <v-form ref="form">
          <v-container grid-list-md>
            <v-layout wrap>

              <v-flex xs12>
                <v-text-field
                  label="dText"
                  v-model="text"
                  tabindex="1"
                ></v-text-field>
              </v-flex>
                
              <v-flex xs12>
                <v-text-field
                  label="Password"
                  v-model="password"
                  :append-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                  :type="showPassword ? 'text' : 'password'"
                  @click:append="showPassword = !showPassword"
                  tabindex="2"
                ></v-text-field>
              </v-flex>
                
              <v-flex xs12>
                <v-text-field
                  label="Number"
                  v-model="number"
                  data-kbtype="number"
                  tabindex="3"
                ></v-text-field>
              </v-flex>
                
              <v-flex xs12>
                <v-text-field
                  label="Integer"
                  v-model="integer"
                  data-kbtype="integer"
                  tabindex="4"
                  mask="####"
                ></v-text-field>
              </v-flex>
                
              <v-flex xs12>
                <v-textarea
                  label="Textarea"
                  v-model="textarea"
                  tabindex="5"
                ></v-textarea>
              </v-flex>
              
            </v-layout>
          </v-container>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer/>
        <v-btn
          @click="close()">close</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
              
</template>

<script>

import bus from '../bus'

export default {
  name: 'KeyboardTestDialog',
  data() {
    return {
      dialog: false,
      text: '',
      password: '',
      showPassword: false,
      number: 0,
      integer: 0,
      textarea: '',
    }
  },
  
  methods: {
    open() {
      this.dialog = true
      bus.$emit('keyboard-install', this.$refs.form)
    },
    close() {
      this.dialog = false
      bus.$emit('keyboard-remove', this.$refs.form)
    },
  },
  
}

</script>
