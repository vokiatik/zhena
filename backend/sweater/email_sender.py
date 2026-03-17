import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
SMTP_PORT = int(os.getenv("SMTP_PORT", "1025"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", "noreply@textanalyser.local")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "false").lower() == "true"


def _send_email(to: str, subject: str, html_body: str) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_FROM
    msg["To"] = to
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        if SMTP_USE_TLS:
            server.starttls()
        if SMTP_USER:
            server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_FROM, to, msg.as_string())


async def send_confirmation_email(to: str, confirm_url: str) -> None:
    html = f"""\
<html>
<body style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
  <h2>Welcome to Text Analyser!</h2>
  <p>Please confirm your email address by clicking the button below:</p>
  <p style="margin: 24px 0;">
    <a href="{confirm_url}"
       style="background: #5a8dee; color: white; padding: 12px 24px;
              border-radius: 6px; text-decoration: none; font-weight: bold;">
      Confirm Email
    </a>
  </p>
  <p style="color: #888; font-size: 0.85rem;">
    This link will expire in 24 hours. If you did not create an account, ignore this email.
  </p>
</body>
</html>"""
    _send_email(to, "Confirm your email — Text Analyser", html)


async def send_password_reset_email(to: str, reset_url: str) -> None:
    html = f"""\
<html>
<body style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
  <h2>Password Reset</h2>
  <p>You requested a password reset. Click the button below to set a new password:</p>
  <p style="margin: 24px 0;">
    <a href="{reset_url}"
       style="background: #5a8dee; color: white; padding: 12px 24px;
              border-radius: 6px; text-decoration: none; font-weight: bold;">
      Reset Password
    </a>
  </p>
  <p style="color: #888; font-size: 0.85rem;">
    This link will expire in 1 hour. If you did not request this, ignore this email.
  </p>
</body>
</html>"""
    _send_email(to, "Reset your password — Text Analyser", html)
