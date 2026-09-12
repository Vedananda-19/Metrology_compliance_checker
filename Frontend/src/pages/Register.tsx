import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api, { errorMessage } from "../apis/api";

function Register() {
    const [form, setForm] = useState({
        username: "",
        password: "",
        confirmPassword: "",
        full_name: "",
    });
    const [errorMsg, setErrorMsg] = useState("");
    const [busy, setBusy] = useState(false);
    const navigate = useNavigate();

    const update = (key: string) => (event: React.ChangeEvent<HTMLInputElement>) =>
        setForm((previous) => ({ ...previous, [key]: event.target.value }));

    const handleRegister = async (event: React.FormEvent) => {
        event.preventDefault();
        setBusy(true);
        try {
            await api.post("/auth/register", form);
            navigate("/login");
        } catch (error) {
            setErrorMsg(errorMessage(error, "Could not register"));
        } finally {
            setBusy(false);
        }
    };

    return (
        <div className="authPage">
            <div className="panel authCard">
                <form className="authForm" onSubmit={handleRegister}>
                    <div className="formHeading">
                        <h1>Register as inspector</h1>
                        <p>Create the account used to sign your inspection reports.</p>
                    </div>
                    <label className="fieldLabel">
                        Username
                        <input className="inset" value={form.username} onChange={update("username")} required autoFocus />
                    </label>
                    <div className="fieldRow">
                        <label className="fieldLabel">
                            Password
                            <input className="inset" type="password" value={form.password} onChange={update("password")} required />
                        </label>
                        <label className="fieldLabel">
                            Confirm password
                            <input
                                className="inset"
                                type="password"
                                value={form.confirmPassword}
                                onChange={update("confirmPassword")}
                                required
                            />
                        </label>
                    </div>
                    <label className="fieldLabel">
                        Full name
                        <input className="inset" value={form.full_name} onChange={update("full_name")} />
                    </label>
                    <button className="primaryButton" type="submit" disabled={busy}>
                        {busy ? "Creating…" : "Create account"}
                    </button>
                    {errorMsg && <p className="errorMessage">{errorMsg}</p>}
                    <Link className="authLink" to="/login">
                        Already registered? Sign in
                    </Link>
                </form>
            </div>
        </div>
    );
}

export default Register;
