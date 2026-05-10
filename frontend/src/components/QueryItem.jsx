// QueryItem.jsx
// Searches for an item across all 4 nodes and runs a consensus check.
// Mirrors query_item_quantity() in main.py.
//
// Consensus rules (same as the Python CLI):
//   AGREE     — all 4 nodes found the item AND all report the same quantity
//   DISAGREE  — item found on some/all nodes but quantities differ
//   NOT_FOUND — item not found on any node

import { useState } from 'react'

// Per-node text colours for the quantity display cards
const NODE_COLOR = { A: 'text-cyan-400', B: 'text-purple-400', C: 'text-emerald-400', D: 'text-amber-400' }

export default function QueryItem({ inventory }) {
  const [id, setId]           = useState('')
  const [results, setResults] = useState(null)

  const query = (e) => {
    e.preventDefault()
    const trimmed = id.trim()

    // Query each node independently — same logic as the Python for-loop over Inventory_Files
    const r = {}
    for (const [node, items] of Object.entries(inventory)) {
      const found = items.find(i => String(i.item_id).trim() === trimmed)
      r[node] = found != null ? found.quantity : null // null means not found on this node
    }
    setResults({ id: trimmed, nodes: r })
  }

  // Derive consensus verdict from the per-node results
  const valid     = results ? Object.values(results.nodes).filter(q => q != null) : []
  const consensus = results
    ? valid.length === 0                                    ? 'NOT_FOUND'  // no node has it
    : valid.length === 4 && new Set(valid).size === 1       ? 'AGREE'      // all nodes match
    : 'DISAGREE'                                                            // mismatch
    : null

  return (
    <div className="max-w-xl">
      <h2 className="text-xl font-semibold text-slate-200 mb-1">Query Item Quantity</h2>
      <p className="text-slate-500 text-sm mb-6">
        Checks all 4 nodes and runs a consensus check on the result.
      </p>

      <form onSubmit={query} className="flex gap-3 mb-6">
        <input
          value={id}
          onChange={e => { setId(e.target.value); setResults(null) }}
          placeholder="Item ID  (e.g. 001)"
          required
          className="field-input flex-1"
        />
        <button
          type="submit"
          className="px-5 py-2 bg-cyan-600 hover:bg-cyan-500 text-white font-medium rounded-lg shrink-0"
        >
          Search
        </button>
      </form>

      {results && (
        <div>
          {/* Per-node quantity cards — grey/muted if the item was not found on that node */}
          <div className="grid grid-cols-4 gap-3 mb-4">
            {Object.entries(results.nodes).map(([node, qty]) => (
              <div key={node} className="bg-slate-900 border border-slate-800 rounded-xl p-3 text-center">
                <div className="text-xs text-slate-500 mb-1">Node {node}</div>
                <div className={`text-xl font-bold ${qty != null ? NODE_COLOR[node] : 'text-slate-600'}`}>
                  {qty != null ? qty : '—'}
                </div>
                <div className="text-xs text-slate-600 mt-0.5">{qty != null ? 'units' : 'not found'}</div>
              </div>
            ))}
          </div>

          {/* Consensus verdict */}
          {consensus === 'AGREE' && (
            <div className="bg-emerald-900/20 border border-emerald-800 rounded-xl p-4">
              <p className="text-emerald-400 font-semibold">✅ Consensus: All nodes agree</p>
              <p className="text-slate-300 text-sm mt-1">
                Item <span className="font-mono text-cyan-400">{results.id}</span> — quantity:&nbsp;
                <span className="font-bold text-white text-lg">{valid[0]}</span>
              </p>
            </div>
          )}
          {consensus === 'DISAGREE' && (
            // Nodes holding different values means the ledger is inconsistent — result is untrusted
            <div className="bg-red-900/20 border border-red-800 rounded-xl p-4">
              <p className="text-red-400 font-semibold">⚠️ Consensus Failed — nodes disagree</p>
              <p className="text-slate-500 text-sm mt-1">Result cannot be trusted.</p>
            </div>
          )}
          {consensus === 'NOT_FOUND' && (
            <div className="bg-slate-800 border border-slate-700 rounded-xl p-4">
              <p className="text-slate-400 font-semibold">🔍 Item not found in any node</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
