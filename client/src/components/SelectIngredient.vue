<template>

  <v-select
    v-bind="this.$attrs"
    :items="ingredients"
    label="Ingredient"
    item-text="name"
    item-value="id"
    v-model="id"
    :data-kbHide="true"
  ></v-select>
          
</template>

<script>

import { mapGetters } from 'vuex'

export default {
  name: 'SelectIngredient',
  props: {
    value: {
      type: Number,
    },
    manageIngredientsStore: {
      type: Boolean,
      default: true
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
      ingredients: 'ingredients/sortedIngredients'
    }),
  },
  
  mounted() {
    if (this.manageIngredientsStore)
      this.$store.dispatch('ingredients/getAll')
  },
  
  destroyed() {
    if (this.manageIngredientsStore)
      this.$store.commit('ingredients/destroy')
  },
  
}
</script>
