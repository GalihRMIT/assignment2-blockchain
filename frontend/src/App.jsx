import { useEffect, useState } from "react";
import "./style.css";

function App() {
  const [inventories, setInventories] = useState({});
  const [addResult, setAddResult] = useState(null);
  const [queryResult, setQueryResult] = useState(null);
  const [queryLoading, setQueryLoading] = useState(false);
  const [deleteResult, setDeleteResult] = useState(null);

  const [recordForm, setRecordForm] = useState({
    item_id: "",
    quantity: "",
    price: "",
    location: "A",
    signer: "A"
  });

  const [queryItemId, setQueryItemId] = useState("");
  const [deleteItemId, setDeleteItemId] = useState("");

  const loadInventories = async () => {
    try {
      const response = await fetch("http://127.0.0.1:5000/inventories");
      const data = await response.json();
      setInventories(data);
    } catch (error) {
      console.error("Error loading inventories:", error);
    }
  };

  useEffect(() => {
    loadInventories();
  }, []);

  const handleAddRecord = async () => {
    const response = await fetch("http://127.0.0.1:5000/add-record", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(recordForm)
    });
    const data = await response.json();
    setAddResult(data);
    loadInventories();
  };

  const handleQuery = async () => {
    setQueryLoading(true);
    setQueryResult(null);
    const response = await fetch("http://127.0.0.1:5000/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ item_id: queryItemId })
    });
    const data = await response.json();
    setQueryResult(data);
    setQueryLoading(false);
  };

  const handleDelete = async () => {
    const response = await fetch("http://127.0.0.1:5000/delete-record", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ item_id: deleteItemId })
    });
    const data = await response.json();
    setDeleteResult(data);
    loadInventories();
  };

  return (
    <div className="page">
      <h1>Secure Inventory System</h1>
      <p>
        Simple web interface for RSA signing, verification, inventory node storage,
        and consensus checking.
      </p>

      {/* Section 1: View Inventories */}
      <section className="tool-box">
        <h2>View Inventory Nodes</h2>
        <button onClick={loadInventories}>Refresh Inventories</button>

        <div className="inventory-grid">
          {Object.entries(inventories).map(([nodeName, records]) => (
            <div className="node-card" key={nodeName}>
              <h3>{nodeName}</h3>
              <table>
                <thead>
                  <tr>
                    <th>Item ID</th>
                    <th>Quantity</th>
                    <th>Price</th>
                    <th>Location</th>
                  </tr>
                </thead>
                <tbody>
                  {records.map((item) => (
                    <tr key={item.item_id}>
                      <td>{item.item_id}</td>
                      <td>{item.quantity}</td>
                      <td>{item.price}</td>
                      <td>{item.location}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ))}
        </div>
      </section>

      {/* Section 2: Add Record */}
      <section className="tool-box">
        <h2>Add New Inventory Record</h2>

        <label>Item ID:</label>
        <input
          value={recordForm.item_id}
          onChange={(e) => setRecordForm({ ...recordForm, item_id: e.target.value })}
        />

        <label>Quantity:</label>
        <input
          type="number"
          value={recordForm.quantity}
          onChange={(e) => setRecordForm({ ...recordForm, quantity: e.target.value })}
        />

        <label>Price:</label>
        <input
          type="number"
          value={recordForm.price}
          onChange={(e) => setRecordForm({ ...recordForm, price: e.target.value })}
        />

        <label>Location:</label>
        <select
          value={recordForm.location}
          onChange={(e) => setRecordForm({ ...recordForm, location: e.target.value })}
        >
          <option>A</option>
          <option>B</option>
          <option>C</option>
          <option>D</option>
        </select>

        <label>Submitting Inventory Node:</label>
        <select
          value={recordForm.signer}
          onChange={(e) => setRecordForm({ ...recordForm, signer: e.target.value })}
        >
          <option>A</option>
          <option>B</option>
          <option>C</option>
          <option>D</option>
        </select>

        <button onClick={handleAddRecord}>Submit Record</button>

        {addResult && (
          <div className="output">
            <h3>Digital Signature and Consensus Output</h3>
            <p><b>Status:</b> {addResult.message}</p>
            <p><b>Submitting Node:</b> {addResult.submitting_node}</p>
            <p><b>Hash Hex:</b> {addResult.hash_hex}</p>
            <p><b>Hash Integer:</b> {addResult.hash_int}</p>
            <p><b>Digital Signature:</b> {addResult.signature}</p>
            
            {addResult.signature_verification && (
              <>
                <h4>Signature Verification</h4>
                <p>
                  <b>Original Hash:</b>{" "}
                  {addResult.signature_verification.original_hash}
                </p>
                <p>
                  <b>Recovered Hash:</b>{" "}
                  {addResult.signature_verification.recovered_hash}
                </p>
                <p>
                  <b>Verification Result:</b>{" "}
                  {addResult.signature_verification.valid ? "VALID" : "INVALID"}
                </p>
              </>
            )}

            <p><b>Consensus Result:</b> {addResult.consensus_result}</p>

            {addResult.pbft_results && (
              <>
                <h4>PBFT Pre-Prepare Phase</h4>
                <p>
                  <b>Proposal:</b>{" "}
                  {addResult.pbft_results.pre_prepare_phase.proposal}
                </p>

                <h4>PBFT Prepare Phase</h4>
                {Object.entries(addResult.pbft_results.prepare_phase).map(
                  ([node, result]) => (
                    <div className="node-result" key={node}>
                      <p><b>{node}</b></p>
                      <p>Signature Check: {result.signature_check}</p>
                      <p>Duplicate Check: {result.duplicate_check}</p>
                      <p>Node Decision: {result.decision}</p>
                    </div>
                  )
                )}
                 <h4>PBFT Commit Phase</h4>
                  <p>
                    <b>Total Nodes:</b>{" "}
                    {addResult.pbft_results.commit_phase.total_nodes}
                  </p>
                  <p>
                    <b>Required Accepts:</b>{" "}
                    {addResult.pbft_results.commit_phase.required_accepts}
                  </p>
                  <p>
                    <b>Accept Count:</b>{" "}
                    {addResult.pbft_results.commit_phase.accept_count}
                  </p>
                  <p>
                    <b>Reject Count:</b>{" "}
                    {addResult.pbft_results.commit_phase.reject_count}
                  </p>
                  <p>
                    <b>Final PBFT Decision:</b>{" "}
                    {addResult.pbft_results.commit_phase.consensus_result}
                  </p>
              </>
            )}
          </div>
        )}
      </section>

      {/* Section 3: Query with Harn Multi-Signature */}
      <section className="tool-box">
        <h2>Query Inventory Node</h2>

        <label>Message:</label>
        <input
          value={queryItemId}
          placeholder="Inventory node ID"
          onChange={(e) => setQueryItemId(e.target.value)}
        />

        <button onClick={handleQuery} disabled={queryLoading}>
          {queryLoading ? "Processing..." : "Query"}
        </button>

        {queryResult && (
          <div className="output">
            <h3>Query Result</h3>
            <p><b>Status:</b> {queryResult.message}</p>
            <p><b>Consensus Result:</b> {queryResult.consensus_result}</p>

            {queryResult.item && (
              <>
                <h4>Item Record</h4>
                <table>
                  <thead>
                    <tr>
                      <th>Item ID</th>
                      <th>Quantity</th>
                      <th>Price</th>
                      <th>Location</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>{queryResult.item.item_id}</td>
                      <td>{queryResult.item.quantity}</td>
                      <td>{queryResult.item.price}</td>
                      <td>{queryResult.item.location}</td>
                    </tr>
                  </tbody>
                </table>
              </>
            )}

            {queryResult.lines && queryResult.lines.length > 0 && (
              <>
                <h4>Cryptographic Proof</h4>
                <div className="crypto-log">
                  {queryResult.lines.map((line, i) => (
                    <div key={i}>{line === "" ? " " : line}</div>
                  ))}
                </div>
              </>
            )}
          </div>
        )}
      </section>

      {/* Section 4: Delete Record */}
      <section className="tool-box">
        <h2>Delete Inventory Record</h2>

        <label>Item ID:</label>
        <input
          value={deleteItemId}
          onChange={(e) => setDeleteItemId(e.target.value)}
        />

        <button onClick={handleDelete}>Delete Record</button>

        {deleteResult && (
          <div className="output">
            <p><b>Status:</b> {deleteResult.message}</p>
          </div>
        )}
      </section>
    </div>
  );
}

export default App;
