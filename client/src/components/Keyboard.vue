<template>
  <div
    class="keyboard"
    @mousedown.prevent=""
  >
    <div
      class="keyboard-row"
      v-for="(row, rowIndex) in layoutRows"
      :key="rowIndex"
      @mousedown.prevent=""
    >
      <button
        v-for="(key, keyIndex) in row"
        :key="keyIndex"
        class="keyboard-key"
        :class="key.class"
        :disabled="!key.action"
        @click.prevent="key.action"  
        @mousedown.prevent=""
      >
        <v-icon v-if="key.icon">{{key.icon}}</v-icon>
        <span v-else>{{ key.label }}</span>
      </button>
    </div>
  </div>
</template>

<style>
  .keyboard {
    padding: 1vh 0;
    font-size: 18px !important;
  }
  .keyboard-row {
    padding: 0.25vh 0;
    text-align: center;
  }
  .keyboard-key {
    border: none;
    outline: none;
    padding: 1vh 2vw;
    min-width: 9vw;
    min-height: 4vh;
    margin: 0 0.3vw;
    background: #EEE;
    color: #666;
    cursor: pointer;
    font-family: inherit;
    font-size: inherit;
    border-radius: 0.5vh;
  }
  .keyboard-key:hover {
    background: #E0E0E0;
  }
  .keyboard-key:active {
    background: #777;
    color: #FFF;
    box-shadow: inset 0 1px 4px rgba(#000, 0.1);
  }
  .keyboard-key:disabled {
    background: transparent;
    cursor: default;
  }
  .keyboard-key.w2 {
    min-width: 16vw;
  }
  .keyboard-key.w3 {
    min-width: 24vw;
  }
  .keyboard-key.w4 {
    min-width: 32vw;
  }
</style>

<script>

export default {
  name: 'Keyboard',
  
  props: [
  ],
  
  data() {
    return {
      layouts: {
        full: [
          [['qwertyuiop']],
          [{ icon: 'mdi-keyboard-tab', action: 'tab' }, ['asdfghjkl']],
          [{ icon: 'mdi-apple-keyboard-shift', action: 'setLayout', args: ['fullCaps'] }, ['zxcvbnm'], { icon: 'mdi-backspace', action: 'backspace' }],
          [{ icon: 'mdi-chevron-down', action: 'hide' },
           { label: '?123', action: 'setLayout', args: ['symbols'] },
           ',',
           { label: 'space', action: 'space', class: 'w4 transparent--text' },
           '.',
           { icon: 'mdi-keyboard-return', action: 'enter', class: 'green w2' }],
        ],
        fullCaps: [
          [['QWERTYUIOP']],
          [{ icon: 'mdi-keyboard-tab', action: 'tab' }, ['ASDFGHJKL']],
          [{ icon: 'mdi-apple-keyboard-shift', action: 'setLayout', args: ['full'] }, ['ZXCVBNM'], { icon: 'mdi-backspace', action: 'backspace' }],
          [{ icon: 'mdi-chevron-down', action: 'hide' },
           { label: '?123', action: 'setLayout', args: ['symbols'] },
           ',',
           { label: 'space', action: 'space', class: 'w4 transparent--text' },
           '.',
           { icon: 'mdi-keyboard-return', action: 'enter', class: 'green w2' }],
        ],
        symbols: [
          [['1234567890']],
          [{ icon: 'mdi-keyboard-tab', action: 'tab' }, ['@#$_&-+()']],
          [['=*"\':;!?/'], { icon: 'mdi-backspace', action: 'backspace' }],
          [{ icon: 'mdi-chevron-down', action: 'hide' },
           { label: 'ABC', action: 'setLayout', args: ['full'] },
           ',',
           { label: 'space', action: 'space', class: 'w4 transparent--text' },
           '.',
           { icon: 'mdi-keyboard-return', action: 'enter', class: 'green w2' }],
        ],
        number: [
          [{}, ['123'], {}],
          [{}, ['456'], {}],
          [{ icon: 'mdi-keyboard-tab', action: 'tab' }, ['789'], { icon: 'mdi-backspace', action: 'backspace' }],
          [{ icon: 'mdi-chevron-down', action: 'hide' }, ['-0.'], { icon: 'mdi-keyboard-return', action: 'enter', class: 'green' }],
        ],
        positiveNumber: [
          [{}, ['123'], {}],
          [{}, ['456'], {}],
          [{ icon: 'mdi-keyboard-tab', action: 'tab' }, ['789'], { icon: 'mdi-backspace', action: 'backspace' }],
          [{ icon: 'mdi-chevron-down', action: 'hide' }, {}, ['0.'], { icon: 'mdi-keyboard-return', action: 'enter', class: 'green' }],
        ],
        integer: [
          [{}, ['123'], {}],
          [{}, ['456'], {}],
          [{ icon: 'mdi-keyboard-tab', action: 'tab' }, ['789'], { icon: 'mdi-backspace', action: 'backspace' }],
          [{ icon: 'mdi-chevron-down', action: 'hide' }, ['-0'], {}, { icon: 'mdi-keyboard-return', action: 'enter', class: 'green' }],
        ],
        positiveInteger: [
          [{}, ['123'], {}],
          [{}, ['456'], {}],
          [{ icon: 'mdi-keyboard-tab', action: 'tab' }, ['789'], { icon: 'mdi-backspace', action: 'backspace' }],
          [{ icon: 'mdi-chevron-down', action: 'hide' }, {}, '0', {}, { icon: 'mdi-keyboard-return', action: 'enter', class: 'green' }],
        ],
      },
      layout: 'full',
      ucFirst: false,
      ucWords: false,
      input: null,
      tabContexts: [],
    }
  },

  computed: {
  
    lines() {
      let layout = this.layouts[this.layout]
      return layout.split('|')
    },
    
    layoutRows() {
      return this.layouts[this.layout].map(row => {
        
        let keys = []
        row.forEach(key => {
          if (Array.isArray(key)) {
            key[0].split('').forEach(ch => {
              keys.push({
                label: ch,
                action: this.insert.bind(this, ch)
              })
            })
            
          } else if ((typeof(key) == 'string') || (typeof(key) == 'number')) {
            keys.push({
              label: key.toString(),
              action: this.insert.bind(this, key.toString())
            })
            
          } else if (typeof(key) == 'object') {
            if (typeof(key.action) == 'string')
              key.action = this[key.action].bind(this, key.args);
            keys.push(key)
          }
        })
        return keys
        
      });
    },
        
  },
      
  methods: {
    
    installHooks(el) {
      this.inputElements(el).forEach(i => {
        i.addEventListener('focus', this.inputFocus)
        i.addEventListener('blur', this.inputBlur)
        i.addEventListener('click', this.inputClick)
      })
      this.tabContexts.push(el)
    },
    
    removeHooks(el) {
      this.hide()
      this.inputElements(el).forEach(i => {
        i.removeEventListener('focus', this.inputFocus)
        i.removeEventListener('blur', this.inputBlur)
        i.removeEventListener('click', this.inputClick)
      })
      if (this.tabContexts[this.tabContexts.length - 1] == el)
        this.tabContexts.pop()
    },
    
    inputElements(el) {
      if (! el) el = document
      return el.querySelectorAll(
        'input[type=text], input[type=password], input[type=email], input[type=number], textarea')
    },

    inputFocus(e) {
      this.input = e.target
      if (this.input.dataset.kbhide) return
      this.ucWords = this.input.dataset.kbucwords
      if (! this.ucWords)
        this.ucFirst = this.input.dataset.kbucfirst
      this.adjustLayout()
      this.$emit('show')
    },
    
    inputBlur(e) {
      if (e.target == this.input) {
        this.hide()
      }
    },
    
    inputClick(e) {
      if (this.input == e.target) {
        this.adjustLayout()
        this.$emit('show')
      }
    },
    
    hide() {
      this.$emit('hide')
    },

    update(v, s, e) {
      this.input.value = v
      this.input.selectionStart = s
      this.input.selectionEnd = e
      this.adjustLayout()
      this.input.dispatchEvent(new Event('input'))
    },

    insert(str) {
      let v = this.input.value
      let s = this.input.selectionStart
      let e = this.input.selectionEnd
      v = v.slice(0, s) + str + v.slice(e)
      s += str.length
      e = s
      this.update(v, s, e)
    },
    
    backspace() {
      let v = this.input.value
      let s = this.input.selectionStart
      let e = this.input.selectionEnd
      if (s == e) {
        if (s > 0) {
          s--
          e = s
          v = v.slice(0, s) + v.slice(e + 1)
        }
      } else {
        v = v.slice(0, s) + v.slice(e)
        e = s
      }
      this.update(v, s, e)
    },
    
    saveNumber() {
      if (this.inputIsNumber) this.input.type = 'text'
    },
    
    restoreNumber() {
      if (this.inputIsNumber) this.input.type = 'number'
    },
    
    tab() {
      let e = this.nextTabbable()
      if (e) e.focus()
    },
    
    space() {
      this.insert(' ')
    },
    
    enter() {
      this.insert('\r')
      this.input.dispatchEvent(new KeyboardEvent('keydown', {bubbles: true, cancelable: true, key: 'Enter', code: 'Enter', keyCode: 13}))
    },
    
    emit() {
      this.$emit.apply(this, arguments)
    },
    
    nextTabbable() {
      let ctx = this.tabContexts[this.tabContexts.length - 1]
      
      let els = Array.prototype.slice.call(ctx.querySelectorAll('input, select, textarea'))
      els = els.filter(e => { return (e != this.input) && (e.tabIndex >= this.input.tabIndex) })
      els.sort((a, b) => { return a.tabIndex - b.tabIndex })
      if (els.length) return els[0]
      
      els = Array.prototype.slice.call(ctx.querySelectorAll('input, select, textarea'))
      els = els.filter(e => { return (e != this.input) && (e.tabIndex > 0) })
      els.sort((a, b) => { return a.tabIndex - b.tabIndex })
      if (els.length) return els[0]
      
      return false
    },
    
    adjustLayout() {
      let layout = this.layout

      if (this.input.dataset.kblayout)
        layout = this.input.dataset.kblayout
          
      else if (this.input.dataset.kbtype == 'number')
        layout = 'number'
          
      else if (this.input.dataset.kbtype == 'positiveNumber')
        layout = 'positiveNumber'
          
      else if (this.input.dataset.kbtype == 'integer')
        layout = 'integer'
      
      else if (this.input.dataset.kbtype == 'positiveInteger')
        layout = 'positiveInteger'
      
      else if ((! this.ucWords) && (! this.ucFirst))
        layout = 'full'
        
      else {
        let s = this.input.selectionStart
        if (s == 0)
          layout = 'fullCaps'
        else if (this.ucWords && (this.input.value.slice(s - 1, s) == ' '))
          layout = 'fullCaps'
        else if ((s > 1) && this.ucFirst && (this.input.value.slice(s - 2, s) == '. '))
          layout = 'fullCaps'
        else
          layout = 'full'
      }
    
      if (layout != this.layout)
        this.setLayout(layout)
    },
    
    setLayout(name) {
      if (! this.layouts[name])
        throw new Error('Unknown keyboard layout "' + name + '"!')
      this.layout = name
    },
    
  },
  
}

</script>
