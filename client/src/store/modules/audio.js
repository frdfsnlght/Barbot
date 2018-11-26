
export default {
    namespaced: true,
    
    state: {
        volume: 1,
    },
    
    mutations: {
        
        socket_audio_volume(state, volume) {
            state.volume = volume
        },
        
    },
    
}
