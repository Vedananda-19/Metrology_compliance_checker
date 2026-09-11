import { Outlet } from "react-router-dom";
import Navbar from "../components/Navbar";
import useUser from "../hooks/useUser";

const RootLayout = () => {
    const { data: user } = useUser();

    return (
        <div className="appShell">
            <Navbar user={user ?? null} />
            <main className="appMain">
                <Outlet />
            </main>
        </div>
    );
};

export default RootLayout;
