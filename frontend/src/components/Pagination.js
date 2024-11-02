// components/Pagination.js
"use client";

export default function Pagination({ currentPage, totalPages, onPageChange }) {
  return (
    <div className="flex justify-center mt-6">
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        className="px-4 py-2 bg-gray-700 text-white rounded-l disabled:opacity-50"
      >
        Previous
      </button>
      <span className="px-4 py-2 bg-gray-900 text-white">
        {currentPage} / {totalPages}
      </span>
      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        className="px-4 py-2 bg-gray-700 text-white rounded-r disabled:opacity-50"
      >
        Next
      </button>
    </div>
  );
}
