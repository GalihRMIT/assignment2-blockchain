// App.jsx
// Root component — owns the shared inventory state and tab navigation.
// Inventory is fetched fresh from Flask on mount (GET /api/inventory) so the
// UI always reflects the actual JSON files on disk.

import { useState, useEffect } from 'react'
import Dashboard    from './components/Dashboard.jsx'
import AddRecord    from './components/AddRecord.jsx'
import QueryItem    from './components/QueryItem.jsx'
import DeleteRecord from './components/DeleteRecord.jsx'
import KeysViewer   from './components/KeysViewer.jsx'

const TABS = ['Dashboard', 'Add Record', 'Query', 'Delete', 'Node Keys']

export default function App() {
  const [tab, setTab]             = useState('Dashboard')
  const [inventory, setInventory] = useState(null)
  const [loadError, setLoadError] = useState(null)

  // Load all 4 node ledgers from Flask on first render
  useEffect(() => {
    fetch('/api/inventory')
      .then(r => r.json())
      .then(setInventory)
      .catch(() => setLoadError('Could not reach the Flask server. Run:  python api.py'))
  }, [])

  return (
    <div className="min-h-screen bg-black text-white">
      <header className="bg-neutral-950 border-b border-neutral-800">
        <div className="max-w-6xl mx-auto px-6 pt-5">
          <h1 className="text-xl font-bold tracking-wide mb-1">Secure DLT Inventory System</h1>
          <p className="text-neutral-500 text-xs mb-4">
            RSA-signed distributed ledger &middot; 4 nodes &middot; SHA-256
          </p>

          {/* Tab bar */}
          <nav className="flex gap-1">
            {TABS.map(t => (
              <button
                key={t}
                onClick={() => setTab(t)}
                className={`px-4 py-2 text-sm rounded-t border-t border-l border-r transition-colors ${
                  tab === t
                    ? 'bg-black text-white border-neutral-700'
                    : 'text-neutral-500 border-transparent hover:text-neutral-300'
                }`}
              >
                {t}
              </button>
            ))}
          </nav>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8">
        {loadError && (
          <div className="border border-neutral-700 rounded px-5 py-4 text-neutral-400 text-sm">
            {loadError}
          </div>
        )}

        {!inventory && !loadError && (
          <div className="text-center py-24 text-neutral-600">
            <p>Loading inventory from Flask...</p>
          </div>
        )}

        {inventory && (
          <>
            {tab === 'Dashboard'  && <Dashboard inventory={inventory} />}
            {tab === 'Add Record' && (
              <AddRecord
                inventory={inventory}
                setInventory={setInventory}
                onDone={() => setTab('Dashboard')}
              />
            )}
            {tab === 'Query'  && <QueryItem inventory={inventory} />}
            {tab === 'Delete' && (
              <DeleteRecord
                inventory={inventory}
                setInventory={setInventory}
                onDone={() => setTab('Dashboard')}
              />
            )}
            {tab === 'Node Keys' && <KeysViewer />}
          </>
        )}
      </main>
    </div>
  )
}
