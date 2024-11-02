"use client";
const SORTING_OPTIONS_MAP = [
  {
    name: "Trending",
    field: "rating",
    order: "desc",
  },
  {
    name: "Latest arrivals",
    field: "created_at",
    order: "desc",
  },
  {
    name: "Price: Low to high",
    field: "price",
    order: "asc",
  },
  {
    name: "Price: High to low",
    field: "price",
    order: "desc",
  },
];

export default function SortMenu({ onSort }) {
  return (
    <div className="mb-6">
      <h3 className="text-lg font-bold mb-2">Sort by</h3>
      <ul>
        {SORTING_OPTIONS_MAP.map((option) => (
          <li
            key={option.name}
            onClick={() => onSort(option)}
            className="cursor-pointer hover:text-blue-400"
          >
            {option.name}
          </li>
        ))}
      </ul>
    </div>
  );
}
