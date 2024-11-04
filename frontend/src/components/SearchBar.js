// components/SearchBar.js
"use client";

export default function SearchBar({ onSearch }) {
  return (
    <div className="relative mb-6 w-1/2">
      <input
        type="text"
        placeholder="Search for products..."
        onChange={(e) => onSearch(e.target.value)}
        className="w-full p-3 bg-white text-gray-900 rounded-md focus:outline-none border-2 border-gray-900"
      />
      <span className="absolute right-3 top-3 text-gray-500">🔍</span>
    </div>
  );
}
