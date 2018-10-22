<template>

  <v-autocomplete
    v-bind="this.$attrs"
    :items="['oz', 'ml']"
    label="Units"
    v-model="units"
  ></v-autocomplete>

</template>

<script>

export default {
  name: 'SelectUnits',
  props: {
    value: {
      type: String,
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
  
  computed: {
  },
  
  created() {
  },
  
  destroyed() {
  },
  
  methods: {
  },

}
</script>
