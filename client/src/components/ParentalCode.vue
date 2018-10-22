<template>

  <v-dialog v-model="dialog" persistent scrollable max-width="400px" @keydown.esc="cancel" @keydown.enter="submit">
    <v-card>
      <v-card-title>
        <span class="headline">Set Parental Code</span>
      </v-card-title>
      
      <v-card-text>
        <v-form ref="form" v-model="valid" lazy-validation>
          <v-container grid-list-md>
            <v-layout wrap>
            
              <v-flex xs12>
                <v-text-field
                  label="Code"
                  v-model="code"
                  :append-icon="showCode ? 'mdi-eye-off' : 'mdi-eye'"
                  :type="showCode ? 'text' : 'password'"
                  autofocus
                  required
                  @click:append="showCode = !showCode"
                  :rules="[v => !!v || 'Code is required']"
                ></v-text-field>
              </v-flex>
              
            </v-layout>
          </v-container>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn
          flat
          @click="cancel()">cancel</v-btn>
        <v-btn
          flat
          @click="submit()">submit</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
  
</template>

<script>

export default {
  name: 'ParentalCode',
  data() {
    return {
      dialog: false,
      resolve: null,
      reject: null,
      code: null,
      showCode: false,
      valid: true,
    }
  },

  methods: {
  
    open() {
      this.$refs.form.reset()
      this.code = null
      this.dialog = true
      return new Promise((resolve, reject) => {
        this.resolve = resolve
        this.reject = reject
      })
    },

    submit() {
      if (! this.$refs.form.validate()) return
      this.$socket.emit('setParentalLock', this.code, (res) => {
        if (res.error) {
          this.$store.commit('setError', res.error)          
        } else {
          this.dialog = false
          this.resolve()
        }
      })
    },

    cancel() {
      this.reject()
      this.dialog = false
    },
    
  }
}

</script>
