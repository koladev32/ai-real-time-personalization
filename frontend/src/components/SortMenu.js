"use client";

export default function SortMenu({ onSort }) {
  const options = [
    "Relevance",
    "Trending",
    "Latest arrivals",
    "Price: Low to high",
    "Price: High to low",
  ];

  return (
    <div className="mb-6">
      <h3 className="text-lg font-bold mb-2">Sort by</h3>
      <ul>
        {options.map((option) => (
          <li
            key={option}
            onClick={() => onSort(option)}
            className="cursor-pointer hover:text-blue-400"
          >
            {option}
          </li>
        ))}
      </ul>
    </div>
  );
}
