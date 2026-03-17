import { useState } from "react";
import { useUser } from "../../contexts";
import { useSearchParams, Link } from "react-router-dom";
import "./Auth.css";

export default function ResetPasswordPage() {
  const { resetPassword } = useUser();
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") || "";
  const [password, setPassword] = useState("");
  const [confirmPw, setConfirmPw] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (password !== confirmPw) {
      setError("Passwords do not match");
      return;
    }

    if (!token) {
      setError("Invalid reset link");
      return;
    }

    setLoading(true);
    try {
      const msg = await resetPassword(token, password);
      setSuccess(msg);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Reset failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <form className="auth-card" onSubmit={handleSubmit}>
        <h1 className="auth-title">Reset Password</h1>
        <p className="auth-subtitle">Enter your new password</p>

        {error && <div className="auth-error">{error}</div>}
        {success && <div className="auth-success">{success}</div>}

        <label className="auth-label">
          New Password
          <input
            className="auth-input"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={6}
            autoFocus
          />
        </label>

        <label className="auth-label">
          Confirm Password
          <input
            className="auth-input"
            type="password"
            value={confirmPw}
            onChange={(e) => setConfirmPw(e.target.value)}
            required
            minLength={6}
          />
        </label>

        <button className="auth-btn" type="submit" disabled={loading}>
          {loading ? "Resetting…" : "Reset Password"}
        </button>

        <div className="auth-links">
          <Link to="/login">Back to Sign In</Link>
        </div>
      </form>
    </div>
  );
}
