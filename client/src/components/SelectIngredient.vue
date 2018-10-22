<template>

  <v-autocomplete
    v-bind="this.$attrs"
    :items="ingredients"
    label="Ingredient"
    item-text="name"
    item-value="id"
    v-model="id"
  ></v-autocomplete>
          
</template>

<script>

import { mapGetters } from 'vuex'

export default {
  name: 'SelectIngredient',
  props: {
    value: {
      type: Number,
    },
  },
  
  data: function() {
    return {
      id: this.value, // only sets initial value!
    }
  },
  
  watch: {
    value: function(v) {
      this.id = v  // update when prop changes!
    },
    id: function(v) {
      this.$emit('input', v)
    },
  },
  
  computed: {
    ...mapGetters({
      ingredients: 'ingredients/sortedItems'
    }),
  },
  
  mounted() {
    this.$store.dispatch('ingredients/loadAll')
  },
  
  destroyed() {
    this.$store.commit('ingredients/destroy')
  },
  
  methods: {
  },

}
</script>
