import { useNavigate } from "react-router-dom";

function Navbar() {
  const navigate = useNavigate();

  const logout = () => {
    localStorage.removeItem("token");
    navigate("/");
  };

  return (
    <nav className="navbar navbar-dark bg-dark px-4 shadow-sm">
    <span
        className="navbar-brand app-title"
        style={{ cursor: "pointer" }}
        onClick={() => navigate("/dashboard")}
    >
        🚀 Innomight Task Manager
    </span>

    <button className="btn btn-outline-light btn-sm" onClick={logout}>
        Logout
    </button>
    </nav>
  );
}

export default Navbar;