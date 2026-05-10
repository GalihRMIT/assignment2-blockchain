// QueryItem.jsx
// Searches for an item across all 4 nodes and runs a consensus check.
// Mirrors query_item_quantity() in main.py.
//
// Consensus rules (same as the Python CLI):
//   AGREE     — all 4 nodes found the item AND all report the same quantity
//   DISAGREE  — item found on some/all nodes but quantities differ
//   NOT_FOUND — item not found on any node

import { useState } from 'react'

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
    ? valid.length === 0                              ? 'NOT_FOUND'  // no node has it
    : valid.length === 4 && new Set(valid).size === 1 ? 'AGREE'      // all nodes match
    : 'DISAGREE'                                                      // mismatch
    : null

  return (
    <div className="max-w-xl">
      <h2 className="text-xl font-semibold text-white mb-1">Query Item Quantity</h2>
      <p className="text-neutral-500 text-sm mb-6">
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
          className="px-5 py-2 bg-white hover:bg-neutral-200 text-black font-medium rounded shrink-0"
        >
          Search
        </button>
      </form>

      {results && (
        <div>
          {/* Per-node quantity cards */}
          <div className="grid grid-cols-4 gap-3 mb-4">
            {Object.entries(results.nodes).map(([node, qty]) => (
              <div key={node} className="bg-neutral-950 border border-neutral-800 rounded p-3 text-center">
                <div className="text-xs text-neutral-500 mb-1">Node {node}</div>
                <div className={`text-xl font-bold ${qty != null ? 'text-white' : 'text-neutral-700'}`}>
                  {qty != null ? qty : '—'}
                </div>
                <div className="text-xs text-neutral-600 mt-0.5">{qty != null ? 'units' : 'not found'}</div>
              </div>
            ))}
          </div>

          {/* Consensus verdict */}
          {consensus === 'AGREE' && (
            <div className="border border-neutral-700 rounded p-4">
              <p className="text-white font-semibold">Consensus: All nodes agree</p>
              <p className="text-neutral-300 text-sm mt-1">
                Item <span className="font-mono text-neutral-200">{results.id}</span> — quantity:&nbsp;
                <span className="font-bold text-white text-lg">{valid[0]}</span>
              </p>
            </div>
          )}
          {consensus === 'DISAGREE' && (
            // Nodes holding different values means the ledger is inconsistent — result is untrusted
            <div className="border border-white rounded p-4">
              <p className="text-white font-semibold">Consensus Failed — nodes disagree</p>
              <p className="text-neutral-500 text-sm mt-1">Result cannot be trusted.</p>
            </div>
          )}
          {consensus === 'NOT_FOUND' && (
            <div className="border border-neutral-800 rounded p-4">
              <p className="text-neutral-400 font-semibold">Item not found in any node</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
