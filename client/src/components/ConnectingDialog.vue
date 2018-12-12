<template>
  <v-dialog
    v-model="visible"
    persistent
    style="z-index: 999"
  >
    <v-card
      color="primary"
      dark
    >
      <v-card-text>
        Attempting to connect...
        <v-progress-linear
          indeterminate
          color="white"
          class="mb-0"
        ></v-progress-linear>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>

export default {
  name: 'ConnectingDialog',
  
  computed: {
    visible: {
      get() {
        return ! this.$store.state.connected
      },
      set() {}
    },
  },

}

</script>
