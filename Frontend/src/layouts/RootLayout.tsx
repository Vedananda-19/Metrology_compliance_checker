import { Outlet } from "react-router-dom";

const RootLayout = () => {
    return (
        <div className="appShell">
            <main className="appMain">
                <Outlet />
            </main>
        </div>
    );
};

export default RootLayout;
