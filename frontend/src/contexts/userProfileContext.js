// contexts/UserProfileContext.js
"use client";
import { createContext, useState, useEffect, useContext } from "react";
import { fetchFromAPI } from "../utils/api";

// Create the UserProfileContext
const UserProfileContext = createContext();

// Create a provider component
export function UserProfileProvider({ children }) {
  const [userProfile, setUserProfile] = useState(null);

  useEffect(() => {
    // Fetch user profile from API when the app loads
    async function fetchUserProfile() {
      try {
        const data = await fetchFromAPI("/user_profile");
        setUserProfile(data);
      } catch (error) {
        console.error("Failed to fetch user profile:", error);
      }
    }

    fetchUserProfile();
  }, []);

  return (
    <UserProfileContext.Provider value={{ userProfile, setUserProfile }}>
      {children}
    </UserProfileContext.Provider>
  );
}

// Custom hook to use the UserProfileContext in any component
export function useUserProfile() {
  return useContext(UserProfileContext);
}
