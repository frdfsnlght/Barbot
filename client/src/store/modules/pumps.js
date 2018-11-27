import Vue from 'vue'

export default {
    namespaced: true,
    
    state: {
        items: [],
        loading: false,
        loadedAll: false,
        setup: false,
        flushing: false,
    },
    
    getters: {
        sortedItems(state) {
            return state.items.slice().sort((a, b) => {
                return a.id - b.id
            })
        },
        sortedFlushablePumps(state) {
            return state.items.filter(p => { return (! p.state) || (p.state == 'dirty') }).sort((a, b) => {
                return a.id - b.id
            })
        },
        sortedReadyPumps(state) {
            return state.items.filter(p => { return (p.state == 'ready') }).sort((a, b) => {
                return a.id - b.id
            })
        },
        anyPumpRunning(state) {
            if (state.flushing) return true
            let i = state.items.find((e) => { return e.running })
            return !!i
        },
        anyPumpReady(state) {
            let i = state.items.find((e) => { return e.state == 'ready' })
            return !!i
        },
    },
  
    mutations: {
        loading(state) {
            state.loading = true
        },
        
        loadedAll(state, items) {
            state.items = items
            state.loading = false
            state.loadedAll = true
        },
        
        destroy(state) {
            state.items = []
            state.item = {}
            state.loadedAll = false
        },
        
        socket_pumpSaved(state, item) {
            if (state.loadedAll) {
                let i = state.items.find((e) => { return e.id === item.id })
                if (i) {
                    Object.assign(i, item)
                }
            }
        },

        socket_pumps(state, pumps) {
            state.items = pumps
            state.loading = false
            state.loadedAll = true
        },
        
        socket_pumps_setup(state, setup) {
            state.setup = setup
        },

        socket_pumps_flushing(state, flushing) {
            state.flushing = flushing
        },

    },
    
    actions: {
        
        loadAll({commit, state}) {
            if (state.loadedAll) return
            commit('loading')
            Vue.prototype.$socket.emit('getPumps', (res) => {
                if (res.error) {
                    commit('setError', res.error, {root: true})
                    commit('loadedAll', [])
                } else {
                    commit('loadedAll', res.items)
                }
            })
        },
        
    }
    
}
