<template>

  <v-dialog v-model="dialog" persistent scrollable max-width="300px" @keydown.esc="cancel" @keydown.enter="login">
    <v-card>
      <v-card-title>
        <span class="headline">Login</span>
      </v-card-title>
      
      <v-card-text>
        <v-form ref="form" v-model="valid" lazy-validation>
          <v-container grid-list-md>
            <v-layout wrap>
            
              <v-flex xs12>
                <v-text-field
                  label="Username"
                  v-model="name"
                  required
                  :rules="[v => !!v || 'Username is required']"
                ></v-text-field>
              </v-flex>
              
              <v-flex xs12>
                <v-text-field
                  label="Password"
                  v-model="password"
                  :append-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                  :type="showPassword ? 'text' : 'password'"
                  autofocus
                  required
                  :error-messages="loginError"
                  @click:append="showPassword = !showPassword"
                  :rules="[v => !!v || 'Password is required']"
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
          @click="login()">login</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
  
</template>

<script>

export default {
  name: 'Login',
  data() {
    return {
      dialog: false,
      resolve: null,
      reject: null,
      name: null,
      password: null,
      showPassword: false,
      valid: true,
      loginError: [],
    }
  },

  methods: {
  
    open() {
      this.$refs.form.reset()
      this.name = 'admin'
      this.password = null
      this.dialog = true
      return new Promise((resolve, reject) => {
        this.resolve = resolve
        this.reject = reject
      })
    },

    login() {
      if (! this.$refs.form.validate()) return
      let params = {
        name: this.name,
        password: this.password
      }
      this.$socket.emit('login', params, (res) => {
        if (res.error) {
          this.loginError = [res.error]
        } else {
          this.$store.commit('setUser', res.user)
          this.dialog = false
          this.resolve()
        }
      })
    },

    logout() {
      return new Promise((resolve, reject) => {
        this.$socket.emit('logout', (res) => {
          if (res.error) {
            console.error(res.error)
            reject()
          } else {
            this.$store.commit('setUser', false)
            resolve()
          }
        })
      })
    },
    
    cancel() {
      this.reject()
      this.dialog = false
    }
  }
}

</script>
