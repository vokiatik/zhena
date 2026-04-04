import { Navigate } from "react-router-dom";
import { useUser } from "../../contexts";

interface RoleGuardProps {
    children: React.ReactNode;
    allowedRoles: string[];
    fallbackPath?: string;
}

/**
 * Wraps a route so only users with at least one of the allowedRoles can access it.
 * Admin always passes. Users with no roles assigned are denied.
 * Unauthenticated users are sent to /login.
 */
export default function RoleGuard({
    children,
    allowedRoles,
    fallbackPath,
}: RoleGuardProps) {
    const { user, isLoading, hasAnyRole } = useUser();

    if (isLoading) return null;
    if (!user) return <Navigate to="/login" replace />;

    if (!hasAnyRole(...allowedRoles)) {
        if (fallbackPath) {
            return <Navigate to={fallbackPath} replace />;
        }
        return <Navigate to="/login" replace />;
    }

    return <>{children}</>;
}
