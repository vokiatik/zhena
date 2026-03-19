import { usePictureScreening } from "../../hooks/usePictureScreening";
import PictureViewer from "./PictureViewer";
import "./PictureScreening.css";

interface PictureScreeningProps {
  tableName: string;
}

export default function PictureScreening({ tableName }: PictureScreeningProps) {
  const {
    currentPicture,
    previousPicture,
    currentIndex,
    total,
    isLoading,
    error,
    verifyAndNext,
    goBack,
  } = usePictureScreening(tableName);

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
        <h2>Picture Screening — {tableName}</h2>
        <span className="ps-counter">{currentIndex + 1} / {total}</span>
      </div>
      <PictureViewer
        picture={currentPicture}
        previousPicture={previousPicture}
        onVerify={verifyAndNext}
        onGoBack={goBack}
      />
    </div>
  );
}
