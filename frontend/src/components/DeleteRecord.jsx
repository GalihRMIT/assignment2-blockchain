// DeleteRecord.jsx
// Removes a record from all 4 nodes simultaneously to keep the ledger consistent.
// Mirrors delete_record() in main.py.

import { useState } from 'react'

async function saveNode(node, records) {
  await fetch('/api/inventory', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ node, records }),
  })
}

export default function DeleteRecord({ inventory, setInventory }) {
  const [id, setId]         = useState('')
  const [result, setResult] = useState(null)
  const [saving, setSaving] = useState(false)

  const handleDelete = async (e) => {
    e.preventDefault()
    const trimmed = id.trim()
    let found = false
    const updated = {}

    for (const [node, items] of Object.entries(inventory)) {
      const before  = items.length
      updated[node] = items.filter(i => String(i.item_id).trim() !== trimmed)
      if (updated[node].length < before) found = true
    }

    if (found) {
      setInventory(updated)
      setSaving(true)
      for (const [node, records] of Object.entries(updated)) {
        await saveNode(node, records)
      }
      setSaving(false)
    }

    setResult({ found, id: trimmed })
    setId('')
  }

  return (
    <div className="max-w-md">
      <h2 className="text-xl font-semibold text-white mb-1">Delete Inventory Record</h2>
      <p className="text-neutral-500 text-sm mb-6">
        Removes the record from all 4 nodes to keep the ledger consistent.
      </p>

      <form onSubmit={handleDelete} className="space-y-4">
        <div>
          <label className="block text-sm text-neutral-400 mb-1.5">Item ID</label>
          <input
            value={id}
            onChange={e => { setId(e.target.value); setResult(null) }}
            placeholder="e.g. 001"
            required
            className="field-input"
          />
        </div>

        <button
          type="submit"
          disabled={saving}
          className="w-full py-2.5 bg-white hover:bg-neutral-200 disabled:opacity-50 text-black font-medium rounded transition-colors"
        >
          {saving ? 'Deleting...' : 'Delete Record'}
        </button>
      </form>

      {result && (
        <div className="mt-5 border border-neutral-700 rounded p-4">
          {result.found ? (
            <p className="text-white font-semibold">DONE</p>
          ) : (
            <p className="text-neutral-500">
              Item <span className="font-mono">{result.id}</span> not found. Nothing deleted.
            </p>
          )}
        </div>
      )}
    </div>
  )
}
