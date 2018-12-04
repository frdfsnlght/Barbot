import Vue from 'vue'

export default {
    namespaced: true,
    
    state: {
        glasses: null,
        glass: {},
        loading: false,
    },
    
    getters: {
        
        sortedGlasses(state) {
            if (state.glasses)
                return state.glasses.slice().sort((a, b) => {
                    if (a.size < b.size) return -1
                    if (a.size > b.size) return 1
                    if (a.units < b.units) return -1
                    if (a.units > b.units) return 1
                    return a.type.localeCompare(b.type, 'en', {'sensitivity': 'base'})
                })
            else
                return []
        }
        
    },
  
    mutations: {
        
        loading(state) {
            state.loading = true
        },
        
        setGlasses(state, glasses) {
            state.glasses = glasses
            state.loading = false
        },
  
        setGlass(state, glass) {
            state.glass = glass
            state.loading = false
        },
  
        destroy(state) {
            state.glasses = null
            state.glass = {}
        },
        
        socket_glass_changed(state, glass) {
            if (state.glasses) {
                let g = state.glasses.find((e) => { return e.id === glass.id })
                if (g) {
                    Object.assign(g, glass)
                    this.commit('notify', 'Glass updated', {root: true})
                } else {
                    state.glasses.push(glass)
                    this.commit('notify', 'Glass added', {root: true})
                }
            }
            if (state.glass.id === glass.id) {
                state.glass = glass
                this.commit('notify', 'Glass updated', {root: true})
            }
        },

        socket_glass_deleted(state, glass) {
            if (state.glasses) {
                let g = state.glasses.find((e) => { return e.id === glass.id })
                if (g) {
                    let i = state.glasses.indexOf(g)
                    if (i != -1) {
                        state.glasses.splice(i, 1)
                        this.commit('notify', 'Glass deleted', {root: true})
                    }
                }
            }
            if (state.glass.id === glass.id) {
                state.glass = null
                this.commit('notify', 'Glass deleted', {root: true})
            }
        },

    },
    
    actions: {
        
        getAll({commit, state}) {
            return new Promise((resolve, reject) => {
                if (state.glasses)
                    resolve()
                else {
                    commit('loading')
                    Vue.prototype.$socket.emit('glass_getAll', (res) => {
                        if (res.error) {
                            commit('setError', res.error, {root: true})
                            reject()
                        } else {
                            commit('setGlasses', res.glasses)
                            resolve(res.glasses)
                        }
                    })
                }
            })
        },
        
        getOne({commit}, id) {
            return new Promise((resolve, reject) => {
                commit('loading')
                Vue.prototype.$socket.emit('glass_getOne', id, (res) => {
                    if (res.error) {
                        commit('setError', res.error, {root: true})
                        reject()
                    } else {
                        commit('setGlass', res.glass)
                        resolve(res.glass)
                    }
                })
            })
        },
        
    }
    
}
