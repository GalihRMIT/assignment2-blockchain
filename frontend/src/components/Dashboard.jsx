// Dashboard.jsx
// Displays all 4 inventory node ledgers and runs a consensus check.
// Mirrors view_all_inventories() in main.py.

export default function Dashboard({ inventory }) {
  const vals    = Object.values(inventory)
  // Consensus: every node must hold identical data
  const allSame = vals.every(v => JSON.stringify(v) === JSON.stringify(vals[0]))

  return (
    <div>
      {/* Consensus banner */}
      <div className={`border rounded px-4 py-3 mb-5 text-sm ${
        allSame ? 'border-neutral-700' : 'border-white'
      }`}>
        <p className="font-medium text-white">
          {allSame ? 'Consensus: all 4 nodes are in sync' : 'Warning: nodes are out of sync'}
        </p>
        <p className="text-neutral-500 text-xs mt-0.5">
          {allSame
            ? 'Every node holds identical inventory data.'
            : 'Node data does not match — ledger may have been tampered with.'}
        </p>
      </div>

      {/* Node cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {Object.entries(inventory).map(([node, items]) => (
          <div key={node} className="bg-neutral-950 border border-neutral-800 rounded p-4">
            <div className="flex items-center gap-3 mb-3">
              <span className="text-xs font-bold border border-neutral-700 px-2.5 py-1 rounded">
                NODE {node}
              </span>
              <span className="text-neutral-600 text-xs">
                {items.length} record{items.length !== 1 ? 's' : ''}
              </span>
            </div>

            {items.length === 0 ? (
              <p className="text-neutral-600 text-sm text-center py-4">No records</p>
            ) : (
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-neutral-600 text-xs border-b border-neutral-800">
                    <th className="text-left pb-1.5 font-medium">ID</th>
                    <th className="text-left pb-1.5 font-medium">Qty</th>
                    <th className="text-left pb-1.5 font-medium">Price</th>
                    <th className="text-left pb-1.5 font-medium">Loc</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((item, i) => (
                    <tr key={i} className="border-b border-neutral-800/50 last:border-0">
                      <td className="py-1.5 font-mono text-white">{item.item_id}</td>
                      <td className="py-1.5 text-neutral-300">{item.quantity}</td>
                      <td className="py-1.5 text-neutral-300">${item.price}</td>
                      <td className="py-1.5 text-neutral-300">{item.location}</td>
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
