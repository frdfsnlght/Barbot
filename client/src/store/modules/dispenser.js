
export default {
    namespaced: true,
    
    state: {
        state: 'wait',
        drinkOrder: null,
        glassReady: true,
    },
    
    mutations: {
        
        socket_dispenserHold(state, dispenserHold) {
            state.dispenserHold = dispenserHold
        },
    
        socket_dispenser_state(state, dState) {
            state.state = dState.state
            state.drinkOrder = dState.drinkOrder
            console.log('dispenser.state=' + state.state)
            console.log('dispenser.drinkOrder=' + state.drinkOrder)
        },
    
        socket_dispenser_glassReady(state, glassReady) {
            state.glassReady = glassReady
        },

    },
    
}
