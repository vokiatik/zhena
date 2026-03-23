import { Navigate, useParams } from "react-router-dom";
import { PictureScreening } from "../../components/PictureScreening";

export default function ScreeningPage() {
    const { role } = useParams<{ role: string }>();
    if (!role) return <Navigate to="/" replace />;
    return <PictureScreening role={role} />;
}