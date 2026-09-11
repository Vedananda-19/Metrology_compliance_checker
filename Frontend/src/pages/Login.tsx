import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import api, { errorMessage } from "../apis/api";
import { queryClient } from "../main";

function Login() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [errorMsg, setErrorMsg] = useState("");
    const [busy, setBusy] = useState(false);
    const navigate = useNavigate();
    const location = useLocation();

    const handleLogin = async (event: React.FormEvent) => {
        event.preventDefault();
        setBusy(true);
        const formData = new URLSearchParams();
        formData.append("username", username);
        formData.append("password", password);
        try {
            const response = await api.post("/auth/login", formData, {
                headers: { "Content-type": "application/x-www-form-urlencoded" },
            });
            localStorage.setItem("access_token", response.data.access_token);
            queryClient.invalidateQueries({ queryKey: ["user"] });
            setErrorMsg("");
            navigate(location.state?.from?.pathname ?? "/dashboard");
        } catch (error) {
            setErrorMsg(errorMessage(error, "Could not sign in"));
            setPassword("");
        } finally {
            setBusy(false);
        }
    };

    return (
        <div className="authPage">
            <div className="panel authCard">
                <form className="authForm" onSubmit={handleLogin}>
                    <div className="formHeading">
                        <h1>Inspector sign in</h1>
                        <p>Access your packaged commodity inspections.</p>
                    </div>
                    <label className="fieldLabel">
                        Username
                        <input
                            className="inset"
                            type="text"
                            value={username}
                            onChange={(event) => setUsername(event.target.value)}
                            required
                            autoFocus
                        />
                    </label>
                    <label className="fieldLabel">
                        Password
                        <input
                            className="inset"
                            type="password"
                            value={password}
                            onChange={(event) => setPassword(event.target.value)}
                            required
                        />
                    </label>
                    <button className="primaryButton" type="submit" disabled={busy}>
                        {busy ? "Signing in…" : "Sign in"}
                    </button>
                    {errorMsg && <p className="errorMessage">{errorMsg}</p>}
                    <Link className="authLink" to="/register">
                        New officer? Register an account
                    </Link>
                </form>
            </div>
        </div>
    );
}

export default Login;
