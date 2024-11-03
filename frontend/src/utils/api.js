// utils/api.js
import { getSessionId } from "./session";

export async function fetchFromAPI(endpoint, options = {}) {
  const url = new URL(`${process.env.NEXT_PUBLIC_API_BASE_URL}${endpoint}`);

  // Attach query parameters for GET requests
  if (options.params) {
    Object.keys(options.params).forEach((key) =>
      url.searchParams.append(key, options.params[key])
    );
  }

  // Include session ID as a query parameter for GET requests or as part of the body for POST requests
  const sessionId = getSessionId();
  if (sessionId !== null && sessionId !== "") {
    if (options.method && options.method.toUpperCase() === "POST") {
      // Add session_id to the request body for POST requests
      options.body = JSON.stringify({
        session_id: sessionId,
        ...(options.body ? JSON.parse(options.body) : {}),
      });
    } else {
      // Add session_id as a query parameter for GET requests
      url.searchParams.append("session_id", sessionId);
    }
  }

  // Set default method to GET if not provided
  const fetchOptions = {
    method: options.method || "GET",
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...(options.body ? { body: options.body } : {}),
  };

  // Perform the fetch
  const response = await fetch(url, fetchOptions);

  if (!response.ok) {
    throw new Error(`Failed to fetch: ${response.statusText}`);
  }

  return await response.json();
}
