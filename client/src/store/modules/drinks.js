import Vue from 'vue'

export default {
    namespaced: true,
    
    state: {
        items: [],
        item: {},
        loading: false,
        loadedAll: false,
        loadedOne: false,
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
        
        loadedOne(state, item) {
            state.item = item
            state.loading = false
            state.loadedOne = true
        },
        
        destroy(state) {
            state.items = []
            state.item = {}
            state.loadedAll = false
            state.loadedOne = false
        },
        
        socket_drinkSaved(state, item) {
            if (state.loadedAll) {
                let d = state.items.find((e) => { return e.id === item.id })
                if (d) {
                    Object.assign(d, item)
                    this.commit('showSnackbar', {text: 'Drink updated'}, {root: true})
                    console.log('updated drink ' + item.id)
                } else {
                    state.items.push(item)
                    this.commit('showSnackbar', {text: 'Drink added'}, {root: true})
                    console.log('added drink '  + item.id)
                }
            }
            if (state.loadedOne && state.item.id === item.id) {
                Object.assign(state.item, item)
                this.commit('showSnackbar', {text: 'Drink updated'}, {root: true})
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
            if (state.loadedOne && state.item.id === item.id) {
                state.item = {}
                this.commit('showSnackbar', {text: 'Drink deleted'}, {root: true})
            }
        },

    },
    
    actions: {
        
        loadAll({commit, state}) {
            if (state.loadedAll) return
            commit('loading')
            Vue.prototype.$socket.emit('getDrinks', (res) => {
                if (res.error) {
                    commit('setError', res.error, {root: true})
                    commit('loadedAll', [])
                } else {
                    commit('loadedAll', res.items)
                }
            })
        },
        
        loadById({commit, state}, id) {
            if (state.loadedOne) return
            commit('loading')
            Vue.prototype.$socket.emit('getDrink', id, (res) => {
                if (res.error) {
                    commit('setError', res.error, {root: true})
                    commit('loadedOne', {})
                } else {
                    commit('loadedOne', res.item)
                }
            })
        },
        
    }
    
}
