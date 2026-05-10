// AddRecord.jsx
// Handles the full add-record flow: form input -> RSA signing -> multi-node
// verification -> ledger update. Mirrors add_new_record() in main.py.
//
// On submit:
//   1. The record is hashed with SHA-256              (hashRecord)
//   2. The signing node signs the hash with its d key (rsaSign)
//   3. All other nodes verify with the signer's e key (rsaVerify)
//   4. If all verify VALID, the record is appended to all 4 nodes in state
//      and written back to the JSON files on disk via POST /api/inventory
//
// The right panel passes all intermediate values to CryptoSteps for display.

import { useState } from 'react'
import { KEYS, hashRecord, rsaSign, rsaVerify } from '../crypto.js'
import CryptoSteps from './CryptoSteps.jsx'

const NODES = ['A', 'B', 'C', 'D']

// Writes one node's updated records back to its JSON file via Flask
async function saveNode(node, records) {
  await fetch('/api/inventory', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ node, records }),
  })
}

export default function AddRecord({ inventory, setInventory, onDone }) {
  const [form, setForm]       = useState({ item_id: '', quantity: '', price: '', location: 'A', signer: 'A' })
  const [steps, setSteps]     = useState(null)   // crypto breakdown shown in right panel
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState(null)

  const set = (k) => (e) => setForm(p => ({ ...p, [k]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setSteps(null)

    const { item_id, quantity, price, location, signer } = form
    const record = { item_id, quantity: Number(quantity), price: Number(price), location }

    // Duplicate check — node A is authoritative since all nodes are always in sync
    if (inventory.A.some(i => String(i.item_id).trim() === item_id.trim())) {
      setError('Item ID already exists — rejected.')
      return
    }

    setLoading(true)
    try {
      const key = KEYS[signer]

      // Step 1 — hash the record to produce hash.str, hash.hex, hash.int
      const hash = await hashRecord(record)

      // Step 2 — sign:  signature = hash.int ^ d  mod  n
      const signature = rsaSign(hash.int, key)

      // Step 3 — every other node verifies using the signer's public key (e, n)
      const verification = {}
      for (const node of NODES) {
        if (node !== signer) {
          // recovered = signature ^ e  mod  n — must equal hash.int for VALID
          const recovered = rsaVerify(signature, key)
          verification[node] = { recovered, valid: recovered === hash.int }
        }
      }

      const accepted = Object.values(verification).every(v => v.valid)

      // Bundle all intermediate values for CryptoSteps to render
      // Note: 'key' is reserved in React, so we use 'nodeKey' here
      setSteps({ record, hash, nodeKey: key, signer, signature, verification, accepted })

      // Only update the ledger if every node verified the signature
      if (accepted) {
        // Build the updated inventory for all nodes first, then apply and persist
        const updatedInventory = {}
        for (const node of NODES) {
          updatedInventory[node] = [...inventory[node], record]
        }

        setInventory(updatedInventory)

        // Write each node's updated list back to its JSON file via Flask
        for (const [node, records] of Object.entries(updatedInventory)) {
          await saveNode(node, records)
        }
      }
    } catch (err) {
      setError('Something went wrong: ' + (err.message || err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">

      {/* Left: input form */}
      <div>
        <h2 className="text-xl font-semibold text-white mb-1">Add New Inventory Record</h2>
        <p className="text-neutral-500 text-sm mb-5">
          The signing node RSA-signs the record. All other nodes verify before anything is stored.
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <Field label="Item ID">
            <input value={form.item_id} onChange={set('item_id')} required placeholder="e.g. 005" className="field-input" />
          </Field>
          <Field label="Quantity">
            <input value={form.quantity} onChange={set('quantity')} type="number" min="0" required placeholder="e.g. 30" className="field-input" />
          </Field>
          <Field label="Price ($)">
            <input value={form.price} onChange={set('price')} type="number" min="0" required placeholder="e.g. 20" className="field-input" />
          </Field>
          <Field label="Location">
            <select value={form.location} onChange={set('location')} className="field-input">
              {/* value={n} ensures state stores 'A'/'B'/... not the display text 'Node A' */}
              {NODES.map(n => <option key={n} value={n}>Node {n}</option>)}
            </select>
          </Field>
          {/* Signing node: uses its private key d to sign; other nodes use its public key e to verify */}
          <Field label="Signing Node" hint="Signs with private key d. Others verify with public key e.">
            <select value={form.signer} onChange={set('signer')} className="field-input">
              {NODES.map(n => <option key={n} value={n}>Node {n}</option>)}
            </select>
          </Field>

          {error && (
            <div className="border border-neutral-700 text-neutral-400 rounded px-4 py-2.5 text-sm">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-white hover:bg-neutral-200 disabled:bg-neutral-800 disabled:text-neutral-600 text-black font-semibold rounded transition-colors"
          >
            {loading ? 'Computing RSA signature...' : 'Sign & Submit'}
          </button>
        </form>

        {steps?.accepted && (
          <button onClick={onDone} className="w-full mt-3 py-2.5 bg-neutral-900 hover:bg-neutral-800 border border-neutral-700 text-white font-medium rounded text-sm">
            Back to Dashboard
          </button>
        )}
      </div>

      {/* Right: step-by-step crypto breakdown (rendered by CryptoSteps) */}
      <div className="overflow-y-auto max-h-[86vh] pr-1">
        {loading && (
          <div className="text-center py-24 text-neutral-400">
            <p className="text-neutral-300">Computing RSA signature...</p>
            <p className="text-neutral-600 text-xs mt-1">pow(hash_int, d, n) with BigInt</p>
          </div>
        )}
        {steps && <CryptoSteps {...steps} />}
        {!loading && !steps && (
          <div className="text-center py-24">
            <p className="text-neutral-600 text-sm">
              Submit a record to see the<br />cryptographic process here
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

// Reusable labelled form field wrapper
function Field({ label, hint, children }) {
  return (
    <div>
      <label className="block text-sm text-neutral-400 mb-1">{label}</label>
      {hint && <p className="text-xs text-neutral-600 mb-1">{hint}</p>}
      {children}
    </div>
  )
}
