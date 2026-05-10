// CryptoSteps.jsx
// Visualises the full RSA signing and verification process step-by-step.
// Receives all intermediate crypto values from AddRecord and renders them
// as numbered cards so the process is fully transparent and traceable.
//
// Steps shown:
//   1. Record → canonical string  (record_to_string)
//   2. SHA-256 hash               (hex digest → integer)
//   3. RSA key values             (p, q, n, φ(n), e, d)
//   4. Digital signature          (hash_int ^ d mod n)
//   5. Verification by other nodes (signature ^ e mod n == hash_int?)

import { useState } from 'react'

// Renders a large BigInt or long string with a show/hide toggle to avoid overflow
function BigNum({ label, value, color = 'text-amber-300' }) {
  const [expanded, setExpanded] = useState(false)
  const s    = typeof value === 'bigint' ? value.toString() : String(value)
  const long = s.length > 50
  return (
    <div className="mb-2">
      {label && <div className="text-slate-500 text-xs mb-0.5">{label}</div>}
      <span className={`font-mono text-xs break-all ${color}`}>
        {long && !expanded ? s.slice(0, 50) + '…' : s}
      </span>
      {long && (
        <button
          onClick={() => setExpanded(x => !x)}
          className="ml-2 text-slate-600 hover:text-slate-400 text-xs underline"
        >
          {expanded ? 'collapse' : 'show full'}
        </button>
      )}
    </div>
  )
}

// Numbered step card with a vertical connecting line between steps
function Step({ n, title, children }) {
  return (
    <div className="flex gap-3 mb-2">
      <div className="flex flex-col items-center shrink-0">
        <div className="w-6 h-6 rounded-full bg-slate-800 border-2 border-cyan-700 flex items-center justify-center text-xs font-bold text-cyan-400">
          {n}
        </div>
        <div className="flex-1 w-px bg-slate-700 mt-1" />
      </div>
      <div className="bg-slate-800/70 border border-slate-700 rounded-xl p-4 flex-1 mb-3">
        <h4 className="text-sm font-semibold text-slate-100 mb-3">{title}</h4>
        {children}
      </div>
    </div>
  )
}

// Dark box used to display mathematical formulas
function Formula({ children }) {
  return (
    <div className="bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-center font-mono text-sm my-3">
      {children}
    </div>
  )
}

// Downward arrow with an optional operation label
function Arrow({ label }) {
  return (
    <div className="text-slate-600 text-xs my-1.5">
      ↓ <span className="text-slate-500">{label}</span>
    </div>
  )
}

