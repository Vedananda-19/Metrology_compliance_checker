import { createBrowserRouter, RouterProvider } from "react-router-dom";
import RootLayout from "./layouts/RootLayout";
import ProtectedRoute from "./layouts/ProtectedRoute";
import RoleRoute from "./layouts/RoleRoute";
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Register from "./pages/Register";
import OfficerDashboard from "./pages/OfficerDashboard";
import OfficerBoard from "./pages/OfficerBoard";
import OfficerCapture from "./pages/OfficerCapture";
import InspectorRepository from "./pages/InspectorRepository";
import InspectorBoard from "./pages/InspectorBoard";
import Rules from "./pages/Rules";
import Scan from "./pages/Scan";
import Inspection from "./pages/Inspection";
import History from "./pages/History";

const router = createBrowserRouter([
    {
        element: <RootLayout />,
        children: [
            { path: "/", element: <Landing /> },
            { path: "/login", element: <Login /> },
            { path: "/register", element: <Register /> },
            {
                element: <ProtectedRoute />,
                children: [
                    { path: "/inspection/:id", element: <Inspection /> },
                    { path: "/rules", element: <Rules /> },
                    { path: "/history", element: <History /> },
                    {
                        element: <RoleRoute allow="OFFICER" />,
                        children: [
                            { path: "/officer", element: <OfficerDashboard /> },
                            { path: "/officer/board", element: <OfficerBoard /> },
                            { path: "/officer/capture", element: <OfficerCapture /> },
                            { path: "/officer/upload", element: <Scan /> },
                        ],
                    },
                    {
                        element: <RoleRoute allow="INSPECTOR" />,
                        children: [
                            { path: "/inspector", element: <InspectorRepository /> },
                            { path: "/inspector/board/:officerId", element: <InspectorBoard /> },
                        ],
                    },
                ],
            },
        ],
    },
]);

function App() {
    return <RouterProvider router={router} />;
}

export default App;
