import { Link, NavLink, useNavigate } from "react-router-dom";
import { queryClient } from "../main";
import type { User } from "../types/inspection";

const Navbar = ({ user }: { user: User | null }) => {
    const navigate = useNavigate();

    const handleLogout = () => {
        localStorage.removeItem("access_token");
        queryClient.removeQueries({ queryKey: ["user"] });
        navigate("/");
    };

    return (
        <header className="navbar">
            <Link to={user ? "/dashboard" : "/"} className="brand">
                <span className="brandMark">LM</span>
                <span className="brandText">
                    <strong>Packaged Commodity Compliance</strong>
                    <small>Legal Metrology Rules, 2011</small>
                </span>
            </Link>

            {user ? (
                <nav className="navLinks">
                    <NavLink to="/dashboard">Dashboard</NavLink>
                    <NavLink to="/scan">New inspection</NavLink>
                    <NavLink to="/history">History</NavLink>
                    <div className="navUser">
                        <span className="navUserName">{user.full_name || user.username}</span>
                    </div>
                    <button className="ghostButton" onClick={handleLogout}>
                        Sign out
                    </button>
                </nav>
            ) : (
                <nav className="navLinks">
                    <NavLink to="/login">Sign in</NavLink>
                    <Link to="/register" className="primaryButton small">
                        Register
                    </Link>
                </nav>
            )}
        </header>
    );
};

export default Navbar;
