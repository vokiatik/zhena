import { Navigate, useParams } from "react-router-dom";
import { PictureScreening } from "../../components/PictureScreening";

export default function ScreeningPage() {
    const { processId } = useParams<{ processId?: string }>();

    if (!processId) return <Navigate to="/" replace />;
    return <PictureScreening processId={processId} />;
}