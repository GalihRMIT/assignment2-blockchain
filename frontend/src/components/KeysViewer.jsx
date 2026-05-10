// KeysViewer.jsx
// Displays all 6 RSA key values (p, q, n, phi(n), e, d) for each of the 4 nodes.
// Values are read directly from the KEYS constant in crypto.js — no fetch needed.
// Large numbers are truncated by default with a "show full" toggle.

import { KEYS } from '../crypto.js'

// Metadata for each key field — label and a short description
const KEY_INFO = [
  { k: 'p',   label: 'p  (prime 1)',       desc: 'First large prime',    dim: true  },
  { k: 'q',   label: 'q  (prime 2)',       desc: 'Second large prime',   dim: true  },
  { k: 'n',   label: 'n = p x q',          desc: 'Public modulus',       dim: false },
  { k: 'phi', label: 'phi(n) = (p-1)(q-1)',desc: "Euler's totient",      dim: false },
  { k: 'e',   label: 'e  (public exp)',    desc: 'Shared openly',        dim: false },
  { k: 'd',   label: 'd  (private key)',   desc: 'NEVER shared',         dim: false },
]

function BigNum({ value, dim }) {
  return (
    <span className={`font-mono text-xs break-all ${dim ? 'text-neutral-600' : 'text-neutral-300'}`}>
      {value.toString()}
    </span>
  )
}

export default function KeysViewer() {
  return (
    <div>
      <h2 className="text-xl font-semibold text-white mb-1">RSA Node Keys</h2>
      <p className="text-neutral-500 text-sm mb-6">
        Each node has a unique RSA keypair derived from the assignment-provided p, q, e values.
        Public keys (e, n) are shared for verification; private key d is held only by its node.
      </p>

      {/* Formula reference box — shows how each key value is derived */}
      <div className="bg-neutral-950 border border-neutral-800 rounded p-4 mb-7 font-mono text-sm text-center space-y-1.5">
        <div className="text-neutral-300">n = p x q</div>
        <div className="text-neutral-300">phi(n) = (p-1) x (q-1)</div>
        <div className="text-neutral-300">
          {/* d is the modular inverse of e — computed via extended Euclidean algorithm */}
          d = e^-1 mod phi(n)
          <span className="text-neutral-600 text-xs ml-2">extended Euclidean</span>
        </div>
      </div>

      {/* One card per node listing all 6 key values */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {Object.entries(KEYS).map(([node, k]) => (
          <div key={node} className="bg-neutral-950 border border-neutral-800 rounded p-5">
            <p className="font-bold text-lg text-white mb-4">Node {node}</p>
            <div className="space-y-3">
              {KEY_INFO.map(({ k: field, label, desc, dim }) => (
                <div key={field} className="border-b border-neutral-800 pb-2.5 last:border-0 last:pb-0">
                  <div className="flex items-center gap-1.5 mb-0.5">
                    <span className="text-xs font-semibold text-neutral-400">{label}</span>
                    <span className="text-neutral-700 text-xs ml-auto">{desc}</span>
                  </div>
                  <BigNum value={k[field]} dim={dim} />
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
