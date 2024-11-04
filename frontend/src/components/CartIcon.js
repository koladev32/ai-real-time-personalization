// components/CartIcon.js
export default function CartIcon({ count, onClick }) {
  return (
    <div className="relative cursor-pointer" onClick={onClick}>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 32 32"
        stroke="#171717"
        className="w-12 h-12 text-white"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          d="M3 3h18l-2 13H5L3 3z"
        />
      </svg>
      {count > 0 && (
        <span className="absolute top-4 right-2 bg-white text-gray-900 rounded-full w-5 h-5 flex items-center justify-center text-xs">
          {count}
        </span>
      )}
    </div>
  );
}
