// Injects Mermaid CDN script into Marp-generated HTML after build
const fs = require('fs')
const file = process.argv[2] || 'slides.html'

const script = `
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs'
  mermaid.initialize({ startOnLoad: true, theme: 'default' })
</script>
`

let html = fs.readFileSync(file, 'utf8')
if (html.includes('mermaid.esm')) {
  console.log('Mermaid already injected, skipping.')
  process.exit(0)
}
html = html.replace('</body>', script + '</body>')
fs.writeFileSync(file, html)
console.log(`Mermaid script injected into ${file}`)
