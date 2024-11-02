"use client";

export default function SearchBar({ onSearch }) {
  return (
    <div className="relative mb-6">
      <input
        type="text"
        placeholder="Search for products..."
        onChange={(e) => onSearch(e.target.value)}
        className="w-full p-3 bg-gray-700 text-white rounded-md focus:outline-none"
      />
      <span className="absolute right-3 top-3 text-gray-500">🔍</span>
    </div>
  );
}
