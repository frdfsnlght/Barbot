<template>
  <v-fade-transition mode="out-in">
    <v-footer
      height="auto"
      v-show="visible"
      color="secondary lighten-3"
      @mousedown.prevent=""
      style="z-index: 400"
      fixed
    >
      <v-layout
        justify-center
        row
        @mousedown.prevent=""
      >
        <keyboard
          ref="keyboard"
          @show="visible = true"
          @hide="visible = false"
        />
      </v-layout>
    </v-footer>
  </v-fade-transition>
</template>

<script>

import Keyboard from './Keyboard'
import bus from '../bus'

export default {
  name: 'KeyboardOverlay',
  
  data() {
    return {
      visible: false,
    }
  },

  components: {
    Keyboard,
  },
  
  created() {
    bus.$on('keyboard-install', (c) => {
      this.$refs.keyboard.installHooks(c.$el)
    })
    bus.$on('keyboard-remove', (c) => {
      this.$refs.keyboard.removeHooks(c.$el)
    })
  },
  
}

</script>
