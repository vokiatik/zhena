import { Navigate, useParams } from "react-router-dom";
import { PictureScreening } from "../../components/PictureScreening";

export default function ScreeningPage() {
    const { role, processId } = useParams<{ role?: string; processId?: string }>();

    if (processId) {
        return <PictureScreening role="process" processId={processId} />;
    }

    if (!role) return <Navigate to="/" replace />;
    return <PictureScreening role={role} />;
}