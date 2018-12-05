import Vue from 'vue'

export default {
    namespaced: true,
    
    state: {
        pumps: null,
        loading: false,
    },
    
    getters: {
        
        sortedPumps(state) {
            if (state.pumps)
                return state.pumps.slice().sort((a, b) => {
                    return a.id - b.id
                })
            else
                return []
        },
        sortedReadyPumps(state) {
            if (state.pumps)
                return state.pumps.filter(p => { return (p.state == 'ready') }).sort((a, b) => {
                    return a.id - b.id
                })
            else
                return []
        },
        anyPumpRunning(state) {
            if (state.pumps)
                return !! state.pumps.find((e) => { return e.running })
            else
                return false
        },
        anyPumpReady(state) {
            if (state.pumps)
                return !! state.pumps.find((e) => { return e.state == 'ready' })
            else
                return false
        },
        getPump(state) {
            return (id) => {
                return state.pumps.find((e) => { return e.id === id })
            }
        },
        
    },
  
    mutations: {
        
        loading(state) {
            state.loading = true
        },
        
        setPumps(state, pumps) {
            state.pumps = pumps
            state.loading = false
        },
        
        destroy(state) {
            state.pumps = null
        },
        
        socket_pump_changed(state, pump) {
            if (state.pumps) {
                let i = state.pumps.find((e) => { return e.id === pump.id })
                if (i) {
                    Object.assign(i, pump)
                }
            }
        },
        
        socket_pumps(state, pumps) {
            state.pumps = pumps
            state.loading = false
        },
        
    },
    
    actions: {
        
        getAll({commit, state}) {
            return new Promise((resolve, reject) => {
                if (state.pumps)
                    resolve()
                else {
                    commit('loading')
                    Vue.prototype.$socket.emit('pump_getAll', (res) => {
                        if (res.error) {
                            commit('setError', res.error, {root: true})
                            reject()
                        } else {
                            commit('loadedAll', res.items)
                            resolve()
                        }
                    })
                }
            })
        },
        
    }
    
}
