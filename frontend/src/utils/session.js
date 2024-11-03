// utils/session.js
export function getSessionId() {
  const sessionKey = "session_id";
  const sessionExpiryKey = "session_expiry";

  // Check if session ID and expiry exist in localStorage
  let sessionId = localStorage.getItem(sessionKey);
  const sessionExpiry = localStorage.getItem(sessionExpiryKey);

  // If session is expired or doesn't exist, generate a new one
  if (!sessionId || new Date().getTime() > new Date(sessionExpiry)) {
    sessionId = crypto.randomUUID();
    const expiryTime = new Date(new Date().getTime() + 48 * 60 * 60 * 1000); // 48 hours
    localStorage.setItem(sessionKey, sessionId);
    localStorage.setItem(sessionExpiryKey, expiryTime.toString());
  }

  return sessionId;
}
