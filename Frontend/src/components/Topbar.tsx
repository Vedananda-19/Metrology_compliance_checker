import { useLocation } from "react-router-dom";
import type { User } from "../types/inspection";
import useTheme from "../hooks/useTheme";
import Icon from "./Icon";

const TITLES: { match: RegExp; title: string }[] = [
    { match: /^\/officer\/board/, title: "Case board" },
    { match: /^\/officer\/capture/, title: "New inspection" },
    { match: /^\/officer\/upload/, title: "Upload images" },
    { match: /^\/officer/, title: "Dashboard" },
    { match: /^\/inspector\/board/, title: "Officer case board" },
    { match: /^\/inspector/, title: "Case repository" },
    { match: /^\/inspection\//, title: "Inspection" },
    { match: /^\/rules/, title: "Rule repository" },
    { match: /^\/history/, title: "History" },
    { match: /^\/login/, title: "Sign in" },
    { match: /^\/register/, title: "Register" },
];

const initialsOf = (user: User) => {
    const source = user.full_name?.trim() || user.username;
    const parts = source.split(/\s+/).filter(Boolean);
    const letters = parts.length > 1 ? parts[0][0] + parts[parts.length - 1][0] : source.slice(0, 2);
    return letters.toUpperCase();
};

const Topbar = ({ user }: { user: User | null }) => {
    const { pathname } = useLocation();
    const { theme, toggle } = useTheme();

    const title = TITLES.find((entry) => entry.match.test(pathname))?.title ?? "Packaged commodity compliance";

    return (
        <header className="topbar">
            <h1 className="topbarTitle">{title}</h1>

            <div className="topbarRight">
                <button
                    className="themeToggle"
                    onClick={toggle}
                    aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}
                    title={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}
                >
                    <span className={theme === "light" ? "isOn" : ""}>
                        <Icon name="sun" size={15} />
                    </span>
                    <span className={theme === "dark" ? "isOn" : ""}>
                        <Icon name="moon" size={15} />
                    </span>
                </button>

                {user ? (
                    <div className="topbarUser">
                        <span className="avatar" aria-hidden="true">
                            {initialsOf(user)}
                        </span>
                        <span className="topbarUserText">
                            <strong>{user.full_name || user.username}</strong>
                            <small>{user.role === "INSPECTOR" ? "Inspector" : "Enforcement Officer"}</small>
                        </span>
                    </div>
                ) : (
                    <span className="muted small">Not signed in</span>
                )}
            </div>
        </header>
    );
};

export default Topbar;
