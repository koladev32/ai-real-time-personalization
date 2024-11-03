// app/layout.js
import "./globals.css";

export const metadata = {
  title: "Ecommerce Store",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="flex min-h-screen bg-gray-900 text-white">
        {children}
      </body>
    </html>
  );
}
