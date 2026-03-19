import { Navigate, useParams } from "react-router-dom";
import { PictureScreening } from "../../components/PictureScreening";

export default function ScreeningPage() {
  const { tableName } = useParams<{ tableName: string }>();
  if (!tableName) return <Navigate to="/" replace />;
  return <PictureScreening tableName={tableName} />;
}