<template>
  <audio ref="volumeEl" src="../assets/volume.wav" type="audio/wav"></audio>
</template>

<script>

import { mapState } from 'vuex'

export default {
  name: 'AudioPlayer',
  
  computed: {
    ...mapState([
      'volume',
    ]),
  },
      
  methods: {
    play(file) {
      let audio = new Audio(this.$socket.io.uri + '/audio/' + file)
      audio.volume = this.volume
      audio.play()
    },
    
    setVolume(volume, play = true) {
      this.$socket.emit('setVolume', volume, (res) => {
        if (res.error) {
          this.$store.commit('setError', res.error)          
        } else if (play) {
          let a = this.$refs.volumeEl
          if (! a.ended) {
            a.pause()
            a.currentTime = 0
          }
          a.volume = this.volume
          a.play()
        }
      })
    }
  },
  
  sockets: {
    playAudio(file) {
      this.play(file)
    },
  },
  
  render: function(h) {
    return h()
  }
}

</script>
