import { Navigate, Outlet } from "react-router-dom";
import useUser from "../hooks/useUser";
import type { Role } from "../types/inspection";

const HOME: Record<Role, string> = { OFFICER: "/officer", INSPECTOR: "/inspector" };

const RoleRoute = ({ allow }: { allow: Role }) => {
    const { data: user, isLoading } = useUser();

    if (isLoading) return <div className="routeState"><h5>Loading…</h5></div>;
    if (!user) return <Navigate to="/login" replace />;
    if (user.role !== allow) return <Navigate to={HOME[user.role]} replace />;

    return <Outlet />;
};

export default RoleRoute;
