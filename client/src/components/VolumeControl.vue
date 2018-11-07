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
          append-icon="mdi-plus"
          @end="changeVolume"
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
        return this.$store.state.volume
      },
      set() {}
    },
  },

  methods: {
    changeVolume(v) {
      this.$emit('changed', v)
    },
  },
  
}

</script>
