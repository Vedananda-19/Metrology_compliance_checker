import { Navigate, Outlet, useLocation } from "react-router-dom";
import useUser from "../hooks/useUser";

const ProtectedRoute = () => {
    const { data: user, isLoading } = useUser();
    const location = useLocation();

    if (isLoading) {
        return (
            <div className="routeState">
                <h5>Loading…</h5>
            </div>
        );
    }

    if (!user) return <Navigate to="/login" state={{ from: location }} replace />;

    return <Outlet />;
};

export default ProtectedRoute;

