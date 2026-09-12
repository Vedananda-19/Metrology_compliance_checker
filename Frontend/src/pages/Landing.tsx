import { Link } from "react-router-dom";
import useUser from "../hooks/useUser";

const PIPELINE = [
    { title: "Computer vision", body: "OpenCV prepares each panel and PaddleOCR reads the text, keeping every bounding box for evidence." },
    { title: "Structured extraction", body: "Declarations are pulled into typed fields with per-field confidence. Nothing is invented when a value is absent." },
    { title: "Deterministic rules", body: "A rule interpreter judges the package against the 2011 Rules. The model never decides compliance." },
    { title: "Inspector review", body: "Every machine value can be corrected. The original is kept alongside the correction for audit." },
];

function Landing() {
    const { data: user } = useUser();

    return (
        <div className="landing">
            <section className="panel landingHero">
                <span className="pill">Stage 1 prototype</span>
                <h1>Check packaged commodities against the Legal Metrology Rules, 2011</h1>
                <p>
                    Upload photographs of a package. The system reads the declarations, works out which provisions
                    apply, evaluates them with a deterministic rule engine, and produces a signed inspection report.
                </p>
                <div className="landingActions">
                    {user ? (
                        <Link className="primaryButton" to={user.role === "INSPECTOR" ? "/inspector" : "/officer"}>
                            Go to your dashboard
                        </Link>
                    ) : (
                        <>
                            <Link className="primaryButton" to="/register">
                                Register as inspector
                            </Link>
                            <Link className="ghostButton" to="/login">
                                Sign in
                            </Link>
                        </>
                    )}
                </div>
            </section>

            <section className="cardGrid">
                {PIPELINE.map((item) => (
                    <article key={item.title} className="panel landingCard">
                        <h3>{item.title}</h3>
                        <p>{item.body}</p>
                    </article>
                ))}
            </section>

            <section className="panel landingNote">
                <h3>What the system will not claim</h3>
                <p>
                    Font height, net quantity error and lot sampling need physical measurement, and registration needs a
                    registry lookup. Those provisions are reported as requiring verification rather than marked
                    compliant, so an unverifiable requirement is never mistaken for a passing one.
                </p>
            </section>
        </div>
    );
}

export default Landing;
