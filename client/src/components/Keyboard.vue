<template>
  <div
    class="keyboard"
  >
    <div
      class="keyboard-row"
      v-for="(row, rowIndex) in layout"
      :key="rowIndex"
    >
      <button
        v-for="(key, keyIndex) in row"
        :key="keyIndex"
        class="keyboard-key"
        :class="key.class"
        :data-label="key.label"
        @click.prevent="key.action"  
        @mousedown.prevent=""
      >{{ key.label }}</button>
    </div>
  </div>
</template>

<style>
  .keyboard {
    padding: 1vh 0;
  }
  .keyboard-row {
    padding: 0.25vh 0;
    text-align: center;
  }
  .keyboard-key {
    border: none;
    outline: none;
    padding: 1vh 2vw;
    min-width: 8vw;
    margin: 0 0.2vw;
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
  .keyboard-key[data-action="space"] {
    min-width: 33vw;
  }
</style>

<script>

export default {
  name: 'Keyboard',
  
  props: {
  },
  
  data() {
    return {
      value: '',
      layouts: {
        normal: [
          [1, 2, 3, 4, 5, 6, 7, 8, 9, 0, { type: 'action', label: 'BS', action: 'backspace' }],
          ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
          ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
          [{ type: 'action', label: 'shift', action: 'setLayout', args: ['NORMAL'] }, 'z', 'x', 'c', 'v', 'b', 'n', 'm'],
          [{ type: 'action', label: 'space', action: 'space' }],
        ],
        NORMAL: [
          ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', { type: 'action', label: 'BS', action: 'backspace' }],
          ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
          ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
          [{ type: 'action', label: 'shift', action: 'setLayout', args: ['normal'] }, 'Z', 'X', 'C', 'V', 'B', 'N', 'M'],
          [{ type: 'action', label: 'space', action: 'space' }],
        ],
        numeric: [
          [1, 2, 3],
          [4, 5, 6],
          [7, 8, 9],
          [0]
        ],
      },
      layoutName: 'numeric',
    }
  },
  
  computed: {
  
    lines() {
      let layout = this.layouts[this.layout]
      return layout.split('|')
    },
    
    layout() {
      return this.layouts[this.layoutName].map(row => {
        
        let keys = []
        row.forEach(key => {
          if ((typeof(key) == 'string') || (typeof(key) == 'number')) {
            keys.push({
              label: key.toString(),
              action: this.append.bind(this, key.toString())
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
    
    space() {
      console.log('space')
    },
    
    append(str) {
      console.log('append: ' + str)
    },
    
    backspace() {
      console.log('backsapce')
    },
    
    setLayout(name) {
      console.log('set layout: ' + name)
      this.layoutName = name
    },
    
  },
  
}

</script>
