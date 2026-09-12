import Icon, { type IconName } from "./Icon";

type Props = {
    label: string;
    value: number | string;
    icon: IconName;
    tone?: "brand" | "good" | "bad" | "warn";
    /** Signed change versus the previous period; omitted when there is no prior data. */
    delta?: number | null;
    deltaNote?: string;
    /** When true a rising delta is bad news (e.g. violations going up). */
    invertDelta?: boolean;
};

const StatCard = ({ label, value, icon, tone = "brand", delta, deltaNote, invertDelta }: Props) => {
    const hasDelta = typeof delta === "number" && Number.isFinite(delta);
    const rising = hasDelta && delta > 0;
    const flat = hasDelta && delta === 0;
    const good = invertDelta ? !rising : rising;

    return (
        <article className={`statCard statCard-${tone}`}>
            <header>
                <span className="statCardLabel">{label}</span>
                <span className="statCardIcon">
                    <Icon name={icon} size={17} />
                </span>
            </header>

            <strong className="statCardValue">{value}</strong>

            {hasDelta && !flat && (
                <p className={`statCardDelta ${good ? "isUp" : "isDown"}`}>
                    <span aria-hidden="true">{rising ? "▲" : "▼"}</span>
                    {Math.abs(delta)}%
                    {deltaNote && <span className="statCardDeltaNote">{deltaNote}</span>}
                </p>
            )}

            {hasDelta && flat && (
                <p className="statCardDelta isFlat">
                    No change
                    {deltaNote && <span className="statCardDeltaNote">{deltaNote}</span>}
                </p>
            )}
        </article>
    );
};

export default StatCard;
