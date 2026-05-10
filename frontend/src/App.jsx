// App.jsx
// Root component — owns the shared inventory state and tab navigation.
// Inventory is initialised directly from the 4 JSON files (no backend needed).
// All changes (add/delete) update React state in memory; the JSON files on disk
// are the source of truth when the page is refreshed.

import { useState } from 'react'
import invA from '../../data/inventory_A.json'
import invB from '../../data/inventory_B.json'
import invC from '../../data/inventory_C.json'
import invD from '../../data/inventory_D.json'
import Dashboard    from './components/Dashboard.jsx'
import AddRecord    from './components/AddRecord.jsx'
import QueryItem    from './components/QueryItem.jsx'
import DeleteRecord from './components/DeleteRecord.jsx'
import KeysViewer   from './components/KeysViewer.jsx'

const TABS = ['Dashboard', 'Add Record', 'Query', 'Delete', 'Node Keys']

export default function App() {
  const [tab, setTab] = useState('Dashboard')

  // Single source of truth for all 4 node ledgers — passed down as props
  const [inventory, setInventory] = useState({
    A: invA, B: invB, C: invC, D: invD,
  })

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="bg-slate-900 border-b border-slate-800">
        <div className="max-w-6xl mx-auto px-6 pt-5">
          <h1 className="text-xl font-bold text-cyan-400 mb-1">⛓️ Secure DLT Inventory System</h1>
          <p className="text-slate-500 text-xs mb-4">RSA-signed distributed ledger · 4 nodes · SHA-256</p>

          {/* Tab bar — controls which feature panel is shown */}
          <nav className="flex gap-1">
            {TABS.map(t => (
              <button
                key={t}
                onClick={() => setTab(t)}
                className={`px-4 py-2 text-sm rounded-t-lg border-t border-l border-r transition-colors ${
                  tab === t
                    ? 'bg-slate-950 text-cyan-400 border-slate-700'
                    : 'text-slate-500 border-transparent hover:text-slate-300'
                }`}
              >
                {t}
              </button>
            ))}
          </nav>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8">
        {tab === 'Dashboard'  && <Dashboard inventory={inventory} />}
        {tab === 'Add Record' && (
          // setInventory lets AddRecord append the new record to all 4 nodes in state
          <AddRecord
            inventory={inventory}
            setInventory={setInventory}
            onDone={() => setTab('Dashboard')}
          />
        )}
        {tab === 'Query'      && <QueryItem inventory={inventory} />}
        {tab === 'Delete'     && (
          // setInventory lets DeleteRecord remove the record from all 4 nodes in state
          <DeleteRecord
            inventory={inventory}
            setInventory={setInventory}
            onDone={() => setTab('Dashboard')}
          />
        )}
        {tab === 'Node Keys'  && <KeysViewer />}
      </main>
    </div>
  )
}
