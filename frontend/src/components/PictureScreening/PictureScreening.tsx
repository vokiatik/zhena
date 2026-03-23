import { usePictureScreening } from "../../hooks/usePictureScreening";
import PictureViewer from "./PictureViewer";
import "./PictureScreening.css";

interface PictureScreeningProps {
    role: string;
}

export default function PictureScreening({ role }: PictureScreeningProps) {
    const {
        currentPicture,
        previousPicture,
        currentIndex,
        canCancelVerification,
        total,
        isLoading,
        error,
        verifyAndNext,
        goBack,
        unverify,
    } = usePictureScreening(role);

    if (isLoading) {
        return <div className="ps-container"><p className="ps-loading">Loading pictures…</p></div>;
    }

    if (error) {
        return <div className="ps-container"><p className="ps-error">{error}</p></div>;
    }

    if (!currentPicture) {
        return (
            <div className="ps-container">
                <p className="ps-done">All pictures have been verified!</p>
            </div>
        );
    }

    return (
        <div className="ps-container">
            <div className="ps-header">
                <h2>Picture Screening — {role}</h2>
                <span className="ps-counter">{currentIndex + 1} / {total}</span>
            </div>
            <PictureViewer
                picture={currentPicture}
                previousPicture={previousPicture}
                canCancelVerification={canCancelVerification}
                onVerify={verifyAndNext}
                onGoBack={goBack}
                onUnverify={unverify}
            />
        </div>
    );
}
