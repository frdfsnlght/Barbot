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
        },
        getById: (state) => (id) => {
            if (! state.loadedAll) return null
            return state.items.find(item => item.id === id)
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
        
        socket_ingredientSaved(state, item) {
            if (state.loadedAll) {
                let i = state.items.find((e) => { return e.id === item.id })
                if (i) {
                    Object.assign(i, item)
                    this.commit('showSnackbar', {text: 'Ingredient updated'}, {root: true})
                    console.log('updated ingredient ' + item.id)
                } else {
                    state.items.push(item)
                    this.commit('showSnackbar', {text: 'Ingredient added'}, {root: true})
                    console.log('added ingredient '  + item.id)
                }
            }
            if (state.loadedOne && state.item.id === item.id) {
                Object.assign(state.item, item)
                this.commit('showSnackbar', {text: 'Ingredient updated'}, {root: true})
            }
        },

        socket_ingredientDeleted(state, item) {
            if (state.loadedAll) {
                let i = state.items.find((e) => { return e.id === item.id })
                if (i) {
                    let idx = state.items.indexOf(i)
                    if (idx != -1) {
                        state.items.splice(idx, 1)
                        this.commit('showSnackbar', {text: 'Ingredient deleted'}, {root: true})
                        console.log('deleted ingredient '  + item.id)
                    }
                }
            }
            if (state.loadedOne && state.item.id === item.id) {
                state.item = {}
                this.commit('showSnackbar', {text: 'Ingredient deleted'}, {root: true})
            }
        },

    },
    
    actions: {
        
        loadAll({commit, state}) {
            if (state.loadedAll) return
            commit('loading')
            Vue.prototype.$socket.emit('getIngredients', (res) => {
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
            Vue.prototype.$socket.emit('getIngredient', id, (res) => {
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
