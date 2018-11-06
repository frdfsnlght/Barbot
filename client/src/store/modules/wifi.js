import Vue from 'vue'

export default {
    namespaced: true,
    
    state: {
        state: false,
        networks: [],
        networksLoading: false,
    },
    
    getters: {
        sortedNetworks: (state) => {
            return state.networks.slice().sort((a, b) => {
                if (a.connected) return -1
                if (b.connected) return 1
                if (!a.saved && b.saved) return -1
                if (a.saved && !b.saved) return 1
                if (a.bars > b.bars) return -1
                if (a.bars < b.bars) return 1
                return a.ssid.localeCompare(b.ssid, 'en', {'sensitivity': 'base'})
            })
        }
    },
  
    mutations: {
        
        networksLoading(state) {
            state.networksLoading = true
        },
        
        networksLoaded(state, networks) {
            state.networks = networks
            state.networksLoading = false
        },
        
        destroyNetworks(state) {
            state.networks = []
        },
        
        setWifiState(state, wifi) {
            state.state = wifi
        },
        
    },
    
    actions: {
        
        loadNetworks({commit}) {
            commit('networksLoading')
            Vue.prototype.$socket.emit('getWifiNetworks', (res) => {
                if (res.error) {
                    commit('setError', res.error, {root: true})
                    commit('networksLoaded', [])
                } else {
                    commit('networksLoaded', res.networks)
                }
            })
        },

        socket_wifiState({commit, dispatch, state}, wifi) {
            if (state.networks && state.state && (state.state.ssid != wifi.ssid)) {
                dispatch('loadNetworks')
            }
            commit('setWifiState', wifi)
        },
        
    }
    
}
