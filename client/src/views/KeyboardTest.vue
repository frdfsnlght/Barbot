<template>

  <v-card flat class="pa-3">
    
    <v-text-field
      label="Text"
      v-model="text"
      tabindex="1"
      :data-kbUCFirst="true"
    ></v-text-field>
    
    <v-text-field
      label="Password"
      v-model="password"
      :append-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
      :type="showPassword ? 'text' : 'password'"
      @click:append="showPassword = !showPassword"
      tabindex="2"
    ></v-text-field>
    
    <v-text-field
      label="Number"
      v-model="number"
      data-kbtype="number"
      tabindex="3"
    ></v-text-field>
    
    <v-text-field
      label="Integer"
      v-model="integer"
      data-kbtype="integer"
      tabindex="4"
      mask="####"
    ></v-text-field>
    
    <v-textarea
      label="Textarea"
      v-model="textarea"
      tabindex="5"
      :data-kbUCFirst="true"
    ></v-textarea>

    <keyboard-test-dialog ref="dialog" />
              
    <v-card-actions>
      <v-spacer/>
      <v-btn
        @click="openDialog()">open</v-btn>
    </v-card-actions>
              
  </v-card>
        
</template>

<script>

import bus from '../bus'
import KeyboardTestDialog from '../components/KeyboardTestDialog'

export default {
  name: 'KeyboardTest',
  data() {
    return {
      text: '',
      password: '',
      showPassword: false,
      number: 0,
      integer: 0,
      textarea: '',
    }
  },
  
  components: {
    KeyboardTestDialog,
  },
  
  methods: {
  
    openDialog() {
      this.$refs.dialog.open()
    },
    
  },
  
  mounted() {
    this.$emit('show-page', 'Keyboard Test')
    bus.$emit('keyboard-install', this)
  },
  
  destroyed() {
    bus.$emit('keyboard-remove', this)
  },
  
}

</script>
