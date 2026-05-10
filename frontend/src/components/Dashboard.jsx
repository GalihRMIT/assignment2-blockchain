// Dashboard.jsx
// Displays all 4 inventory node ledgers side-by-side in a grid.
// Also runs a consensus check — if every node holds identical data the
// ledger is considered consistent; any mismatch flags a potential tampering.
// Mirrors view_all_inventories() in main.py.

// Per-node accent colours for the left border and badge
const BORDER = { A: 'border-l-cyan-500',    B: 'border-l-purple-500',
                  C: 'border-l-emerald-500', D: 'border-l-amber-500' }
const BADGE  = { A: 'bg-cyan-900 text-cyan-300',      B: 'bg-purple-900 text-purple-300',
                  C: 'bg-emerald-900 text-emerald-300', D: 'bg-amber-900 text-amber-300' }

export default function Dashboard({ inventory }) {
  const vals    = Object.values(inventory)
  // Consensus: stringify-compare every node's data against node A's data
  const allSame = vals.every(v => JSON.stringify(v) === JSON.stringify(vals[0]))

  return (
    <div>
      {/* Consensus banner — green if all nodes match, red if they diverge */}
      <div className={`flex items-center gap-3 px-4 py-3 rounded-xl border mb-5 ${
        allSame ? 'bg-emerald-900/20 border-emerald-800' : 'bg-red-900/20 border-red-800'
      }`}>
        <span className="text-lg">{allSame ? '✅' : '⚠️'}</span>
        <div>
          <p className={`font-medium text-sm ${allSame ? 'text-emerald-400' : 'text-red-400'}`}>
            {allSame ? 'All 4 nodes in consensus — ledger is consistent' : 'Nodes are out of sync!'}
          </p>
          <p className="text-slate-500 text-xs mt-0.5">
            {allSame
              ? 'Every node holds identical inventory data.'
              : 'Node data does not match — ledger may have been tampered with.'}
          </p>
        </div>
      </div>

      {/* One card per node showing its records as a table */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {Object.entries(inventory).map(([node, items]) => (
          <div key={node} className={`bg-slate-900 border border-slate-800 border-l-4 ${BORDER[node]} rounded-xl p-4`}>
            <div className="flex items-center gap-2 mb-3">
              <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${BADGE[node]}`}>
                NODE {node}
              </span>
              <span className="text-slate-500 text-xs">{items.length} record{items.length !== 1 ? 's' : ''}</span>
            </div>

            {items.length === 0 ? (
              <p className="text-slate-600 text-sm italic text-center py-4">No records</p>
            ) : (
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-slate-600 text-xs border-b border-slate-800">
                    <th className="text-left pb-1.5 font-medium">ID</th>
                    <th className="text-left pb-1.5 font-medium">Qty</th>
                    <th className="text-left pb-1.5 font-medium">Price</th>
                    <th className="text-left pb-1.5 font-medium">Loc</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((item, i) => (
                    <tr key={i} className="border-b border-slate-800/50 last:border-0">
                      <td className="py-1.5 font-mono text-cyan-400">{item.item_id}</td>
                      <td className="py-1.5 text-slate-300">{item.quantity}</td>
                      <td className="py-1.5 text-slate-300">${item.price}</td>
                      <td className="py-1.5 text-slate-300">{item.location}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
