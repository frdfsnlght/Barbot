<template>
  <v-snackbar
    v-model="visible"
    :color="notificationColor"
    :timeout="notificationTimeout"
  >
    {{notification}}
    <v-btn
      dark
      flat
      icon
      @click="clearNotification()"
    >
      <v-icon>mdi-close</v-icon>
    </v-btn>
  </v-snackbar>
</template>

<script>

import { mapState } from 'vuex'

export default {
  name: 'Notifier',
  
  computed: {
    visible: {
      get() {
        return !! this.notification
      },
      set() {}
    },
    ...mapState([
      'notification',
      'notificationColor',
      'notificationTimeout',
    ]),
  },

  methods: {
    clearNotification() {
      this.$store.commit('clearNotification')
    },
  },
  
}

</script>
