
export default {
    namespaced: true,
    
    state: {
        parentalCode: false,
    },
    
    mutations: {
        
        socket_core_parentalCode(state, parentalCode) {
            state.parentalCode = parentalCode
        },

    },
    
}
