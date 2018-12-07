import Vue from 'vue'

export default {
    namespaced: true,
    
    state: {
        drinkOrders: null,
        drinkOrder: {},
        loading: false,
    },
    
    getters: {
        
        sortedDrinkOrders(state) {
            if (state.drinkOrders)
                return state.drinkOrders.slice().sort((a, b) => {
                    if ((! a.userHold) && b.userHold) return -1
                    if (a.userHold && (! b.userHold)) return 1
                    if ((! a.ingredientHold) && b.ingredientHold) return -1
                    if (a.ingredientHold && (! b.ingredientHold)) return 1
                    let da = Date.parse(a.createdDate)
                    let db = Date.parse(b.createdDate)
                    if (da < db) return -1
                    if (da > db) return 1
                    return a.drink.name.localeCompare(b.drink.name, 'en', {'sensitivity': 'base'})
                })
            else
                return []
        }
    },
  
    mutations: {
        
        loading(state) {
            state.loading = true
        },
        
        setWaiting(state, drinkOrders) {
            state.drinkOrders = drinkOrders
            state.loading = false
        },
        
        setOne(state, drinkOrder) {
            state.drinkOrder = drinkOrder
            state.loading = false
        },
        
        destroy(state) {
            state.drinkOrders = null
            state.drinkOrder = {}
        },
        
        socket_drinkOrder_changed(state, drinkOrder) {
            if (state.drinkOrders) {
                let o = state.drinkOrders.find((e) => { return e.id === drinkOrder.id })
                if (o) {
                    if (drinkOrder.startedDate) {
                        let i = state.drinkOrders.indexOf(o)
                        if (i != -1) {
                            state.drinkOrders.splice(i, 1)
                        }
                    } else {
                        Object.assign(o, drinkOrder)
                    }
                } else {
                    if (drinkOrder.startedDate) return
                    state.drinkOrders.push(drinkOrder)
                    this.commit('notify', 'Drink order submitted', {root: true})
                }
            }
            if (state.drinkOrder.id === drinkOrder.id) {
                if (drinkOrder.startedDate) {
                    state.drinkOrder = {}
                } else {
                    Object.assign(state.drinkOrder, drinkOrder)
                }
            }
        },

        socket_drinkOrder_deleted(state, drinkOrder) {
            if (state.drinkOrders) {
                let o = state.drinkOrders.find((e) => { return e.id === drinkOrder.id })
                if (o) {
                    let i = state.drinkOrders.indexOf(o)
                    if (i != -1) {
                        state.drinkOrders.splice(i, 1)
                        this.commit('notify', 'Drink order cancelled', {root: true})
                    }
                }
            }
            if (state.drinkOrder.id === drinkOrder.id) {
                state.drinkOrder = {}
                this.commit('notify', 'Drink order cancelled', {root: true})
            }
        },

    },
    
    actions: {
        
        getWaiting({commit, state}) {
            return new Promise((resolve, reject) => {
                if (state.drinkOrders)
                    resolve()
                else {
                    commit('loading')
                    Vue.prototype.$socket.emit('drinkOrder_getWaiting', (res) => {
                        if (res.error) {
                            commit('setError', res.error, {root: true})
                            reject()
                        } else {
                            commit('setWaiting', res.drinkOrders)
                            resolve(res.drinkOrders)
                        }
                    })
                }
            })
        },
        
        getOne({commit}, id) {
            return new Promise((resolve, reject) => {
                commit('loading')
                Vue.prototype.$socket.emit('drinkOrder_getOne', id, (res) => {
                    if (res.error) {
                        commit('setError', res.error, {root: true})
                        reject()
                    } else {
                        commit('setOne', res.drinkOrder)
                        resolve(res.drinkOrder)
                    }
                })
            })
        },
        
    }
    
}
