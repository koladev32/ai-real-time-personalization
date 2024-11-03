import { getSessionId } from "./session";

// utils/api.js
export async function fetchFromAPI(endpoint, params = {}) {
  const url = new URL(`${process.env.NEXT_PUBLIC_API_BASE_URL}${endpoint}`);
  Object.keys(params).forEach((key) =>
    url.searchParams.append(key, params[key])
  );

  const sessionId = getSessionId();

  if (sessionId !== null && sessionId !== "") {
    url.searchParams.append("session_id", sessionId);
  }

  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch: ${response.statusText}`);
  }
  return await response.json();
}
