// KeysViewer.jsx
// Displays all 6 RSA key values (p, q, n, φ(n), e, d) for each of the 4 nodes.
// Values are read directly from the KEYS constant in crypto.js — no fetch needed.
// Large numbers are truncated by default with a "show full" toggle.

import { useState } from 'react'
import { KEYS } from '../crypto.js'

// Per-node accent colours
const NODE_COLOR  = { A: 'text-cyan-400',      B: 'text-purple-400',
                      C: 'text-emerald-400',    D: 'text-amber-400' }
const NODE_BORDER = { A: 'border-l-cyan-500',   B: 'border-l-purple-500',
                      C: 'border-l-emerald-500', D: 'border-l-amber-500' }

// Metadata for each key field — label, colour, icon, and a short description
const KEY_INFO = [
  { k: 'p',   label: 'p  (prime 1)',       color: 'text-slate-300',  icon: '🔢', desc: 'First large prime' },
  { k: 'q',   label: 'q  (prime 2)',       color: 'text-slate-300',  icon: '🔢', desc: 'Second large prime' },
  { k: 'n',   label: 'n = p×q',            color: 'text-purple-400', icon: '🔓', desc: 'Public modulus' },
  { k: 'phi', label: 'φ(n) = (p−1)(q−1)', color: 'text-purple-300', icon: '📐', desc: "Euler's totient" },
  { k: 'e',   label: 'e  (public exp)',    color: 'text-green-400',  icon: '🔓', desc: 'Shared openly' },
  { k: 'd',   label: 'd  (private key)',   color: 'text-red-400',    icon: '🔒', desc: 'NEVER shared' },
]

// Renders a BigInt value with a collapse/expand toggle for long numbers
function BigNum({ value, color }) {
  const [expanded, setExpanded] = useState(false)
  const s    = value.toString()
  const long = s.length > 45
  return (
    <span>
      <span className={`font-mono text-xs break-all ${color}`}>
        {long && !expanded ? s.slice(0, 45) + '…' : s}
      </span>
      {long && (
        <button
          onClick={() => setExpanded(x => !x)}
          className="ml-1.5 text-slate-600 hover:text-slate-400 text-xs underline"
        >
          {expanded ? 'collapse' : 'show full'}
        </button>
      )}
    </span>
  )
}

export default function KeysViewer() {
  return (
    <div>
      <h2 className="text-xl font-semibold text-slate-200 mb-1">RSA Node Keys</h2>
      <p className="text-slate-500 text-sm mb-6">
        Each node has a unique RSA keypair derived from the assignment-provided p, q, e values.
        Public keys (e, n) are shared for verification; private key d is held only by its node.
      </p>

      {/* Formula reference box — shows how each key value is derived */}
      <div className="bg-slate-900 border border-slate-700 rounded-xl p-4 mb-7 font-mono text-sm text-center space-y-1.5">
        <div><span className="text-purple-400">n</span><span className="text-slate-500"> = </span><span className="text-slate-300">p × q</span></div>
        <div><span className="text-purple-300">φ(n)</span><span className="text-slate-500"> = </span><span className="text-slate-400">(p−1) × (q−1)</span></div>
        <div>
          {/* d is the modular inverse of e — computed via extended Euclidean algorithm */}
          <span className="text-red-400">d</span>
          <span className="text-slate-500"> = </span>
          <span className="text-green-400">e</span>
          <span className="text-slate-500">⁻¹ mod φ(n)</span>
          <span className="text-slate-600 text-xs ml-2">← extended Euclidean</span>
        </div>
      </div>

      {/* One card per node listing all 6 key values */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {Object.entries(KEYS).map(([node, k]) => (
          <div key={node} className={`bg-slate-900 border border-slate-800 border-l-4 ${NODE_BORDER[node]} rounded-xl p-5`}>
            <p className={`font-bold text-lg mb-4 ${NODE_COLOR[node]}`}>Node {node}</p>
            <div className="space-y-3">
              {KEY_INFO.map(({ k: field, label, color, icon, desc }) => (
                <div key={field} className="border-b border-slate-800 pb-2.5 last:border-0 last:pb-0">
                  <div className="flex items-center gap-1.5 mb-0.5">
                    <span>{icon}</span>
                    <span className={`text-xs font-semibold ${color}`}>{label}</span>
                    <span className="text-slate-600 text-xs ml-auto">{desc}</span>
                  </div>
                  <BigNum value={k[field]} color={color} />
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
