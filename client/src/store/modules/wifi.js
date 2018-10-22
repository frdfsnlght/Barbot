import Vue from 'vue'

export default {
    namespaced: true,
    
    state: {
        state: false,
        networks: [],
        networksLoading: false,
        networksLoaded: false,
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
            state.networksLoaded = false
            console.log('loading networks...')
        },
        
        networksLoaded(state, networks) {
            state.networks = networks
            state.networksLoading = false
            state.networksloaded = true
            console.log('loaded ' + networks.length + ' networks')
            console.dir(networks)
        },
        
        destroyNetworks(state) {
            state.networks = []
            state.networksLoaded = false
            console.log('destroyed networks')
        },
        
        socket_wifiState(state, wifi) {
            state.state = wifi
        },
        
    },
    
    actions: {
        
        loadNetworks({commit, state}) {
            if (state.networksLoaded) return
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
        
    }
    
}
