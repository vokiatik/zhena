import { useState } from "react";
import { useUser } from "../../contexts";
import { Link } from "react-router-dom";
import "./Auth.css";

export default function ForgotPasswordPage() {
  const { forgotPassword } = useUser();
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setLoading(true);
    try {
      const msg = await forgotPassword(email);
      setSuccess(msg);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Request failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <form className="auth-card" onSubmit={handleSubmit}>
        <h1 className="auth-title">Forgot Password</h1>
        <p className="auth-subtitle">Enter your email to receive a reset link</p>

        {error && <div className="auth-error">{error}</div>}
        {success && <div className="auth-success">{success}</div>}

        <label className="auth-label">
          Email
          <input
            className="auth-input"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoFocus
          />
        </label>

        <button className="auth-btn" type="submit" disabled={loading}>
          {loading ? "Sending…" : "Send Reset Link"}
        </button>

        <div className="auth-links">
          <Link to="/login">Back to Sign In</Link>
        </div>
      </form>
    </div>
  );
}
