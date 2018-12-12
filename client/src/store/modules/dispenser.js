
export default {
    namespaced: true,
    
    state: {
        state: 'wait',
        drinkOrder: null,
        glass: true,
        hold: false,
    },
    
    mutations: {
        
        socket_dispenser_state(state, dState) {
            state.state = dState.state
            state.drinkOrder = dState.drinkOrder
        },
    
        socket_dispenser_glass(state, glass) {
            state.glass = glass
        },

        socket_dispenser_hold(state, hold) {
            state.hold = hold
        },

    },
    
}
