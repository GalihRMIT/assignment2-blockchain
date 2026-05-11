import { useState, useEffect, useRef } from 'react'

export default function App() {
  const [log, setLog]         = useState([])
  const [itemId, setItemId]   = useState('126')
  const [loading, setLoading] = useState(false)
  const logRef = useRef(null)

  // Auto-scroll log to bottom whenever it updates
  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight
    }
  }, [log])

  const handleSubmit = async () => {
    setLoading(true)
    setLog([])

    const res  = await fetch('/api/query', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ item_id: itemId }),
    })
    const data = await res.json()
    setLog(data.lines)
    setLoading(false)
  }

  return (
    <div className="container">

      {/* Header */}
      <div className="header">
        <h1>Distributed Inventory Query System</h1>
      </div>
      <div className="divider" />

      {/* Query form */}
      <div className="form-row">
        <span className="label">Inventory ID:</span>
        <select
          value={itemId}
          onChange={e => setItemId(e.target.value)}
          className="select"
        >
          <option value="126">126</option>
          <option value="127">127</option>
          <option value="128">128</option>
          <option value="129">129</option>
        </select>

        <button
          onClick={handleSubmit}
          disabled={loading}
          className="btn"
        >
          {loading ? 'Processing...' : 'Submit Query Request'}
        </button>
      </div>
      <div className="divider" />

      {/* Output log */}
      <div className="log" ref={logRef}>
        {log.map((line, i) => (
          <div key={i} className="log-line">
            {line === '' ? ' ' : line}
          </div>
        ))}
      </div>

    </div>
  )
}
