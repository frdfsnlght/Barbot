
export default {
    namespaced: true,
    
    state: {
        state: 'wait',
        drinkOrder: null,
        glass: true,
    },
    
    mutations: {
        
        socket_dispenser_state(state, dState) {
            state.state = dState.state
            state.drinkOrder = dState.drinkOrder
        },
    
        socket_dispenser_glass(state, glass) {
            state.glass = glass
        },

    },
    
}
