
export default {
    namespaced: true,
    
    state: {
        state: 'wait',
        drinkOrder: null,
        glass: true,
        parentalCode: false,
    },
    
    mutations: {
        
        socket_dispenserHold(state, dispenserHold) {
            state.dispenserHold = dispenserHold
        },
    
        socket_dispenser_state(state, dState) {
            state.state = dState.state
            state.drinkOrder = dState.drinkOrder
            console.log('state=' + state.state)
            console.log('drinkOrder=' + state.drinkOrder)
        },
    
        socket_dispenser_glass(state, glass) {
            state.glass = glass
        },

        socket_dispenser_parentalCode(state, parentalCode) {
            state.parentalCode = parentalCode
        },
        
    },
    
}
