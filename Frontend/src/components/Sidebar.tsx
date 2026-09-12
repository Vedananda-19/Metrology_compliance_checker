import { Link, NavLink } from "react-router-dom";
import type { User } from "../types/inspection";

const OFFICER_LINKS = [
    { to: "/officer", label: "Dashboard", end: true },
    { to: "/officer/board", label: "Inspection case board" },
    { to: "/officer/capture", label: "New inspection" },
    { to: "/officer/upload", label: "Upload images" },
    { to: "/history", label: "Inspection history" },
    { to: "/rules", label: "Rule repository" },
];

const INSPECTOR_LINKS = [
    { to: "/inspector", label: "Case repository", end: true },
    { to: "/history", label: "Inspection history" },
    { to: "/rules", label: "Rule repository" },
];

const Sidebar = ({ user }: { user: User | null }) => {
    const links = user ? (user.role === "INSPECTOR" ? INSPECTOR_LINKS : OFFICER_LINKS) : [];
    const home = user ? (user.role === "INSPECTOR" ? "/inspector" : "/officer") : "/";

    return (
        <aside className="sidebar">
            <Link to={home} className="sidebarBrand">
                <strong>MetroGuard</strong>
                <small>Legal Metrology Compliance</small>
            </Link>

            <nav className="sidebarNav">
                {links.map((link) => (
                    <NavLink key={link.to} to={link.to} end={link.end}>
                        {link.label}
                    </NavLink>
                ))}
                {!user && (
                    <>
                        <NavLink to="/login">Sign in</NavLink>
                        <NavLink to="/register">Register</NavLink>
                    </>
                )}
            </nav>

            <div className="sidebarFoot">
                <span>Legal Metrology (Packaged Commodities) Rules, 2011</span>
            </div>
        </aside>
    );
};

export default Sidebar;
