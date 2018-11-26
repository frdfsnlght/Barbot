<template>
  <v-menu
    bottom left
    offset-y
    :close-on-content-click="false"
  >
    <v-btn
      slot="activator"
      dark
      icon
    >
      <v-icon v-if="volume < 0.33">mdi-volume-low</v-icon>
      <v-icon v-else-if="volume >= 0.33 && volume < 0.66">mdi-volume-medium</v-icon>
      <v-icon v-else>mdi-volume-high</v-icon>
    </v-btn>
    <v-list>
      <v-list-tile>
        <v-slider
          v-model="volume"
          min="0"
          max="1"
          step="0.05"
          prepend-icon="mdi-minus"              
          @click:prepend="volumeDown"              
          append-icon="mdi-plus"
          @click:append="volumeUp"              
        ></v-slider>
      </v-list-tile>
    </v-list>
  </v-menu>
</template>

<script>

export default {
  name: 'VolumeControl',

  computed: {
    volume: {
      get() {
        return this.$store.state.audio.volume
      },
      set(v) {
        this.$socket.emit('audio_setVolume', v, (res) => {
          if (res.error)
            this.$store.commit('setError', res.error)
        })
      }
    },
  },

  methods: {
    volumeDown() {
      this.volume = this.volume - 0.05
    },
    
    volumeUp() {
      this.volume = this.volume + 0.05
    },
  },
  
}

</script>
