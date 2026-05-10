// AddRecord.jsx
// Handles the full add-record flow: form input → RSA signing → multi-node
// verification → ledger update. Mirrors add_new_record() in main.py.
//
// On submit:
//   1. The record is hashed with SHA-256              (hashRecord)
//   2. The signing node signs the hash with its d key (rsaSign)
//   3. All other nodes verify with the signer's e key (rsaVerify)
//   4. If all verify VALID, the record is appended to all 4 nodes in state
//
// The right panel passes all intermediate values to CryptoSteps for display.

import { useState } from 'react'
import { KEYS, hashRecord, rsaSign, rsaVerify } from '../crypto.js'
import CryptoSteps from './CryptoSteps.jsx'

const NODES = ['A', 'B', 'C', 'D']

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
      setSteps({ record, hash, key, signer, signature, verification, accepted })

      // Only update the ledger if every node verified the signature
      if (accepted) {
        setInventory(prev => {
          const next = {}
          for (const node of NODES) next[node] = [...prev[node], record]
          return next
        })
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">

      {/* ── Left: input form ── */}
      <div>
        <h2 className="text-xl font-semibold text-slate-200 mb-1">Add New Inventory Record</h2>
        <p className="text-slate-500 text-sm mb-5">
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
              {NODES.map(n => <option key={n}>Node {n}</option>)}
            </select>
          </Field>
          {/* Signing node: uses its private key d to sign; other nodes use its public key e to verify */}
          <Field label="Signing Node" hint="Signs with private key d. Others verify with public key e.">
            <select value={form.signer} onChange={set('signer')} className="field-input">
              {NODES.map(n => <option key={n}>Node {n}</option>)}
            </select>
          </Field>

          {error && (
            <div className="bg-red-900/30 border border-red-800 text-red-300 rounded-xl px-4 py-2.5 text-sm">
              ❌ {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-cyan-600 hover:bg-cyan-500 disabled:bg-slate-700 disabled:text-slate-500 text-white font-semibold rounded-xl transition-colors"
          >
            {loading ? '🔐 Computing RSA signature…' : '🔐 Sign & Submit'}
          </button>
        </form>

        {steps?.accepted && (
          <button onClick={onDone} className="w-full mt-3 py-2.5 bg-emerald-800 hover:bg-emerald-700 text-white font-medium rounded-xl text-sm">
            ← Back to Dashboard
          </button>
        )}
      </div>

      {/* ── Right: step-by-step crypto breakdown (rendered by CryptoSteps) ── */}
      <div className="overflow-y-auto max-h-[86vh] pr-1">
        {loading && (
          <div className="text-center py-24 text-slate-400">
            <div className="text-5xl mb-3 animate-pulse">🔐</div>
            <p className="text-slate-300">Computing RSA signature…</p>
            <p className="text-slate-600 text-xs mt-1">pow(hash_int, d, n) with BigInt</p>
          </div>
        )}
        {steps && <CryptoSteps {...steps} />}
        {!loading && !steps && (
          <div className="text-center py-24">
            <div className="text-6xl opacity-20 mb-4">🔒</div>
            <p className="text-slate-600 text-sm">
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
      <label className="block text-sm text-slate-400 mb-1">{label}</label>
      {hint && <p className="text-xs text-slate-600 mb-1">{hint}</p>}
      {children}
    </div>
  )
}
