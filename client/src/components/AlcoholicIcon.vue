<template>
  <v-icon v-if="alcoholic">mdi-flash</v-icon>
  <v-icon v-else>mdi-baby-buggy</v-icon>
</template>

<script>

export default {
  name: 'AlcoholicIcon',
  props: {
    alcoholic: Boolean,
  },
}

</script>
