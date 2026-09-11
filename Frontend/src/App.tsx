import { createBrowserRouter, RouterProvider } from "react-router-dom";
import RootLayout from "./layouts/RootLayout";
import Home from "./pages/Home";

const router = createBrowserRouter([
    {
        element: <RootLayout />,
        children: [{ path: "/", element: <Home /> }],
    },
]);

function App() {
    return <RouterProvider router={router} />;
}

export default App;
