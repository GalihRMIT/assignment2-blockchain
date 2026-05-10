// CryptoSteps.jsx
// Visualises the full RSA signing and verification process step-by-step.
// Receives all intermediate crypto values from AddRecord and renders them
// as numbered cards so the process is fully transparent and traceable.
//
// Steps shown:
//   1. Record -> canonical string  (record_to_string)
//   2. SHA-256 hash               (hex digest -> integer)
//   3. RSA key values             (p, q, n, phi(n), e, d)
//   4. Digital signature          (hash_int ^ d mod n)
//   5. Verification by other nodes (signature ^ e mod n == hash_int?)

import { useState } from 'react'

// Renders a large BigInt or long string with a show/hide toggle to avoid overflow
function BigNum({ label, value, dim = false }) {
  const [expanded, setExpanded] = useState(false)
  const s    = typeof value === 'bigint' ? value.toString() : String(value)
  const long = s.length > 50
  return (
    <div className="mb-2">
      {label && <div className="text-neutral-500 text-xs mb-0.5">{label}</div>}
      <span className={`font-mono text-xs break-all ${dim ? 'text-neutral-500' : 'text-neutral-200'}`}>
        {long && !expanded ? s.slice(0, 50) + '...' : s}
      </span>
      {long && (
        <button
          onClick={() => setExpanded(x => !x)}
          className="ml-2 text-neutral-600 hover:text-neutral-400 text-xs underline"
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
        <div className="w-6 h-6 rounded-full bg-neutral-900 border border-neutral-600 flex items-center justify-center text-xs font-bold text-white">
          {n}
        </div>
        <div className="flex-1 w-px bg-neutral-800 mt-1" />
      </div>
      <div className="bg-neutral-950 border border-neutral-800 rounded p-4 flex-1 mb-3">
        <h4 className="text-sm font-semibold text-white mb-3">{title}</h4>
        {children}
      </div>
    </div>
  )
}

// Dark box used to display mathematical formulas
function Formula({ children }) {
  return (
    <div className="bg-black border border-neutral-800 rounded px-4 py-2.5 text-center font-mono text-sm my-3">
      {children}
    </div>
  )
}

// Downward arrow with an optional operation label
function Arrow({ label }) {
  return (
    <div className="text-neutral-600 text-xs my-1.5">
      {'>>'} <span className="text-neutral-500">{label}</span>
    </div>
  )
}

export default function CryptoSteps({ record, hash, nodeKey: sk, signer, signature, verification, accepted }) {
  return (
    <div>
      <h3 className="text-base font-semibold text-white mb-4">Cryptographic Process</h3>

      {/* Overall result banner — shown before the steps for quick orientation */}
      <div className={`flex items-center gap-3 px-4 py-3 rounded border mb-5 ${
        accepted ? 'border-neutral-700' : 'border-white'
      }`}>
        <div>
          <p className="font-bold text-sm text-white">
            {accepted ? 'Record Accepted & Added to All Nodes' : 'Record Rejected — Not Stored'}
          </p>
          <p className="text-neutral-500 text-xs mt-0.5">
            {accepted
              ? 'All receiving nodes verified the digital signature.'
              : 'At least one node failed signature verification.'}
          </p>
        </div>
      </div>

      {/* Step 1: Serialise the record into a canonical string */}
      <Step n={1} title="Record to Canonical String">
        <p className="text-neutral-500 text-xs mb-2">
          The record is serialised as <code className="bg-neutral-900 px-1 rounded">item_id,quantity,price,location</code> before hashing.
          This guarantees a consistent byte sequence across all nodes.
        </p>
        <pre className="bg-black border border-neutral-800 rounded p-3 text-xs text-neutral-300 font-mono overflow-x-auto mb-2">
{JSON.stringify(record, null, 2)}
        </pre>
        <Arrow label='record_to_string(record)' />
        <BigNum label="canonical string" value={`"${hash.str}"`} />
      </Step>

      {/* Step 2: SHA-256 produces a fixed-length digest */}
      <Step n={2} title="SHA-256 Hash">
        <p className="text-neutral-500 text-xs mb-2">
          SHA-256 produces a fixed 256-bit digest. Converting it to an integer
          lets us apply RSA modular exponentiation.
        </p>
        <BigNum label="input string" value={`"${hash.str}"`} />
        <Arrow label="sha256( string.encode() ).hexdigest()" />
        <BigNum label="hash hex  (64 chars)" value={hash.hex} />
        <Arrow label="int( hash_hex, 16 )" />
        <BigNum label="hash integer" value={hash.int} />
      </Step>

      {/* Step 3: Show all 6 RSA key values for the signing node */}
      <Step n={3} title={`Node ${signer}'s RSA Key Values`}>
        <p className="text-neutral-500 text-xs mb-2">
          Keys are derived from the assignment-provided p, q, e values.
        </p>
        <Formula>
          <div className="space-y-1 text-left inline-block text-neutral-300">
            <div>n = p x q</div>
            <div>phi(n) = (p-1) x (q-1)</div>
            <div>
              {/* d is the private key — derived via modular inverse of e */}
              d = e^-1 mod phi(n)
              <span className="text-neutral-600 text-xs ml-2">pow(e, -1, phi(n))</span>
            </div>
          </div>
        </Formula>
        <BigNum label="p  (prime 1)"      value={sk.p}   dim />
        <BigNum label="q  (prime 2)"      value={sk.q}   dim />
        <BigNum label="n = p x q"         value={sk.n}   />
        <BigNum label="phi(n)"            value={sk.phi} />
        <BigNum label="e  (public exp)"   value={sk.e}   />
        <BigNum label="d  (private key)"  value={sk.d}   />
      </Step>

      {/* Step 4: Signing — uses the private key d */}
      <Step n={4} title={`Digital Signature — Node ${signer} Signs`}>
        <p className="text-neutral-500 text-xs mb-1">
          Node {signer} uses its private key d to sign the hash.
          Only the holder of d can produce a valid signature.
        </p>
        <Formula>
          <span className="text-neutral-300">
            signature = hash_int ^ d mod n
          </span>
          <br />
          <span className="text-neutral-500 text-xs">pow( hash_int, d, n )</span>
        </Formula>
        <BigNum label="hash_int"    value={hash.int}  />
        <BigNum label="d"           value={sk.d}      />
        <BigNum label="n"           value={sk.n}      />
        <Arrow label="pow( hash_int, d, n )" />
        <BigNum label="signature"   value={signature} />
      </Step>

      {/* Step 5: Verification — each other node uses the signer's public key */}
      <Step n={5} title="Verification by Other Nodes">
        <p className="text-neutral-500 text-xs mb-1">
          Each receiving node uses Node {signer}'s public key (e, n) to
          recover the original hash. A match proves the record is authentic and unmodified.
        </p>
        <Formula>
          <span className="text-neutral-300">
            recovered = signature ^ e mod n
          </span>
          <br />
          {/* Valid only if the recovered hash matches the original hash_int */}
          <span className="text-neutral-500 text-xs">valid  if  recovered == hash_int</span>
        </Formula>

        <div className="space-y-3 mt-2">
          {Object.entries(verification).map(([node, v]) => (
            <div
              key={node}
              className={`rounded border p-3 ${
                v.valid ? 'border-neutral-700' : 'border-white'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold text-white text-sm">Node {node}</span>
                <span className={`text-xs font-bold px-2.5 py-0.5 rounded ${
                  v.valid ? 'bg-neutral-800 text-white' : 'bg-white text-black'
                }`}>
                  {v.valid ? 'VALID' : 'INVALID'}
                </span>
              </div>
              <BigNum label="recovered hash" value={v.recovered} />
              <p className="font-mono text-xs mt-1 text-neutral-500">
                recovered == hash_int: <strong className="text-white">{v.valid ? 'TRUE' : 'FALSE'}</strong>
              </p>
            </div>
          ))}
        </div>
      </Step>
    </div>
  )
}