export default function CryptoSteps({ record, hash, key: sk, signer, signature, verification, accepted }) {
  return (
    <div>
      <h3 className="text-base font-semibold text-cyan-400 mb-4">🔐 Cryptographic Process</h3>

      {/* Overall result banner — shown before the steps for quick orientation */}
      <div className={`flex items-center gap-3 px-4 py-3 rounded-xl border mb-5 ${
        accepted ? 'bg-emerald-900/25 border-emerald-700' : 'bg-red-900/25 border-red-700'
      }`}>
        <span className="text-xl">{accepted ? '✅' : '❌'}</span>
        <div>
          <p className={`font-bold text-sm ${accepted ? 'text-emerald-400' : 'text-red-400'}`}>
            {accepted ? 'Record Accepted & Added to All Nodes' : 'Record Rejected — Not Stored'}
          </p>
          <p className="text-slate-500 text-xs mt-0.5">
            {accepted
              ? 'All receiving nodes verified the digital signature.'
              : 'At least one node failed signature verification.'}
          </p>
        </div>
      </div>

      {/* ── Step 1: Serialise the record into a canonical string ── */}
      <Step n={1} title="Record → Canonical String">
        <p className="text-slate-500 text-xs mb-2">
          The record is serialised as <code className="bg-slate-700 px-1 rounded">item_id,quantity,price,location</code> before hashing.
          This guarantees a consistent byte sequence across all nodes.
        </p>
        <pre className="bg-slate-900 rounded-lg p-3 text-xs text-cyan-300 font-mono overflow-x-auto mb-2">
{JSON.stringify(record, null, 2)}
        </pre>
        <Arrow label='record_to_string(record)' />
        <BigNum label="canonical string" value={`"${hash.str}"`} color="text-yellow-300" />
      </Step>

      {/* ── Step 2: SHA-256 produces a fixed-length digest ── */}
      <Step n={2} title="SHA-256 Hash">
        <p className="text-slate-500 text-xs mb-2">
          SHA-256 produces a fixed 256-bit digest. Converting it to an integer
          lets us apply RSA modular exponentiation.
        </p>
        <BigNum label="input string" value={`"${hash.str}"`} color="text-yellow-300" />
        <Arrow label="sha256( string.encode() ).hexdigest()" />
        <BigNum label="hash hex  (64 chars)" value={hash.hex} color="text-green-400" />
        <Arrow label="int( hash_hex, 16 )" />
        <BigNum label="hash integer" value={hash.int} color="text-amber-300" />
      </Step>

      {/* ── Step 3: Show all 6 RSA key values for the signing node ── */}
      <Step n={3} title={`Node ${signer}'s RSA Key Values`}>
        <p className="text-slate-500 text-xs mb-2">
          Keys are derived from the assignment-provided p, q, e values.
        </p>
        <Formula>
          <div className="space-y-1 text-left inline-block">
            <div><span className="text-purple-400">n</span><span className="text-slate-500"> = p × q</span></div>
            <div><span className="text-purple-300">φ(n)</span><span className="text-slate-500"> = (p−1) × (q−1)</span></div>
            <div>
              {/* d is the private key — derived via modular inverse of e */}
              <span className="text-red-400">d</span>
              <span className="text-slate-500"> = </span>
              <span className="text-green-400">e</span>
              <span className="text-slate-500">⁻¹ mod φ(n)</span>
              <span className="text-slate-600 text-xs ml-2">← pow(e, −1, φ(n))</span>
            </div>
          </div>
        </Formula>
        <BigNum label="p  (prime 1)"      value={sk.p}   color="text-slate-300" />
        <BigNum label="q  (prime 2)"      value={sk.q}   color="text-slate-300" />
        <BigNum label="n = p×q"           value={sk.n}   color="text-purple-400" />
        <BigNum label="φ(n)"              value={sk.phi} color="text-purple-300" />
        <BigNum label="e  (public exp)"   value={sk.e}   color="text-green-400" />
        <BigNum label="d  (private key)"  value={sk.d}   color="text-red-400" />
      </Step>

      {/* ── Step 4: Signing — uses the private key d ── */}
      <Step n={4} title={`Digital Signature — Node ${signer} Signs`}>
        <p className="text-slate-500 text-xs mb-1">
          Node {signer} uses its <span className="text-red-400">private key d</span> to sign the hash.
          Only the holder of d can produce a valid signature.
        </p>
        <Formula>
          <span className="text-cyan-300">signature</span>
          <span className="text-slate-500"> = </span>
          <span className="text-amber-300">hash_int</span>
          <span className="text-slate-400"> ^ </span>
          <span className="text-red-400">d</span>
          <span className="text-slate-500"> mod </span>
          <span className="text-purple-400">n</span>
          <br />
          <span className="text-slate-500 text-xs">pow( hash_int, d, n )</span>
        </Formula>
        <BigNum label="hash_int"    value={hash.int}  color="text-amber-300" />
        <BigNum label="d"           value={sk.d}      color="text-red-400" />
        <BigNum label="n"           value={sk.n}      color="text-purple-400" />
        <Arrow label="pow( hash_int, d, n )" />
        <BigNum label="→ signature" value={signature} color="text-cyan-400" />
      </Step>

      {/* ── Step 5: Verification — each other node uses the signer's public key ── */}
      <Step n={5} title="Verification by Other Nodes">
        <p className="text-slate-500 text-xs mb-1">
          Each receiving node uses Node {signer}'s <span className="text-green-400">public key (e, n)</span> to
          recover the original hash. A match proves the record is authentic and unmodified.
        </p>
        <Formula>
          <span className="text-cyan-300">recovered</span>
          <span className="text-slate-500"> = </span>
          <span className="text-amber-300">signature</span>
          <span className="text-slate-400"> ^ </span>
          <span className="text-green-400">e</span>
          <span className="text-slate-500"> mod </span>
          <span className="text-purple-400">n</span>
          <br />
          {/* Valid only if the recovered hash matches the original hash_int */}
          <span className="text-slate-500 text-xs">valid  if  recovered == hash_int</span>
        </Formula>

        <div className="space-y-3 mt-2">
          {Object.entries(verification).map(([node, v]) => (
            <div
              key={node}
              className={`rounded-xl border p-3 ${
                v.valid ? 'border-emerald-800 bg-emerald-950/50' : 'border-red-800 bg-red-950/50'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold text-slate-200 text-sm">Node {node}</span>
                <span className={`text-xs font-bold px-2.5 py-0.5 rounded-full ${
                  v.valid ? 'bg-emerald-700 text-white' : 'bg-red-700 text-white'
                }`}>
                  {v.valid ? '✓ VALID' : '✗ INVALID'}
                </span>
              </div>
              <BigNum label="recovered hash" value={v.recovered} color={v.valid ? 'text-emerald-400' : 'text-red-400'} />
              <p className={`font-mono text-xs mt-1 ${v.valid ? 'text-emerald-600' : 'text-red-600'}`}>
                recovered == hash_int → <strong>{v.valid ? 'TRUE' : 'FALSE'}</strong>
              </p>
            </div>
          ))}
        </div>
      </Step>
    </div>
  )
}
