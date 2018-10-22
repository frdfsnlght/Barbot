import Vue from 'vue'
import VueSocketio from 'vue-socket.io-extended';
import io from 'socket.io-client';
import store from '../store/store'

var loc = location.href
if (process.env.NODE_ENV === 'development') {
    if (process.env.VUE_APP_SERVER_LOCATION)
        loc = process.env.VUE_APP_SERVER_LOCATION
    else
        loc = 'http://localhost:8080'
}

Vue.use(VueSocketio, io(loc), {
    store,
    actionPrefix: 'socket_',
    eventToActionTransformer: (ev) => {
        return ev
    },
    mutationPrefix: 'socket_',
    eventToMutationTransformer: (ev) => {
        return ev
    },
});

// eslint-disable-next-line
console.log('Server location is ' + loc)
