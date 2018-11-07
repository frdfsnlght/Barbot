<template>
  <v-icon v-if="!wifiOn">mdi-wifi-off</v-icon>
  <v-icon v-else-if="bars === 0">mdi-wifi-strength-outline</v-icon>
  <v-icon v-else-if="bars === 1">mdi-wifi-strength-1</v-icon>
  <v-icon v-else-if="bars === 2">mdi-wifi-strength-2</v-icon>
  <v-icon v-else-if="bars === 3">mdi-wifi-strength-3</v-icon>
  <v-icon v-else-if="bars === 4">mdi-wifi-strength-4</v-icon>
</template>

<script>

export default {
  name: 'WifiSignalIcon',
  
  props: {
    wifiOn: Boolean,
    bars: Number,
  },
    
}

</script>
