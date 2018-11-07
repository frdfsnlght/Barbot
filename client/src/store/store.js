import Vue from 'vue'
import Vuex from 'vuex'

import wifi from './modules/wifi'
import drinkOrders from './modules/drinkOrders'
import glasses from './modules/glasses'
import ingredients from './modules/ingredients'
import drinks from './modules/drinks'
import drinksMenu from './modules/drinksMenu'
import pumps from './modules/pumps'

Vue.use(Vuex)

export default new Vuex.Store({
    modules: {
        wifi: wifi,
        drinkOrders: drinkOrders,
        ingredients: ingredients,
        glasses: glasses,
        drinks: drinks,
        drinksMenu: drinksMenu,
        pumps: pumps,
        
    },
    
    state: {
        connected: false,
        options: {},
        error: false,
        notification: false,
        notificationColor: 'info',
        notificationTimeout: 4000,
        isConsole: location.hostname === 'localhost',
        dispenserHold: false,
        dispenseState: {},
        pumpSetup: false,
        glassReady: true,
        parentalLock: false,
        volume: 1,
        user: {},
        alerts: [],
    },
    
    mutations: {
        socket_connect(state) {
            state.connected = true
        },
        socket_disconnect(state) {
            state.connected = false
        },
        
        socket_clientOptions(state, options) {
            state.options = options
            //console.log('clientOptions:')
            //console.dir(options)
            if (! options.autoConsole) {
                if (options.isConsole !== state.isConsole) {
                    state.isConsole = options.isConsole
                    console.log('Client is now ' + (state.isConsole ? '' : 'NOT ') + 'running as console.')
                }
            }
        },
        
        socket_dispenserHold(state, dispenserHold) {
            state.dispenserHold = dispenserHold
        },
    
        socket_dispenseState(state, dispenseState) {
            //console.log('dispenseState:')
            //console.dir(dispenseState)
            state.dispenseState = dispenseState
        },
    
        socket_pumpSetup(state, pumpSetup) {
            state.pumpSetup = pumpSetup
        },

        socket_glassReady(state, glassReady) {
            state.glassReady = glassReady
        },

        socket_parentalLock(state, parentalLock) {
            state.parentalLock = parentalLock
        },

        socket_volume(state, volume) {
            state.volume = volume
        },

        socket_alerts(state, alerts) {
            state.alerts = alerts
        },
        
    
        setError(state, error) {
            state.error = error
        },
        
        clearError(state) {
            state.error = false
        },
        
        notify(state, options) {
            if (typeof(options) == 'string') {
                state.notification = options
                state.notificationColor = 'info'
                state.notificationTimeout = 4000
            } else if (options instanceof Object) {
                state.notification = options.text
                state.notificationColor = options.color ? options.color : 'info'
                state.notificationTimeout = options.timeout ? options.timeout : 4000
            }
        },
        
        clearNotification(state) {
            state.notification = false
        },
        
        setUser(state, user) {
            if (user == false)
                state.user = {}
            else
                state.user = user
        },
        
    },
    
    actions: {
        
    }
    
})
