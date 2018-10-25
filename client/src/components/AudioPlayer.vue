<template>
  <audio ref="volumeEl" src="../assets/volume.wav" type="audio/wav"></audio>
</template>

<script>

import { mapState } from 'vuex'

export default {
  name: 'AudioPlayer',
  
  data() {
    return {
      player: false,
      playing: false,
      queue: [],
    }
  },
  
  computed: {
    ...mapState([
      'volume',
    ]),
  },
      
  methods: {
  
    playNext() {
      this.playing = false
      let file = this.queue.shift()
      if (file) {
        this.player.src = this.$socket.io.uri + '/audio/' + file
        this.player.volume = this.volume
        this.player.play()
        this.playing = true
      }
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
      this.queue.push(file)
      if (! this.player) {
        this.player = new Audio()
        this.player.onended = this.playNext.bind(this)
        this.playNext()
      } else if (! this.playing) {
        this.playNext()
      }
    },
  },
  
  render: function(h) {
    return h()
  }
}

</script>
