
export default {
    
    toML(amount, units) {
        if (units == 'ml')
            return amount
        if (units == 'oz')
            return amount * 29.5735
        console.error('unknown units: ' + units)
        return amount
    },

    convertUnits(fromAmount, fromUnits, toUnits) {
        let amount = this.toML(fromAmount, fromUnits)
        if (toUnits == 'ml')
            return amount
        if (toUnits == 'oz')
            return amount / 29.5735
        console.error('unknown units: ' + toUnits)
        return amount
    }
    
}

