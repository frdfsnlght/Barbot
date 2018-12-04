import Vue from 'vue'

export default {
    namespaced: true,
    
    state: {
        ingredients: null,
        ingredient: {},
        loading: false,
    },
    
    getters: {
        
        sortedIngredients(state) {
            if (state.ingredients)
                return state.ingredients.slice().sort((a, b) => {
                    return a.name.localeCompare(b.name, 'en', {'sensitivity': 'base'})
                })
            else
                return []
        },
        
        getById: (state) => (id) => {
            if (! state.ingredients) return null
            return state.ingredients.find(ingredient => ingredient.id === id)
        }
        
    },
  
    mutations: {
        
        loading(state) {
            state.loading = true
        },
        
        setIngredients(state, ingredients) {
            state.ingredients = ingredients
            state.loading = false
        },
        
        setIngredient(state, ingredient) {
            state.ingredient = ingredient
            state.loading = false
        },
        
        destroy(state) {
            state.ingredients = null
            state.ingredient = {}
        },
        
        socket_ingredient_changed(state, ingredient) {
            if (state.ingredients) {
                let i = state.ingredients.find((e) => { return e.id === ingredient.id })
                if (i) {
                    Object.assign(i, ingredient)
                    this.commit('notify', 'Ingredient updated', {root: true})
                } else {
                    state.ingredients.push(ingredient)
                    this.commit('notify', 'Ingredient added', {root: true})
                }
            }
            if (state.ingredient.id === ingredient.id) {
                Object.assign(state.ingredient, ingredient)
                this.commit('notify', 'Ingredient updated', {root: true})
            }
        },

        socket_ingredient_deleted(state, ingredient) {
            if (state.ingredients) {
                let i = state.ingredients.find((e) => { return e.id === ingredient.id })
                if (i) {
                    let idx = state.ingredients.indexOf(i)
                    if (idx != -1) {
                        state.ingredients.splice(idx, 1)
                        this.commit('notify', 'Ingredient deleted', {root: true})
                    }
                }
            }
            if (state.ingredient.id === ingredient.id) {
                state.ingredient = {}
                this.commit('notify', 'Ingredient deleted', {root: true})
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
                    Vue.prototype.$socket.emit('ingredient_getAll', (res) => {
                        if (res.error) {
                            commit('setError', res.error, {root: true})
                            reject()
                        } else {
                            commit('setIngredients', res.ingredients)
                            resolve(res.ingredients)
                        }
                    })
                }
            })
        },
        
        getOne({commit}, id) {
            return new Promise((resolve, reject) => {
                commit('loading')
                Vue.prototype.$socket.emit('ingredient_getOne', id, (res) => {
                    if (res.error) {
                        commit('setError', res.error, {root: true})
                        reject()
                    } else {
                        commit('setIngredient', res.ingredient)
                        resolve(res.ingredient)
                    }
                })
            })
        },
        
    }
    
}
