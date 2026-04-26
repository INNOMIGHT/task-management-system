import { useEffect, useState } from "react";
import API from "../services/api";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";

function Dashboard() {
  const [clients, setClients] = useState([]);
  const [name, setName] = useState("");
  const navigate = useNavigate();

  const fetchClients = async () => {
    try {
      const res = await API.get("/clients/");
      setClients(res.data);
    } catch {
      alert("Error fetching clients");
    }
  };

  useEffect(() => {
    fetchClients();
  }, []);

  const addClient = async () => {
    if (!name) return;
    try {
      await API.post("/clients/", { name });
      setName("");
      fetchClients();
    } catch {
      alert("Error adding client");
    }
  };

  return (
    <>
      <Navbar />

      <div className="container mt-4">
        <h3 className="mb-4">Your Clients</h3>

        {/* Add Client */}
        <div className="d-flex mb-4">
          <input
            className="form-control me-2"
            placeholder="New client name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <button className="btn btn-dark" onClick={addClient}>
            Add
          </button>
        </div>

        {/* Client List */}
        <div className="row">
          {clients.map((client) => (
            <div key={client.id} className="col-md-4 mb-3">
              <div
                className="card shadow-sm p-3"
                style={{ cursor: "pointer" }}
                onClick={() => navigate(`/client/${client.id}`)}
              >
                <h5>{client.name}</h5>
                <small className="text-muted">
                  Click to manage tasks →
                </small>
              </div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

export default Dashboard;