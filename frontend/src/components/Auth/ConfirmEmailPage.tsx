import { useState, useEffect } from "react";
import { useUser } from "../../contexts";
import { useSearchParams, Link } from "react-router-dom";
import "./Auth.css";

export default function ConfirmEmailPage() {
  const { confirmEmail } = useUser();
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") || "";
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setMessage("Invalid confirmation link.");
      return;
    }

    confirmEmail(token)
      .then((msg) => {
        setStatus("success");
        setMessage(msg);
      })
      .catch((err) => {
        setStatus("error");
        setMessage(err.response?.data?.detail || "Confirmation failed");
      });
  }, [token, confirmEmail]);

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-title">Email Confirmation</h1>

        {status === "loading" && <p className="auth-subtitle">Confirming your email…</p>}
        {status === "success" && <div className="auth-success">{message}</div>}
        {status === "error" && <div className="auth-error">{message}</div>}

        <div className="auth-links">
          <Link to="/login">Go to Sign In</Link>
        </div>
      </div>
    </div>
  );
}
