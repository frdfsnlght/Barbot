import Vue from 'vue'

export default {
    namespaced: true,
    
    state: {
        drinks: null,
        loading: false,
    },
    
    getters: {
        
        sortedDrinks(state) {
            if (state.drinks)
                return state.drinks.slice().sort((a, b) => {
                    return a.name.localeCompare(b.name, 'en', {'sensitivity': 'base'})
                })
            else
                return []
        }
    },
  
    mutations: {
        
        loading(state) {
            state.loading = true
        },
        
        setDrinks(state, drinks) {
            state.drinks = drinks
            state.loading = false
        },
        
        destroy(state) {
            state.drinks = null
        },
        
        socket_drink_changed(state, drink) {
            if (state.drinks) {
                let d = state.drinks.find((e) => { return e.id === drink.id })
                if (d) {
                    Object.assign(d, drink)
                    this.commit('notify', 'Drink updated', {root: true})
                }
            }
        },

        socket_drink_deleted(state, drink) {
            if (state.drinks) {
                let d = state.drinks.find((e) => { return e.id === drink.id })
                if (d) {
                    let i = state.drinks.indexOf(d)
                    if (i != -1) {
                        state.drinks.splice(i, 1)
                        this.commit('notify', 'Drink deleted', {root: true})
                    }
                }
            }
        },

        socket_drink_menuChanged(state) {
            if (state.drinks) {
                this.dispatch('getAll').then(() => {
                    this.commit('notify', 'Drinks menu updated', {root: true})
                })
            }
        },
        
    },
    
    actions: {
        
        getAll({commit, state}) {
            return new Promise((resolve, reject) => {
                if (state.drinks)
                    resolve()
                else {
                    commit('loading')
                    Vue.prototype.$socket.emit('drink_getMenu', (res) => {
                        if (res.error) {
                            commit('setError', res.error, {root: true})
                            reject()
                        } else {
                            commit('setDrinks', res.drinks)
                            resolve(res.drinks)
                        }
                    })
                }
            })
        },
        
    }
    
}
