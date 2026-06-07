import { useEffect, useState } from "react";
import API from "../services/api";

function TaskModal({ task, onClose, refreshTasks }) {
  const [logs, setLogs] = useState([]);
  const [date, setDate] = useState("");
  const [hours, setHours] = useState("");
  const [desc, setDesc] = useState("");

  const fetchLogs = async () => {
    const res = await API.get(`/tasks/${task.id}/logs`);
    setLogs(res.data);
  };

  useEffect(() => {
    if (task) fetchLogs();
  }, [task]);

  const addLog = async () => {
    if (!date || !hours) return;

    await API.post(`/tasks/${task.id}/log-time`, {
      date,
      hours: parseFloat(hours),
      description: desc,
    });

    setDate("");
    setHours("");
    setDesc("");
    fetchLogs();
    refreshTasks();
  };

  const totalHours = logs.reduce((sum, l) => sum + l.hours, 0);

  return (
    <div className="modal show d-block" style={{ background: "rgba(0,0,0,0.5)" }}>
      <div className="modal-dialog">
        <div className="modal-content p-3">

          <div className="d-flex justify-content-between">
            <h5>{task.title}</h5>
            <button className="btn btn-sm btn-danger" onClick={onClose}>X</button>
          </div>

          <hr />

          {/* Add Log */}
          <h6>Add Time Log</h6>

          <input
            type="date"
            className="form-control my-2"
            value={date}
            onChange={(e) => setDate(e.target.value)}
          />

          <input
            type="number"
            className="form-control my-2"
            placeholder="Hours"
            value={hours}
            onChange={(e) => setHours(e.target.value)}
          />

          <input
            className="form-control my-2"
            placeholder="Description"
            value={desc}
            onChange={(e) => setDesc(e.target.value)}
          />

          <button className="btn btn-dark w-100" onClick={addLog}>
            Add Log
          </button>

          <hr />

          {/* Logs List */}
          <h6>Logs (Total: {totalHours}h)</h6>

          {logs.map((log) => (
            <div key={log.id} className="card p-2 my-2">
              <strong>{log.hours}h</strong> — {log.date}
              <div className="text-muted small">{log.description}</div>
            </div>
          ))}

        </div>
      </div>
    </div>
  );
}

export default TaskModal;