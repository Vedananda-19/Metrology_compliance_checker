import { Outlet, useLocation, useNavigate } from "react-router-dom";
import axios from "axios";
import useUser from "../hooks/useUser";

const ProtectedRoute = () => {
    const { data: user, isLoading, error } = useUser();
    const navigate = useNavigate();
    const location = useLocation();

    if (isLoading) {
        return (
            <div className="routeState">
                <h5>Loading…</h5>
            </div>
        );
    }

    if (!user || (axios.isAxiosError(error) && error.response?.status === 401)) {
        return (
            <div className="routeState">
                <h3>Sign in required</h3>
                <p>This inspection record is only visible to signed-in officers.</p>
                <button
                    className="primaryButton"
                    onClick={() => navigate("/login", { state: { from: location }, replace: true })}
                >
                    Sign in
                </button>
            </div>
        );
    }

    if (error) {
        return (
            <div className="routeState">
                <p>An error occurred loading your session.</p>
            </div>
        );
    }

    return <Outlet />;
};

export default ProtectedRoute;
