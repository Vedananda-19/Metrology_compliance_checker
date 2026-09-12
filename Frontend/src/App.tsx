import { createBrowserRouter, RouterProvider } from "react-router-dom";
import RootLayout from "./layouts/RootLayout";
import ProtectedRoute from "./layouts/ProtectedRoute";
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
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
                    { path: "/dashboard", element: <Dashboard /> },
                    { path: "/scan", element: <Scan /> },
                    { path: "/inspection/:id", element: <Inspection /> },
                    { path: "/history", element: <History /> },
                ],
            },
        ],
    },
]);

function App() {
    return <RouterProvider router={router} />;
}

export default App;
