import { Outlet } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import useUser from "../hooks/useUser";

const RootLayout = () => {
    const { data: user } = useUser();

    return (
        <div className="appShell">
            <Sidebar user={user ?? null} />
            <div className="appBody">
                <Topbar user={user ?? null} />
                <main className="appMain">
                    <Outlet />
                </main>
            </div>
        </div>
    );
};

export default RootLayout;
