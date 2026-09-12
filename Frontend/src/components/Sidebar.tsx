import { Link, NavLink } from "react-router-dom";
import { queryClient } from "../main";
import type { User } from "../types/inspection";
import Icon, { type IconName } from "./Icon";

type NavItem = { to: string; label: string; icon: IconName; end?: boolean };

const OFFICER_LINKS: NavItem[] = [
    { to: "/officer", label: "Dashboard", icon: "gauge", end: true },
    { to: "/officer/board", label: "Case board", icon: "columns" },
    { to: "/officer/capture", label: "New inspection", icon: "aperture" },
];

const INSPECTOR_LINKS: NavItem[] = [
    { to: "/inspector", label: "Case repository", icon: "stack", end: true },
];

const SHARED_LINKS: NavItem[] = [
    { to: "/history", label: "History", icon: "clock" },
    { to: "/rules", label: "Rule repository", icon: "book" },
];

const Sidebar = ({ user }: { user: User | null }) => {
    const primary = user ? (user.role === "INSPECTOR" ? INSPECTOR_LINKS : OFFICER_LINKS) : [];
    const links = user ? [...primary, ...SHARED_LINKS] : [];
    const home = user ? (user.role === "INSPECTOR" ? "/inspector" : "/officer") : "/";

    const signOut = () => {
        localStorage.removeItem("access_token");
        queryClient.clear();
        window.location.replace("/login");
    };

    return (
        <aside className="sidebar">
            <Link to={home} className="sidebarBrand">
                <span className="sidebarMark" aria-hidden="true">
                    <Icon name="vault" size={18} />
                </span>
                <span className="sidebarBrandText">
                    <strong>MetroGuard</strong>
                    <small>Legal Metrology</small>
                </span>
            </Link>

            <nav className="sidebarNav" aria-label="Main">
                {links.map((link) => (
                    <NavLink key={link.to} to={link.to} end={link.end}>
                        <Icon name={link.icon} size={17} />
                        <span>{link.label}</span>
                    </NavLink>
                ))}

                {!user && (
                    <>
                        <NavLink to="/login">
                            <Icon name="exit" size={17} />
                            <span>Sign in</span>
                        </NavLink>
                        <NavLink to="/register">
                            <Icon name="spark" size={17} />
                            <span>Register</span>
                        </NavLink>
                    </>
                )}
            </nav>

            {user && (
                <div className="sidebarLower">
                    <button className="sidebarSignOut" onClick={signOut}>
                        <Icon name="exit" size={17} />
                        <span>Sign out</span>
                    </button>

                    <div className="supportCard">
                        <span className="supportBadge" aria-hidden="true">
                            <Icon name="book" size={16} />
                        </span>
                        <p>Checking a provision? The full 2011 rule text is searchable.</p>
                        <Link to="/rules" className="supportLink">
                            Open rule repository
                        </Link>
                    </div>
                </div>
            )}

            <div className="sidebarFoot">
                <span>Packaged Commodities Rules, 2011</span>
            </div>
        </aside>
    );
};

export default Sidebar;
