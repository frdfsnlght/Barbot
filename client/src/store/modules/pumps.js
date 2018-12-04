import Vue from 'vue'

export default {
    namespaced: true,
    
    state: {
        items: [],
        loading: false,
        loadedAll: false,
    },
    
    getters: {
        sortedItems(state) {
            return state.items.slice().sort((a, b) => {
                return a.id - b.id
            })
        },
        sortedReadyPumps(state) {
            return state.items.filter(p => { return (p.state == 'ready') }).sort((a, b) => {
                return a.id - b.id
            })
        },
        anyPumpRunning(state) {
            let i = state.items.find((e) => { return e.running })
            return !!i
        },
        anyPumpReady(state) {
            let i = state.items.find((e) => { return e.state == 'ready' })
            return !!i
        },
        getPump(state) {
            return (id) => {
                return state.items.find((e) => { return e.id === id })
            }
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
        
        socket_pump_changed(state, item) {
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
        
    },
    
    actions: {
        
        loadAll({commit, state}) {
            if (state.loadedAll) return
            commit('loading')
            Vue.prototype.$socket.emit('pump_getAll', (res) => {
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
