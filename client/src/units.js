
import store from './store/store'


export default {

    toML(otherAmount, otherUnits) {
        let units = store.state.units
        if (! (otherUnits in units.conversions))
            throw 'Invalid units: ' + otherUnits
        return otherAmount * units.conversions[otherUnits].toML
    },

    toOther(mlAmount, otherUnits) {
        let units = store.state.units
        if (! (otherUnits in units.conversions))
            throw 'Invalid units: ' + otherUnits
        return mlAmount / units.conversions[otherUnits].toML
    },
    
    format(otherAmount, otherUnits, appendUnits = true) {
        let units = store.state.units
        if (! (otherUnits in units.conversions))
            return ''
            //throw 'Invalid units: ' + otherUnits
        let str = otherAmount.toFixed(units.conversions[otherUnits].precision)
        if (appendUnits)
            str += ' ' + otherUnits
        return str
    },
    
    defaultUnits() {
        let units = store.state.units
        return units['default']
    },
    
    units() {
        let units = store.state.units
        return units['order']
    },
    
}

