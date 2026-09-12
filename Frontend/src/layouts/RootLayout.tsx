import { Outlet } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import useUser from "../hooks/useUser";

const RootLayout = () => {
    const { data: user } = useUser();

    return (
        <div className="appShell">
            <a className="skipLink" href="#content">
                Skip to content
            </a>
            <Sidebar user={user ?? null} />
            <div className="appBody">
                <Topbar user={user ?? null} />
                <main className="appMain" id="content">
                    <Outlet />
                </main>
            </div>
        </div>
    );
};

export default RootLayout;
