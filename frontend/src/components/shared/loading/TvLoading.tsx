import "./TvLoading.css";

type TvLoadingProps = {
    text?: string;
};

export default function TvLoading({
    text = "Loading...",
}: TvLoadingProps) {
    return (
        <div className="tv-loading-page">
            <div className="tv-noise" />
            <div className="tv-scanlines" />
            <div className="tv-vignette" />

            <div className="tv-content">
                <div className="tv-screen">
                    <div className="tv-flicker" />
                    <div className="tv-rolling-band" />

                    <div className="tv-center">
                        <div className="tv-spinner">
                            <span />
                            <span />
                            <span />
                        </div>

                        <h1 className="tv-title">{text}</h1>
                        <p className="tv-subtitle">Please wait while the signal stabilizes</p>
                    </div>
                </div>
            </div>
        </div>
    );
}