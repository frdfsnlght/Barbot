<script>
export default {
  name: 'HTMLTitle',
  props: ['title'],
  created () {
    document.title = this.title;
  },
  watch: {
    title () {
      // only used when the title changes after page load
      document.title = this.title;
    }
  },
  render () {
    return ''
  },
}
</script>
