import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import API from "../services/api";
import Navbar from "../components/Navbar";

import {
  DragDropContext,
  Droppable,
  Draggable,
} from "@hello-pangea/dnd";


const columns = ["pending", "ongoing", "completed"];

function TaskBoard() {
  const { id } = useParams();
  const [tasks, setTasks] = useState([]);
  const [title, setTitle] = useState("");

  const fetchTasks = async () => {
    const res = await API.get(`/tasks/client/${id}`);
    setTasks(res.data);
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  const addTask = async () => {
    if (!title) return;

    await API.post(`/tasks/client/${id}`, {
      title,
      description: "",
    });

    setTitle("");
    fetchTasks();
  };

  // 🔥 DRAG LOGIC
  const handleDragEnd = async (result) => {
    if (!result.destination) return;

    const { draggableId, destination } = result;

    const taskId = parseInt(draggableId);
    const newStatus = destination.droppableId;
    const newPosition = destination.index;

    await API.patch("/tasks/reorder", {
      task_id: taskId,
      new_status: newStatus,
      new_position: newPosition,
    });

    fetchTasks();
  };

  // group tasks
  const grouped = {
    pending: [],
    ongoing: [],
    completed: [],
  };

  tasks.forEach((t) => {
    grouped[t.status].push(t);
  });

  // sort by priority
  columns.forEach((col) => {
    grouped[col].sort((a, b) => a.priority - b.priority);
  });

  return (
    <>
      <Navbar />

      <div className="container mt-4">
        <h3 className="mb-3">Task Board</h3>

        {/* Add Task */}
        <div className="d-flex mb-4">
          <input
            className="form-control me-2"
            placeholder="New task"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
          <button className="btn btn-dark" onClick={addTask}>
            Add
          </button>
        </div>

        <DragDropContext onDragEnd={handleDragEnd}>
          <div className="row">
            {columns.map((col) => (
              <div key={col} className="col-md-4">
                <h5 className="text-capitalize mb-2">{col}</h5>

                <Droppable droppableId={col}>
                  {(provided) => (
                    <div
                      ref={provided.innerRef}
                      {...provided.droppableProps}
                      className="p-2 bg-light rounded"
                      style={{ minHeight: "400px" }}
                    >
                      {grouped[col].map((task, index) => (
                        <Draggable
                          key={task.id}
                          draggableId={task.id.toString()}
                          index={index}
                        >
                          {(provided) => (
                            <div
                              ref={provided.innerRef}
                              {...provided.draggableProps}
                              {...provided.dragHandleProps}
                              className="card p-2 mb-2 shadow-sm"
                            >
                              <strong>{task.title}</strong>
                            </div>
                          )}
                        </Draggable>
                      ))}

                      {provided.placeholder}
                    </div>
                  )}
                </Droppable>
              </div>
            ))}
          </div>
        </DragDropContext>
      </div>
    </>
  );
}

export default TaskBoard;