// components/Pagination.js
"use client";

export default function Pagination({ currentPage, totalPages, onPageChange }) {
  return (
    <div className="flex justify-center mt-6">
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        className="px-4 py-2 bg-white text-gray-900 rounded-l disabled:opacity-50"
      >
        Previous
      </button>
      <span className="px-4 py-2 bg-white text-gray-900">
        {currentPage} / {totalPages}
      </span>
      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        className="px-4 py-2 bg-white text-gray-900 rounded-r disabled:opacity-50"
      >
        Next
      </button>
    </div>
  );
}
