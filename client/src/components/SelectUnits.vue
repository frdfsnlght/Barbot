<template>

  <v-select
    v-bind="this.$attrs"
    :items="unitsList"
    label="Units"
    v-model="units"
  ></v-select>

</template>

<script>

import units from '../units'

export default {
  name: 'SelectUnits',
  props: {
    value: {
      type: String,
    },
  },
  
  computed: {
    unitsList() {
      return units.units()
    },
  },
  
  data: function() {
    return {
      units: this.value, // only sets initial value!
    }
  },
  
  watch: {
    value: function(v) {
      this.units = v  // update when prop changes!
    },
    units: function(v) {
      this.$emit('input', v)
    },
  },
  
}
</script>
