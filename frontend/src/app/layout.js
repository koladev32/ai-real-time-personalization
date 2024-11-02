// app/layout.js
import "./globals.css";
import Sidebar from "../components/Sidebar";

export const metadata = {
  title: "Ecommerce Store",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="flex min-h-screen bg-gray-900 text-white">
        <Sidebar />
        <main className="flex-1 p-6">{children}</main>
      </body>
    </html>
  );
}
