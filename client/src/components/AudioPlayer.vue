<template>
  <audio ref="volumeEl" src="../assets/volume.wav" type="audio/wav"></audio>
</template>

<script>

import { mapState } from 'vuex'

export default {
  name: 'AudioPlayer',
  
  data() {
    return {
      suppressVolumeBing: true,
      player: false,
      playing: false,
      queue: [],
    }
  },
  
  computed: {
    ...mapState({
      isConsole: state => state.isConsole,
      volume: state => state.settings.volume,
    }),
  },
  
  watch: {
    volume() {
      if (! this.isConsole) return
      if (this.suppressVolumeBing)
        this.suppressVolumeBing = false
      else {
        let a = this.$refs.volumeEl
        if (! a.ended) {
          a.pause()
          a.currentTime = 0
        }
        a.volume = this.volume
        a.play().then(()=>{},()=>{})
      }
    },
  },
    
  methods: {
  
    playNext() {
      this.playing = false
      let file = this.queue.shift()
      if (file) {
        this.player.src = this.$socket.io.uri + '/audio/' + file
        this.player.volume = this.isConsole ? this.volume : 1
        this.player.play().then(()=>{},()=>{})
        this.playing = true
      }
    },
    
  },
  
  sockets: {
  
    audio_playFile(file) {
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
