// app/layout.js
import { UserProfileProvider } from "@/contexts/userProfileContext";
import "./globals.css";

export const metadata = {
  title: "Ecommerce Store",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="flex min-h-screen bg-white text-gray-900">
        <UserProfileProvider>{children}</UserProfileProvider>
      </body>
    </html>
  );
}
