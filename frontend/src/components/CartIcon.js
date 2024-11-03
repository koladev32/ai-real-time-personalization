// components/CartIcon.js
export default function CartIcon({ count, onClick }) {
  return (
    <div className="relative cursor-pointer" onClick={onClick}>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        className="w-6 h-6 text-white"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          d="M3 3h18l-2 13H5L3 3z"
        />
      </svg>
      {count > 0 && (
        <span className="absolute top-0 right-0 bg-blue-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs">
          {count}
        </span>
      )}
    </div>
  );
}