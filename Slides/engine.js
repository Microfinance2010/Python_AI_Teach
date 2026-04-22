// Marp engine with Mermaid support
// Pre-renders Mermaid diagrams to static SVG at build time using mmdc.
// This avoids the SVG-inside-foreignObject problem in Marp's presentation mode.
const { Marp } = require('@marp-team/marp-core')
const { execSync } = require('child_process')
const fs = require('fs')
const os = require('os')
const path = require('path')

module.exports = (opts) => {
  const marp = new Marp({ ...opts, html: true })

  const { fence } = marp.markdown.renderer.rules
  marp.markdown.renderer.rules.fence = (tokens, idx, options, env, slf) => {
    const token = tokens[idx]
    if (token.info.trim() === 'mermaid') {
      try {
        const tmpMmd = path.join(os.tmpdir(), `marp_mermaid_${idx}.mmd`)
        const tmpPng = path.join(os.tmpdir(), `marp_mermaid_${idx}.png`)
        fs.writeFileSync(tmpMmd, token.content, 'utf8')
        execSync(`mmdc -i "${tmpMmd}" -o "${tmpPng}" --backgroundColor white --width 1000`, { timeout: 20000 })
        const png = fs.readFileSync(tmpPng)
        const b64 = png.toString('base64')
        return `<div style="text-align:center"><img src="data:image/png;base64,${b64}" style="max-width:90%;height:auto;margin:0 auto;display:block;" /></div>\n`
      } catch (e) {
        console.error(`[mermaid] render failed: ${e.message}`)
        // Fall back to plain code block on error
        return fence
          ? fence(tokens, idx, options, env, slf)
          : slf.renderToken(tokens, idx, options)
      }
    }
    return fence
      ? fence(tokens, idx, options, env, slf)
      : slf.renderToken(tokens, idx, options)
  }

  return marp
}
