// DeleteRecord.jsx
// Removes a record from all 4 nodes simultaneously to keep the ledger consistent.
// Mirrors delete_record() in main.py.
//
// Uses a two-step confirmation (click once to arm, click again to confirm)
// so an accidental click doesn't immediately destroy data.

import { useState } from 'react'

export default function DeleteRecord({ inventory, setInventory, onDone }) {
  const [id, setId]               = useState('')
  const [confirmed, setConfirmed] = useState(false) // true = waiting for second click
  const [result, setResult]       = useState(null)

  const handleDelete = (e) => {
    e.preventDefault()

    // First click — arm the confirmation warning; don't delete yet
    if (!confirmed) { setConfirmed(true); return }

    const trimmed = id.trim()
    let found = false
    const updated = {}

    // Filter out the target record from every node's list
    for (const [node, items] of Object.entries(inventory)) {
      const before    = items.length
      updated[node]   = items.filter(i => String(i.item_id).trim() !== trimmed)
      if (updated[node].length < before) found = true // item existed on at least one node
    }

    if (found) setInventory(updated) // only update state if something was actually removed
    setResult({ found, id: trimmed })
    setConfirmed(false)
  }

  return (
    <div className="max-w-md">
      <h2 className="text-xl font-semibold text-slate-200 mb-1">Delete Inventory Record</h2>
      <p className="text-slate-500 text-sm mb-6">
        Removes the record from all 4 nodes to keep the ledger consistent.
      </p>

      <form onSubmit={handleDelete} className="space-y-4">
        <div>
          <label className="block text-sm text-slate-400 mb-1.5">Item ID</label>
          <input
            value={id}
            onChange={e => { setId(e.target.value); setConfirmed(false); setResult(null) }}
            placeholder="e.g. 001"
            required
            className="field-input"
          />
        </div>

        {/* Confirmation warning — shown after the first click */}
        {confirmed && (
          <div className="bg-red-900/20 border border-red-800 rounded-xl p-3 text-sm text-red-300">
            ⚠️ Permanently delete <span className="font-mono font-bold">{id}</span> from all 4 nodes?
          </div>
        )}

        <div className="flex gap-3">
          {/* Button label changes to make the two-step confirmation obvious */}
          <button
            type="submit"
            className={`flex-1 py-2.5 font-medium rounded-xl transition-colors ${
              confirmed
                ? 'bg-red-600 hover:bg-red-500 text-white'
                : 'bg-slate-700 hover:bg-slate-600 text-slate-200'
            }`}
          >
            {confirmed ? '⚠️ Confirm Delete' : '🗑️ Delete Record'}
          </button>
          {confirmed && (
            <button
              type="button"
              onClick={() => setConfirmed(false)}
              className="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-400 rounded-xl text-sm"
            >
              Cancel
            </button>
          )}
        </div>
      </form>

      {/* Result feedback after deletion attempt */}
      {result && (
        <div className={`mt-5 rounded-xl border p-4 ${
          result.found ? 'bg-emerald-900/20 border-emerald-800' : 'bg-slate-800 border-slate-700'
        }`}>
          {result.found ? (
            <>
              <p className="text-emerald-400 font-semibold mb-1">✅ Deleted from all nodes</p>
              <p className="text-slate-400 text-sm">
                Item <span className="font-mono text-cyan-400">{result.id}</span> removed.
              </p>
              <button onClick={onDone} className="mt-3 text-sm text-cyan-400 hover:text-cyan-300 underline">
                ← View Dashboard
              </button>
            </>
          ) : (
            // Item was not found on any node — nothing changed
            <p className="text-slate-400">
              Item <span className="font-mono">{result.id}</span> not found. Nothing deleted.
            </p>
          )}
        </div>
      )}
    </div>
  )
}
