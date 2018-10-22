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
                return a.name.localeCompare(b.name, 'en', {'sensitivity': 'base'})
            })
        }
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
            state.loadedAll = false
        },
        
        socket_drinkSaved(state, item) {
            if (state.loadedAll) {
                let d = state.items.find((e) => { return e.id === item.id })
                if (d) {
                    Object.assign(d, item)
                    this.commit('showSnackbar', {text: 'Drink updated'}, {root: true})
                    console.log('updated drink ' + item.id)
                }
            }
        },

        socket_drinkDeleted(state, item) {
            if (state.loadedAll) {
                let d = state.items.find((e) => { return e.id === item.id })
                if (d) {
                    let i = state.items.indexOf(d)
                    if (i != -1) {
                        state.items.splice(i, 1)
                        this.commit('showSnackbar', {text: 'Drink deleted'}, {root: true})
                        console.log('deleted drink '  + item.id)
                    }
                }
            }
        },

        socket_drinksMenuUpdated(state) {
            if (state.loadedAll) {
                this.dispatch('loadAll')
                this.commit('showSnackbar', {text: 'Drinks menu updated'}, {root: true})
            }
        },
        
    },
    
    actions: {
        
        loadAll({commit, state}) {
            if (state.loadedAll) return
            commit('loading')
            Vue.prototype.$socket.emit('getDrinksMenu', (res) => {
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
