
export default {
    namespaced: true,
    
    state: {
        alerts: [],
    },
    
    mutations: {
        
        socket_alerts_changed(state, alerts) {
            state.alerts = alerts
        },
        
    },
    
}
