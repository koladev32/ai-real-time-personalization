// utils/tracking.js
import { getSessionId, setSessionId } from "./session"; // Utility functions to manage session ID

// Track an event
export async function trackEvent(eventType, additionalData = {}) {
  const sessionId = getSessionId();

  const eventData = {
    session_id: sessionId,
    event_type: eventType,
    timestamp: new Date().toISOString(),
    ...additionalData,
  };

  try {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/track`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(eventData),
      }
    );

    if (!response.ok) {
      throw new Error(`Tracking failed: ${response.statusText}`);
    }

    const responseData = await response.json();
    console.log("Event tracked:", responseData);
  } catch (error) {
    console.error("Error tracking event:", error);
  }
}
