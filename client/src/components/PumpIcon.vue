<template>
  <v-icon v-if="pump.running" class="pumpIcon green--text">mdi-refresh</v-icon>
  <v-icon v-else-if="!pump.state" class="pumpIcon">mdi-close</v-icon>
  <v-icon v-else-if="pump.state=='loaded'" class="pumpIcon">mdi-plus</v-icon>
  <v-icon v-else-if="pump.state=='ready'" class="pumpIcon">mdi-check</v-icon>
  <v-icon v-else-if="pump.state=='empty'" class="pumpIcon red--text">mdi-battery-outline</v-icon>
  <v-icon v-else-if="pump.state=='dirty'" class="pumpIcon">mdi-spray-bottle</v-icon>
</template>

<style>
.pumpIcon {
  font-size: 22px;
  margin: 0 0.1vw;
  border: 0.1em solid #757575;
  border-radius: 50%;
}

</style>

<script>

export default {
  name: 'PumpIcon',
  props: {
    pump: Object,
  },
}

</script>
