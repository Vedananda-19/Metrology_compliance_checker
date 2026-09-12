import { useNavigate } from "react-router-dom";
import { queryClient } from "../main";
import type { User } from "../types/inspection";

const Topbar = ({ user }: { user: User | null }) => {
    const navigate = useNavigate();

    const handleLogout = () => {
        localStorage.removeItem("access_token");
        queryClient.clear();
        navigate("/");
    };

    return (
        <header className="topbar">
            <div className="topbarLeft">
                <span className="topbarTitle">Packaged Commodity Compliance</span>
            </div>

            {user ? (
                <div className="topbarRight">
                    <span className="muted small">Signed in as</span>
                    <span className="topbarUser">
                        {user.role === "INSPECTOR" ? "Inspector" : "Enforcement Officer"} —{" "}
                        {user.full_name || user.username}
                    </span>
                    <button className="ghostButton small" onClick={handleLogout}>
                        Sign out
                    </button>
                </div>
            ) : (
                <div className="topbarRight">
                    <span className="muted small">Not signed in</span>
                </div>
            )}
        </header>
    );
};

export default Topbar;
